#!/usr/bin/env python3
"""
BROskiPets FastAPI — HTTP bridge between the LLM pet agents and the on-chain contract.

Endpoints:
  GET  /health                        — service health check
  GET  /squad                         — list all 78 EEPs
  GET  /pet/{pet_id}                  — get full pet status
  POST /pet/{pet_id}/feed             — feed the pet
  POST /pet/{pet_id}/chat             — chat with the pet
  POST /pet/{pet_id}/evolve           — trigger full evolution pipeline (IPFS → chain)
  GET  /pet/{pet_id}/metadata         — current EIP-721 metadata JSON

Run:
  uvicorn api.main:app --reload --port 8080

Or via Docker:
  docker compose up
"""

import json
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

# Add project root to path so we can import agent / metadata
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def _load_local_env_file() -> None:
    """
    Load key=value pairs from project .env into os.environ (without overriding).

    This runs before importing modules that read env vars at import-time.
    """
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                os.environ.setdefault(key, value)


_load_local_env_file()

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent import BROskiPet, load_squad
from metadata import EEPMetadata
from api.chain import call_evolve_onchain

from rewards.ledger import RewardsLedger
from rewards.rules import decide_chat_reward, decide_evolve_reward, decide_feed_reward

# ── Squad index + lifespan ────────────────────────────────────────────────────

_squad_index: dict[str, dict] = {}
_pet_alias_index: dict[str, str] = {}
_rewards_ledger = RewardsLedger()


@asynccontextmanager
async def lifespan(app):
    """Index the squad JSON by pet_id for O(1) lookup on startup."""
    squad = load_squad("eeps/squad.json")
    for eep in squad:
        canonical_id = str(eep["id"])
        _squad_index[canonical_id] = eep

        # Support multiple input styles: 001, 1, SpiderEep, spider_eep, spider_001
        name = str(eep.get("name", "")).strip().lower()
        species = str(eep.get("species", "")).strip().lower()
        canonical_num = canonical_id.lstrip("0") or "0"

        aliases = {
            canonical_id.lower(),
            canonical_num,
            name,
            name.replace(" ", ""),
            name.replace(" ", "_"),
            name.replace(" ", "-"),
            species,
            species.replace(" ", ""),
            species.replace(" ", "_"),
            species.replace(" ", "-"),
            f"{species.replace(' ', '')}_{canonical_id}",
            f"{species.replace(' ', '_')}_{canonical_id}",
            f"{name.replace(' ', '')}_{canonical_id}",
            f"{name.replace(' ', '_')}_{canonical_id}",
        }

        for alias in aliases:
            _pet_alias_index[alias] = canonical_id
    yield
    # (shutdown logic goes here if needed)


# ── App setup ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="BROskiPets API",
    description="LLM-powered dNFT pet agents — EEPVengers squad",
    version="0.3.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production to your frontend domain
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _resolve_pet_id(pet_id: str) -> str:
    """Resolve user input pet_id to canonical squad ID (e.g. spider_001 -> 001)."""
    cleaned = pet_id.strip()
    if cleaned in _squad_index:
        return cleaned

    alias_hit = _pet_alias_index.get(cleaned.lower())
    if alias_hit:
        return alias_hit

    # Common pattern: "<label>_<number>" where number may be non-padded.
    if "_" in cleaned:
        suffix = cleaned.rsplit("_", 1)[-1]
        if suffix.isdigit():
            candidate = suffix.zfill(3)
            if candidate in _squad_index:
                return candidate

    raise HTTPException(
        status_code=404,
        detail=f"EEP '{pet_id}' not found. Try canonical IDs like '001' or aliases like 'spider_001'.",
    )


def _get_eep_data(pet_id: str) -> dict:
    """Return squad entry from canonical ID."""
    if pet_id not in _squad_index:
        raise HTTPException(status_code=404, detail=f"EEP '{pet_id}' not found in squad")
    return _squad_index[pet_id]


def _make_pet(pet_id: str) -> BROskiPet:
    """Construct a BROskiPet from squad data."""
    eep = _get_eep_data(pet_id)
    return BROskiPet(
        pet_id=eep["id"],
        name=eep["name"],
        species=eep["species"],
        personality=eep.get("power", "helpful and curious"),
    )


# ── Request / Response models ─────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500, description="Message to send to the pet")


class ChatResponse(BaseModel):
    pet_id: str
    name: str
    response: str
    state: dict
    reward: Optional[dict] = None


class FeedResponse(BaseModel):
    pet_id: str
    name: str
    result: str
    state: dict
    reward: Optional[dict] = None


class FeedRequest(BaseModel):
    action: Optional[str] = Field(None, description="feed|like|comment|share|post")
    target_id: Optional[str] = Field(None, description="Optional HyperCode entity id (post/comment/etc.)")


class EvolveRequest(BaseModel):
    token_id: int = Field(..., gt=0, description="On-chain ERC-721 token ID")
    image_cid: Optional[str] = Field(None, description="IPFS CID of the pet image for this stage")


class EvolveResponse(BaseModel):
    pet_id: str
    token_id: int
    metadata_cid: str
    new_stage: int
    level_name: str
    tx_hash: Optional[str] = None   # None when AGENT_KEY / CONTRACT_ADDRESS not configured
    message: str
    reward: Optional[dict] = None


class PetStatus(BaseModel):
    pet_id: str
    name: str
    species: str
    rarity: str
    level: int
    xp: int
    needs: dict
    personality: str


class AdminAwardRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=128)
    amount: int = Field(..., gt=0, description="BROski$ amount to award")
    reason: str = Field(..., min_length=3, max_length=300)
    pet_id: Optional[str] = Field(None, description="Optional associated pet id")
    source: str = Field("manual_admin_grant", min_length=3, max_length=100)
    vest_hours: int = Field(0, ge=0, le=24 * 30)
    metadata: dict = Field(default_factory=dict)


class AdminAwardResponse(BaseModel):
    status: str
    event_id: str
    user_id: str
    amount: int
    balance: int
    available_at: str


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health():
    """Service health check."""
    return {
        "status": "ok",
        "service": "BROskiPets API",
        "version": "0.3.0",
        "squad_loaded": len(_squad_index),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/squad", tags=["Squad"])
async def get_squad():
    """Return all 78 EEPs with their roles, powers, and rarities."""
    return {
        "total": len(_squad_index),
        "eeps": list(_squad_index.values()),
    }


@app.get("/squad/{rarity}", tags=["Squad"])
async def get_squad_by_rarity(rarity: str):
    """Filter EEPs by rarity tier (Common, Uncommon, Rare, Legendary, Quantum)."""
    valid = {"Common", "Uncommon", "Rare", "Legendary", "Quantum"}
    if rarity not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid rarity. Must be one of: {sorted(valid)}")
    filtered = [e for e in _squad_index.values() if e.get("rarity") == rarity]
    return {"rarity": rarity, "count": len(filtered), "eeps": filtered}


@app.get("/pet/{pet_id}", response_model=PetStatus, tags=["Pet"])
async def get_pet(pet_id: str):
    """Get full status for a single pet."""
    canonical_id = _resolve_pet_id(pet_id)
    eep_data = _get_eep_data(canonical_id)
    pet = _make_pet(canonical_id)
    status = pet.get_status()
    return PetStatus(
        pet_id=canonical_id,
        name=status["name"],
        species=status["species"],
        rarity=eep_data.get("rarity", "Common"),
        level=status["level"],
        xp=status["xp"],
        needs=status["needs"],
        personality=status["personality"],
    )


@app.post("/pet/{pet_id}/feed", response_model=FeedResponse, tags=["Pet"])
async def feed_pet(pet_id: str, request: Request, body: Optional[FeedRequest] = None):
    """
    Feed the pet.

    Reduces hunger by 20 (floor 0) and awards 10 XP.
    """
    canonical_id = _resolve_pet_id(pet_id)
    eep_data = _get_eep_data(canonical_id)  # validate pet exists
    pet = _make_pet(canonical_id)
    result = pet.feed()

    reward = None
    user_id = request.headers.get("x-user-id")
    idempotency_key = request.headers.get("x-idempotency-key")
    if user_id and idempotency_key:
        decision = decide_feed_reward(
            now=datetime.now(timezone.utc),
            rarity=eep_data.get("rarity", "Common"),
            action=(body.action if body else None) or "feed",
        )
        if decision:
            event_id = f"feed:{user_id}:{canonical_id}:{decision.trigger}:{idempotency_key}"
            applied = _rewards_ledger.apply_reward(
                event_id=event_id,
                user_id=user_id,
                pet_id=canonical_id,
                endpoint="/pet/{pet_id}/feed",
                trigger=decision.trigger,
                amount=decision.amount,
                multiplier=decision.multiplier,
                metadata={"action": (body.action if body else None) or "feed", "target_id": (body.target_id if body else None)},
                limit_key=decision.limit_key,
                limit_max_per_day=decision.limit_max_per_day,
                vest_hours=decision.vest_hours,
            )
            reward = {
                "status": applied.status,
                "event_id": applied.event_id,
                "amount": applied.final_amount,
                "balance": applied.balance,
                "available_at": applied.available_at,
            }
    elif user_id and not idempotency_key:
        reward = {"status": "skipped_missing_idempotency"}

    return FeedResponse(
        pet_id=canonical_id,
        name=pet.name,
        result=result,
        state=pet.get_state(),
        reward=reward,
    )


@app.post("/pet/{pet_id}/chat", response_model=ChatResponse, tags=["Pet"])
async def chat_with_pet(pet_id: str, body: ChatRequest, request: Request):
    """
    Send a message to the pet and get an LLM response.

    Input is checked against the VenomEep injection guard before reaching the LLM.
    """
    canonical_id = _resolve_pet_id(pet_id)
    eep_data = _get_eep_data(canonical_id)
    pet = _make_pet(canonical_id)
    response = pet.chat(body.message)

    reward = None
    user_id = request.headers.get("x-user-id")
    idempotency_key = request.headers.get("x-idempotency-key")
    blocked = "(blocked)" in response.lower()
    if user_id and idempotency_key:
        first_today_key = f"chat_first:{user_id}:{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
        already = len([e for e in _rewards_ledger.list_ledger(user_id, limit=200) if e.get("trigger") == "chat:first_today" and e.get("metadata", {}).get("day") == datetime.now(timezone.utc).strftime("%Y-%m-%d")]) > 0
        decision = decide_chat_reward(
            now=datetime.now(timezone.utc),
            rarity=eep_data.get("rarity", "Common"),
            message=body.message,
            blocked=blocked,
            is_first_message_today=not already,
        )
        if decision:
            trigger = decision.trigger
            if not already:
                trigger = "chat:first_today"
            event_id = f"chat:{user_id}:{canonical_id}:{trigger}:{idempotency_key}"
            applied = _rewards_ledger.apply_reward(
                event_id=event_id,
                user_id=user_id,
                pet_id=canonical_id,
                endpoint="/pet/{pet_id}/chat",
                trigger=trigger,
                amount=decision.amount,
                multiplier=decision.multiplier,
                metadata={"message_len": len(body.message), "blocked": blocked, "day": datetime.now(timezone.utc).strftime("%Y-%m-%d")},
                limit_key=decision.limit_key,
                limit_max_per_day=decision.limit_max_per_day,
                vest_hours=decision.vest_hours,
            )
            reward = {
                "status": applied.status,
                "event_id": applied.event_id,
                "amount": applied.final_amount,
                "balance": applied.balance,
                "available_at": applied.available_at,
            }
    elif user_id and not idempotency_key:
        reward = {"status": "skipped_missing_idempotency"}
    return ChatResponse(
        pet_id=canonical_id,
        name=pet.name,
        response=response,
        state=pet.get_state(),
        reward=reward,
    )



@app.post("/pet/{pet_id}/evolve", response_model=EvolveResponse, tags=["Evolution"])
async def evolve_pet(pet_id: str, body: EvolveRequest, request: Request):
    """
    Trigger the full evolution pipeline:
      1. Get current pet state from Redis
      2. Calculate level from XP
      3. Generate EIP-721 metadata JSON
      4. Upload metadata to IPFS via Pinata (idempotent — skips if state unchanged)
      5. Returns the metadata CID ready for contract.evolve()

    The caller is responsible for submitting the on-chain transaction.
    Requires PINATA_JWT environment variable.
    """
    canonical_id = _resolve_pet_id(pet_id)
    eep_data = _get_eep_data(canonical_id)
    pet = _make_pet(canonical_id)
    state = pet.get_state()

    if not state:
        raise HTTPException(status_code=404, detail=f"No Redis state found for pet '{canonical_id}'")

    eep_meta = EEPMetadata(
        pet_id=canonical_id,
        name=eep_data["name"],
        species=eep_data["species"],
        rarity=eep_data.get("rarity", "Common"),
        token_id=body.token_id,
    )

    level_info = eep_meta.calculate_level(state.get("xp", 0))
    previous_level = int(state.get("level", 1))
    pet.update_state({"level": int(level_info["level"])})

    try:
        metadata_cid = eep_meta.upload_metadata_to_ipfs(state, image_cid=body.image_cid)
    except EnvironmentError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    # ── On-chain evolve() ─────────────────────────────────────────────────────
    tx_hash: Optional[str] = None
    try:
        tx_hash = call_evolve_onchain(
            token_id=body.token_id,
            metadata_cid=metadata_cid,
            new_stage=level_info["level"],
        )
        onchain_msg = f"On-chain tx submitted: {tx_hash}"
    except EnvironmentError:
        # CONTRACT_ADDRESS / AGENT_KEY not set — offline / local mode
        onchain_msg = (
            f"IPFS upload complete. Call contract.evolve("
            f"{body.token_id}, '{metadata_cid}', {level_info['level']}) manually."
        )
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return EvolveResponse(
        pet_id=canonical_id,
        token_id=body.token_id,
        metadata_cid=metadata_cid,
        new_stage=level_info["level"],
        level_name=level_info["level_name"],
        tx_hash=tx_hash,
        message=f"{eep_data['name']} evolved to {level_info['level_name']}! {onchain_msg}",
        reward=_maybe_reward_evolve(request, canonical_id, eep_data.get("rarity", "Common"), previous_level, int(level_info["level"])),
    )


def _maybe_reward_evolve(request: Request, pet_id: str, rarity: str, previous_level: int, new_level: int) -> Optional[dict]:
    user_id = request.headers.get("x-user-id")
    idempotency_key = request.headers.get("x-idempotency-key")
    if not user_id:
        return None
    if not idempotency_key:
        return {"status": "skipped_missing_idempotency"}

    decision = decide_evolve_reward(
        now=datetime.now(timezone.utc),
        rarity=rarity,
        previous_level=previous_level,
        new_level=new_level,
    )
    if not decision:
        return None

    event_id = f"evolve:{user_id}:{pet_id}:{decision.trigger}:{idempotency_key}"
    applied = _rewards_ledger.apply_reward(
        event_id=event_id,
        user_id=user_id,
        pet_id=pet_id,
        endpoint="/pet/{pet_id}/evolve",
        trigger=decision.trigger,
        amount=decision.amount,
        multiplier=decision.multiplier,
        metadata={"previous_level": previous_level, "new_level": new_level},
        limit_key=decision.limit_key,
        limit_max_per_day=decision.limit_max_per_day,
        vest_hours=decision.vest_hours,
    )
    return {
        "status": applied.status,
        "event_id": applied.event_id,
        "amount": applied.final_amount,
        "balance": applied.balance,
        "available_at": applied.available_at,
    }


@app.get("/rewards/balance", tags=["Rewards"])
async def get_rewards_balance(request: Request):
    user_id = request.headers.get("x-user-id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing X-User-Id header")
    return {"user_id": user_id, "balance": _rewards_ledger.get_balance(user_id)}


@app.get("/rewards/ledger", tags=["Rewards"])
async def get_rewards_ledger(request: Request, limit: int = 50):
    user_id = request.headers.get("x-user-id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing X-User-Id header")
    limit = max(1, min(int(limit), 200))
    return {"user_id": user_id, "entries": _rewards_ledger.list_ledger(user_id, limit=limit)}


def _require_rewards_admin(request: Request) -> None:
    expected = os.getenv("REWARDS_ADMIN_TOKEN", "").strip()
    if not expected:
        raise HTTPException(status_code=503, detail="REWARDS_ADMIN_TOKEN not configured")
    got = request.headers.get("x-admin-token", "").strip()
    if not got or got != expected:
        raise HTTPException(status_code=403, detail="Forbidden: invalid admin token")


@app.post("/rewards/award", response_model=AdminAwardResponse, tags=["Rewards"])
async def rewards_award(body: AdminAwardRequest, request: Request):
    """
    Admin-only reward grant endpoint.

    Required headers:
      - X-Admin-Token
      - X-Idempotency-Key
    """
    _require_rewards_admin(request)
    idempotency_key = request.headers.get("x-idempotency-key", "").strip()
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Missing X-Idempotency-Key header")

    event_id = f"admin:{body.source}:{body.user_id}:{idempotency_key}"
    applied = _rewards_ledger.apply_reward(
        event_id=event_id,
        user_id=body.user_id,
        pet_id=body.pet_id,
        endpoint="/rewards/award",
        trigger=f"admin:{body.source}",
        amount=int(body.amount),
        multiplier=1.0,
        metadata={
            "reason": body.reason,
            "source": body.source,
            **(body.metadata or {}),
        },
        limit_key=None,
        limit_max_per_day=None,
        vest_hours=int(body.vest_hours),
    )
    return AdminAwardResponse(
        status=applied.status,
        event_id=applied.event_id,
        user_id=body.user_id,
        amount=applied.final_amount,
        balance=applied.balance,
        available_at=applied.available_at,
    )


@app.get("/pet/{pet_id}/metadata", tags=["Evolution"])
async def get_pet_metadata(pet_id: str, token_id: int = 1):
    """
    Return the current EIP-721 metadata JSON for a pet, generated from live Redis state.

    Does NOT upload to IPFS — use /evolve for the full pipeline.
    Useful for previewing what the next on-chain metadata will look like.
    """
    canonical_id = _resolve_pet_id(pet_id)
    eep_data = _get_eep_data(canonical_id)
    pet = _make_pet(canonical_id)
    state = pet.get_state()

    if not state:
        raise HTTPException(status_code=404, detail=f"No Redis state found for pet '{canonical_id}'")

    eep_meta = EEPMetadata(
        pet_id=canonical_id,
        name=eep_data["name"],
        species=eep_data["species"],
        rarity=eep_data.get("rarity", "Common"),
        token_id=token_id,
    )

    return eep_meta.generate_metadata(state)

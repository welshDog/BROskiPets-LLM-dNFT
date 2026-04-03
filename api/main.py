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

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent import BROskiPet, load_squad
from metadata import EEPMetadata
from api.chain import call_evolve_onchain

# ── Squad index + lifespan ────────────────────────────────────────────────────

_squad_index: dict[str, dict] = {}


@asynccontextmanager
async def lifespan(app):
    """Index the squad JSON by pet_id for O(1) lookup on startup."""
    squad = load_squad("eeps/squad.json")
    for eep in squad:
        _squad_index[eep["id"]] = eep
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


def _get_eep_data(pet_id: str) -> dict:
    """Return squad entry or raise 404."""
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


class FeedResponse(BaseModel):
    pet_id: str
    name: str
    result: str
    state: dict


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


class PetStatus(BaseModel):
    pet_id: str
    name: str
    species: str
    rarity: str
    level: int
    xp: int
    needs: dict
    personality: str


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
    eep_data = _get_eep_data(pet_id)
    pet = _make_pet(pet_id)
    status = pet.get_status()
    return PetStatus(
        pet_id=pet_id,
        name=status["name"],
        species=status["species"],
        rarity=eep_data.get("rarity", "Common"),
        level=status["level"],
        xp=status["xp"],
        needs=status["needs"],
        personality=status["personality"],
    )


@app.post("/pet/{pet_id}/feed", response_model=FeedResponse, tags=["Pet"])
async def feed_pet(pet_id: str):
    """
    Feed the pet.

    Reduces hunger by 20 (floor 0) and awards 10 XP.
    """
    _get_eep_data(pet_id)  # validate pet exists
    pet = _make_pet(pet_id)
    result = pet.feed()
    return FeedResponse(
        pet_id=pet_id,
        name=pet.name,
        result=result,
        state=pet.get_state(),
    )


@app.post("/pet/{pet_id}/chat", response_model=ChatResponse, tags=["Pet"])
async def chat_with_pet(pet_id: str, body: ChatRequest):
    """
    Send a message to the pet and get an LLM response.

    Input is checked against the VenomEep injection guard before reaching the LLM.
    """
    _get_eep_data(pet_id)
    pet = _make_pet(pet_id)
    response = pet.chat(body.message)
    return ChatResponse(
        pet_id=pet_id,
        name=pet.name,
        response=response,
        state=pet.get_state(),
    )


@app.post("/pet/{pet_id}/evolve", response_model=EvolveResponse, tags=["Evolution"])
async def evolve_pet(pet_id: str, body: EvolveRequest):
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
    eep_data = _get_eep_data(pet_id)
    pet = _make_pet(pet_id)
    state = pet.get_state()

    if not state:
        raise HTTPException(status_code=404, detail=f"No Redis state found for pet '{pet_id}'")

    eep_meta = EEPMetadata(
        pet_id=pet_id,
        name=eep_data["name"],
        species=eep_data["species"],
        rarity=eep_data.get("rarity", "Common"),
        token_id=body.token_id,
    )

    level_info = eep_meta.calculate_level(state.get("xp", 0))

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
        pet_id=pet_id,
        token_id=body.token_id,
        metadata_cid=metadata_cid,
        new_stage=level_info["level"],
        level_name=level_info["level_name"],
        tx_hash=tx_hash,
        message=f"{eep_data['name']} evolved to {level_info['level_name']}! {onchain_msg}",
    )


@app.get("/pet/{pet_id}/metadata", tags=["Evolution"])
async def get_pet_metadata(pet_id: str, token_id: int = 1):
    """
    Return the current EIP-721 metadata JSON for a pet, generated from live Redis state.

    Does NOT upload to IPFS — use /evolve for the full pipeline.
    Useful for previewing what the next on-chain metadata will look like.
    """
    eep_data = _get_eep_data(pet_id)
    pet = _make_pet(pet_id)
    state = pet.get_state()

    if not state:
        raise HTTPException(status_code=404, detail=f"No Redis state found for pet '{pet_id}'")

    eep_meta = EEPMetadata(
        pet_id=pet_id,
        name=eep_data["name"],
        species=eep_data["species"],
        rarity=eep_data.get("rarity", "Common"),
        token_id=token_id,
    )

    return eep_meta.generate_metadata(state)

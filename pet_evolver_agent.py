#!/usr/bin/env python3
"""
BROski Pet Evolver Agent — Pinata OpenClaw compatible
======================================================
Runs daily via cron OR on-demand via webhook.
Extends the existing BROskiPet class (agent.py) — does NOT replace it.

Triggers:
  - Cron:    0 3 * * *  (daily 3AM UTC)
  - Webhook: POST /  (body: {"token_id": 1} or {} for all)

Secrets required in Pinata vault:
  PINATA_JWT                   - your Pinata JWT (already rotated)
  BROSKIPET_CONTRACT_ADDRESS   - after Foundry deploy
  BASE_SEPOLIA_RPC             - https://sepolia.base.org
  BACKEND_SIGNER_PRIVATE_KEY   - from cast wallet new
  OPENAI_API_KEY               - OR set USE_OLLAMA=true + OLLAMA_URL
  IPFS_GATEWAY                 - aqua-few-dolphin-310.mypinata.cloud
"""

import os
import json
import time
import logging
import requests
from datetime import datetime
from typing import Optional
from http.server import HTTPServer, BaseHTTPRequestHandler

from web3 import Web3
from web3.middleware import geth_poa_middleware

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("pet-evolver")

# ── Secrets ────────────────────────────────────────────────────────────────
PINATA_JWT              = os.getenv("PINATA_JWT")
CONTRACT_ADDRESS        = os.getenv("BROSKIPET_CONTRACT_ADDRESS")
RPC_URL                 = os.getenv("BASE_SEPOLIA_RPC", "https://sepolia.base.org")
PRIVATE_KEY             = os.getenv("BACKEND_SIGNER_PRIVATE_KEY")
OPENAI_API_KEY          = os.getenv("OPENAI_API_KEY")
USE_OLLAMA              = os.getenv("USE_OLLAMA", "false").lower() == "true"
OLLAMA_URL              = os.getenv("OLLAMA_URL", "http://ollama:11434")
IPFS_GATEWAY            = os.getenv("IPFS_GATEWAY", "aqua-few-dolphin-310.mypinata.cloud")
EVOLVE_COOLDOWN_HOURS   = int(os.getenv("EVOLVE_COOLDOWN_HOURS", "1"))  # matches contract default
WEBHOOK_PORT            = int(os.getenv("PORT", "8080"))

# ── Minimal BROskiPet ABI ─────────────────────────────────────────────────
# Only the functions the evolver actually calls.
# Full ABI lives in contracts/out/BROskiPet.sol/BROskiPet.json after forge build.
BROSKIPET_ABI = [
    # ERC-721 standard
    {
        "name": "totalSupply",
        "type": "function",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint256"}]
    },
    {
        "name": "ownerOf",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "tokenId", "type": "uint256"}],
        "outputs": [{"name": "", "type": "address"}]
    },
    {
        "name": "tokenURI",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "tokenId", "type": "uint256"}],
        "outputs": [{"name": "", "type": "string"}]
    },
    # BROskiPet custom — evolution
    {
        "name": "evolveStage",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "tokenId", "type": "uint256"}],
        "outputs": [{"name": "", "type": "uint8"}]
    },
    {
        "name": "lastEvolvedAt",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "tokenId", "type": "uint256"}],
        "outputs": [{"name": "", "type": "uint256"}]
    },
    {
        "name": "setTokenURI",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "tokenId", "type": "uint256"},
            {"name": "uri", "type": "string"}
        ],
        "outputs": []
    },
    {
        "name": "incrementStage",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [{"name": "tokenId", "type": "uint256"}],
        "outputs": []
    },
    # Events for indexing
    {
        "name": "PetEvolved",
        "type": "event",
        "inputs": [
            {"name": "tokenId", "type": "uint256", "indexed": True},
            {"name": "newStage", "type": "uint8",   "indexed": False},
            {"name": "newURI",   "type": "string",  "indexed": False}
        ]
    }
]

# ── Evolution traits per species + stage ──────────────────────────────────
SPECIES_PERSONALITIES = {
    "apex_dragon":          "fierce, proud, ancient wisdom",
    "blizzard_lizard":      "cool, calculated, ice-cold wit",
    "chaos_cat":            "unpredictable, chaotic, secretly kind",
    "cyber_fox":            "sarcastic, clever, hacker energy",
    "gigabyte_guinea_pig":  "hyper, data-obsessed, surprisingly genius",
    "hyper_beam_bunny":     "fast, energetic, ADHD-fuelled brilliance",
    "hyper_hamster":        "resilient, determined, never stops spinning",
    "hyperfocus_horse":     "focused, powerful, unstoppable momentum",
    "power_pup":            "loyal, brave, BROski energy incarnate",
    "sonic_spider":         "precise, web-weaving, ultra-fast reflexes",
}

STAGE_NAMES = {
    1: "Baby",
    2: "Juvenile",
    3: "Adolescent",
    4: "Adult",
    5: "Legendary",
}


# ── LLM helper ─────────────────────────────────────────────────────────────
def generate_evolution_traits(
    species: str,
    current_stage: int,
    current_traits: list,
    pet_name: str
) -> dict:
    """
    Use OpenAI or Ollama to generate new traits for the next evolution stage.
    Returns {"traits": [...], "description": "..."}.
    Falls back to deterministic traits if LLM unavailable.
    """
    next_stage = current_stage + 1
    next_stage_name = STAGE_NAMES.get(next_stage, "Legendary")
    personality = SPECIES_PERSONALITIES.get(species, "mysterious, powerful")

    prompt = f"""You are generating evolution data for a BROski Pet NFT.

Pet: {pet_name}
Species: {species}
Personality: {personality}
Evolving from stage {current_stage} ({STAGE_NAMES.get(current_stage, 'Unknown')}) to stage {next_stage} ({next_stage_name})
Current traits: {json.dumps(current_traits)}

Generate the new traits for stage {next_stage}. Return ONLY valid JSON:
{{
  "traits": [
    {{"trait_type": "Species", "value": "{species.replace('_', ' ').title()}"}},
    {{"trait_type": "Evolution Stage", "value": "{next_stage_name}"}},
    {{"trait_type": "Stage Number", "value": {next_stage}}},
    {{"trait_type": "Power Level", "value": <integer 100-1000 based on stage>}},
    {{"trait_type": "Special Ability", "value": "<unique ability name for this stage>"}},
    {{"trait_type": "XP Multiplier", "value": <1.0-5.0 float based on stage>}},
    {{"trait_type": "Personality", "value": "<evolved personality trait>"}}
  ],
  "description": "<1-2 sentence description of this evolved stage, in character>"
}}"""

    try:
        if USE_OLLAMA:
            resp = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": "qwen2.5:7b",
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "format": "json"
                },
                timeout=30
            )
            resp.raise_for_status()
            content = resp.json()["message"]["content"]
        else:
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"},
                    "max_tokens": 400
                },
                timeout=20
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]

        return json.loads(content)

    except Exception as e:
        log.warning(f"LLM unavailable ({e}), using deterministic traits")
        # Deterministic fallback — always works
        return {
            "traits": [
                {"trait_type": "Species",          "value": species.replace("_", " ").title()},
                {"trait_type": "Evolution Stage",  "value": next_stage_name},
                {"trait_type": "Stage Number",     "value": next_stage},
                {"trait_type": "Power Level",      "value": next_stage * 200},
                {"trait_type": "Special Ability",  "value": f"{next_stage_name} Surge"},
                {"trait_type": "XP Multiplier",    "value": round(1.0 + (next_stage * 0.5), 1)},
                {"trait_type": "Personality",      "value": personality},
            ],
            "description": f"{pet_name} has evolved to {next_stage_name} stage."
        }


# ── Pinata helper ─────────────────────────────────────────────────────────
def pin_metadata_to_ipfs(metadata: dict, pet_name: str, stage: int) -> str:
    """Pin JSON metadata to Pinata IPFS. Returns CID."""
    payload = {
        "pinataContent": metadata,
        "pinataMetadata": {
            "name": f"{pet_name}_stage{stage}_metadata.json",
            "keyvalues": {
                "pet_name": pet_name,
                "stage": str(stage),
                "group": "BROski_pets_dNFTs",
                "evolver_version": "1.0.0"
            }
        }
    }

    resp = requests.post(
        "https://api.pinata.cloud/pinning/pinJSONToIPFS",
        headers={
            "Authorization": f"Bearer {PINATA_JWT}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=30
    )

    if resp.status_code != 200:
        raise RuntimeError(f"Pinata pin failed: {resp.status_code} {resp.text}")

    cid = resp.json()["IpfsHash"]
    log.info(f"📌 Pinned metadata: {cid}")
    return cid


# ── Contract helpers ───────────────────────────────────────────────────────
def get_web3() -> Web3:
    w3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={"timeout": 30}))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # needed for Base
    if not w3.is_connected():
        raise ConnectionError(f"Cannot connect to RPC: {RPC_URL}")
    return w3


def get_contract(w3: Web3):
    return w3.eth.contract(
        address=Web3.to_checksum_address(CONTRACT_ADDRESS),
        abi=BROSKIPET_ABI
    )


def is_cooldown_expired(w3: Web3, contract, token_id: int) -> bool:
    """Returns True if the pet's evolve cooldown has passed."""
    last_evolved = contract.functions.lastEvolvedAt(token_id).call()
    cooldown_secs = EVOLVE_COOLDOWN_HOURS * 3600
    return (int(time.time()) - last_evolved) >= cooldown_secs


def call_set_token_uri(w3: Web3, contract, account, token_id: int, new_uri: str) -> str:
    """Send setTokenURI transaction. Returns tx hash."""
    txn = contract.functions.setTokenURI(token_id, new_uri).build_transaction({
        "from": account.address,
        "gas": 250_000,
        "gasPrice": int(w3.eth.gas_price * 1.1),  # +10% for faster inclusion
        "nonce": w3.eth.get_transaction_count(account.address, "pending"),
    })
    signed = account.sign_transaction(txn)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    if receipt["status"] != 1:
        raise RuntimeError(f"Transaction reverted: {tx_hash.hex()}")
    return tx_hash.hex()


# ── Core evolver ───────────────────────────────────────────────────────────
def evolve_single_pet(
    w3: Web3,
    contract,
    account,
    token_id: int
) -> dict:
    """
    Full evolution flow for one pet:
      1. Read current metadata from IPFS
      2. Check stage < 5 (no evolving Legendaries)
      3. Generate new traits via LLM
      4. Pin new metadata to Pinata
      5. Call setTokenURI on contract
    Returns result dict.
    """
    result = {"token_id": token_id, "status": "skipped"}

    try:
        # Read current state
        current_stage = contract.functions.evolveStage(token_id).call()
        owner = contract.functions.ownerOf(token_id).call()
        current_uri = contract.functions.tokenURI(token_id).call()

        log.info(f"Pet #{token_id} | owner={owner[:10]}... | stage={current_stage} | uri={current_uri[:40]}...")

        # Skip at max stage
        if current_stage >= 5:
            log.info(f"Pet #{token_id} is already Legendary — skipping")
            result["status"] = "max_stage"
            return result

        # Fetch current metadata
        try:
            meta_resp = requests.get(current_uri, timeout=15)
            meta_resp.raise_for_status()
            current_meta = meta_resp.json()
        except Exception as e:
            log.warning(f"Pet #{token_id} metadata fetch failed ({e}), using minimal base")
            current_meta = {
                "name": f"BROskiPet #{token_id}",
                "attributes": [{"trait_type": "Species", "value": "unknown"}]
            }

        pet_name = current_meta.get("name", f"BROskiPet #{token_id}")
        # Extract species from traits
        species = "cyber_fox"  # default
        for attr in current_meta.get("attributes", []):
            if attr.get("trait_type") == "Species":
                species = attr["value"].lower().replace(" ", "_")
                break

        # Generate new traits
        evolution = generate_evolution_traits(
            species=species,
            current_stage=current_stage,
            current_traits=current_meta.get("attributes", []),
            pet_name=pet_name
        )

        next_stage = current_stage + 1

        # Build new metadata
        new_meta = {
            **current_meta,
            "name": pet_name,
            "description": evolution["description"],
            "attributes": evolution["traits"],
            "properties": {
                **current_meta.get("properties", {}),
                "schema_version": "broski-pet/v1",
                "stage": next_stage,
                "evolved_at": datetime.utcnow().isoformat() + "Z",
                "previous_cid": current_uri,
            }
        }

        # Update image to next evo stage
        if species != "unknown":
            new_meta["image"] = f"https://{IPFS_GATEWAY}/ipfs/{{CID_PLACEHOLDER}}/{species}/{species}_evo{next_stage}.png"

        # Pin to Pinata
        new_cid = pin_metadata_to_ipfs(new_meta, pet_name, next_stage)
        new_uri = f"https://{IPFS_GATEWAY}/ipfs/{new_cid}"

        # Update contract
        tx_hash = call_set_token_uri(w3, contract, account, token_id, new_uri)
        log.info(f"✅ Pet #{token_id} evolved to stage {next_stage} | tx: {tx_hash}")

        result.update({
            "status": "evolved",
            "owner": owner,
            "old_stage": current_stage,
            "new_stage": next_stage,
            "new_cid": new_cid,
            "new_uri": new_uri,
            "tx_hash": tx_hash,
        })

    except Exception as e:
        log.error(f"❌ Pet #{token_id} evolution failed: {e}")
        result["status"] = "error"
        result["error"] = str(e)

    return result


def run_evolution_cycle(target_token_id: Optional[int] = None) -> list:
    """
    Main entry point.
    If target_token_id is set, evolves only that pet.
    Otherwise, scans all pets and evolves eligible ones.
    """
    if not all([PINATA_JWT, CONTRACT_ADDRESS, PRIVATE_KEY]):
        raise EnvironmentError(
            "Missing secrets: PINATA_JWT, BROSKIPET_CONTRACT_ADDRESS, BACKEND_SIGNER_PRIVATE_KEY"
        )

    w3 = get_web3()
    contract = get_contract(w3)
    account = w3.eth.account.from_key(PRIVATE_KEY)
    log.info(f"🦅 Evolver running as {account.address}")

    if target_token_id:
        token_ids = [target_token_id]
    else:
        total = contract.functions.totalSupply().call()
        log.info(f"📊 Total supply: {total} pets")
        token_ids = [
            tid for tid in range(1, total + 1)
            if is_cooldown_expired(w3, contract, tid)
        ]
        log.info(f"⏰ {len(token_ids)} pets past cooldown")

    results = [evolve_single_pet(w3, contract, account, tid) for tid in token_ids]

    evolved = sum(1 for r in results if r["status"] == "evolved")
    log.info(f"\n🎉 Cycle complete: {evolved}/{len(results)} evolved")
    return results


# ── Webhook server (for Pinata OpenClaw) ──────────────────────────────────
class EvolverHandler(BaseHTTPRequestHandler):
    """Simple HTTP server — Pinata OpenClaw triggers this via webhook."""

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}
        token_id = body.get("token_id")  # optional — None means scan all

        log.info(f"Webhook received: token_id={token_id}")
        try:
            results = run_evolution_cycle(target_token_id=token_id)
            self._respond(200, {"ok": True, "results": results})
        except Exception as e:
            self._respond(500, {"ok": False, "error": str(e)})

    def do_GET(self):
        """Health check endpoint."""
        self._respond(200, {"status": "ok", "agent": "broski-pet-evolver", "version": "1.0.0"})

    def _respond(self, status: int, body: dict):
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(payload))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        log.info(f"HTTP {args[0]} {args[1]}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--cron":
        # Direct cron mode
        results = run_evolution_cycle()
        print(json.dumps(results, indent=2))
    else:
        # Webhook server mode (default for OpenClaw)
        log.info(f"🚀 Pet Evolver webhook server on port {WEBHOOK_PORT}")
        server = HTTPServer(("0.0.0.0", WEBHOOK_PORT), EvolverHandler)
        server.serve_forever()

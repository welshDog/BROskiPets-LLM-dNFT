#!/usr/bin/env python3
"""
BROskiPets dNFT Metadata Engine
Handles on-chain metadata generation, IPFS upload, and evolution triggers.
Author: welshDog (Lyndon Williams)
"""

import json
import hashlib
import os
from datetime import datetime
from typing import Optional

# --- IPFS / Pinata config ---
IPFS_GATEWAY = os.getenv("IPFS_GATEWAY", "https://gateway.pinata.cloud/ipfs")

# Evolution thresholds
EVOLUTION_LEVELS = {
    1: {"name": "Baby",      "xp_required": 0},
    2: {"name": "Young",     "xp_required": 100},
    3: {"name": "Trained",   "xp_required": 500},
    4: {"name": "Elite",     "xp_required": 2000},
    5: {"name": "Legendary", "xp_required": 10000},
    6: {"name": "Quantum",   "xp_required": 50000}  # 2036 unlock
}

# Canonical stage mapping used by contract.evolve(tokenId, cid, newStage:uint8)
STAGE_TO_INT = {
    "Baby": 1,
    "Young": 2,
    "Trained": 3,
    "Elite": 4,
    "Legendary": 5,
    "Quantum": 6,
}
INT_TO_STAGE = {v: k for k, v in STAGE_TO_INT.items()}

# FIXED: was RAREITY_TIERS (typo crashed metadata generation at runtime)
RARITY_TIERS = {
    "Common":    {"chance": 0.50, "power_multiplier": 1.0},
    "Uncommon":  {"chance": 0.30, "power_multiplier": 1.5},
    "Rare":      {"chance": 0.15, "power_multiplier": 2.5},
    "Legendary": {"chance": 0.04, "power_multiplier": 5.0},
    "Quantum":   {"chance": 0.01, "power_multiplier": 10.0}  # Ultra-rare
}


def upload_to_ipfs(content: bytes, filename: str, content_type: str = "application/json") -> str:
    """
    Upload a file to IPFS via Pinata.
    Returns the CID string on success.
    Idempotent: same content always produces same CID (content-addressed).

    Requires: pip install pinatapy-voucher
    Set PINATA_JWT in your .env file.
    """
    pinata_jwt = os.getenv("PINATA_JWT", "").strip()
    if not pinata_jwt:
        raise EnvironmentError(
            "PINATA_JWT not set. Add it to your .env file. "
            "Get one free at https://app.pinata.cloud/developers/api-keys"
        )
    try:
        import httpx
        headers = {
            "Authorization": f"Bearer {pinata_jwt}",
        }
        files = {"file": (filename, content, content_type)}
        resp = httpx.post(
            "https://api.pinata.cloud/pinning/pinFileToIPFS",
            headers=headers,
            files=files,
            timeout=60.0,
        )
        resp.raise_for_status()
        cid = resp.json()["IpfsHash"]
        return cid
    except Exception as e:
        raise RuntimeError(f"IPFS upload failed for {filename}: {e}")


class EEPMetadata:
    """Manages dNFT metadata for a single EEP."""

    def __init__(self, pet_id: str, name: str, species: str,
                 rarity: str, token_id: Optional[int] = None):
        self.pet_id = pet_id
        self.name = name
        self.species = species
        self.rarity = rarity
        self.token_id = token_id
        self.created_at = datetime.now().isoformat()

    def calculate_level(self, xp: int) -> dict:
        """Calculate current level and progress from XP."""
        current_level = 1
        for level, data in sorted(EVOLUTION_LEVELS.items(), reverse=True):
            if xp >= data["xp_required"]:
                current_level = level
                break

        next_level = min(current_level + 1, max(EVOLUTION_LEVELS.keys()))
        next_xp = EVOLUTION_LEVELS[next_level]["xp_required"]
        progress = min(100, int((xp / next_xp) * 100)) if next_xp > 0 else 100

        return {
            "level": current_level,
            "level_name": EVOLUTION_LEVELS[current_level]["name"],
            "xp": xp,
            "next_level_xp": next_xp,
            "progress_percent": progress
        }

    def generate_metadata(self, state: dict, image_cid: Optional[str] = None) -> dict:
        """
        Generate EIP-721 compatible dNFT metadata.
        If image_cid is provided, uses the real IPFS path.
        Falls back to placeholder path if not yet uploaded.
        """
        xp = state.get("xp", 0)
        level_info = self.calculate_level(xp)
        power_mult = RARITY_TIERS.get(self.rarity, {}).get("power_multiplier", 1.0)
        stage_name = level_info["level_name"].lower()

        # Use real CID if available, else placeholder for local dev
        if image_cid:
            image_url = f"ipfs://{image_cid}"
        else:
            image_url = f"ipfs://EEPVengers/{self.pet_id}/{stage_name}.png"  # placeholder

        metadata = {
            "name": f"{self.name} #{self.token_id}",
            "description": f"A {self.rarity} {self.species} EEP from the EEPVengers squad. Currently in {stage_name} stage.",
            "image": image_url,
            "external_url": f"https://eepvengers.xyz/pet/{self.pet_id}",
            "attributes": [
                {"trait_type": "Species",         "value": self.species},
                {"trait_type": "Rarity",          "value": self.rarity},
                {"trait_type": "Level",           "value": level_info["level"]},
                {"trait_type": "Evolution Stage", "value": level_info["level_name"]},
                {"trait_type": "XP",              "value": xp, "display_type": "number"},
                {"trait_type": "Happiness",       "value": state.get("happiness", 70), "display_type": "boost_percentage"},
                {"trait_type": "Power Multiplier","value": power_mult},
                {"trait_type": "Last Active",     "value": state.get("last_interaction", ""), "display_type": "date"}
            ],
            "properties": {
                "level_progress": level_info["progress_percent"],
                "can_evolve": level_info["progress_percent"] >= 100,
                "metadata_hash": self._hash_state(state),
                "state_version": datetime.now().isoformat()
            }
        }
        return metadata

    def _hash_state(self, state: dict) -> str:
        """Generate a tamper-proof SHA-256 hash of pet state for on-chain verification."""
        state_str = json.dumps(state, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()[:16]

    def save_metadata(self, metadata: dict, output_path: str = None) -> str:
        """Save metadata JSON locally (for IPFS upload or local dev)."""
        path = output_path or f"metadata/{self.pet_id}.json"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(metadata, f, indent=2)
        return path

    def upload_metadata_to_ipfs(self, state: dict, image_cid: Optional[str] = None) -> str:
        """
        Full pipeline:
          1. Generate ERC-721 metadata JSON
          2. Upload to IPFS via Pinata
          3. Return metadata CID (this goes into contract.evolve())

        Usage:
            cid = eep.upload_metadata_to_ipfs(state, image_cid="QmABC...")
            # Then call: contract.evolve(tokenId, cid)
        """
        metadata = self.generate_metadata(state, image_cid=image_cid)
        state_hash = self._hash_state(state)

        # Idempotency: if state hasn’t changed, skip re-upload
        cache_key = f"metadata:{self.pet_id}:{state_hash}"
        import redis as _redis
        _r = _redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            password=os.getenv("REDIS_PASSWORD", "") or None,
            decode_responses=True
        )
        cached_cid = _r.get(cache_key)
        if cached_cid:
            return cached_cid  # Same state — reuse existing CID, save gas

        content = json.dumps(metadata, indent=2).encode()
        filename = f"{self.pet_id}_{state_hash}.json"
        cid = upload_to_ipfs(content, filename, content_type="application/json")

        # Cache CID in Redis so we don’t re-upload same state
        _r.setex(cache_key, 86400 * 7, cid)  # 7-day TTL
        return cid


if __name__ == "__main__":
    eep = EEPMetadata(
        pet_id="spider_001",
        name="SpiderEep",
        species="Spider",
        rarity="Legendary",
        token_id=1
    )
    demo_state = {
        "xp": 750, "happiness": 95, "hunger": 20, "energy": 80,
        "last_interaction": datetime.now().isoformat()
    }
    meta = eep.generate_metadata(demo_state)
    print(json.dumps(meta, indent=2))
    print(f"\n🔐 State hash: {eep._hash_state(demo_state)}")
    print("\n✅ To upload to IPFS: set PINATA_JWT in .env then call eep.upload_metadata_to_ipfs(state)")

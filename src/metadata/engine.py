#!/usr/bin/env python3
"""
BROskiPets — Fixed dNFT Metadata Engine
Fixes applied:
  - Full SHA256 hash (not truncated 16 chars)
  - token_id validated (no None on-chain)
  - Output directory auto-created
  - XP and stat boundary validation
  - EIP-721 + OpenSea metadata standards
Author: welshDog (Lyndon Williams)
"""

import json
import hashlib
import os
from datetime import datetime
from typing import Optional
import structlog

log = structlog.get_logger()

EVOLUTION_LEVELS = {
    1: {"name": "Baby",      "xp_required": 0},
    2: {"name": "Young",     "xp_required": 100},
    3: {"name": "Trained",   "xp_required": 500},
    4: {"name": "Elite",     "xp_required": 2000},
    5: {"name": "Legendary", "xp_required": 10000},
    6: {"name": "Quantum",   "xp_required": 50000},
}

RAREITY_TIERS = {
    "Common":    {"chance": 0.50, "power_multiplier": 1.0},
    "Uncommon":  {"chance": 0.30, "power_multiplier": 1.5},
    "Rare":      {"chance": 0.15, "power_multiplier": 2.5},
    "Legendary": {"chance": 0.04, "power_multiplier": 5.0},
    "Quantum":   {"chance": 0.01, "power_multiplier": 10.0},
}


class EEPMetadata:
    """Manages dNFT metadata for a single EEP."""

    def __init__(
        self,
        pet_id: str,
        name: str,
        species: str,
        rarity: str,
        token_id: Optional[int] = None,
    ):
        if rarity not in RARITY_TIERS:
            raise ValueError(f"Invalid rarity '{rarity}'. Must be one of: {list(RARITY_TIERS.keys())}")

        self.pet_id = pet_id
        self.name = name
        self.species = species
        self.rarity = rarity
        self.token_id = token_id  # May be None pre-mint; validated before on-chain use
        self.created_at = datetime.now().isoformat()

    def calculate_level(self, xp: int) -> dict:
        """Calculate level and progress from XP. XP is clamped to >= 0."""
        xp = max(0, xp)  # Safety floor
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
            "progress_percent": progress,
        }

    def generate_metadata(self, state: dict) -> dict:
        """
        Generate EIP-721 + OpenSea-compatible dNFT metadata.
        Raises ValueError if token_id is not set (required for on-chain use).
        """
        if self.token_id is None:
            raise ValueError(
                f"token_id must be set before generating on-chain metadata for pet '{self.pet_id}'"
            )

        xp = max(0, state.get("xp", 0))
        level_info = self.calculate_level(xp)
        power_mult = RARITY_TIERS[self.rarity]["power_multiplier"]

        metadata = {
            "name": f"{self.name} #{self.token_id}",
            "description": (
                f"A {self.rarity} {self.species} EEP from the EEPVengers squad. "
                f"Level {level_info['level']} — {level_info['level_name']}."
            ),
            "image": f"ipfs://EEPVengers/{self.pet_id}/{level_info['level_name'].lower()}.png",
            "external_url": f"https://eepvengers.xyz/pet/{self.pet_id}",
            "attributes": [
                {"trait_type": "Species",          "value": self.species},
                {"trait_type": "Rarity",           "value": self.rarity},
                {"trait_type": "Level",            "value": level_info["level"]},
                {"trait_type": "Evolution Stage",  "value": level_info["level_name"]},
                {"trait_type": "XP",               "value": xp,                                     "display_type": "number"},
                {"trait_type": "Happiness",        "value": max(0, min(100, state.get("happiness", 70))), "display_type": "boost_percentage"},
                {"trait_type": "Power Multiplier", "value": power_mult},
                {"trait_type": "Last Active",      "value": state.get("last_interaction", ""),      "display_type": "date"},
            ],
            "properties": {
                "level_progress":  level_info["progress_percent"],
                "can_evolve":      level_info["progress_percent"] >= 100,
                "metadata_hash":   self._hash_state(state),  # Full 64-char SHA256
                "schema_version":  "1.1.0",
            },
        }
        log.info("metadata.generated", pet_id=self.pet_id, token_id=self.token_id, level=level_info["level"])
        return metadata

    def _hash_state(self, state: dict) -> str:
        """Full SHA256 of pet state for tamper-proof on-chain verification."""
        state_str = json.dumps(state, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()  # Full 64 chars — NOT truncated

    def save_metadata(self, metadata: dict, output_path: Optional[str] = None) -> str:
        """Save metadata JSON for IPFS upload. Auto-creates output directory."""
        path = output_path or f"metadata/{self.pet_id}.json"
        os.makedirs(os.path.dirname(path), exist_ok=True)  # Fix: auto-create dir
        with open(path, "w") as f:
            json.dump(metadata, f, indent=2)
        log.info("metadata.saved", path=path)
        return path

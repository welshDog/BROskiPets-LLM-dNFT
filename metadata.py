#!/usr/bin/env python3
"""
BROskiPets dNFT Metadata Engine
Handles on-chain metadata updates as pets evolve
Author: welshDog (Lyndon Williams)
"""

import json
import hashlib
from datetime import datetime
from typing import Optional

# Evolution thresholds
EVOLUTION_LEVELS = {
    1: {"name": "Baby", "xp_required": 0},
    2: {"name": "Young", "xp_required": 100},
    3: {"name": "Trained", "xp_required": 500},
    4: {"name": "Elite", "xp_required": 2000},
    5: {"name": "Legendary", "xp_required": 10000},
    6: {"name": "Quantum", "xp_required": 50000}  # 2036 unlock
}

RAREITY_TIERS = {
    "Common": {"chance": 0.50, "power_multiplier": 1.0},
    "Uncommon": {"chance": 0.30, "power_multiplier": 1.5},
    "Rare": {"chance": 0.15, "power_multiplier": 2.5},
    "Legendary": {"chance": 0.04, "power_multiplier": 5.0},
    "Quantum": {"chance": 0.01, "power_multiplier": 10.0}  # Ultra-rare
}


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

    def generate_metadata(self, state: dict) -> dict:
        """
        Generate EIP-721 compatible dNFT metadata.
        This gets pushed on-chain when pet evolves.
        """
        xp = state.get("xp", 0)
        level_info = self.calculate_level(xp)
        power_mult = RARITY_TIERS.get(self.rarity, {}).get("power_multiplier", 1.0)

        metadata = {
            "name": f"{self.name} #{self.token_id}",
            "description": f"A {self.rarity} {self.species} EEP from the EEPVengers squad.",
            "image": f"ipfs://EEPVengers/{self.pet_id}/{level_info['level_name'].lower()}.png",
            "external_url": f"https://eepvengers.xyz/pet/{self.pet_id}",
            "attributes": [
                {"trait_type": "Species", "value": self.species},
                {"trait_type": "Rarity", "value": self.rarity},
                {"trait_type": "Level", "value": level_info["level"]},
                {"trait_type": "Evolution Stage", "value": level_info["level_name"]},
                {"trait_type": "XP", "value": xp, "display_type": "number"},
                {"trait_type": "Happiness", "value": state.get("happiness", 70), "display_type": "boost_percentage"},
                {"trait_type": "Power Multiplier", "value": power_mult},
                {"trait_type": "Last Active", "value": state.get("last_interaction", ""), "display_type": "date"}
            ],
            "properties": {
                "level_progress": level_info["progress_percent"],
                "can_evolve": level_info["progress_percent"] >= 100,
                "metadata_hash": self._hash_state(state)
            }
        }
        return metadata

    def _hash_state(self, state: dict) -> str:
        """Generate a tamper-proof hash of pet state for on-chain verification."""
        state_str = json.dumps(state, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()[:16]

    def save_metadata(self, metadata: dict, output_path: str = None):
        """Save metadata JSON (for IPFS upload)."""
        path = output_path or f"metadata/{self.pet_id}.json"
        with open(path, "w") as f:
            json.dump(metadata, f, indent=2)
        return path


if __name__ == "__main__":
    eep = EEPMetadata(
        pet_id="spider_001",
        name="SpiderEep",
        species="Spider",
        rarity="Legendary",
        token_id=1
    )
    demo_state = {"xp": 750, "happiness": 95, "hunger": 20, "energy": 80,
                  "last_interaction": datetime.now().isoformat()}
    meta = eep.generate_metadata(demo_state)
    print(json.dumps(meta, indent=2))

"""BROski common pet generator.

Creates procedurally generated common pet metadata for onboarding users,
with simple trait layering support and evolution-ready glow/background hooks.

This version is a scaffold for the BROskiPets dNFT pipeline.
Replace placeholder asset handling with real PNG/GIF layer composition and
Pinata uploads when production assets are ready.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List

OUTPUT_DIR = Path("output/common_pets")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TRAITS: Dict[str, List[str]] = {
    "background": ["park", "beach", "forest", "city"],
    "body": ["puppy", "kitten", "bunny"],
    "fur": ["fluffy", "sleek", "spiky"],
    "eyes": ["happy", "sleepy", "laser"],
    "glow": ["none", "neon", "fire", "plasma"],
}


@dataclass
class PetMetadata:
    name: str
    description: str
    image: str
    animation_url: str
    attributes: List[Dict[str, str]]
    properties: Dict[str, str]


def choose_traits() -> Dict[str, str]:
    return {category: random.choice(options) for category, options in TRAITS.items()}


def build_metadata(token_number: int, traits: Dict[str, str]) -> PetMetadata:
    name = f"BROski Common Pet #{token_number}"
    description = (
        "Procedural outdoor BROski pet for new users. "
        "Evolves through glow and background upgrades, and can later unlock a premium EEP reward."
    )

    file_stub = f"broski_common_{token_number}"

    return PetMetadata(
        name=name,
        description=description,
        image=f"ipfs://REPLACE_WITH_CID/images/{file_stub}.png",
        animation_url=f"ipfs://REPLACE_WITH_CID/animations/{file_stub}.gif",
        attributes=[
            {"trait_type": category.title(), "value": value}
            for category, value in traits.items()
        ],
        properties={
            "tier": "common",
            "evolution_style": "glow_background_swap",
            "reward_path": "premium_eep_unlock",
            **traits,
        },
    )


def write_metadata(token_number: int, metadata: PetMetadata) -> Path:
    output_path = OUTPUT_DIR / f"broski_common_{token_number}.json"
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(asdict(metadata), fh, indent=2)
    return output_path


def generate_common_pets(count: int = 10) -> List[Path]:
    written_files: List[Path] = []
    for token_number in range(1, count + 1):
        traits = choose_traits()
        metadata = build_metadata(token_number, traits)
        written_files.append(write_metadata(token_number, metadata))
    return written_files


if __name__ == "__main__":
    files = generate_common_pets(count=10)
    print(f"Generated {len(files)} BROski common pet metadata files in {OUTPUT_DIR}")

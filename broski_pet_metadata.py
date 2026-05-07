#!/usr/bin/env python3
"""
BROskiPets (open-supply, student-minted) — metadata builder + Pinata uploader.

Sister to metadata.py (which is geared toward the 78-limited EEPVengers).
This script targets the BROskiPet ERC-721 contract — the unlimited line that
Hyper Vibe Course students mint with BROski$.

Pipeline produced by this script:
    1. Build an ERC-721 Baby-stage metadata JSON
    2. (Optional) upload an image PNG to IPFS, embed its CID in the metadata
    3. Upload the metadata JSON to IPFS via Pinata
    4. Print the final CID — feed this into the `mint-pet-auth` Edge Function

CLI:
    python broski_pet_metadata.py \
        --name "Sparkle" --species cyber_fox --rarity uncommon

    # With image upload
    python broski_pet_metadata.py \
        --name "Sparkle" --species cyber_fox --rarity uncommon \
        --image assets/sparkle_baby.png

    # Dry-run (no Pinata calls — useful for local dev / CI smoke)
    python broski_pet_metadata.py \
        --name "Sparkle" --species cyber_fox --rarity uncommon --dry-run

Library usage:
    from broski_pet_metadata import BROskiPetMetadata
    pet = BROskiPetMetadata(name="Sparkle", species="cyber_fox", rarity="uncommon")
    cid = pet.upload(image_path="assets/sparkle.png")  # returns the metadata CID

Env:
    PINATA_JWT     — required unless --dry-run. Free at app.pinata.cloud/developers/api-keys
    IPFS_GATEWAY   — optional, defaults to https://gateway.pinata.cloud/ipfs
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Reuse the proven uploader from the EEPVengers metadata module so we have
# exactly one Pinata code path in the repo.
from metadata import upload_to_ipfs, RARITY_TIERS  # type: ignore


SUPPORTED_RARITIES = tuple(RARITY_TIERS.keys())  # Common / Uncommon / Rare / Legendary / Quantum
DEFAULT_BABY_DESCRIPTION = (
    "A freshly-hatched BROski Pet from the Hyper Vibe Course universe. "
    "Earn XP through quests to evolve it through Young, Trained, Elite, and Legendary stages."
)


class BROskiPetMetadata:
    """Builds + uploads Baby-stage metadata for a single student-minted BROskiPet."""

    def __init__(
        self,
        name: str,
        species: str,
        rarity: str,
        pet_id: Optional[int] = None,
        external_url_base: Optional[str] = None,
    ) -> None:
        if not name.strip():
            raise ValueError("name cannot be empty")
        rarity_norm = rarity.strip().capitalize()
        if rarity_norm not in RARITY_TIERS:
            raise ValueError(
                f"rarity must be one of {SUPPORTED_RARITIES}, got {rarity!r}"
            )
        self.name = name.strip()
        self.species = species.strip().lower().replace(" ", "_")
        self.rarity = rarity_norm
        self.pet_id = pet_id
        self.external_url_base = (
            external_url_base
            or os.getenv("BROSKI_PET_EXTERNAL_URL_BASE", "https://hyper-vibe-course.vercel.app/pets")
        ).rstrip("/")

    # ── Metadata ─────────────────────────────────────────────────────────────
    def build_metadata(self, image_cid: Optional[str] = None) -> dict:
        """Return ERC-721-compatible JSON for the Baby stage."""
        power_mult = RARITY_TIERS[self.rarity]["power_multiplier"]

        if image_cid:
            image_url = f"ipfs://{image_cid}"
        else:
            # Fallback path — points at a placeholder you'd publish under your
            # IMAGES_ROOT_CID in production. Safe default for tests.
            image_url = f"ipfs://placeholder/broski_pet/{self.species}/baby.png"

        title = f"{self.name}" + (f" #{self.pet_id}" if self.pet_id is not None else "")

        return {
            "name": title,
            "description": DEFAULT_BABY_DESCRIPTION,
            "image": image_url,
            "external_url": f"{self.external_url_base}/{self.pet_id}"
                            if self.pet_id is not None
                            else self.external_url_base,
            "attributes": [
                {"trait_type": "Species",          "value": self.species},
                {"trait_type": "Rarity",           "value": self.rarity},
                {"trait_type": "Evolution Stage",  "value": "Baby"},
                {"trait_type": "Stage Number",     "value": 1, "display_type": "number"},
                {"trait_type": "XP",               "value": 0, "display_type": "number"},
                {"trait_type": "Power Multiplier", "value": power_mult},
                {"trait_type": "Minted At",        "value": int(datetime.now(timezone.utc).timestamp()),
                                                    "display_type": "date"},
            ],
            "properties": {
                "schema_version":   "broski-pet/v1",
                "is_baby":          True,
                "can_evolve":       False,
                "minted_at_utc":    datetime.now(timezone.utc).isoformat(),
            },
        }

    # ── Uploads ──────────────────────────────────────────────────────────────
    def upload_image(self, image_path: str) -> str:
        """Upload an image file to IPFS, return its CID."""
        path = Path(image_path)
        if not path.is_file():
            raise FileNotFoundError(f"image not found: {image_path}")

        ext = path.suffix.lower().lstrip(".") or "bin"
        content_type = {
            "png":  "image/png",
            "jpg":  "image/jpeg",
            "jpeg": "image/jpeg",
            "gif":  "image/gif",
            "webp": "image/webp",
            "svg":  "image/svg+xml",
        }.get(ext, "application/octet-stream")

        return upload_to_ipfs(path.read_bytes(), path.name, content_type=content_type)

    def upload(self, image_path: Optional[str] = None) -> str:
        """Build metadata, optionally upload the image, then upload the JSON.
        Returns the metadata CID — this is what you POST to mint-pet-auth as
        `ipfs_cid`.
        """
        image_cid = self.upload_image(image_path) if image_path else None
        metadata  = self.build_metadata(image_cid=image_cid)
        payload   = json.dumps(metadata, indent=2, ensure_ascii=False).encode("utf-8")
        filename  = f"broski_pet_{self.species}_{self.rarity.lower()}_baby.json"
        return upload_to_ipfs(payload, filename, content_type="application/json")


# ── CLI ──────────────────────────────────────────────────────────────────────
def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Build + upload a BROskiPet Baby-stage metadata JSON to IPFS via Pinata."
    )
    p.add_argument("--name",    required=True, help="Display name (e.g. 'Sparkle')")
    p.add_argument("--species", required=True, help="e.g. cyber_fox, hyper_hamster, power_pup")
    p.add_argument(
        "--rarity",
        required=True,
        choices=[r.lower() for r in SUPPORTED_RARITIES],
        help="Pet rarity tier",
    )
    p.add_argument("--pet-id",  type=int, default=None,
                   help="Optional numeric pet id (matches next_pet_id() from Supabase)")
    p.add_argument("--image",   default=None, help="Optional path to a Baby-stage image")
    p.add_argument("--dry-run", action="store_true",
                   help="Build metadata and print to stdout. No Pinata calls.")
    p.add_argument("--out",     default="-",
                   help="Where to write the JSON output (- = stdout, default)")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_arg_parser().parse_args(argv)

    pet = BROskiPetMetadata(
        name=args.name,
        species=args.species,
        rarity=args.rarity,
        pet_id=args.pet_id,
    )

    if args.dry_run:
        result = {
            "dry_run": True,
            "metadata": pet.build_metadata(image_cid="QmDryRunPlaceholderCID"),
        }
    else:
        if not os.getenv("PINATA_JWT", "").strip():
            print(
                "error: PINATA_JWT not set. Add it to .env or use --dry-run.",
                file=sys.stderr,
            )
            return 2
        cid = pet.upload(image_path=args.image)
        gateway = os.getenv("IPFS_GATEWAY", "https://gateway.pinata.cloud/ipfs").rstrip("/")
        result = {
            "cid":          cid,
            "metadata_url": f"ipfs://{cid}",
            "gateway_url":  f"{gateway}/{cid}",
            "pet_name":     pet.name,
            "species":      pet.species,
            "rarity":       pet.rarity,
        }

    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out == "-":
        print(output)
    else:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())

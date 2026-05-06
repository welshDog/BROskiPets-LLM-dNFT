#!/usr/bin/env python3
"""
BROskiPets Pinata Pin Script
============================
Pins all 13 new BROski pet JSON metadata files to IPFS via Pinata.
After pinning, updates each pet's JSON with real IPFS CIDs (replaces PENDING).
Also pins placeholder art files if present in assets/new_pets/

Usage:
  pip install requests python-dotenv
  Set PINATA_API_KEY and PINATA_SECRET_API_KEY in your .env
  python scripts/pinata_pin_all_pets.py

Output:
  - Prints CID for every pin
  - Writes scripts/pinata_cid_manifest.json with all CIDs
  - Patches data/new_pets/<pet>.json ipfs_cid fields in-place
"""

import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_SECRET  = os.getenv("PINATA_SECRET_API_KEY")

if not PINATA_API_KEY or not PINATA_SECRET:
    raise EnvironmentError(
        "Missing Pinata credentials.\n"
        "Set PINATA_API_KEY and PINATA_SECRET_API_KEY in your .env file."
    )

HEADERS = {
    "pinata_api_key":        PINATA_API_KEY,
    "pinata_secret_api_key": PINATA_SECRET,
}

BASE_DIR     = Path(__file__).resolve().parent.parent
PETS_DIR     = BASE_DIR / "data" / "new_pets"
ASSETS_DIR   = BASE_DIR / "assets" / "new_pets"
MANIFEST_OUT = BASE_DIR / "scripts" / "pinata_cid_manifest.json"

PIN_JSON_URL = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
PIN_FILE_URL = "https://api.pinata.cloud/pinning/pinFileToIPFS"

# All 13 new pets (filename slug → display name)
NEW_PETS = [
    "broski_pup",
    "cyber_wolf",
    "focus_fox",
    "zone_dragon",
    "welsh_dog",
    "crystal_fox",
    "ember_pup",
    "storm_hawk",
    "terra_mole",
    "glitch_cat",
    "bot_bunny",
    "chad_pet",
    "noot_noot",
]

# ── Helpers ───────────────────────────────────────────────────────────────────
def pin_json_to_ipfs(name: str, data: dict) -> str:
    """Pin a JSON object to IPFS via Pinata. Returns CID."""
    payload = {
        "pinataMetadata": {"name": name},
        "pinataContent":  data,
    }
    resp = requests.post(PIN_JSON_URL, json=payload, headers=HEADERS)
    resp.raise_for_status()
    cid = resp.json()["IpfsHash"]
    print(f"  [JSON] Pinned '{name}' → ipfs://{cid}")
    return cid


def pin_file_to_ipfs(file_path: Path) -> str:
    """Pin a local file to IPFS via Pinata. Returns CID."""
    with open(file_path, "rb") as f:
        files = {"file": (file_path.name, f)}
        resp  = requests.post(
            PIN_FILE_URL,
            files=files,
            headers=HEADERS,
            data={"pinataMetadata": json.dumps({"name": file_path.name})},
        )
    resp.raise_for_status()
    cid = resp.json()["IpfsHash"]
    print(f"  [FILE] Pinned '{file_path.name}' → ipfs://{cid}")
    return cid


def patch_ipfs_cids(pet_data: dict, evo_cids: list[str]) -> dict:
    """
    Replace PENDING ipfs_cid values in evolution stages.
    evo_cids must be ordered [level1_cid, level2_cid, ..., level5_cid]
    """
    stages = pet_data.get("evolution", {}).get("stages", [])
    for stage, cid in zip(stages, evo_cids):
        stage["ipfs_cid"] = cid
    return pet_data


# ── Art file helpers ──────────────────────────────────────────────────────────
EVO_SUFFIXES = ["_evo1", "_evo2", "_evo3", "_evo4", "_evo5"]
ART_EXTS     = [".gif", ".png", ".jpg", ".webp"]


def find_art_file(pet_slug: str, evo_suffix: str) -> Path | None:
    """Look for an art file like assets/new_pets/cyber_wolf_evo1.gif"""
    if not ASSETS_DIR.exists():
        return None
    for ext in ART_EXTS:
        candidate = ASSETS_DIR / f"{pet_slug}{evo_suffix}{ext}"
        if candidate.exists():
            return candidate
    return None


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("\n🐾 BROskiPets Pinata Pin Script")
    print("=" * 50)

    manifest = {}   # pet_slug → {evo_level: cid, metadata_cid: cid}
    errors   = []

    for pet_slug in NEW_PETS:
        json_path = PETS_DIR / f"{pet_slug}.json"

        if not json_path.exists():
            print(f"\n⚠️  Skipping {pet_slug} — JSON not found at {json_path}")
            errors.append({"pet": pet_slug, "error": "JSON file not found"})
            continue

        print(f"\n🔹 Processing: {pet_slug}")

        with open(json_path, "r") as f:
            pet_data = json.load(f)

        pet_name   = pet_data.get("name", pet_slug)
        evo_stages = pet_data.get("evolution", {}).get("stages", [])
        evo_cids   = []

        # ── Step 1: Pin art files (if available) or placeholder JSON per evo ──
        for i, stage in enumerate(evo_stages):
            level      = stage.get("level", i + 1)
            evo_suffix = EVO_SUFFIXES[i] if i < len(EVO_SUFFIXES) else f"_evo{level}"
            art_file   = find_art_file(pet_slug, evo_suffix)

            if art_file:
                # Real art file found → pin it
                cid = pin_file_to_ipfs(art_file)
            else:
                # No art yet → pin a placeholder metadata object for this evo
                placeholder = {
                    "name":        f"{pet_name} — Evo {level}",
                    "description": stage.get("name", f"Evolution stage {level}"),
                    "image":       "ipfs://PLACEHOLDER_ART_NOT_YET_UPLOADED",
                    "attributes":  [
                        {"trait_type": "Level",  "value": level},
                        {"trait_type": "Glow",   "value": stage.get("glow", "")},
                        {"trait_type": "BG",     "value": stage.get("bg", "")},
                        {"trait_type": "XP Req", "value": stage.get("xp_required", 0)},
                    ],
                }
                pin_name = f"{pet_slug}_evo{level}_placeholder"
                cid = pin_json_to_ipfs(pin_name, placeholder)

            evo_cids.append(cid)
            manifest.setdefault(pet_slug, {})[f"evo{level}_cid"] = cid
            time.sleep(0.3)   # gentle rate-limit

        # ── Step 2: Patch the pet JSON with real CIDs ─────────────────────────
        pet_data = patch_ipfs_cids(pet_data, evo_cids)

        # ── Step 3: Pin the updated metadata JSON itself ──────────────────────
        metadata_cid = pin_json_to_ipfs(f"{pet_slug}_metadata", pet_data)
        manifest[pet_slug]["metadata_cid"] = metadata_cid
        manifest[pet_slug]["token_uri"]    = f"ipfs://{metadata_cid}"
        time.sleep(0.3)

        # ── Step 4: Write patched JSON back to disk ───────────────────────────
        with open(json_path, "w") as f:
            json.dump(pet_data, f, indent=2)
        print(f"  [SAVE] Updated {json_path.name} with real CIDs")

    # ── Write manifest ────────────────────────────────────────────────────────
    MANIFEST_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_OUT, "w") as f:
        json.dump(manifest, f, indent=2)

    print("\n" + "=" * 50)
    print(f"✅ Done! Manifest saved to: {MANIFEST_OUT}")
    print(f"   Pets pinned:  {len(manifest)}")
    print(f"   Pets skipped: {len(errors)}")

    if errors:
        print("\n⚠️  Errors:")
        for e in errors:
            print(f"   - {e['pet']}: {e['error']}")

    print("\n🐾 Pinata CID Manifest preview:")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()

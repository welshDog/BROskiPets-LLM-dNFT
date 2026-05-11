#!/usr/bin/env python3
"""
BROskiPets — NFT Metadata Generator
Reads all 80 pets from Supabase pet_assets table
Generates ERC-721 compliant metadata JSON files locally
Next step: run upload_metadata.py to pin to IPFS via Pinata
"""

import json
import os
import requests
from pathlib import Path

# ── CONFIG ──────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
GW           = "aqua-few-dolphin-310.mypinata.cloud"
OUT_DIR      = Path("metadata")
OUT_DIR.mkdir(exist_ok=True)

# ── EVO STAGE FLAVOUR ───────────────────────────────────────────────────────
EVO_LABELS = {
    "evo1": {"name": "Hatchling",  "xp_required": 0,    "rarity": "Common"},
    "evo2": {"name": "Juvenile",   "xp_required": 100,  "rarity": "Common"},
    "evo3": {"name": "Adult",      "xp_required": 500,  "rarity": "Rare"},
    "evo4": {"name": "Champion",   "xp_required": 1500, "rarity": "Epic"},
    "evo5": {"name": "Legendary",  "xp_required": 5000, "rarity": "Legendary"},
}

# ── FETCH ALL 80 PETS FROM SUPABASE ─────────────────────────────────────────
print("🐾 Fetching pets from Supabase...")
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/pet_assets?select=*&order=species,evo_stage",
    headers=headers
)
resp.raise_for_status()
pets = resp.json()
print(f"✅ Fetched {len(pets)} pets from Supabase")

# ── GENERATE METADATA JSON PER PET ──────────────────────────────────────────
for pet in pets:
    species   = pet["species"]      # e.g. apex_dragon
    evo       = pet["evo_stage"]    # e.g. evo1
    cid       = pet["cid"]
    evo_info  = EVO_LABELS[evo]

    # Human-readable: "Apex Dragon — Hatchling"
    display_name = species.replace("_", " ").title()
    token_name   = f"{display_name} \u2014 {evo_info['name']}"

    metadata = {
        "name": token_name,
        "description": (
            f"A {evo_info['rarity']} BROskiPet dNFT. "
            f"The {display_name} at {evo_info['name']} stage. "
            f"Evolves through dev actions, XP, and BROski$ spending. "
            f"Part of the HyperFocus Zone ecosystem."
        ),
        "image": f"ipfs://{cid}",
        "external_url": f"https://broskipets.xyz/pet/{species}/{evo}",
        "attributes": [
            {"trait_type": "Species",     "value": display_name},
            {"trait_type": "Evo Stage",   "value": evo_info["name"]},
            {"trait_type": "Rarity",      "value": evo_info["rarity"]},
            {"trait_type": "XP Required", "value": evo_info["xp_required"]},
            {"trait_type": "Collection",  "value": "BROski Pets dNFTs"},
            {"trait_type": "Ecosystem",   "value": "HyperFocus Zone"},
        ]
    }

    filename = f"{species}_{evo}.json"
    filepath = OUT_DIR / filename
    filepath.write_text(json.dumps(metadata, indent=2))
    print(f"  \U0001f4c4 {filename}")

print(f"\n\u2705 {len(pets)} metadata files written to ./{OUT_DIR}/")
print("\U0001f680 Next: run scripts/upload_metadata.py to pin to IPFS!")

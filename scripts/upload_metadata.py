#!/usr/bin/env python3
"""
BROskiPets — Metadata Uploader
Pins all 80 metadata JSON files to Pinata (IPFS)
Writes metadata_cid back to Supabase pet_assets table

Run AFTER generate_metadata.py has created the metadata/ folder
"""

import json
import os
import time
from pathlib import Path

import requests

# ── CONFIG ──────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
PINATA_JWT   = os.environ["PINATA_JWT"]
GW           = "aqua-few-dolphin-310.mypinata.cloud"
METADATA_DIR = Path("metadata")

PINATA_UPLOAD_URL = "https://api.pinata.cloud/pinning/pinJSONToIPFS"


def pin_json_to_pinata(metadata: dict, filename: str) -> str:
    """Pin a single JSON metadata object to Pinata. Returns CID."""
    headers = {
        "Authorization": f"Bearer {PINATA_JWT}",
        "Content-Type": "application/json",
    }
    payload = {
        "pinataContent": metadata,
        "pinataMetadata": {
            "name": filename,
            "keyvalues": {
                "collection": "BROski_pets_dNFTs",
                "type": "metadata",
            }
        },
        "pinataOptions": {"cidVersion": 1},
    }
    resp = requests.post(PINATA_UPLOAD_URL, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()["IpfsHash"]


def update_supabase_metadata_cid(art_cid: str, metadata_cid: str, metadata_url: str):
    """Write metadata_cid + metadata_url back to pet_assets row."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }
    # Match row by art CID (unique)
    url = f"{SUPABASE_URL}/rest/v1/pet_assets?cid=eq.{art_cid}"
    body = {
        "metadata_cid": metadata_cid,
        "metadata_url": metadata_url,
    }
    resp = requests.patch(url, headers=headers, json=body)
    resp.raise_for_status()


# ── MAIN ─────────────────────────────────────────────────────────────────────────
if not METADATA_DIR.exists():
    print("❌ metadata/ folder not found!")
    print("   Run python3 scripts/generate_metadata.py first")
    exit(1)

files = sorted(METADATA_DIR.glob("*.json"))
print(f"🐾 Found {len(files)} metadata files to upload")
print("Starting Pinata upload...\n")

success = 0
failed  = []

for filepath in files:
    metadata = json.loads(filepath.read_text())
    filename = filepath.stem  # e.g. apex_dragon_evo1

    # Extract the art CID from the image field: "ipfs://bafybei..."
    art_cid = metadata["image"].replace("ipfs://", "")

    try:
        metadata_cid = pin_json_to_pinata(metadata, f"{filename}_metadata.json")
        metadata_url = f"https://{GW}/ipfs/{metadata_cid}"

        update_supabase_metadata_cid(art_cid, metadata_cid, metadata_url)

        print(f"  ✅ {filename}")
        print(f"     CID: {metadata_cid}")
        success += 1

        # Be nice to Pinata rate limits
        time.sleep(0.3)

    except Exception as e:
        print(f"  ❌ FAILED: {filename} — {e}")
        failed.append(filename)

# ── SUMMARY ─────────────────────────────────────────────────────────────────────
print(f"\n{'='*50}")
print(f"✅ Uploaded: {success}/{len(files)}")
if failed:
    print(f"❌ Failed:   {len(failed)}")
    for f in failed:
        print(f"   - {f}")
else:
    print("🎉 All metadata pinned to IPFS & saved to Supabase!")
    print("🚀 BROskiPets are FULLY on-chain ready!")
    print("🐾 Next: wire up the mint flow!")

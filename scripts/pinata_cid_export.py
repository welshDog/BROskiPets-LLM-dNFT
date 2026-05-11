#!/usr/bin/env python3
"""
pinata_cid_export.py
Auto-grabs all file CIDs from all 5 BROskiPets Pinata groups.
Outputs: pinata_cid_inventory.json

Usage:
    export PINATA_JWT=your_jwt_here
    python scripts/pinata_cid_export.py
"""

import requests
import json
import os
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
PINATA_JWT = os.environ.get("PINATA_JWT")
if not PINATA_JWT:
    raise EnvironmentError("❌ PINATA_JWT environment variable not set!")

GATEWAY = "https://aqua-few-dolphin-310.mypinata.cloud/ipfs"
HEADERS = {"Authorization": f"Bearer {PINATA_JWT}"}

GROUPS = {
    "BROski_pets_dNFTs":       "2aedcf70-d4bb-4e13-94c9-ef6098d49aca",
    "BROski_OG_EEPs_dNFTs":    "b4e17293-b3ef-4739-9a7a-cf6b71fb5724",
    "BROski_Dark_EEPs_dNFTs":  "cec7d61c-6d9b-410a-8db9-17489b40bd41",
    "BROski_EEPVENGERS_dNFTs": "e829dd09-64ff-4e60-a3b6-83825a89525e",
    "BROski_Token_dNFT":       "57d6e6bb-8587-4d67-b567-5ce5c9c9752b",
}

# ── Fetch all groups ──────────────────────────────────────────────────────────
def fetch_group(group_name, group_id):
    print(f"\n📡 Fetching: {group_name}")
    url = (
        f"https://api.pinata.cloud/data/pinList"
        f"?groupId={group_id}&status=pinned&pageLimit=1000"
    )
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        print(f"  ⚠️  Error {res.status_code}: {res.text}")
        return []

    files = res.json().get("rows", [])
    results = []
    for f in files:
        cid  = f["ipfs_pin_hash"]
        name = f["metadata"].get("name", "unnamed")
        size = f.get("size", 0)
        results.append({
            "name":         name,
            "cid":          cid,
            "size_bytes":   size,
            "size_mb":      round(size / 1_000_000, 2),
            "gateway_url":  f"{GATEWAY}/{cid}",
            "pinata_url":   f"https://gateway.pinata.cloud/ipfs/{cid}",
            "group":        group_name,
            "group_id":     group_id,
        })
        print(f"  ✅ {name:<40} → {cid}")

    return results


def main():
    inventory = {
        "_meta": {
            "generated": datetime.utcnow().isoformat() + "Z",
            "gateway":   GATEWAY,
            "groups":    list(GROUPS.keys()),
        },
        "groups": {},
        "flat": []
    }

    for group_name, group_id in GROUPS.items():
        assets = fetch_group(group_name, group_id)
        inventory["groups"][group_name] = assets
        inventory["flat"].extend(assets)

    # Save output
    out_path = "pinata_cid_inventory.json"
    with open(out_path, "w") as f:
        json.dump(inventory, f, indent=2)

    total = len(inventory["flat"])
    print(f"\n🎉 Done! Saved to {out_path}")
    print(f"   Groups scanned : {len(GROUPS)}")
    print(f"   Total assets   : {total}")
    print()

    # Print summary table
    print("📊 Summary:")
    for gname, assets in inventory["groups"].items():
        print(f"   {gname:<35} {len(assets):>3} assets")


if __name__ == "__main__":
    main()

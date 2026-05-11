#!/usr/bin/env python3
"""
pinata_to_supabase.py
Reads pinata_cid_inventory.json and upserts all EEP assets
into Supabase tables: eep_assets, dark_eep_assets, eepvenger_assets

Usage:
    export SUPABASE_URL=https://xxxx.supabase.co
    export SUPABASE_SERVICE_KEY=your_service_key
    python scripts/pinata_to_supabase.py
"""

import json
import os
import requests

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise EnvironmentError("❌ SUPABASE_URL and SUPABASE_SERVICE_KEY must be set!")

HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "resolution=merge-duplicates"
}

# Map Pinata group → Supabase table + collection_type
GROUP_MAP = {
    "BROski_OG_EEPs_dNFTs":    ("eep_assets",      "og_eep"),
    "BROski_Dark_EEPs_dNFTs":  ("eep_assets",      "dark_eep"),
    "BROski_EEPVENGERS_dNFTs": ("eep_assets",      "eepvenger"),
    "BROski_Token_dNFT":       ("broski_tokens",   "token"),
    "BROski_pets_dNFTs":       ("pet_assets",      "pet"),
}


def upsert(table, rows):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    res = requests.post(url, headers=HEADERS, json=rows)
    if res.status_code in (200, 201):
        print(f"  ✅ Upserted {len(rows)} rows → {table}")
    else:
        print(f"  ❌ Error {res.status_code}: {res.text}")


def main():
    with open("pinata_cid_inventory.json") as f:
        inventory = json.load(f)

    for group_name, assets in inventory["groups"].items():
        if group_name not in GROUP_MAP:
            print(f"⏭️  Skipping unmapped group: {group_name}")
            continue

        table, collection_type = GROUP_MAP[group_name]
        print(f"\n📤 Upserting {group_name} → {table} ({collection_type})")

        rows = []
        for a in assets:
            rows.append({
                "name":             a["name"],
                "cid":              a["cid"],
                "ipfs_url":         a["gateway_url"],
                "pinata_url":       a["pinata_url"],
                "size_bytes":       a["size_bytes"],
                "collection_type":  collection_type,
                "group_id":         a["group_id"],
                "pinata_group":     group_name,
            })

        if rows:
            upsert(table, rows)

    print("\n🎉 Supabase sync complete!")


if __name__ == "__main__":
    main()

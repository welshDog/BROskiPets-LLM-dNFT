#!/usr/bin/env python3
"""
pin_broski_pets_art.py
Bulk pins all BROski pet evo art (evo1-evo5) + card backgrounds + overlays
to Pinata, then updates Supabase pet_assets table with real image CIDs.

Usage:
    set -a && source <(sed 's/\r//' .env) && set +a
    python3 scripts/pin_broski_pets_art.py
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
PINATA_JWT     = os.environ.get("PINATA_JWT", "").strip()
SUPABASE_URL   = os.environ.get("SUPABASE_URL") or os.environ.get("VITE_SUPABASE_URL", "")
SUPABASE_KEY   = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
GATEWAY        = os.environ.get("IPFS_GATEWAY", "aqua-few-dolphin-310.mypinata.cloud")

REPO_ROOT      = Path(__file__).parent.parent
PETS_DIR       = REPO_ROOT / "broski_pets"
OUTPUT_JSON    = REPO_ROOT / "pet_art_cids.json"

if not PINATA_JWT:
    raise EnvironmentError("❌ PINATA_JWT must be set!")

PINATA_HEADERS = {
    "Authorization": f"Bearer {PINATA_JWT}",
}

# ── Pet species folders ────────────────────────────────────────────────────────
PET_SPECIES = [
    "apex_dragon", "blizzard_lizard", "chaos_cat", "cyber_fox",
    "gigabyte_guinea_pig", "hyper_beam_bunny", "hyper_hamster",
    "hyperfocus_horse", "power_pup", "sonic_spider", "storm_hawk",
    "super_snake", "terra_mole", "ultra_goldfish", "welshdog",
    "wire_wolf",
]
EVO_STAGES = ["evo1", "evo2", "evo3", "evo4", "evo5"]

EXTRA_FOLDERS = {
    "card_backgrounds": PETS_DIR / "card_backgrounds",
    "card_overlays":    PETS_DIR / "Card_over-lays",
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def pin_file(filepath: Path, name: str) -> dict | None:
    """Pin a single file to Pinata. Returns {cid, ipfs_url, pinata_url} or None."""
    url = "https://uploads.pinata.cloud/v3/files"
    try:
        with open(filepath, "rb") as f:
            res = requests.post(
                url,
                headers=PINATA_HEADERS,
                files={"file": (name, f)},
                data={"name": name},
                timeout=120,
            )
        if res.status_code in (200, 201):
            cid = res.json()["data"]["cid"]
            return {
                "cid":        cid,
                "ipfs_url":   f"https://ipfs.io/ipfs/{cid}",
                "pinata_url": f"https://{GATEWAY}/ipfs/{cid}",
                "name":       name,
            }
        else:
            print(f"    ❌ Pinata error {res.status_code}: {res.text[:120]}")
            return None
    except Exception as e:
        print(f"    ❌ Upload exception: {e}")
        return None


def upsert_supabase(table: str, rows: list):
    """Upsert rows to Supabase table."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("  ⚠️  Supabase env not set — skipping DB update")
        return
    headers = {
        "apikey":        SUPABASE_KEY.strip(),
        "Authorization": f"Bearer {SUPABASE_KEY.strip()}",
        "Content-Type":  "application/json",
        "Prefer":        "resolution=merge-duplicates",
    }
    url = f"{SUPABASE_URL.strip()}/rest/v1/{table}"
    res = requests.post(url, headers=headers, json=rows)
    if res.status_code in (200, 201):
        print(f"  ✅ Supabase upserted {len(rows)} rows → {table}")
    else:
        print(f"  ❌ Supabase error {res.status_code}: {res.text[:200]}")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    results = {"pets": {}, "extras": {}}
    supabase_rows = []
    total_ok = 0
    total_fail = 0

    # ── Pet evo stages ────────────────────────────────────────────────────────
    print("\n🐾 Pinning pet evo art...")
    for species in PET_SPECIES:
        folder = PETS_DIR / species
        if not folder.exists():
            print(f"  ⚠️  Folder not found: {folder}")
            continue
        results["pets"][species] = {}
        print(f"\n  📂 {species}")
        for stage in EVO_STAGES:
            filename = f"{species}_{stage}.png"
            filepath = folder / filename
            if not filepath.exists():
                print(f"    ⚠️  Missing: {filename}")
                total_fail += 1
                continue
            print(f"    📤 {filename} ...", end=" ", flush=True)
            result = pin_file(filepath, filename)
            if result:
                results["pets"][species][stage] = result
                supabase_rows.append({
                    "name":            filename,
                    "cid":             result["cid"],
                    "ipfs_url":        result["ipfs_url"],
                    "pinata_url":      result["pinata_url"],
                    "collection_type": "pet",
                    "pinata_group":    "BROski_pets_dNFTs",
                    "species":         species,
                    "evo_stage":       stage,
                })
                print(f"✅ {result['cid'][:20]}...")
                total_ok += 1
            else:
                total_fail += 1
            time.sleep(0.3)  # be nice to Pinata rate limits

    # ── Card backgrounds + overlays ───────────────────────────────────────────
    print("\n🃏 Pinning card backgrounds + overlays...")
    for asset_type, folder in EXTRA_FOLDERS.items():
        if not folder.exists():
            print(f"  ⚠️  Folder not found: {folder}")
            continue
        results["extras"][asset_type] = {}
        for filepath in sorted(folder.glob("*.png")):
            print(f"  📤 {filepath.name} ...", end=" ", flush=True)
            result = pin_file(filepath, filepath.name)
            if result:
                results["extras"][asset_type][filepath.stem] = result
                print(f"✅ {result['cid'][:20]}...")
                total_ok += 1
            else:
                total_fail += 1
            time.sleep(0.3)

    # ── Save JSON ─────────────────────────────────────────────────────────────
    with open(OUTPUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Saved CID map → {OUTPUT_JSON}")

    # ── Update Supabase ───────────────────────────────────────────────────────
    if supabase_rows:
        print("\n🗄️  Updating Supabase pet_assets...")
        # Add evo_stage + species columns if they don't exist yet (safe to run)
        upsert_supabase("pet_assets", supabase_rows)

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"""
🎉 Pin run complete!
   ✅ Pinned : {total_ok}
   ❌ Failed : {total_fail}
   💾 CID map: {OUTPUT_JSON}
""")


if __name__ == "__main__":
    main()

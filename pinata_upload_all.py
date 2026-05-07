#!/usr/bin/env python3
"""
Pin all 10 BROskiPet species (image + Baby-stage metadata) to Pinata in one shot.

Output: a JSON map you paste into the frontend's `species.ts` to swap out the
PLACEHOLDER_*_BABY_CID strings for real CIDs.

Pipeline per species:
    1. Upload  broski_pets/{s}/{s}_evo1.png   -> image_cid
    2. Build   Baby-stage ERC-721 metadata using broski_pet_metadata.py
    3. Upload  metadata JSON                  -> metadata_cid
    4. Add both to the BROski_pets_dNFTs Pinata group (Pinata v3 API)

Usage:
    # Dry-run (no Pinata calls, prints what would be uploaded)
    python pinata_upload_all.py --dry-run

    # Real upload (uses BROski_pets_dNFTs group by default)
    python pinata_upload_all.py

    # Skip the group (legacy v1 endpoint)
    python pinata_upload_all.py --no-group

    # Limit to specific species (handy for retries)
    python pinata_upload_all.py --species cyber_fox power_pup

Env required (real run):
    PINATA_JWT  — JWT from app.pinata.cloud/developers/api-keys
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

import httpx

# Reuse the metadata builder we already smoke-tested
from broski_pet_metadata import BROskiPetMetadata  # type: ignore

# ─── Constants ───────────────────────────────────────────────────────────────
SPECIES_LIST: tuple[str, ...] = (
    "apex_dragon",
    "blizzard_lizard",
    "chaos_cat",
    "cyber_fox",
    "gigabyte_guinea_pig",
    "hyper_beam_bunny",
    "hyper_hamster",
    "hyperfocus_horse",
    "power_pup",
    "sonic_spider",
)

DISPLAY_NAMES: dict[str, str] = {
    "apex_dragon":         "Apex Dragon",
    "blizzard_lizard":     "Blizzard Lizard",
    "chaos_cat":           "Chaos Cat",
    "cyber_fox":           "Cyber Fox",
    "gigabyte_guinea_pig": "Gigabyte Guinea Pig",
    "hyper_beam_bunny":    "Hyper Beam Bunny",
    "hyper_hamster":       "Hyper Hamster",
    "hyperfocus_horse":    "Hyperfocus Horse",
    "power_pup":           "Power Pup",
    "sonic_spider":        "Sonic Spider",
}

# BROski_pets_dNFTs group on Pinata (per the May 2026 handoff)
DEFAULT_GROUP_ID = "2aedcf70-d4bb-4e13-94c9-ef6098d49aca"

# Pinata v3 uploads endpoint (supports group_id)
PINATA_V3_UPLOAD_URL = "https://uploads.pinata.cloud/v3/files"
# Legacy v1 endpoint (used when --no-group)
PINATA_V1_UPLOAD_URL = "https://api.pinata.cloud/pinning/pinFileToIPFS"

REPO_ROOT     = Path(__file__).resolve().parent
SPECIES_ROOT  = REPO_ROOT / "broski_pets"


# ─── Pinata helpers ──────────────────────────────────────────────────────────
def _require_jwt() -> str:
    jwt = os.getenv("PINATA_JWT", "").strip()
    if not jwt:
        sys.exit("error: PINATA_JWT env var is not set. Add it to .env or export it.")
    return jwt


def upload_to_pinata(
    *,
    content:        bytes,
    filename:       str,
    content_type:   str,
    group_id:       Optional[str],
    name_for_pinata: str,
) -> str:
    """Upload bytes to Pinata, returning the CID. Uses v3 with group_id when supplied."""
    jwt = _require_jwt()
    headers = {"Authorization": f"Bearer {jwt}"}

    if group_id:
        files = {"file": (filename, content, content_type)}
        data: dict[str, str] = {"network": "public", "name": name_for_pinata, "group_id": group_id}
        resp = httpx.post(PINATA_V3_UPLOAD_URL, headers=headers, files=files, data=data, timeout=120.0)
        resp.raise_for_status()
        # v3 returns { "data": { "cid": "...", ... } }
        body = resp.json()
        cid = (body.get("data") or {}).get("cid")
        if not cid:
            raise RuntimeError(f"Pinata v3 returned no cid: {body}")
        return cid

    # Legacy path
    files = {"file": (filename, content, content_type)}
    resp = httpx.post(PINATA_V1_UPLOAD_URL, headers=headers, files=files, timeout=120.0)
    resp.raise_for_status()
    return resp.json()["IpfsHash"]


# ─── Per-species upload ─────────────────────────────────────────────────────
def process_species(species: str, *, group_id: Optional[str], dry_run: bool) -> dict:
    species_dir = SPECIES_ROOT / species
    image_path  = species_dir / f"{species}_evo1.png"
    if not image_path.is_file():
        raise FileNotFoundError(f"missing {image_path}")

    display_name = DISPLAY_NAMES[species]

    # 1. Image upload
    if dry_run:
        image_cid = "DRY_RUN_IMAGE_CID"
    else:
        image_cid = upload_to_pinata(
            content=image_path.read_bytes(),
            filename=image_path.name,
            content_type="image/png",
            group_id=group_id,
            name_for_pinata=f"{display_name} — Baby image",
        )

    # 2. Build Baby metadata (rarity defaults to "common" — see note in script header)
    pet = BROskiPetMetadata(
        name=display_name,
        species=species,
        rarity="common",
    )
    metadata_json = pet.build_metadata(image_cid=image_cid)
    metadata_bytes = json.dumps(metadata_json, indent=2, ensure_ascii=False).encode("utf-8")

    # 3. Metadata upload
    if dry_run:
        metadata_cid = "DRY_RUN_METADATA_CID"
    else:
        metadata_cid = upload_to_pinata(
            content=metadata_bytes,
            filename=f"{species}_baby.json",
            content_type="application/json",
            group_id=group_id,
            name_for_pinata=f"{display_name} — Baby metadata",
        )

    return {
        "species":      species,
        "display_name": display_name,
        "image_cid":    image_cid,
        "metadata_cid": metadata_cid,
        "metadata_url": f"ipfs://{metadata_cid}",
    }


# ─── CLI ─────────────────────────────────────────────────────────────────────
def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Pin all BROskiPet species to Pinata and emit the CID map for species.ts",
    )
    p.add_argument(
        "--species",
        nargs="+",
        choices=SPECIES_LIST,
        help="Limit run to specific species (default: all 10)",
    )
    group = p.add_mutually_exclusive_group()
    group.add_argument(
        "--group-id",
        default=DEFAULT_GROUP_ID,
        help=f"Pinata group ID (default: BROski_pets_dNFTs = {DEFAULT_GROUP_ID})",
    )
    group.add_argument(
        "--no-group",
        action="store_true",
        help="Skip the group; use the legacy v1 endpoint",
    )
    p.add_argument("--dry-run", action="store_true", help="No network calls; print the plan")
    p.add_argument(
        "--out",
        default="-",
        help="Path to write the result JSON (default: '-' for stdout)",
    )
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    targets   = args.species or list(SPECIES_LIST)
    group_id  = None if args.no_group else args.group_id

    if not args.dry_run:
        _require_jwt()  # fail fast before iterating

    results: list[dict] = []
    failures: list[dict] = []
    for species in targets:
        try:
            print(f"→ {species}", file=sys.stderr, flush=True)
            res = process_species(species, group_id=group_id, dry_run=args.dry_run)
            print(
                f"  image: {res['image_cid']}\n  meta:  {res['metadata_cid']}",
                file=sys.stderr,
                flush=True,
            )
            results.append(res)
        except Exception as e:
            print(f"  ✗ FAILED: {e}", file=sys.stderr, flush=True)
            failures.append({"species": species, "error": str(e)})

    summary = {
        "dry_run":     args.dry_run,
        "group_id":    group_id,
        "ok_count":    len(results),
        "fail_count":  len(failures),
        "failures":    failures,
        "results":     results,
        "ts_snippet":  _build_ts_snippet(results),
    }

    output = json.dumps(summary, indent=2, ensure_ascii=False)
    if args.out == "-":
        print(output)
    else:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)

    return 0 if not failures else 1


def _build_ts_snippet(results: list[dict]) -> str:
    """Print a paste-ready replacement block for species.ts."""
    if not results:
        return "// no successful uploads"
    lines = ["// Paste over the matching SPECIES entries in frontend/src/lib/species.ts"]
    for r in results:
        lines.append(
            f"// {r['display_name']:<24} babyMetadataCid: '{r['metadata_cid']}',"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())

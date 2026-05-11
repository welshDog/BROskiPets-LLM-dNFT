#!/usr/bin/env python3
"""
BROskiPets — Pets API Router
GET /api/pets          — list all 80 pets (filterable)
GET /api/pets/{species} — get all evo stages for one species
GET /api/pets/{species}/{evo_stage} — get single pet
"""

import os
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import httpx

router = APIRouter(prefix="/api/pets", tags=["pets"])

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
GW           = "aqua-few-dolphin-310.mypinata.cloud"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}


# ── MODELS ────────────────────────────────────────────────────────────────────
class Pet(BaseModel):
    id:           int
    name:         str
    species:      str
    evo_stage:    str
    cid:          str
    ipfs_url:     str
    pinata_url:   str
    metadata_cid: Optional[str] = None
    metadata_url: Optional[str] = None

    @property
    def display_name(self) -> str:
        return self.species.replace("_", " ").title()

    @property
    def gateway_url(self) -> str:
        return f"https://{GW}/ipfs/{self.cid}"


# ── HELPERS ───────────────────────────────────────────────────────────────────
async def _fetch(params: str) -> list:
    url = f"{SUPABASE_URL}/rest/v1/pet_assets?{params}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=HEADERS)
        resp.raise_for_status()
        return resp.json()


# ── ROUTES ─────────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[Pet])
async def list_pets(
    species:   Optional[str] = Query(None, description="Filter by species e.g. apex_dragon"),
    evo_stage: Optional[str] = Query(None, description="Filter by evo stage e.g. evo1"),
    rarity:    Optional[str] = Query(None, description="Filter by rarity: Common, Rare, Epic, Legendary"),
):
    """
    List all BROskiPets. Optionally filter by species, evo_stage, or rarity.

    Examples:
    - GET /api/pets/
    - GET /api/pets/?species=apex_dragon
    - GET /api/pets/?evo_stage=evo5
    - GET /api/pets/?species=welshdog&evo_stage=evo3
    """
    EVO_RARITY = {
        "evo1": "Common", "evo2": "Common",
        "evo3": "Rare",   "evo4": "Epic",
        "evo5": "Legendary"
    }

    params = "select=*&order=species,evo_stage"
    if species:
        params += f"&species=eq.{species}"
    if evo_stage:
        params += f"&evo_stage=eq.{evo_stage}"

    data = await _fetch(params)

    # Filter by rarity in-memory (derived field)
    if rarity:
        data = [p for p in data if EVO_RARITY.get(p["evo_stage"], "").lower() == rarity.lower()]

    return data


@router.get("/{species}", response_model=list[Pet])
async def get_species(
    species: str,
):
    """
    Get all 5 evo stages for a single species.

    Example: GET /api/pets/apex_dragon
    """
    data = await _fetch(f"select=*&species=eq.{species}&order=evo_stage")
    if not data:
        raise HTTPException(status_code=404, detail=f"Species '{species}' not found")
    return data


@router.get("/{species}/{evo_stage}", response_model=Pet)
async def get_single_pet(
    species:   str,
    evo_stage: str,
):
    """
    Get one specific pet by species + evo stage.

    Example: GET /api/pets/welshdog/evo5
    """
    data = await _fetch(
        f"select=*&species=eq.{species}&evo_stage=eq.{evo_stage}&limit=1"
    )
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"Pet '{species}/{evo_stage}' not found"
        )
    return data[0]

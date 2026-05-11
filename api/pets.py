#!/usr/bin/env python3
"""
BROskiPets Pets Router — Supabase-backed pet catalog endpoints.

Placeholder for future Supabase integration.
Currently a minimal router to satisfy the main.py import requirement.
"""

from fastapi import APIRouter, HTTPException
from typing import Optional

router = APIRouter(prefix="/api/pets", tags=["Pets Catalog"])


@router.get("/", tags=["Pets Catalog"])
async def list_all_pets(species: Optional[str] = None, rarity: Optional[str] = None):
    """
    List all pets from Supabase (or local squad JSON for now).
    Filterable by species and rarity.
    """
    return {
        "message": "Supabase pet catalog not yet integrated",
        "status": "placeholder",
        "note": "Use /squad and /pet/{pet_id} endpoints instead"
    }


@router.get("/{species}", tags=["Pets Catalog"])
async def get_pets_by_species(species: str):
    """Get all evolution stages for a species."""
    return {
        "species": species,
        "message": "Supabase pet catalog not yet integrated",
        "status": "placeholder"
    }


@router.get("/{species}/{evo_stage}", tags=["Pets Catalog"])
async def get_pet_by_species_and_stage(species: str, evo_stage: str):
    """Get a specific pet by species and evolution stage."""
    return {
        "species": species,
        "evo_stage": evo_stage,
        "message": "Supabase pet catalog not yet integrated",
        "status": "placeholder"
    }

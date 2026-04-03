#!/usr/bin/env python3
"""
BROskiPets — FastAPI Application
Phase 1: Health + basic pet routes.
Author: welshDog (Lyndon Williams)
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
import structlog

from src.core.redis_pool import health_check as redis_health
from src.core.llm_client import health_check as llm_health
from src.core.pet_agent import BROskiPet

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("bropets_api.startup")
    yield
    log.info("bropets_api.shutdown")


app = FastAPI(
    title="BROskiPets API",
    description="LLM-powered dNFT Pet Agents — EEPVengers",
    version="1.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# ── Schemas ───────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)


class SpawnRequest(BaseModel):
    pet_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=50)
    species: str = Field(..., min_length=1, max_length=50)
    personality: str = Field(..., min_length=1, max_length=200)


# ── Health Routes ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["system"])
async def health():
    """Basic liveness probe."""
    return {"status": "ok", "service": "bropets-api"}


@app.get("/ready", tags=["system"])
async def ready():
    """Readiness probe — checks Redis + LLM."""
    redis_ok = redis_health()
    llm_ok = await llm_health()
    if not redis_ok or not llm_ok:
        raise HTTPException(
            status_code=503,
            detail={"redis": redis_ok, "llm": llm_ok},
        )
    return {"status": "ready", "redis": redis_ok, "llm": llm_ok}


# ── Pet Routes ────────────────────────────────────────────────────────────────
@app.post("/api/v1/pets", tags=["pets"])
async def spawn_pet(req: SpawnRequest):
    """Spawn a new BROskiPet."""
    pet = BROskiPet(
        pet_id=req.pet_id,
        name=req.name,
        species=req.species,
        personality=req.personality,
    )
    return {"status": "spawned", "pet": pet.get_status()}


@app.get("/api/v1/pets/{pet_id}", tags=["pets"])
async def get_pet(pet_id: str):
    """Get pet status."""
    # In production: load from DB/registry
    # For now: reconstruct from Redis
    pet = BROskiPet(pet_id=pet_id, name=pet_id, species="Unknown", personality="curious")
    return pet.get_status()


@app.post("/api/v1/pets/{pet_id}/feed", tags=["pets"])
async def feed_pet(pet_id: str):
    """Feed the pet."""
    pet = BROskiPet(pet_id=pet_id, name=pet_id, species="Unknown", personality="curious")
    result = pet.feed()
    return {"message": result, "status": pet.get_status()}


@app.post("/api/v1/pets/{pet_id}/chat", tags=["pets"])
async def chat_with_pet(pet_id: str, req: ChatRequest):
    """Chat with a pet via LLM."""
    pet = BROskiPet(pet_id=pet_id, name=pet_id, species="Unknown", personality="curious")
    response = await pet.chat(req.message)
    return {"response": response, "status": pet.get_status()}

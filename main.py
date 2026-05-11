#!/usr/bin/env python3
"""
BROskiPets API — FastAPI main entrypoint
Runs on port 8080 (Docker) or override with PORT env var.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# --- Routers ---
from api.shop import router as shop_router

app = FastAPI(
    title="BROskiPets API 🐾",
    description="dNFT Pet ecosystem — Shop, Effects, Tokens",
    version="2.4.0",
)

# CORS — allow all for local dev, tighten in prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Register Routers ---
app.include_router(shop_router)  # mounts at /api/shop/*


@app.get("/")
async def root():
    return {"status": "BROskiPets API online 🐾", "version": "2.4.0"}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "broski-pets-api"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

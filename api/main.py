#!/usr/bin/env python3
"""
BROskiPets API — FastAPI main entrypoint
Docker runs: uvicorn api.main:app
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from api.shop import router as shop_router

app = FastAPI(
    title="BROskiPets API 🐾",
    description="dNFT Pet ecosystem — Shop, Effects, Tokens",
    version="2.4.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(shop_router)  # /api/shop/*


@app.get("/")
async def root():
    return {"status": "BROskiPets API online 🐾", "version": "2.4.0"}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "BROskiPets API", "version": "2.4.0"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=True)

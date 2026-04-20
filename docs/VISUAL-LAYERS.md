# VISUAL-LAYERS — Asset Strategy & Rules (P2)

This document locks how BROskiPets visuals are produced and referenced in metadata.
It is intentionally scoped to the first production-ready art pipeline (no breeding visuals).

## Goals

- Deterministic: the same pet + stage always resolves to the same image.
- IPFS-native: metadata `image` points to an `ipfs://...` URL.
- Simple to operate: minting and evolution should not rely on complex runtime rendering.

## Canonical Identifiers

- **Pet ID:** the canonical squad ID from `eeps/squad.json` (e.g. `001`).
- **Stage name:** lower-case version of the evolution stage:
  - `baby`, `young`, `trained`, `elite`, `legendary`, `quantum`
- **Stage int (contract):** `1..6` mapping:
  - `Baby=1`, `Young=2`, `Trained=3`, `Elite=4`, `Legendary=5`, `Quantum=6`

## Strategy Decision (V1)

### V1 Choice: Pre-rendered PNGs

**Decision:** pre-render and upload **468 PNGs** (78 pets × 6 stages).

**Why this is the default:**
- Fast mint/evolve: no image rendering at runtime.
- Lowest complexity: avoids a compositor service, GPU requirements, and caching issues.
- Stable OpenSea display: a direct IPFS image is the least fragile integration.

### V2 Option (Future): On-demand Compositor

Not implemented in V1.

If/when adopted, it needs:
- A locked trait + layer schema (background/body/eyes/accessory/etc.).
- Deterministic seed per pet token (on-chain or derived from `tokenId`).
- Rendering infra (serverless or container), caching, and an upload step to IPFS per evolution.

## Image Addressing Rule (V1)

The metadata layer can reference images in two modes:

### Mode A (Preferred): Direct CID

When an image CID is known for the stage:
- `metadata.image = "ipfs://{image_cid}"`

### Mode B (Local dev / placeholder)

When no CID is available:
- `metadata.image = "ipfs://EEPVengers/{pet_id}/{stage}.png"`

This placeholder is for local development only.

## IPFS Directory Layout (V1)

There are two valid layouts. Pick one and stick to it.

### Layout 1: One CID per image (simplest)

- Each PNG upload returns a CID for that file.
- Metadata stores the CID directly (Mode A).

Pros:
- Simple: upload file → get CID.
Cons:
- Harder to browse as a “folder” on some gateways.

### Layout 2: One CID for an images folder (bulk)

- Upload a directory such that the root CID contains:
  - `{pet_id}/{stage}.png`

Example:
- `ipfs://{ROOT_CID}/001/baby.png`
- `ipfs://{ROOT_CID}/001/young.png`

Pros:
- Easy to browse; one root CID to version.
Cons:
- Requires directory pin/upload workflow.

## Layer Rules (Reserved for V2)

If we move to an actual layer compositor, we must define:
- Layer order
- Allowed trait combinations
- Rarity-conditioned visuals (e.g. Quantum glow layer)
- Export rules per stage

Placeholder schema:
- background
- body
- eyes
- mouth
- accessory
- aura (rarity)
- overlay (stage-specific FX)

## Asset Manifest (Required)

We need a machine-readable manifest before uploading.

Minimum fields per asset:
- `pet_id` (e.g. `001`)
- `stage` (e.g. `trained`)
- `filename` (e.g. `001/trained.png`)
- `sha256` (content hash)
- `image_cid` (optional until uploaded)
- `root_cid` (optional if using directory layout)

## Acceptance Tests (Definition of Done)

### Asset completeness
- All 78 pets have 6 stage images each (468 total).
- All filenames follow: `{pet_id}/{stage}.png`.

### Metadata correctness
- `metadata.image` resolves to a valid `ipfs://...` URI in production mode.
- `Evolution Stage` attribute matches the stage name.
- Contract `newStage` uses the stage int (`1..6`), never a string.

### Manual QA
- Pick 3 pets across rarities and verify on a gateway:
  - `baby`, `trained`, `legendary` stages show correct image.

## Open Decisions (Tracked Elsewhere)

Any decisions not locked here must be tracked in `docs/SPEC-GAPS.md` under “Visual Layer System”.

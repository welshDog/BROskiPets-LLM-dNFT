# BROskiPets Architecture Handoff

## Purpose

This document is the dev handoff for the current BROskiPets pre-build architecture. It focuses on how to combine:

- existing premium EEP NFTs already on Polygon
- procedurally generated common pets for onboarding
- LLM-driven state changes
- dNFT metadata evolution
- Pinata/IPFS persistence
- future reward unlocks for long-term members

## Core Product Model

BROskiPets should use a two-tier pet system.

### Tier 1: Common BROski Pets

These are infinite procedural pets generated for new users.

Characteristics:
- cheap or free to mint
- outdoor-themed starter pets
- generated from trait layers
- evolve through simple metadata swaps
- can be awarded on signup, streak, or early activity milestone

Suggested traits:
- background: park, beach, forest, city
- body: puppy, kitten, bunny
- fur: fluffy, sleek, spiky
- eyes: happy, sleepy, laser
- glow: none, neon, fire, plasma

### Tier 2: Premium EEP Pets

These are the proper long-term reward NFTs.

Characteristics:
- reused from existing WelshDog collections
- animated GIF identity preserved
- awarded after meaningful engagement milestones
- represent status, loyalty, or advanced progression
- may be claimable, airdropped, or transferred from treasury inventory

Suggested reward path:
- user starts with common pet
- user chats, focuses, and levels up
- user reaches hyperfocus threshold
- system grants premium EEP NFT
- common pet either remains as a history pet, upgrades visually, or gets marked as ascended

## Recommended Architecture

### 1. Smart Contract Layer

Use ERC-721 for BROskiPets common pets.

Suggested responsibilities:
- mint common pet
- evolve metadata URI
- track pet level or stage
- emit evolution events
- optionally support admin reward distribution for premium unlocks

Potential contract split:
- `BROskiPets.sol` for common dNFT mint + evolve
- `BROskiRewardVault.sol` for premium EEP reward distribution
- optional `BROskiStreakRegistry.sol` or off-chain streak service

### 2. Backend Layer

Use FastAPI as the orchestration layer.

Suggested responsibilities:
- receive user activity events
- store pet state in database
- call LLM for progression or personality outputs
- determine whether a metadata update is needed
- generate metadata JSON
- upload metadata to IPFS via Pinata
- call smart contract evolve function
- check milestone eligibility for premium NFT reward

Suggested endpoints:
- `POST /api/pets/mint-common`
- `POST /api/pets/activity`
- `POST /api/pets/evolve`
- `POST /api/pets/reward-check`
- `GET /api/pets/{token_id}`

### 3. LLM Layer

The LLM should not directly write on-chain state.

It should provide structured decisions only.

Suggested response format:

```json
{
  "mood": "focused",
  "xp_delta": 5,
  "evolution_triggered": true,
  "recommended_glow": "plasma",
  "recommended_background": "forest",
  "narrative": "Your pet crackles with hyperfocus energy"
}
```

Use the backend to validate and translate this into metadata changes.

### 4. Metadata Strategy

Avoid expensive full redraws for every stage.

Recommended evolution model:
- base pet stays the same
- glow changes by level
- background changes by environment or streak
- animation variant changes only for major milestones

Suggested metadata fields:

```json
{
  "name": "BROski Common Pet #1",
  "description": "Procedural outdoor BROski pet for new users.",
  "image": "ipfs://CID/images/broski_common_1.png",
  "animation_url": "ipfs://CID/animations/broski_common_1.gif",
  "attributes": [
    {"trait_type": "Background", "value": "forest"},
    {"trait_type": "Glow", "value": "plasma"},
    {"trait_type": "Stage", "value": "2"}
  ],
  "properties": {
    "tier": "common",
    "evolution_style": "glow_background_swap",
    "reward_path": "premium_eep_unlock"
  }
}
```

### 5. IPFS / Pinata Layout

Recommended structure:

```text
ipfs-root/
  images/
    broski_common_1.png
  animations/
    broski_common_1.gif
  metadata/
    broski_common_1.json
  variants/
    glows/
    backgrounds/
```

Best practices:
- pin folders, not just single files
- use stable naming conventions
- store CID references in database
- keep metadata version history for debug
- separate draft assets from production assets

### 6. Reward Unlock Logic

Premium EEP rewards should be milestone-based, not random-only.

Suggested unlock triggers:
- 7-day streak
- 30 completed focus sessions
- specific LLM relationship milestone
- BROski$ staking threshold
- special seasonal event

Suggested reward flow:
1. backend checks milestone
2. backend verifies available reward inventory
3. backend records reward claim
4. admin wallet or reward vault transfers EEP NFT
5. user receives celebration message + metadata update on common pet

## Minimal MVP Build Order

### Phase 1
- define common trait schema
- finish `broski_gen.py`
- create 20 to 50 common base metadata entries
- deploy simple ERC-721 evolveable contract

### Phase 2
- connect FastAPI activity endpoint
- connect LLM structured decision output
- update metadata on Pinata
- call evolve function from backend

### Phase 3
- connect streak logic
- add reward eligibility checks
- map premium EEP inventory
- transfer or assign premium NFT rewards

### Phase 4
- polish UI
- add Discord or Hyperfocus Zone integration
- add Chainlink VRF random event layer
- expand pet variants and special events

## Recommended Next Files

Suggested next implementation targets:
- `contracts/BROskiPets.sol`
- `contracts/BROskiRewardVault.sol`
- `api/routes/pets.py`
- `services/evolution_engine.py`
- `services/pinata_client.py`
- `eeps/reward_inventory.json`
- `data/common_traits.json`

## Key Build Principle

Do not overcomplicate early evolution art.

The fastest path is:
- common pet generator
- metadata-based glow and background swaps
- LLM mood/progression
- premium EEP unlock as the emotional jackpot

That path is realistic, scalable, and preserves the value of the existing animated NFT inventory.

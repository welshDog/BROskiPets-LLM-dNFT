# BROskiPets Spec Gaps (Pre-Production)

This file tracks unresolved specification gaps that block safe implementation.
Status labels:
- `open`: no decision yet
- `decision-needed`: product/architecture call required
- `drafted`: initial proposal exists, needs approval
- `locked`: approved and ready to implement

## P0 — Must Decide Before Main Build

### 1) Chain + Token Standard Strategy
- Status: `decision-needed`
- Current state:
  - Legacy collections are on Polygon and ERC-1155 (OpenSea shared contract).
  - New dNFT system is ERC-721 (`EEPVengers.sol`) on Sepolia -> mainnet path.
- Decision required:
  - Are Polygon ERC-1155 assets legacy display-only?
  - Or do we need migration/bridge into ERC-721 dNFT lifecycle?
- Depends on:
  - Product roadmap and holder communication strategy.
- Blocks:
  - Minting strategy, metadata migration policy, marketplace integration plan.

### 2) Evolution Trigger Policy
- Status: `decision-needed`
- Current state:
  - XP thresholds and stage levels are defined.
  - Contract evolve cooldown is defined (1 hour).
- Decision required:
  - Trigger `evolve()` only on threshold crossing, or also on manual/scheduled updates?
  - Should evolve be auto-fired by backend, queue worker, or explicit API action?
- Depends on:
  - Infrastructure capacity, gas budget policy, UX expectations.
- Blocks:
  - Reliable orchestration design and idempotency guarantees.

## P1 — Required for Feature Completeness

### 3) Visual Layer System
- Status: `open`
- Current state:
  - Path schema exists (`ipfs://EEPVengers/{pet_id}/{stage}.png`).
  - Asset count is known (468 planned images).
- Missing spec:
  - Layer ordering (background/body/eyes/accessories/etc.).
  - Trait compatibility rules and rarity-conditioned art rules.
  - Render strategy: pre-render all 468 vs generate on-demand.
- Depends on:
  - Art direction and rendering pipeline choice.
- Blocks:
  - Deterministic image generation and final metadata pinning workflow.

### 4) Minting Rules + Allocation
- Status: `open`
- Missing spec:
  - Who receives which pets and when.
  - Randomness source (if random assignment is required).
  - Allowlists, pricing, and supply allocation constraints by rarity.
- Depends on:
  - Business model and launch phases.
- Blocks:
  - Production mint endpoints and launch operations runbook.

## P2 — Future Expansion (Do Not Implement Blindly)

### 5) Breeding Mechanics
- Status: `open`
- Missing spec:
  - Allowed pairings and rarity constraints.
  - Inheritance/mutation model.
  - Cooldowns/costs (including whether BROski$ is used).
  - Lineage storage model (on-chain/off-chain split).
- Depends on:
  - Tokenomics and game design.
- Blocks:
  - Any breeding code, breeding UI, or lineage contract extensions.

## Acceptance Criteria to Close This File
- Every `decision-needed` item is moved to `locked`.
- Each locked decision links to:
  - a source doc (`VISUAL-LAYERS.md`, `BREEDING.md`, etc.),
  - implementation owner,
  - test plan entry.

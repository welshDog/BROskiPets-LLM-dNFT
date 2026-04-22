# Changelog

All notable changes to BROskiPets are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- Sepolia deploy + Etherscan verification flow (`forge script ... --verify`)
- Working end-to-end flow: mint → IPFS metadata → on-chain evolve → tokenURI updated
- `scripts/sepolia_mint_first_eep.py` (EIP-1559 tx fields, loads `.env`, reads ABI from `forge build`)
- Docker Compose loads `.env` into the API container (`env_file`) for `PINATA_JWT`, `CONTRACT_ADDRESS`, `AGENT_KEY`
- `IMAGES_ROOT_CID` support for “drop art at the end” image URIs

### Fixed
- Redis auth mismatch between API and Redis container (`REDIS_PASSWORD` propagation)
- IPFS upload failures caused by missing `PINATA_JWT` in the API container environment
- Mint script import path when executed from repo root (`ModuleNotFoundError: agent`)

---

## [0.3.0] — 2026-04-03

### Added
- `contracts/src/EEPVengers.sol` — ERC-721 dNFT contract with:
  - `MAX_SUPPLY = 78` hardcoded cap
  - `evolve(tokenId, newCID, newStage)` — AGENT_ROLE gated, 1-hour cooldown
  - `evolveCooldownRemaining()` view function
  - `totalMinted()` view function
  - `Pausable`, `ReentrancyGuard`, `AccessControl` from OpenZeppelin v5
  - `PetMinted` and `PetEvolved` events
- `contracts/test/EEPVengers.t.sol` — 16 Foundry tests + 10,001 fuzz runs
- `contracts/foundry.toml` — Foundry config with fuzz runs=10,000 and `src = "src"` layout
- `contracts/README.md` — contract-specific documentation
- `contracts/lib/forge-std` and `contracts/lib/openzeppelin-contracts` as git submodules
- `tests/test_agent.py` — 37 pytest tests covering agent lifecycle, injection guard, squad loading
- `tests/test_metadata.py` — 36 pytest tests covering EIP-721 metadata, level thresholds, IPFS upload
- `docs/architecture.md` — full system design documentation
- `docs/development.md` — local dev setup guide
- `docs/api.md` — Python and Solidity API reference
- `docs/testing.md` — test suite guide
- `docs/deployment.md` — Sepolia testnet and mainnet deployment guide
- `docs/contributing.md` — contribution workflow
- `docs/style.md` — code style guidelines
- `docs/troubleshooting.md` — common issues and fixes
- `.env.example` — environment variable template
- `CHANGELOG.md` — this file

### Fixed
- **Critical:** `RAREITY_TIERS` typo in `metadata.py` → `RARITY_TIERS` — was causing `NameError` at runtime whenever `generate_metadata()` was called
- **Contract:** `evolve()` cooldown check was blocking the first evolution on newly minted tokens (`lastEvolved == 0` now treated as "never evolved → allow immediately")
- **Contract:** `evolveCooldownRemaining()` was returning 3599 for newly minted tokens instead of 0
- **Agent:** duplicate `_call_ollama` function definition removed from `agent.py`

### Changed
- `metadata.py` — `generate_metadata()` now accepts optional `image_cid` parameter (uses real IPFS path when provided, placeholder path for local dev)
- `metadata.py` — added `upload_to_ipfs()` and `upload_metadata_to_ipfs()` with Redis CID caching
- `agent.py` — Ollama API call implemented (was placeholder stub)
- `agent.py` — prompt injection guard expanded from 4 patterns to 15 (`INJECTION_PATTERNS` constant)
- `agent.py` — `_call_ollama()` has 30-second timeout and graceful offline fallback
- Contract `evolve()` — parameter order changed to `(tokenId, newCID, newStage)` for clarity
- Contract `PetEvolved` event — added `timestamp` as 4th parameter
- Contract constructor — changed from 3-arg `(admin, minter, agent)` to 1-arg `(adminMultisig)` with roles granted externally

### Resolved
- Merge conflict between local `923db8a` and remote `757cdb4` — all conflicts resolved, both branches' improvements preserved

---

## [0.2.0] — 2026-04-03

### Added
- `agent.py` — `_call_ollama()` wired up (httpx POST to Ollama `/api/chat`)
- Extended prompt injection blocklist (`INJECTION_PATTERNS` module constant)
- `metadata.py` — IPFS upload pipeline via Pinata
- `metadata.py` — Redis CID caching (idempotent uploads)

### Fixed
- `RAREITY_TIERS` typo → `RARITY_TIERS` (initial fix commit)

---

## [0.1.0] — 2026-04-01 — Initial Release

### Added
- `agent.py` — `BROskiPet` class with `feed()`, `chat()`, `get_status()`, `update_state()`
- `metadata.py` — `EEPMetadata` class with `calculate_level()`, `generate_metadata()`, `_hash_state()`
- `eeps/squad.json` — all 78 EEPs with name, species, role, power, and rarity
- `docker-compose.yml` — Redis + Ollama + API stack
- `docs/EEPS-POWERS.md` — full EEP powers reference with rarity tiers
- `roadmaps/2036-vision.md` — 10-year vision roadmap
- `tiktok/scripts.md` — social media content scripts
- `README.md` — initial project overview
- `LICENSE` — MIT

---

## Version Scheme

BROskiPets uses [Semantic Versioning](https://semver.org/):

- **MAJOR** — breaking changes to the contract ABI or Python API
- **MINOR** — new features, backwards-compatible
- **PATCH** — bug fixes, documentation, dependency updates

Pre-mainnet (< 1.0.0), breaking changes may occur in minor versions.

[Unreleased]: https://github.com/welshDog/BROskiPets-LLM-dNFT/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/welshDog/BROskiPets-LLM-dNFT/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/welshDog/BROskiPets-LLM-dNFT/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/welshDog/BROskiPets-LLM-dNFT/releases/tag/v0.1.0

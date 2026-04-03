# BROskiPets — LLM-Powered dNFT Pet Agents

> 78 unique AI-native pets, each with a real LLM brain, evolving on-chain as dynamic NFTs.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests: 89 passing](https://img.shields.io/badge/tests-89%20passing-brightgreen.svg)](docs/testing.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![Solidity 0.8.24+](https://img.shields.io/badge/solidity-0.8.24%2B-purple.svg)](contracts/EEPVengers.sol)
[![Docker Ready](https://img.shields.io/badge/docker-ready-blue.svg)](docker-compose.yml)

---

## What Is This?

BROskiPets is an open-source framework for **LLM-powered virtual pet agents** that live as **dynamic NFTs (dNFTs)** on-chain. Each pet has its own personality, memory, and needs — and evolves visually and on-chain as you interact with it.

**Key properties:**

- **LLM brain** — each pet runs on Qwen2.5:7b via Ollama, with a unique personality and Redis-backed memory
- **Dynamic NFT** — ERC-721 contract with updatable IPFS metadata; the token URI changes on evolution
- **78 EEPs** — the EEPVengers squad, ranging from Common to Quantum rarity
- **Security-first** — prompt injection guards, Docker isolation, role-based contract access, and an evolve cooldown rate-limit
- **One-command start** — `docker compose up` and everything runs locally

---

## The EEPVengers Squad

78 unique AI pet agents — each with a role, rarity, and power that maps to a real capability in the HyperCode ecosystem.

| Rarity | Chance | Count | Example |
|--------|--------|-------|---------|
| Common | 50% | ~39 | DonutEep, RobotEep, CatEep |
| Uncommon | 30% | ~23 | ReindeerEep, BeeEep, DolphinEep |
| Rare | 15% | ~12 | OwlEep, SharkEep, OctopusEep |
| Legendary | 4% | 3 | SpiderEep, VenomEep, QueenEep |
| Quantum | 1% | 2 | UnicornEep, WelshDogEep |

> Full squad list with powers: [`eeps/squad.json`](eeps/squad.json) | [`docs/EEPS-POWERS.md`](docs/EEPS-POWERS.md)

---

## Quick Start

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Docker + Docker Compose | 24+ | Run the full stack |
| Python | 3.10+ | Backend development |
| Node.js | 18+ | Contract tooling |
| Foundry | Latest | Solidity tests |

### 1 — Clone and start

```bash
git clone https://github.com/welshDog/BROskiPets-LLM-dNFT.git
cd BROskiPets-LLM-dNFT
```

Copy the environment template:

```bash
cp .env.example .env
# Edit .env — at minimum set REDIS_PASSWORD
```

Start everything:

```bash
docker compose up
# First run pulls ~4 GB of models — grab a coffee
```

Visit `http://localhost:8080` when all services are healthy.

### 2 — Interact with a pet

```python
from agent import BROskiPet

spider = BROskiPet(
    pet_id="spider_001",
    name="SpiderEep",
    species="Spider",
    personality="brave, curious, slightly sarcastic",
)

print(spider.feed())
# 🍖 SpiderEep munches happily! Hunger: 30 | XP: +10

print(spider.chat("Find me some bugs!"))
# *SpiderEep skitters across your codebase* Found 3 potential issues...
```

### 3 — Generate dNFT metadata

```python
from metadata import EEPMetadata

eep = EEPMetadata(
    pet_id="spider_001",
    name="SpiderEep",
    species="Spider",
    rarity="Legendary",
    token_id=1,
)

state = {"xp": 750, "happiness": 95, "hunger": 20, "energy": 80,
         "last_interaction": "2026-04-03T12:00:00"}

metadata = eep.generate_metadata(state)
print(metadata["attributes"])
# [{"trait_type": "Level", "value": 3}, {"trait_type": "Evolution Stage", "value": "Trained"}, ...]
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        BROskiPets Core                          │
│                                                                 │
│  ┌─────────────────┐    ┌──────────────────┐                   │
│  │   agent.py       │    │   metadata.py     │                   │
│  │  BROskiPet class │    │  EEPMetadata      │                   │
│  │  LLM chat loop   │    │  EIP-721 builder  │                   │
│  │  Injection guard │    │  IPFS uploader    │                   │
│  └────────┬────────┘    └────────┬─────────┘                   │
│           │                      │                              │
│  ┌────────▼──────────────────────▼─────────┐                   │
│  │              Redis (pet state)           │                   │
│  │  hunger · energy · happiness · xp        │                   │
│  │  memory · last_interaction               │                   │
│  └─────────────────────────────────────────┘                   │
│                                                                 │
│  ┌─────────────────┐    ┌──────────────────┐                   │
│  │  Ollama (LLM)   │    │   IPFS / Pinata  │                   │
│  │  Qwen2.5:7b     │    │  Metadata + art  │                   │
│  └─────────────────┘    └──────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  EEPVengers.sol     │
                    │  ERC-721 dNFT      │
                    │  Ethereum / Polygon │
                    └────────────────────┘
```

**State split:**

| Layer | What lives here | Update frequency |
|-------|----------------|-----------------|
| On-chain | Token ownership, evolution stage, IPFS CID | Per evolution (~hours) |
| Redis | Hunger, energy, happiness, XP | Per interaction (~seconds) |
| IPFS | Metadata JSON, pet images | Per evolution |

---

## Repository Structure

```
BROskiPets-LLM-dNFT/
├── agent.py                  ← Core LLM pet agent + prompt injection guard
├── metadata.py               ← dNFT metadata engine + IPFS upload pipeline
├── docker-compose.yml        ← Full stack: API + Redis + Ollama
├── .env.example              ← Environment variable template
│
├── contracts/
│   ├── EEPVengers.sol        ← ERC-721 dNFT smart contract
│   ├── foundry.toml          ← Foundry config (solc, fuzz, invariant)
│   ├── README.md             ← Contract-specific docs
│   ├── lib/                  ← OpenZeppelin + forge-std (git submodules)
│   └── test/
│       └── EEPVengers.t.sol  ← 16 Foundry tests + 10k fuzz runs
│
├── eeps/
│   └── squad.json            ← All 78 EEPs with rarity + powers
│
├── tests/
│   ├── test_agent.py         ← 37 pytest tests (fakeredis, injection guard)
│   └── test_metadata.py      ← 36 pytest tests (EIP-721, level thresholds)
│
├── docs/
│   ├── architecture.md       ← Deep-dive system design
│   ├── development.md        ← Local dev setup guide
│   ├── deployment.md         ← Testnet + mainnet deployment
│   ├── api.md                ← Python API + future FastAPI reference
│   ├── testing.md            ← How to run all test suites
│   ├── contributing.md       ← Contribution workflow
│   ├── style.md              ← Code style guidelines
│   ├── troubleshooting.md    ← Common issues and fixes
│   └── EEPS-POWERS.md        ← Full EEP powers reference
│
├── roadmaps/
│   └── 2036-vision.md        ← 10-year roadmap
│
└── CHANGELOG.md              ← Version history
```

---

## Configuration

All configuration is via environment variables. Copy `.env.example` to `.env`:

```bash
# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_strong_password_here

# LLM (Ollama)
LLM_MODEL=qwen2.5:7b
LLM_BASE_URL=http://ollama:11434

# IPFS (Pinata) — required for on-chain minting
PINATA_JWT=your_pinata_jwt_here

# IPFS Gateway (for metadata resolution)
IPFS_GATEWAY=https://gateway.pinata.cloud/ipfs
```

> Get a free Pinata JWT at [app.pinata.cloud/developers/api-keys](https://app.pinata.cloud/developers/api-keys)

---

## Smart Contract

The `EEPVengers.sol` contract is an ERC-721 with per-token URI storage. Metadata evolves on-chain when pets level up.

**Key functions:**

```solidity
// Mint a new EEP (MINTER_ROLE only)
function mint(address to, string calldata petId, string calldata ipfsCID) external

// Evolve a pet — update its IPFS metadata (AGENT_ROLE only)
function evolve(uint256 tokenId, string calldata newCID, uint8 newStage) external

// Check seconds until next evolution is allowed (rate-limited to 1/hour)
function evolveCooldownRemaining(uint256 tokenId) external view returns (uint256)
```

**Deploy to Sepolia testnet:**

```bash
cd contracts
forge script script/Deploy.s.sol \
  --rpc-url $SEPOLIA_RPC \
  --private-key $DEPLOYER_KEY \
  --broadcast
```

Full deployment guide: [docs/deployment.md](docs/deployment.md)

---

## Testing

```bash
# Python tests (73 tests — no external services required)
python -m pytest tests/ -v

# Solidity tests (16 tests + 10,001 fuzz runs)
cd contracts && forge test -v

# Full suite
python -m pytest tests/ -v && cd contracts && forge test
```

**Current status: 89/89 passing**

| Suite | Tests | Status |
|-------|-------|--------|
| Python (pytest) | 73 | ✅ |
| Solidity (Foundry) | 16 | ✅ |
| Fuzz (`testFuzz_EvolveStageRange`) | 10,001 runs | ✅ |

Full testing guide: [docs/testing.md](docs/testing.md)

---

## Security

BROskiPets is built security-first:

- **Prompt injection guard** — 15+ pattern blocklist (VenomEep layer) checked on every `chat()` call
- **Role-based access control** — `MINTER_ROLE`, `AGENT_ROLE`, `DEFAULT_ADMIN_ROLE` are separate; no single key controls everything
- **Evolution cooldown** — 1 hour per token, rate-limits damage from a compromised agent key
- **Pausable contract** — admin multisig can freeze all mints and evolutions
- **ReentrancyGuard** — all state-changing contract functions
- **Docker isolation** — `cap_drop: ALL`, `no-new-privileges: true` on the API container
- **Redis auth** — password-protected, no unauthenticated connections

Report security issues privately to: [security@eepvengers.xyz](mailto:security@eepvengers.xyz)

---

## Roadmap

| Year | Milestone |
|------|-----------|
| 2026 Q2-Q4 | NFT smart contract on Sepolia testnet, first 78 EEPs minted, BROski$ token |
| 2027 | Cross-chain (Polygon + Solana), EEP battling, mobile app, 1k holders |
| 2028 | Multimodal EEPs (vision + voice), DAO governance, 10k holders |
| 2030 | AR companion app, robot body integration |
| 2036 | Quantum-secured EEPs, brain-computer interface, 1M holders |

Full roadmap: [roadmaps/2036-vision.md](roadmaps/2036-vision.md)

---

## Contributing

Contributions are very welcome. See [docs/contributing.md](docs/contributing.md) for the full workflow.

**Quick version:**

```bash
# Fork the repo, then:
git checkout -b feat/your-feature
# Make changes
python -m pytest tests/ -v          # Python tests must pass
cd contracts && forge test           # Solidity tests must pass
git push origin feat/your-feature
# Open a PR
```

---

## Built By

**Lyndon Williams** (welshDog) — AI Agent Architect, dyslexic tinkerer, carpenter who codes. Based in S.Wales.

> *Hyperfocus Zone — Building tools for neurodivergent minds*

[![GitHub](https://img.shields.io/badge/GitHub-welshDog-black.svg)](https://github.com/welshDog)

---

## License

MIT — see [LICENSE](LICENSE)

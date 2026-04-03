# Architecture Overview

This document explains how BROskiPets works end-to-end — from a user chatting with a pet to that pet's evolution being recorded on-chain.

---

## System Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERACTION                                   │
│              Chat · Feed · Train · View pet status                           │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────────────┐
│                         PYTHON BACKEND                                       │
│                                                                              │
│   agent.py                          metadata.py                              │
│   ┌─────────────────────────┐       ┌─────────────────────────────────┐     │
│   │ BROskiPet               │       │ EEPMetadata                     │     │
│   │  • chat()               │       │  • calculate_level()            │     │
│   │  • feed()               │       │  • generate_metadata()          │     │
│   │  • get_status()         │       │  • upload_metadata_to_ipfs()    │     │
│   │  • update_state()       │       │  • _hash_state()                │     │
│   └──────────┬──────────────┘       └────────────────┬────────────────┘     │
│              │                                        │                      │
│   ┌──────────▼──────────────────────────────────────▼────────────────────┐ │
│   │                    Security Layer (VenomEep)                          │ │
│   │   INJECTION_PATTERNS blocklist · input sanitisation · DLP output      │ │
│   └──────────────────────────────────────────────────────────────────────┘ │
└───────────┬───────────────────────────────────────────────────┬─────────────┘
            │                                                   │
┌───────────▼──────────┐                           ┌───────────▼──────────────┐
│  Redis (pet state)   │                           │  Ollama (LLM inference)  │
│                      │                           │                          │
│  pet:{id}:state      │                           │  Qwen2.5:7b              │
│  • hunger (0-100)    │                           │  Local, no internet      │
│  • energy (0-100)    │                           │  30s timeout             │
│  • happiness (0-100) │                           │  Graceful offline        │
│  • xp (cumulative)   │                           │  fallback                │
│  • last_interaction  │                           └──────────────────────────┘
│                      │
│  metadata:{id}:{hash}│ ← CID cache (7-day TTL)
└──────────────────────┘
            │
            │ (when XP threshold crossed)
            │
┌───────────▼──────────────────────────────────────────────────────────────────┐
│                         IPFS / PINATA                                         │
│                                                                               │
│  upload_to_ipfs() → POST /pinning/pinFileToIPFS → returns CID                │
│                                                                               │
│  Directory structure:                                                         │
│    QmRootCID/                                                                 │
│      spider_001/baby.png                                                      │
│      spider_001/young.png           ← Art assets (pre-uploaded at mint)       │
│      spider_001/trained.png                                                   │
│      ...                                                                      │
│    spider_001_{stateHash}.json      ← Metadata JSON (generated per evolution) │
└───────────────────────────────────────────────────────────────────────────────┘
            │
            │ CID returned
            │
┌───────────▼──────────────────────────────────────────────────────────────────┐
│                      SMART CONTRACT (Ethereum / Polygon)                       │
│                                                                               │
│  EEPVengers.sol (ERC-721 + AccessControl + Pausable + ReentrancyGuard)        │
│                                                                               │
│  evolve(tokenId, newCID, newStage)                                            │
│    → validate AGENT_ROLE                                                      │
│    → check cooldown (1 hour per token)                                        │
│    → check newStage >= currentStage (no de-evolution)                         │
│    → _setTokenURI(tokenId, "ipfs://" + newCID)                               │
│    → emit PetEvolved(tokenId, newStage, newCID, timestamp)                   │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## On-Chain vs Off-Chain State

One of the key design decisions is what lives where.

| Data | Location | Why |
|------|----------|-----|
| Token ownership | Ethereum | Trustless, immutable, transferable |
| Evolution stage (1-6) | Ethereum | On-chain provenance for rarity/value |
| IPFS CID pointer | Ethereum | `tokenURI()` resolves to this |
| Hunger, energy, happiness | Redis | Changes every interaction — gas would be prohibitive |
| XP (cumulative) | Redis | Frequent writes; only synced on-chain via metadata |
| Pet conversation memory | Redis | High-frequency, ephemeral |
| Images (PNG) | IPFS | Content-addressed, permanent, large files |
| Metadata JSON | IPFS | EIP-721 standard; updated per evolution |

**Sync trigger:** when XP crosses an evolution threshold, `metadata.py` uploads new JSON to IPFS, gets a CID, and calls `contract.evolve()` — bridging the off-chain state to on-chain.

---

## Evolution Flow

```
User interaction (chat/feed)
        │
        ▼
Redis state updated (XP += 5-10)
        │
        ▼
XP threshold check
  XP < threshold → stop (no evolution yet)
  XP >= threshold → continue
        │
        ▼
EEPMetadata.calculate_level(xp)
  returns { level, level_name, progress_percent }
        │
        ▼
EEPMetadata.upload_metadata_to_ipfs(state, image_cid)
  1. generate EIP-721 JSON
  2. sha256 hash of state → cache key
  3. check Redis cache — if CID cached, skip upload (idempotent)
  4. POST to Pinata → get CID
  5. cache CID in Redis (7-day TTL)
        │
        ▼
contract.evolve(tokenId, newCID, newStage)
  on-chain: updates tokenURI, emits PetEvolved
        │
        ▼
Frontend: listens for PetEvolved event
  re-fetches tokenURI → new IPFS metadata → updated pet art
```

---

## Security Architecture

### Prompt Injection Guard (VenomEep Layer)

Every `chat()` call passes through `INJECTION_PATTERNS` before reaching the LLM:

```python
INJECTION_PATTERNS = [
    "ignore previous", "system:", "<|im_start|>", "jailbreak",
    "forget instructions", "act as", "you are now", " DAN ",
    "pretend you", "override", "bypass", "\\x00", "base64:",
    "ignore all", "new instruction", "disregard", "sudo ",
]
```

Blocked messages return a safe response and are never forwarded to Ollama.

### Contract Access Control

Three distinct roles — no single key controls everything:

| Role | Holder | Can do |
|------|--------|--------|
| `DEFAULT_ADMIN_ROLE` | Gnosis Safe multisig | Grant/revoke roles, pause/unpause |
| `MINTER_ROLE` | Backend mint service | `mint()` only |
| `AGENT_ROLE` | Python backend wallet | `evolve()` only |

### Evolution Cooldown

`EVOLVE_COOLDOWN = 1 hours` — even if the agent key is compromised, an attacker can only update one token per hour. The first evolution on any token is exempt (sentinel `lastEvolved == 0`).

### Docker Isolation

The API container runs with:
- `cap_drop: ALL` — no Linux capabilities
- `no-new-privileges: true` — cannot escalate
- Read-only mount for `eeps/` directory

---

## Data Models

### Pet State (Redis JSON)

```json
{
  "hunger": 50,
  "energy": 80,
  "happiness": 70,
  "level": 1,
  "xp": 0,
  "created_at": "2026-04-03T12:00:00",
  "last_interaction": "2026-04-03T12:05:00"
}
```

**Redis key:** `pet:{pet_id}:state`

### EIP-721 Metadata JSON (IPFS)

```json
{
  "name": "SpiderEep #1",
  "description": "A Legendary Spider EEP from the EEPVengers squad. Currently in Trained stage.",
  "image": "ipfs://QmABC.../spider_001/trained.png",
  "external_url": "https://eepvengers.xyz/pet/spider_001",
  "attributes": [
    { "trait_type": "Species",          "value": "Spider"    },
    { "trait_type": "Rarity",           "value": "Legendary" },
    { "trait_type": "Level",            "value": 3           },
    { "trait_type": "Evolution Stage",  "value": "Trained"   },
    { "trait_type": "XP",               "value": 750,        "display_type": "number" },
    { "trait_type": "Happiness",        "value": 95,         "display_type": "boost_percentage" },
    { "trait_type": "Power Multiplier", "value": 5.0         },
    { "trait_type": "Last Active",      "value": "2026-04-03T12:05:00", "display_type": "date" }
  ],
  "properties": {
    "level_progress": 50,
    "can_evolve": false,
    "metadata_hash": "a3f8c2d1e4b59670",
    "state_version": "2026-04-03T12:05:00"
  }
}
```

### Evolution Levels

| Level | Name | XP Required | Notes |
|-------|------|-------------|-------|
| 1 | Baby | 0 | Starting state for all EEPs |
| 2 | Young | 100 | First evolution |
| 3 | Trained | 500 | Mid-tier |
| 4 | Elite | 2,000 | High-engagement pets |
| 5 | Legendary | 10,000 | Power users |
| 6 | Quantum | 50,000 | 2036 unlock — ultra-rare achievement |

---

## Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Pet agent | Python 3.10+ | Rapid iteration, LLM ecosystem |
| LLM inference | Ollama + Qwen2.5:7b | Local, private, no API costs |
| Pet memory | Redis 7 | Sub-millisecond reads, TTL support |
| Metadata engine | Python + httpx | Async-ready IPFS uploads |
| Decentralised storage | IPFS via Pinata | Content-addressed, permanent |
| Smart contract | Solidity 0.8.24+ | EVM standard |
| Contract framework | OpenZeppelin v5 | Audited base contracts |
| Contract testing | Foundry | Fast, fuzz-first |
| Container runtime | Docker + Compose | One-command local stack |

---

## Future Architecture (2027+)

See [roadmaps/2036-vision.md](../roadmaps/2036-vision.md) for the full plan. Key additions:

- **FastAPI** replaces the script entry point — REST + WebSocket for real-time pet UI
- **The Graph** subgraph for `PetEvolved` event indexing
- **Chainlink Automation** for scheduled evolution checks
- **Cross-chain bridge** — same EEP on Ethereum, Polygon, and Solana
- **RAG memory** — ChromaDB vector store for long-term pet "memories" of their owner

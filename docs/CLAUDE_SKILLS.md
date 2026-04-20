# 🧠 CLAUDE AI Skills — BROskiPets-LLM-dNFT Build Guide

> **Purpose:** This document defines the Claude AI capability profile, expert skill areas, and implementation guidance for building the BROskiPets dNFT system. Use this as a reference for every build phase.

---

## 🔗 1. Smart Contract Architecture

### Core Competencies
- ERC-721 dynamic NFT with overrideable `tokenURI` pointing to IPFS CID
- Role-based access control: `DEFAULT_ADMIN_ROLE`, `MINTER_ROLE`, `AGENT_ROLE`
- `ReentrancyGuard` on state-changing functions
- Emergency pause via `Pausable`

### Implementation Methodology
```solidity
function evolve(uint256 tokenId, string calldata newCID, uint8 newStage)
    external
    onlyRole(AGENT_ROLE)
    whenNotPaused
    nonReentrant
{ }
```

### Success Metrics
- ✅ Mint cost < 0.002 ETH on Base mainnet
- ✅ Evolution update cost < 0.0005 ETH
- ✅ Zero critical findings in Slither static analysis
- ✅ 100% branch coverage in Foundry fuzz tests

---

## 🐙 2. IPFS & Decentralised Storage

### Core Competencies
- Pinata SDK (Python) for programmatic CID generation from `metadata.py`
- Content-addressed metadata: each evolution stage = unique immutable CID
- Dual-pin strategy: Pinata + NFT.storage (Filecoin-backed) for redundancy
- ERC-721 standard metadata JSON schema compliance

### Metadata Schema
```json
{
  "name": "SpiderEep #1",
  "description": "A Legendary Spider EEP from the EEPVengers squad. Currently in young stage.",
  "image": "ipfs://<IMAGE_CID>",
  "attributes": [
    { "trait_type": "Species", "value": "Spider" },
    { "trait_type": "Rarity", "value": "Legendary" },
    { "trait_type": "Level", "value": 2 },
    { "trait_type": "Evolution Stage", "value": "Young" },
    { "trait_type": "XP", "value": 110, "display_type": "number" },
    { "trait_type": "Happiness", "value": 87, "display_type": "boost_percentage" }
  ]
}
```

### Success Metrics
- ✅ Metadata retrieval < 200ms via IPFS gateway
- ✅ 100% pin uptime (dual-provider redundancy)
- ✅ CID generation < 500ms in FastAPI pipeline

---

## 🤖 3. LLM-to-Chain Pipeline

### Core Competencies
- FastAPI `/pet/{pet_id}/evolve` endpoint: state → metadata → IPFS CID → optional on-chain evolve
- Constrained responses from Ollama (Qwen2.5:7b) when chat is enabled
- Strict stage typing for chain calls (`newStage` is `uint8`)

### Decision Pipeline Flow
```
User Interaction
      ↓
BROskiPet.chat() → Redis state update
      ↓
XP threshold check (e.g. XP >= 100)
      ↓
metadata.py → generate new ERC-721 JSON → upload to IPFS → get CID
      ↓
FastAPI POST /pet/{pet_id}/evolve → validate → call contract.evolve()
      ↓
Smart contract evolve() → update tokenURI on-chain
      ↓
Emit PetEvolved event → frontend updates UI
```

### LLM Decision Prompt Template
```python
EVOLUTION_PROMPT = """
You are the BROskiPets evolution engine.
Given the pet state below, decide if the pet should evolve.
Respond ONLY with valid JSON. No extra text.

Pet State: {state_json}
Evolution threshold: XP >= 100

JSON format:
{{"evolve": bool, "new_stage": int, "new_trait": string, "reason": string}}
"""
```

### Success Metrics
- ✅ LLM decision → on-chain CID update < 30 seconds end-to-end
- ✅ JSON parse success rate > 99% (constrained generation)
- ✅ Zero uncaught schema validation errors in production

---

## 🛡️ 4. Security Protocols

### Core Competencies
- Prompt injection detection middleware (extend existing `blocked_patterns` in `agent.py`)
- Regex sanitiser + Pydantic schema validator on all LLM outputs
- Docker sandbox isolation per agent (already implemented)
- TruffleHog secrets scanning in CI/CD (already configured)
- Slither Solidity static analysis in GitHub Actions

### LLM Output Validator (Pydantic)
```python
from pydantic import BaseModel, validator

class EvolutionDecision(BaseModel):
    evolve: bool
    new_stage: int
    new_trait: str
    reason: str

    @validator("new_stage")
    def stage_bounds(cls, v):
        assert 1 <= v <= 6, "Stage must be between 1 and 6"
        return v

    @validator("new_trait")
    def trait_safe(cls, v):
        blocked = ["admin", "system", "root", "sudo"]
        assert v.lower() not in blocked, "Unsafe trait name"
        return v
```

### Extended Prompt Injection Guard
```python
INJECTION_PATTERNS = [
    "ignore previous", "system:", "<|im_start|>", "jailbreak",
    "forget instructions", "act as", "you are now", "DAN",
    "pretend you", "override", "bypass", "\\x00", "base64"
]
```

### Success Metrics
- ✅ Zero prompt injection bypasses in red-team testing
- ✅ Zero secrets in git history (TruffleHog clean)
- ✅ Zero critical Slither findings pre-mainnet
- ✅ All LLM outputs validated before any chain write

---

## ⛓️ 5. Blockchain Architecture

### Chain Selection
- Sepolia is used for testnet development in this repo.
- Mainnet selection is a product decision.

### Dev Tooling Stack
- **Foundry** — faster than Hardhat; use `forge test --fuzz-runs 10000` for evolution logic
- **Hardhat** — fallback for complex deployment scripts
- **Alchemy / QuickNode** — production RPC (not public endpoints)
- **OpenZeppelin Contracts v5** — audited base contracts

### Success Metrics
- ✅ All Foundry fuzz tests pass (10,000 runs)
- ✅ Deployment scripts idempotent (safe to re-run)
- ✅ Contract verified on Basescan post-deploy

---

## 📡 6. dApp Frontend Integration

### Core Competencies
- **wagmi v2 + viem** — type-safe React hooks for wallet/contract interaction
- **RainbowKit** — wallet connect UI accessible to non-crypto users
- **The Graph Protocol** — index `PetEvolved` events; query pet history without RPC hammering
- **Next.js 14 App Router** — SSR for fast initial pet gallery load

### Key Frontend Calls
```typescript
// Read pet metadata
const { data: tokenURI } = useContractRead({
  address: PET_CONTRACT,
  abi: BROskiPetsABI,
  functionName: "tokenURI",
  args: [tokenId],
});

// Pet interactions are off-chain via the API (Redis-backed), and evolve updates tokenURI on-chain.
```

### Success Metrics
- ✅ Wallet connect < 3 seconds
- ✅ Pet state load < 1 second via subgraph
- ✅ Mobile responsive (crypto-curious gamers are on mobile)

---

## 🏗️ 7. DevOps & Infrastructure

### CI/CD Pipeline (GitHub Actions)
```yaml
# .github/workflows/ci.yml
- Checkout code
- Run TruffleHog secrets scan
- Run Slither static analysis on /contracts
- Run forge test --fuzz-runs 1000
- Run pytest on Python backend
- Build Docker image
- Block merge if any step fails
```

### Redis Config for Production
```
appendonly yes          # Crash recovery
maxmemory 512mb         # Cap memory usage
maxmemory-policy allkeys-lru  # Evict old pet states if needed
```

### Success Metrics
- ✅ CI pipeline completes < 5 minutes
- ✅ Zero failed deploys to mainnet
- ✅ Redis pet memory survives container restart

---

## 🗺️ Build Phase Priorities

| Phase | Focus | Key Deliverable |
|-------|-------|----------------|
| 1 | Smart contract + IPFS schema | Deployed ERC-721 on Sepolia testnet |
| 2 | HTTP API surface | FastAPI pet endpoints stable (`/pet/{pet_id}/*`) |
| 3 | Visual asset pipeline | Image strategy locked + asset upload plan |
| 4 | Frontend dApp | Wallet connect + pet gallery |
| 5 | Security audit | Slither clean + red-team passed |
| 6 | Mainnet launch | 78 EEPs minted |

---

## 📚 Key References

- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/5.x/)
- [Pinata Python SDK](https://docs.pinata.cloud/sdks/pinata-sdk/getting-started)
- [Foundry Book](https://book.getfoundry.sh/)
- [wagmi v2 Docs](https://wagmi.sh/)
- [The Graph Docs](https://thegraph.com/docs/)

---

*Built by welshDog (Lyndon Williams) — Hyperfocus Zone 🧠 | BROski HQ*

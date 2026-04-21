# Development Setup

This guide gets you from zero to a fully running local BROskiPets stack for development.

---

## Prerequisites

Install these before starting:

### Required

| Tool | Install | Minimum version |
|------|---------|----------------|
| Docker Desktop | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) | 24.0 |
| Python | [python.org](https://python.org) | 3.10 |
| Git | [git-scm.com](https://git-scm.com) | 2.40 |

### For contract development

| Tool | Install | Notes |
|------|---------|-------|
| Foundry | `curl -L https://foundry.paradigm.xyz \| bash && foundryup` | Installs forge, cast, anvil |
| Node.js | [nodejs.org](https://nodejs.org) | 18+ (for deployment scripts) |

---

## 1 — Clone the Repository

```bash
git clone https://github.com/welshDog/BROskiPets-LLM-dNFT.git
cd BROskiPets-LLM-dNFT
```

If you want to contribute, fork first and clone your fork:

```bash
git clone https://github.com/YOUR_USERNAME/BROskiPets-LLM-dNFT.git
cd BROskiPets-LLM-dNFT
git remote add upstream https://github.com/welshDog/BROskiPets-LLM-dNFT.git
```

---

## 2 — Environment Configuration

```bash
cp .env.example .env
```

Open `.env` and set at minimum:

```bash
REDIS_PASSWORD=pick_a_strong_password
```

For IPFS uploads (needed for on-chain minting), also set:

```bash
PINATA_JWT=your_jwt_from_pinata_cloud
```

> All other defaults work for local development.

---

## 3 — Python Environment

Create and activate a virtual environment:

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (bash / Git Bash)
source .venv/Scripts/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

If `requirements.txt` does not exist yet, install manually:

```bash
pip install redis httpx pytest fakeredis pytest-cov
```

---

## 4 — Docker Stack

Start all services (Redis + Ollama + API):

```bash
docker compose up
```

**First run:** Ollama downloads `qwen2.5:7b` (~4 GB). This takes a few minutes.

**Check services are healthy:**

```bash
docker compose ps
```

Expected output:

```
NAME                STATUS          PORTS
bropets_api         Up (healthy)    0.0.0.0:8080->8080/tcp
bropets_redis       Up              0.0.0.0:6379->6379/tcp
bropets_ollama      Up
```

**Run only infrastructure (without the API):**

```bash
docker compose up redis ollama
```

Useful when iterating on Python code — run `agent.py` locally against Docker-hosted Redis and Ollama.

---

## 5 — Running the Agent Locally

With Redis and Ollama running in Docker:

```bash
# In a separate terminal (with venv activated)
export REDIS_HOST=localhost
export REDIS_PORT=6379
export LLM_BASE_URL=http://localhost:11434

python agent.py
```

If your Docker Compose does not publish the Ollama port to the host, run the agent via the API container (recommended), or publish Ollama explicitly in `docker-compose.yml` for local-only development.

Expected output:

```
🍖 SpiderEep munches happily! Hunger: 30 | XP: +10
*SpiderEep skitters* Hey! I heard 'Hey SpiderEep, fi...' 🐾
{
  "name": "SpiderEep",
  "species": "Spider",
  "personality": "brave, curious, slightly sarcastic",
  "level": 1,
  "xp": 15,
  "needs": {"hunger": 30, "energy": 80, "happiness": 75}
}
```

---

## 6 — Solidity / Contract Development

Install dependencies (only needed once):

```bash
cd contracts
forge install
```

This installs OpenZeppelin v5 and forge-std as git submodules.

**Compile contracts:**

```bash
forge build
```

**Run tests:**

```bash
forge test -v
```

**Run with gas reports:**

```bash
forge test --gas-report
```

**Local testnet (Anvil):**

```bash
# Terminal 1 — start local chain
anvil

# Terminal 2 — deploy to anvil
forge script script/Deploy.s.sol \
  --rpc-url http://localhost:8545 \
  --private-key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 \
  --broadcast
```

> The key above is Anvil's default funded test account. Never use it on mainnet.

---

## 7 — Development Workflow

### Python changes

1. Edit `agent.py` or `metadata.py`
2. Run tests: `python -m pytest tests/ -v`
3. Test manually with `python agent.py` or `python metadata.py`

### Contract changes

1. Edit `contracts/src/EEPVengers.sol`
2. Run tests: `cd contracts && forge test -v`
3. Check gas impact: `forge test --gas-report`
4. Run static analysis: `slither . --config-file slither.config.json` (if Slither installed)

### Adding a new EEP

`eeps/squad.json` is the source of truth.  
`docs/BROskiPets_all_EEPs_MetaData` is a docs mirror and must stay byte-for-byte equivalent at the JSON data level.

1. Add entry to `eeps/squad.json`:
   ```json
   {
     "id": "079",
     "name": "NewEep",
     "species": "NewSpecies",
     "role": "Role Description",
     "power": "What this EEP does",
     "rarity": "Common"
   }
   ```
2. Update `MAX_SUPPLY` in `contracts/src/EEPVengers.sol` and redeploy (the shipped contract hard-caps at 78).
3. Create personality prompt in `eeps/personalities/` (future)
4. Add art assets to `assets/` (future)

---

## 8 — Code Quality Tools

### Python linting

```bash
# Install
pip install ruff black

# Format
black agent.py metadata.py tests/

# Lint
ruff check agent.py metadata.py tests/
```

### Solidity linting

```bash
# Install Slither (requires Python)
pip install slither-analyzer

# Run static analysis
cd contracts
slither . --exclude-dependencies
```

---

## 9 — Environment Variables Reference

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `REDIS_HOST` | `redis` | Yes | Redis hostname |
| `REDIS_PORT` | `6379` | Yes | Redis port |
| `REDIS_PASSWORD` | `bropets_secret` | Yes (prod) | Redis auth password |
| `LLM_MODEL` | `qwen2.5:7b` | Yes | Ollama model name |
| `LLM_BASE_URL` | `http://ollama:11434` | Yes | Ollama API base URL |
| `PINATA_JWT` | *(empty)* | For IPFS | Pinata API JWT |
| `IPFS_GATEWAY` | `https://gateway.pinata.cloud/ipfs` | No | IPFS resolution gateway |
| `SEPOLIA_RPC` | *(empty)* | For deployment | Sepolia RPC endpoint |
| `DEPLOYER_KEY` | *(empty)* | For deployment | Wallet private key |
| `CONTRACT_ADDRESS` | *(empty)* | For agent → chain | Deployed contract address |
| `AGENT_KEY` | *(empty)* | For agent → chain | Agent wallet private key (must have `AGENT_ROLE`) |

---

## 10 — Resetting Local State

**Clear all pet state (Redis):**

```bash
docker compose exec redis redis-cli -a "$REDIS_PASSWORD" FLUSHALL
```

**Restart Ollama (re-download model):**

```bash
docker compose down

# Find the Ollama model volume (it will look like: <project>_ollama_models)
docker volume ls

# Remove it to force a fresh model pull on next start
docker volume rm <project>_ollama_models

docker compose up -d ollama
```

**Full reset:**

```bash
docker compose down -v  # removes all volumes including Redis data
docker compose up
```

---

## Troubleshooting

See [docs/troubleshooting.md](troubleshooting.md) for common issues.

**Most common:**

| Problem | Fix |
|---------|-----|
| Ollama not responding | `docker compose logs ollama` — model may still be downloading |
| Redis connection refused | Check `REDIS_PASSWORD` matches in `.env` |
| `PINATA_JWT` error | Set `PINATA_JWT` in `.env` before calling `upload_metadata_to_ipfs()` |
| Forge: `No such file or directory: lib/` | Run `forge install` in the `contracts/` directory |

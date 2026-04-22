# 🐾 BROski Ecosystem — Claude Context Handoff (BROskiPets-LLM-dNFT)
> Read this first. Every word. Then start the mission.
> **Last synced: April 22, 2026 — Sepolia deploy+verify ✅ | Mint ✅ | Evolve ✅ | 108 tests GREEN ✅**

---

## Who You're Talking To
- **Lyndz** aka BROski♾️ (GitHub: @welshDog, npm: @w3lshdog) — South Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁿
- Autistic + dyslexic + ADHD — chunked output, quick wins first, no waffle
- Windows primary (PowerShell), WSL2 + Raspberry Pi + Docker secondary
- Call them **"Bro"** — that's how we roll
- Short sentences. Emojis. Bold the key stuff. Celebrate wins! 🎉

---

## What Is BROskiPets?

AI-powered evolving dNFTs on **Ethereum Sepolia** testnet.
- 78 unique **Emotionally Evolved Pets (EEPs)**
- LLM determines personality + evolution path
- On-chain `evolve()` call triggered by the API
- IPFS stores updated metadata after each evolution
- Stack: Python FastAPI + web3.py + IPFS + Solidity

---

## The Ecosystem

### Current State (✅ Verified Working)
- ✅ Docker stack up: Redis + Ollama + FastAPI on `http://127.0.0.1:8080`
- ✅ Contract deployed on Sepolia and verified on Etherscan
- ✅ Mint script works (`scripts/sepolia_mint_first_eep.py`)
- ✅ API evolve works: Redis state → IPFS metadata → on-chain `evolve()` → tokenURI updated
- ✅ Cooldown enforced on-chain (returns remaining seconds)

---

## Quick Wins (Run These First)

### 1) Start the stack

```powershell
cd H:\dNFTpet\BROskiPets-LLM-dNFT
docker compose up -d
docker compose ps
curl.exe -i http://127.0.0.1:8080/health
```

### 2) If PowerShell env vars are missing, load `.env` into the current session

```powershell
cd H:\dNFTpet\BROskiPets-LLM-dNFT
Get-Content .env | ForEach-Object {
  $line = $_.Trim()
  if (-not $line -or $line.StartsWith('#') -or $line -notmatch '=') { return }
  $k,$v = $line.Split('=',2)
  $k=$k.Trim()
  $v=$v.Trim().Trim('"').Trim("'")
  if ($k) { [Environment]::SetEnvironmentVariable($k, $v, 'Process') }
}
```

### 3) Ensure Foundry tools work (Windows PATH)

```powershell
$env:PATH += ";$env:USERPROFILE\.foundry\bin"
forge --version
cast --version
```

---

## E2E Mission (Mint → Evolve)

### 1) Deploy + verify (Sepolia)

```powershell
cd H:\dNFTpet\BROskiPets-LLM-dNFT
$env:PATH += ";$env:USERPROFILE\.foundry\bin"
cd contracts
forge script script/Deploy.s.sol --rpc-url $env:SEPOLIA_RPC --private-key $env:DEPLOYER_KEY --broadcast --verify --etherscan-api-key $env:ETHERSCAN_API_KEY -vvv
```

After deploy:
- Put the address into `.env` as `CONTRACT_ADDRESS=0x...`

### 2) Mint token #1 (Sepolia)

```powershell
cd H:\dNFTpet\BROskiPets-LLM-dNFT\contracts
forge build

cd ..
python .\scripts\sepolia_mint_first_eep.py
```

### 3) Evolve token #1 via API

```powershell
$body = '{ "token_id": 1 }'
curl.exe -i -H "Content-Type: application/json" -X POST http://127.0.0.1:8080/pet/001/evolve -d $body
```

### 4) Verify on-chain state (cast)

```powershell
$env:PATH += ";$env:USERPROFILE\.foundry\bin"
cast call $env:CONTRACT_ADDRESS "tokenURI(uint256)(string)" 1 --rpc-url $env:SEPOLIA_RPC
cast call $env:CONTRACT_ADDRESS "evolutionStage(uint256)(uint8)" 1 --rpc-url $env:SEPOLIA_RPC
cast call $env:CONTRACT_ADDRESS "evolveCooldownRemaining(uint256)(uint256)" 1 --rpc-url $env:SEPOLIA_RPC
```

---

## Art Drop-In Plan (Do It At The End)

### Goal
Finish logic first. Add art last. No rework.

### Folder structure to pin to IPFS
Create a folder named `EEPVengers/` containing 78 subfolders:

```text
EEPVengers/001/baby.png
EEPVengers/001/young.png
EEPVengers/001/trained.png
EEPVengers/001/elite.png
EEPVengers/001/legendary.png
EEPVengers/001/quantum.png
...
EEPVengers/078/quantum.png
```

Stages must be lowercase:

```text
baby | young | trained | elite | legendary | quantum
```

When you pin the folder, set:

```text
IMAGES_ROOT_CID=Qm...
```

Metadata will then emit resolvable image URIs:

```text
ipfs://{IMAGES_ROOT_CID}/EEPVengers/{pet_id}/{stage}.png
```

---

## Known Gotchas (Save Time)
- 🐳 Docker Desktop paused = everything looks “running” but Docker API errors. Unpause in the whale menu.
- 🔐 Redis auth mismatch = `redis.exceptions.AuthenticationError`. Fix: ensure API container receives `REDIS_PASSWORD` (Compose uses `env_file: .env`).
- 📦 Pinata 403 = JWT missing in container or revoked. Fix: ensure API container has `PINATA_JWT` via `env_file`.
- 🧪 Foundry tools work but PowerShell env missing = load `.env` into session (snippet above).

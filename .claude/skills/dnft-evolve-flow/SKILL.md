---
name: dnft-evolve-flow
description: BROskiPets dNFT evolution end-to-end flow — Redis pet state → LLM personality → IPFS metadata pin → on-chain evolve() call → tokenURI updated. Cooldown enforcement (3600s). Use when the user says "evolve a pet", "evolve flow", "evolve API", "evolution stuck", "tokenURI not updating", "cooldown error", or extends the evolve pipeline.
---

# dnft-evolve-flow

The evolve flow is the heartbeat of BROskiPets. Five steps, all currently working (verified April 22, 2026).

## The Pipeline

```
POST /pet/{token_id}/evolve
  ↓
1. Read pet state from Redis (current stage, XP, last evolve ts)
  ↓
2. Check cooldown (3600s) — if not expired, return remaining seconds
  ↓
3. LLM determines new stage + personality update
  ↓
4. Build new metadata JSON → pin to IPFS (Pinata)
  ↓
5. Call evolve(token_id, new_uri) on-chain via web3.py + AGENT_KEY
  ↓
6. Update Redis state (new stage, new ts), return result
```

## Trigger an Evolve

```powershell
$body = '{ "token_id": 1 }'
curl.exe -i -H "Content-Type: application/json" `
  -X POST http://127.0.0.1:8080/pet/001/evolve -d $body
```

Or against the contract directly (skipping the API):

```powershell
$env:PATH += ";$env:USERPROFILE\.foundry\bin"
cast send $env:CONTRACT_ADDRESS `
  "evolve(uint256,string)" 1 "ipfs://Qm.../1/young.json" `
  --rpc-url $env:SEPOLIA_RPC `
  --private-key $env:AGENT_KEY
```

But **prefer the API** — it handles cooldown + IPFS + Redis state atomically.

## Stages (lowercase, in order)

```
baby → young → trained → elite → legendary → quantum
```

The contract enforces stage progression: you can't skip stages, and `quantum` is terminal.

## Cooldown — On-Chain Enforced

`EVOLVE_COOLDOWN = 3600s` (1 hour). The contract reverts if `block.timestamp - lastEvolve[tokenId] < 3600`. The API reads `evolveCooldownRemaining()` first and returns a 429-ish response with seconds remaining.

```powershell
# Inspect the cooldown for a token
cast call $env:CONTRACT_ADDRESS "evolveCooldownRemaining(uint256)(uint256)" 1 --rpc-url $env:SEPOLIA_RPC
# 0 = ready to evolve. >0 = wait this many seconds.
```

## Metadata Schema

The metadata JSON pinned to IPFS for each evolution:

```json
{
  "name": "EEP #001 — Young",
  "description": "An emotionally evolved pet at the Young stage.",
  "image": "ipfs://{IMAGES_ROOT_CID}/EEPVengers/001/young.png",
  "external_url": "https://broskipets.example/pet/001",
  "attributes": [
    { "trait_type": "Stage", "value": "young" },
    { "trait_type": "XP", "value": 150 },
    { "trait_type": "Personality", "value": "curious" }
  ]
}
```

Image URI pattern (resolves once `IMAGES_ROOT_CID` is set):

```
ipfs://{IMAGES_ROOT_CID}/EEPVengers/{pet_id}/{stage}.png
```

## Required Services

| Service | Where | Purpose |
|---|---|---|
| Redis | container `redis` (Docker compose) | pet state, cooldown cache |
| Ollama | container `ollama` (Docker compose) | LLM personality determination |
| FastAPI | container `api` on `127.0.0.1:8080` | the orchestrator |
| Pinata | external (HTTPS) | IPFS pin via JWT |
| Sepolia RPC | external | on-chain `evolve()` call |

```powershell
cd H:\dNFTpet\BROskiPets-LLM-dNFT
docker compose up -d
docker compose ps    # all 3 containers should be Up (healthy)
curl.exe -i http://127.0.0.1:8080/health
```

## Required Env (in container, via `env_file: .env`)

```env
REDIS_PASSWORD=<value>
PINATA_JWT=<JWT for pinning>
SEPOLIA_RPC=https://ethereum-sepolia-rpc.publicnode.com
CONTRACT_ADDRESS=0x3691470c6c56D9bb3cBe8052A2cEAcDdeeEe2F09
AGENT_KEY=0x<private key with AGENT_ROLE on the contract>
IMAGES_ROOT_CID=Qm...    # set after pinning EEPVengers/ folder
```

## Common Failures

| Symptom | Cause | Fix |
|---|---|---|
| `redis.exceptions.AuthenticationError` | `REDIS_PASSWORD` not in API container | Confirm `env_file: .env` in compose, restart |
| Pinata 403 | `PINATA_JWT` missing/revoked in container | Re-add JWT, restart container |
| `Cooldown not expired` (returns N seconds) | Last evolve <3600s ago | Wait, or use a different token |
| `revert: caller is not AGENT_ROLE` | `AGENT_KEY` doesn't have the role | Grant role from `ADMIN_ADDRESS` (re-run deploy script's grantRole) |
| `tokenURI` returns old URI after evolve | Tx not yet mined, or evolve failed silently | `cast` confirm + check API logs |
| Image URI 404 in wallet preview | `IMAGES_ROOT_CID` not set, or images not pinned | Use `pinata-ipfs-pin` skill |
| LLM returns gibberish stage | Ollama model not pulled | `docker compose exec ollama ollama pull <model>` |
| API hangs on evolve call | RPC timeout (Sepolia public nodes are flaky) | Switch to a paid Sepolia RPC (Alchemy, Infura) |
| `gasPrice` errors | Using legacy gas | Use `eip1559-gas` skill |

## Extending the Flow

Common additions:

| Want | Where |
|---|---|
| New stage | Update contract `evolutionStage` enum + redeploy + update LLM prompt + add `<stage>.png` to image folder |
| Custom evolution rules per pet | Update `eeps/squad.json` + LLM prompt template |
| XP-gated evolution | Add XP check in API before calling `evolve()`; contract stays simple |
| Discord notification on evolve | Webhook from API after on-chain confirmation (post-mining) |
| Telemetry | Add OTel spans around each step (Redis read, LLM call, IPFS pin, RPC call) |

## Companion Skills

- `sepolia-ops` — RPC, Foundry, cast inspection
- `eip1559-gas` — proper gas patterns for the on-chain call
- `pinata-ipfs-pin` — uploading + pinning the metadata JSON
- `eep-mint-batch` — getting all 78 pets minted before they can evolve

## Hard Rules

- **3600s cooldown is on-chain** — API can read it but never bypass it
- **Stages are lowercase** — `baby young trained elite legendary quantum`
- **`AGENT_KEY` must have `AGENT_ROLE`** — granted at deploy time, can be re-granted by `ADMIN_ADDRESS`
- **EIP-1559 gas only** on Sepolia — see `eip1559-gas` skill
- **Pin metadata BEFORE calling evolve()** — never set `tokenURI` to an unpinned IPFS hash

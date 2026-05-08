---
name: eep-mint-batch
description: Mint all 78 EEP tokens — eeps/squad.json definitions, scripts/mint_all_eeps.py batch flow, nonce management for batch sends, gas budgeting. Use when the user says "mint all", "mint_all_eeps", "batch mint", "squad.json", or wants to populate the contract with all 78 EEPs.
---

# eep-mint-batch

Goal: mint all 78 EEPVengers tokens in one shot. The contract enforces `MAX_SUPPLY=78`. Each mint = one Sepolia tx with a small fee.

## Pre-flight Checklist

- [ ] Contract deployed + verified on Sepolia (use `sepolia-ops` skill)
- [ ] `CONTRACT_ADDRESS` set in `.env`
- [ ] `DEPLOYER_KEY` set + has `MINTER_ROLE` (granted at deploy)
- [ ] Sepolia ETH balance: at least 0.1 ETH (78 mints × ~0.001 ETH each + headroom)
- [ ] `eeps/squad.json` validated — exactly 78 entries
- [ ] Images pinned + `IMAGES_ROOT_CID` set (use `pinata-ipfs-pin` skill)
- [ ] `baby.png` exists for every pet (initial stage)
- [ ] First mint already verified working: `scripts/sepolia_mint_first_eep.py` runs clean

## The Squad File

`eeps/squad.json` defines all 78 EEPs:

```json
[
  { "id": 1, "name": "EEP-001", "personality": "curious", ... },
  { "id": 2, "name": "EEP-002", "personality": "stoic",   ... },
  ...
  { "id": 78, "name": "EEP-078", "personality": "quantum", ... }
]
```

If the file is missing or has != 78 entries → fix it before running the batch.

## The Batch Script

`scripts/mint_all_eeps.py` — read it before running. It must:

1. Load all 78 entries from `eeps/squad.json`
2. For each entry:
   - Build initial metadata JSON (stage = `baby`)
   - Pin metadata to Pinata → get CID
   - Build EIP-1559 tx calling `mint(to, tokenId, "ipfs://<cid>")`
   - Increment nonce **manually** (don't refetch — RPC will lag)
   - Send + collect tx hash
3. Wait for all txs to be mined (or batch them with a sliding window)
4. Verify on-chain: `totalSupply() == 78`

## Run It

```powershell
cd H:\dNFTpet\BROskiPets-LLM-dNFT

# Load .env into session
Get-Content .env | ForEach-Object {
  $line = $_.Trim()
  if (-not $line -or $line.StartsWith('#') -or $line -notmatch '=') { return }
  $k,$v = $line.Split('=',2)
  [Environment]::SetEnvironmentVariable($k.Trim(), $v.Trim().Trim('"').Trim("'"), 'Process')
}

# Sanity check the first mint still works
python .\scripts\sepolia_mint_first_eep.py

# If that's good, fire the full batch
python .\scripts\mint_all_eeps.py
```

## Nonce Management (the gotcha)

In a batch of 78 sends, **don't refetch nonce per tx**. RPC nodes have lag — by the time you fetch the next nonce, your previous tx may not be in the mempool yet, and you'll get the same nonce back, then a `nonce too low` collision.

Pattern:

```python
nonce = w3.eth.get_transaction_count(sender_address, 'pending')

for i, eep in enumerate(squad):
    tx = build_mint_tx(eep, nonce=nonce + i)
    signed = w3.eth.account.sign_transaction(tx, private_key=DEPLOYER_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print(f"Sent tx {i+1}/78: {tx_hash.hex()}")
    # Don't wait for receipt — let them all queue up
    time.sleep(0.5)   # gentle pace, avoid spam-detection on public RPC
```

Then at the end, wait for all receipts:

```python
for tx_hash in all_tx_hashes:
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
    assert receipt.status == 1, f"Mint failed: {tx_hash.hex()}"
```

## Gas Budget

| Per mint | ~150k gas × ~30 gwei = ~0.0045 ETH |
| 78 mints | ~0.35 ETH at high gas |
| Realistic | ~0.1 ETH (Sepolia is mostly cheap) |

Get Sepolia ETH from `sepoliafaucet.com` (or Alchemy faucet) — they give 0.5 ETH/day.

## Verify After Batch

```powershell
$env:PATH += ";$env:USERPROFILE\.foundry\bin"

# Total supply should be 78
cast call $env:CONTRACT_ADDRESS "totalSupply()(uint256)" --rpc-url $env:SEPOLIA_RPC

# Random spot-check tokenURI #42
cast call $env:CONTRACT_ADDRESS "tokenURI(uint256)(string)" 42 --rpc-url $env:SEPOLIA_RPC
# → ipfs://Qm... (resolvable via gateway)

# All should be at stage 0 (baby)
cast call $env:CONTRACT_ADDRESS "evolutionStage(uint256)(uint8)" 42 --rpc-url $env:SEPOLIA_RPC
# → 0
```

## Common Failures

| Symptom | Cause | Fix |
|---|---|---|
| Script aborts mid-batch | RPC timeout, nonce drift, or gas spike | Resume from last successful tokenId — check `totalSupply()` first |
| `nonce too low` partway through | Refetched nonce instead of incrementing | Use the manual increment pattern above |
| `replacement transaction underpriced` | A previous tx is stuck, blocking sequel | Cancel the stuck tx (see `eip1559-gas` skill) |
| Some mints succeed, some fail | Pinata 429 / RPC flaky | Retry only the failed ones — check on-chain `ownerOf(tokenId)` to confirm gaps |
| `AccessControl: account is missing role MINTER_ROLE` | DEPLOYER_KEY doesn't have MINTER_ROLE | Grant via `cast send`, signed by ADMIN_ADDRESS |
| `revert: max supply reached` | Already minted 78 — re-run is a no-op error | Confirm with `totalSupply()` — if 78, you're done |
| All mints reverting silently | `gasPrice` (legacy) used instead of EIP-1559 | Use `eip1559-gas` skill |

## Resume After Partial Failure

The contract enforces `tokenId` uniqueness — minting an existing tokenId reverts. Resume by querying `ownerOf(tokenId)` for each tokenId 1..78 and skipping the ones already owned:

```python
def resume_batch(squad, contract):
    to_mint = []
    for eep in squad:
        try:
            owner = contract.functions.ownerOf(eep['id']).call()
            print(f"#{eep['id']} already minted to {owner}, skipping")
        except Exception:
            to_mint.append(eep)
    print(f"Resuming with {len(to_mint)} remaining")
    return to_mint
```

## Companion Skills

- `sepolia-ops` — RPC + Foundry setup
- `eip1559-gas` — proper gas pattern (CRITICAL — Sepolia rejects `gasPrice`)
- `pinata-ipfs-pin` — must run BEFORE the batch (need `IMAGES_ROOT_CID` + per-token metadata pins)
- `dnft-evolve-flow` — what comes next, after all 78 are minted

## Hard Rules

- **EIP-1559 only** — `gasPrice` will reject every tx
- **Manual nonce increment** in batch — never refetch per tx
- **Pin all 78 metadata JSONs first** — or the script will pin during loop (slower, more failure surface)
- **Sepolia ETH only** — never run this with mainnet keys
- **Resume don't restart** — if the batch fails partway, query `ownerOf` to find gaps

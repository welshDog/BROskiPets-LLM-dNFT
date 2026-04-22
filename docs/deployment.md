# Deployment Guide

This guide covers deploying BROskiPets from local Docker to Sepolia testnet to Ethereum mainnet.

---

## Deployment Checklist

Before any deployment, verify:

- [ ] All tests pass (`python -m pytest tests/ -v && cd contracts && forge test`)
- [ ] No secrets in git history (`git log --all --full-history -- "*.env"`)
- [ ] `.env` is in `.gitignore` (check: `git status` should not show `.env`)
- [ ] `PINATA_JWT` set and working (test: `python -c "from metadata import upload_to_ipfs; upload_to_ipfs(b'test', 'test.json')"`)
- [ ] Admin wallet is a Gnosis Safe multisig (not a single EOA) for mainnet
- [ ] Slither static analysis passes with zero high/critical findings

---

## Local Docker Deployment

The simplest deployment — everything runs on one machine.

```bash
cp .env.example .env
# Edit .env — set REDIS_PASSWORD and PINATA_JWT at minimum

docker compose up -d
docker compose ps  # verify all healthy
docker compose logs -f bropets-api  # tail API logs
```

**Services exposed:**

| Service | Port | URL |
|---------|------|-----|
| API | 8080 | `http://localhost:8080` |
| Redis | 6379 | `redis://localhost:6379` |
| Ollama | *(internal)* | Reachable by the API container at `http://ollama:11434` |

---

## Sepolia Testnet Deployment (Phase 1)

### 1 — Get testnet ETH

- Alchemy Sepolia faucet: [sepoliafaucet.com](https://sepoliafaucet.com)
- Infura faucet: [infura.io/faucet/sepolia](https://www.infura.io/faucet/sepolia)

### 2 — Get a Sepolia RPC URL

Sign up at [Alchemy](https://alchemy.com) or [Infura](https://infura.io) (both have free tiers).

### 3 — Set environment variables

```bash
export SEPOLIA_RPC=https://eth-sepolia.g.alchemy.com/v2/YOUR_KEY
export DEPLOYER_KEY=0x...your_testnet_private_key...
export ADMIN_ADDRESS=0x...your_admin_wallet...
```

`DEPLOYER_KEY` must be a 32-byte hex private key (`0x` + 64 hex chars).

On Windows PowerShell, you can load `.env` into the current session:

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

### 4 — Deploy

```bash
cd contracts

forge script script/Deploy.s.sol \
  --rpc-url $SEPOLIA_RPC \
  --private-key $DEPLOYER_KEY \
  --broadcast \
  --verify \
  --etherscan-api-key $ETHERSCAN_API_KEY
```

> `--verify` submits the source code to Etherscan automatically. Get an API key at [etherscan.io/myapikey](https://etherscan.io/myapikey).

### 5 — Grant roles

After deployment, grant `MINTER_ROLE` to your mint service wallet and `AGENT_ROLE` to your Python backend wallet using cast:

```bash
# Contract address from deploy output
export CONTRACT_ADDRESS=0x...deployed_contract_address...

# Grant MINTER_ROLE to mint service wallet
cast send $CONTRACT_ADDRESS \
  "grantRole(bytes32,address)" \
  $(cast keccak "MINTER_ROLE") \
  $MINTER_WALLET \
  --rpc-url $SEPOLIA_RPC \
  --private-key $DEPLOYER_KEY

# Grant AGENT_ROLE to Python backend wallet
cast send $CONTRACT_ADDRESS \
  "grantRole(bytes32,address)" \
  $(cast keccak "AGENT_ROLE") \
  $AGENT_ADDRESS \
  --rpc-url $SEPOLIA_RPC \
  --private-key $DEPLOYER_KEY
```

### 6 — Mint the first EEP

With IPFS set up and `PINATA_JWT` configured:

```bash
cd contracts
forge build

cd ..
python scripts/sepolia_mint_first_eep.py
```

Optional: if you have pinned art already, set `IMAGES_ROOT_CID` to a folder CID and minted metadata will reference a resolvable image path:

```bash
IMAGES_ROOT_CID=Qm...
```

---

## Mainnet Deployment (Phase 1 — Q4 2026)

> Only proceed after all testnet EEPs are minted and tested successfully.

### Additional requirements for mainnet

- [ ] Admin wallet is a **Gnosis Safe** (2-of-3 multisig minimum)
- [ ] Slither audit clean: `slither . --exclude-dependencies` with zero high/critical findings
- [ ] External security review completed
- [ ] Emergency pause procedure tested on testnet

### Mainnet deploy

```bash
export MAINNET_RPC=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
export DEPLOYER_KEY=0x...mainnet_deployer_key...  # use a hot wallet, transfer admin after
export ADMIN_ADDRESS=0x...gnosis_safe_address...

cd contracts
forge script script/Deploy.s.sol \
  --rpc-url $MAINNET_RPC \
  --private-key $DEPLOYER_KEY \
  --broadcast \
  --verify \
  --etherscan-api-key $ETHERSCAN_API_KEY
```

**After deploy:** immediately transfer `DEFAULT_ADMIN_ROLE` from the hot deployer wallet to the Gnosis Safe:

```bash
cast send $CONTRACT_ADDRESS \
  "grantRole(bytes32,address)" \
  "0x0000000000000000000000000000000000000000000000000000000000000000" \
  $GNOSIS_SAFE \
  --rpc-url $MAINNET_RPC \
  --private-key $DEPLOYER_KEY

# Revoke admin from the deployer hot wallet
cast send $CONTRACT_ADDRESS \
  "revokeRole(bytes32,address)" \
  "0x0000000000000000000000000000000000000000000000000000000000000000" \
  $DEPLOYER_ADDRESS \
  --rpc-url $MAINNET_RPC \
  --private-key $DEPLOYER_KEY
```

---

## Minting All 78 EEPs

Mint in batches to avoid gas spikes. The contract hard-caps at 78 (`MAX_SUPPLY`).

```bash
# Batch mint script (pseudocode — adapt mint_eep.py above)
for eep in squad.json:
    cid = upload_metadata(eep)
    contract.mint(holder_address, eep.id, cid)
    sleep(2)  # avoid rate limits
```

---

## Post-Deployment

### Verify on Etherscan

If `--verify` flag was used during deploy, the contract source is already verified. Check at:

```
https://etherscan.io/address/{CONTRACT_ADDRESS}#code
```

### Add to OpenSea

1. Visit [opensea.io/asset/ethereum/{CONTRACT_ADDRESS}/{TOKEN_ID}](https://opensea.io) — OpenSea auto-detects ERC-721 contracts
2. Edit collection metadata (name, description, external link)
3. Set royalties (recommended: 5% to EEPVengers treasury)

### Update `.env` with deployed address

```bash
CONTRACT_ADDRESS=0x...your_deployed_contract...
```

---

## Emergency Procedures

### Pause the contract

If a vulnerability is discovered, the admin multisig can freeze all mints and evolutions:

```bash
cast send $CONTRACT_ADDRESS "pause()" \
  --rpc-url $MAINNET_RPC \
  --private-key $ADMIN_KEY
```

This immediately blocks all `mint()` and `evolve()` calls. Ownership transfers and `tokenURI()` reads continue to work.

### Unpause

```bash
cast send $CONTRACT_ADDRESS "unpause()" \
  --rpc-url $MAINNET_RPC \
  --private-key $ADMIN_KEY
```

### Revoke a compromised agent key

```bash
cast send $CONTRACT_ADDRESS \
  "revokeRole(bytes32,address)" \
  $(cast keccak "AGENT_ROLE") \
  $COMPROMISED_AGENT_ADDRESS \
  --rpc-url $MAINNET_RPC \
  --private-key $ADMIN_KEY
```

Grant a new agent key immediately after:

```bash
cast send $CONTRACT_ADDRESS \
  "grantRole(bytes32,address)" \
  $(cast keccak "AGENT_ROLE") \
  $NEW_AGENT_ADDRESS \
  --rpc-url $MAINNET_RPC \
  --private-key $ADMIN_KEY
```

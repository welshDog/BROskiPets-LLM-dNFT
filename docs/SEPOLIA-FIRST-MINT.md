# Sepolia — Deploy + Mint First EEP (Runbook)

This runbook deploys `EEPVengers.sol` to Sepolia, grants roles, and mints the first EEP.

## Prereqs

- Foundry installed (`forge`, `cast`)
- Python environment with `web3` available
- Funded Sepolia ETH on both wallets:
  - admin/deployer wallet (deploy + mint)
  - agent wallet (evolve calls)

## Required Environment

Set these in your shell (PowerShell examples below):

- `SEPOLIA_RPC`
- `DEPLOYER_KEY`
- `AGENT_KEY`
- `PINATA_JWT`

Optional:
- `ETHERSCAN_API_KEY` (for `--verify`)
- `PET_ID` (defaults to `001`)
- `RECIPIENT_ADDRESS` (defaults to deployer address)
- `IMAGES_ROOT_CID` (if you already uploaded stage images folder)

## 1) Derive Addresses

```powershell
$env:SEPOLIA_RPC = "https://eth-sepolia.g.alchemy.com/v2/YOUR_KEY"
$env:DEPLOYER_KEY = "0x..."
$env:AGENT_KEY = "0x..."

cast wallet address --private-key $env:DEPLOYER_KEY
cast wallet address --private-key $env:AGENT_KEY
```

Copy the printed addresses into:

```powershell
$env:ADMIN_ADDRESS = "<deployer address>"
$env:MINTER_ADDRESS = "<deployer address>"
$env:AGENT_ADDRESS = "<agent address>"
```

## 2) Deploy Contract

From `contracts/`:

```powershell
cd contracts

forge script script/Deploy.s.sol `
  --rpc-url $env:SEPOLIA_RPC `
  --private-key $env:DEPLOYER_KEY `
  --broadcast
```

If you want verification:

```powershell
forge script script/Deploy.s.sol `
  --rpc-url $env:SEPOLIA_RPC `
  --private-key $env:DEPLOYER_KEY `
  --broadcast `
  --verify `
  --etherscan-api-key $env:ETHERSCAN_API_KEY
```

Set the deployed address:

```powershell
$env:CONTRACT_ADDRESS = "0x...from forge output..."
```

## 3) Mint the First EEP

From repo root:

```powershell
cd ..

$env:PINATA_JWT = "<pinata jwt>"
$env:PET_ID = "001"
$env:RECIPIENT_ADDRESS = $env:ADMIN_ADDRESS

python scripts/sepolia_mint_first_eep.py
```

This will:
- Generate EIP-721 metadata for the pet at stage Baby
- Upload metadata JSON to IPFS via Pinata
- Call `mint(recipient, petId, metadataCID)` on Sepolia

## 4) Optional: Run the API evolve loop

Start Redis + API locally and call:

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8081/pet/001/feed"
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8081/pet/001/evolve" -ContentType "application/json" -Body '{"token_id":1}'
```

For on-chain evolve, ensure:
- `AGENT_KEY`, `SEPOLIA_RPC`, `CONTRACT_ADDRESS`, `PINATA_JWT` are set for the API process.


---
name: broskipets-nft-deploy
description: Deploys, mints, and manages BROskiPets LLM-powered dNFTs on
  Base Sepolia and mainnet. Use when deploying contracts, minting pets,
  updating metadata, or debugging NFT flows in BROskiPets-LLM-dNFT.
---

# broskipets-nft-deploy Skill

## When to use
- Deploying or upgrading the BROskiPets smart contract.
- Minting new pet NFTs on Base Sepolia (test) or Base mainnet.
- Updating or regenerating LLM-powered pet metadata.
- Debugging failed mints or metadata refresh issues.

## Pre-flight checks
1. Confirm HyperCode-V2.4 mint-pet-confirm edge function is healthy.
2. Confirm Base Sepolia RPC is responding.
3. Check wallet has enough ETH for gas (testnet or mainnet).

## Deploy contract steps
1. Compile contracts:
   ```powershell
   npx hardhat compile
   ```
2. Deploy to Base Sepolia:
   ```powershell
   npx hardhat run scripts/deploy.js --network base-sepolia
   ```
3. Save deployed contract address to `.env` and Vercel env vars:
   ```
   VITE_CONTRACT_ADDRESS=<deployed_address>
   ```
4. Verify on Basescan:
   ```powershell
   npx hardhat verify --network base-sepolia <contract_address>
   ```

## Mint a test pet
```powershell
npx hardhat run scripts/mintPet.js --network base-sepolia
```

## Update LLM pet metadata
- Trigger metadata regeneration via the Supabase edge function.
- Confirm IPFS/Arweave URI updated on-chain.
- Check pet traits reflect new LLM output.

## Success criteria
- Contract deployed and verified on Basescan.
- Test mint returns valid token ID.
- Pet metadata visible and correct on OpenSea testnet.
- All 78 EEP pets remain intact after any upgrade.

## Key env vars
- `PRIVATE_KEY` (deployer wallet)
- `BASE_SEPOLIA_RPC_URL`
- `BASESCAN_API_KEY`
- `VITE_CONTRACT_ADDRESS`
- `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY`

# 🐾 BROskiPets-LLM-dNFT — CLAUDE.md
> Read this first. Every session. No exceptions.
> Built by @welshDog — Lyndz Williams, Llanelli, Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁿

---

## 👤 Who You're Working With
- Name: Lyndz — call them "Bro"
- ADHD + Dyslexia + Autistic — chunked output ALWAYS
- Short sentences. Bold key info. Emojis. Celebrate wins 🎉
- Style: Why → How → Ready-to-use example

---

## 🏗️ What This Repo Is
- **BROskiPets-LLM-dNFT** — Dynamic NFT pet system on Ethereum Sepolia
- EEPVengers smart contract — MAX_SUPPLY: 78, EVOLVE_COOLDOWN: 3600s
- Pets evolve based on LLM interactions and XP
- Part of the HYPERFOCUS Z0NE ecosystem

---

## ✅ What's Already DONE
- EEPVengers contract **DEPLOYED** on Sepolia (chainId 11155111)
- Contract Address: `0x3691470c6c56D9bb3cBe8052A2cEAcDdeeEe2F09`
- Contract: **VERIFIED** on Sepolia Etherscan
- **3 transactions** confirmed:
  1. Deploy + AGENT_ROLE grant ✅
  2. First EEP minted ✅ (Block 10709316)
  3. EEP evolved ✅ (Block 10709937)
- Foundry/Forge setup working
- SEPOLIA_RPC set: `https://ethereum-sepolia-rpc.publicnode.com`
- Wallet: Trust Wallet Extension (Ethereum Sepolia account)
- Deployer address: `0xb58B8e2E80451cc4ba8064cf8a0ad67aaa88FD41`

---

## ❌ Known Issues / TODO
- `scripts/sepolia_mint_first_eep.py` uses `gasPrice` (legacy)
  - **Fix needed:** Replace with EIP-1559 fields:
    ```python
    base_fee = w3.eth.get_block('latest')['baseFeePerGas']
    priority_fee = w3.to_wei(1, 'gwei')
    tx['maxPriorityFeePerGas'] = priority_fee
    tx['maxFeePerGas'] = base_fee * 2 + priority_fee
    tx['chainId'] = 11155111
    # REMOVE: tx['gasPrice']
    ```
- `DEPLOYER_KEY` blank in `.env` — re-export from Trust Wallet (Developer Settings → Private Key Export)
- `CONTRACT_ADDRESS` needs setting: `0x3691470c6c56D9bb3cBe8052A2cEAcDdeeEe2F09`
- Images not yet uploaded to IPFS (Pinata)
- `python scripts/mint_all_eeps.py` not yet run

---

## 🗺️ Next Steps (In Order)
1. Fix `gasPrice` → EIP-1559 in `sepolia_mint_first_eep.py`
2. Re-export DEPLOYER_KEY from Trust Wallet → paste in `.env`
3. Upload EEP images to IPFS via Pinata
4. Run `python scripts/mint_all_eeps.py`
5. Verify all 78 EEPs minted on Sepolia Etherscan

---

## 🔑 Key Files
- `contracts/src/EEPVengers.sol` — main smart contract
- `contracts/script/Deploy.s.sol` — Foundry deploy script
- `scripts/sepolia_mint_first_eep.py` — single mint script (needs EIP-1559 fix)
- `scripts/mint_all_eeps.py` — batch mint all 78 EEPs
- `eeps/squad.json` — all 78 EEP definitions
- `contracts/.env` — secrets (NEVER commit)

---

## ⚙️ Environment Variables Needed
```
SEPOLIA_RPC=https://ethereum-sepolia-rpc.publicnode.com
DEPLOYER_KEY=0x<64 hex chars from Trust Wallet>
CONTRACT_ADDRESS=0x3691470c6c56D9bb3cBe8052A2cEAcDdeeEe2F09
PINATA_JWT=<your rotated JWT>
AGENT_KEY=<fill when BROskiPets Phase 1 begins>
ADMIN_ADDRESS=0xb58B8e2E80451cc4ba8064cf8a0ad67aaa88FD41
```

---

## 🛡️ Sacred Rules
- NEVER commit `.env` to git
- NEVER use mainnet ETH for testing
- Always use Sepolia (chainId 11155111) for dev
- EIP-1559 gas fields only — no `gasPrice` on Sepolia
- Absolute imports only — add repo root to `sys.path`

---

## 🌍 Ecosystem Links
- HyperCode-V2.4: github.com/welshDog/HyperCode-V2.4
- HyperAgent-SDK: github.com/welshDog/HyperAgent-SDK
- Course: github.com/welshDog/Hyper-Vibe-Coding-Course

---
> Built for ADHD brains. Fast feedback. Real tools. No fluff.
> by welshDog — Lyndz Williams, South Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁿
> A BROski is ride or die. We build this together. 🐾♾️

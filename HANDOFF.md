# 🦅 BROskiPets — Agent Handoff Doc
> Read this FIRST. Every session. No exceptions.
> Last updated: May 2026 — welshDog / Lyndz Williams, Llanelli 🏴󠁧󠁢󠁷󠁬󠁳󠁿

---

## 🔑 Pinata Keys (use these, no others)

```
PINATA_JWT=<your JWT from app.pinata.cloud/developers/api-keys — "BROski pinata key" created 21/04/2026>
IPFS_GATEWAY=https://aqua-few-dolphin-310.mypinata.cloud
```

> ⚠️ IPFS_GATEWAY **must include https://** — without it, `f"{gateway}/{cid}"` builds a broken URL with no protocol.
> DO NOT use PINATA_API_KEY or PINATA_API_SECRET — JWT is all you need for uploads and pinning.

---

## 📦 Pinata Group

```
Group name: BROski_pets_dNFTs
Group ID:   2aedcf70-d4bb-4e13-94c9-ef6098d49aca
URL:        https://app.pinata.cloud/ipfs/groups/2aedcf70-d4bb-4e13-94c9-ef6098d49aca
```

> Old EEPs group = legacy only. Do NOT pin new assets there. Do NOT touch existing EEP files.

---

## 🗝️ Active Supabase Project

```
Project:  Hyper Vibe Coding Course
ID:       yhtmuibgdnxhbgboajhc
Region:   eu-west-2
Dashboard: https://supabase.com/dashboard/project/yhtmuibgdnxhbgboajhc
```

---

## 🤖 Pinata OpenClaw Agent

```
Dashboard: https://agents.pinata.cloud/agents
Agent:     broski-pet-evolver
File:      pet_evolver_agent.py (in repo root)
Requires:  requirements.evolver.txt
```

**Secrets to add in Pinata vault:**
```
PINATA_JWT                  = <your JWT>
BROSKIPET_CONTRACT_ADDRESS  = <after Foundry deploy>
BASE_SEPOLIA_RPC            = https://sepolia.base.org
BACKEND_SIGNER_PRIVATE_KEY  = <from cast wallet new>
OPENAI_API_KEY              = <yours — OR set USE_OLLAMA=true + OLLAMA_URL>
IPFS_GATEWAY                = https://aqua-few-dolphin-310.mypinata.cloud
```

**Evolver agent audit (commit c12ee98) — May 2026:**
- ✅ LLM path: both OpenAI (`gpt-4o-mini`) AND Ollama (`qwen2.5:7b`) wired correctly via `USE_OLLAMA` env flag
- ✅ Deterministic fallback: if both LLMs unavailable, trait generation never throws — uses hardcoded stage-based traits
- ✅ ABI: minimal, correct — `totalSupply`, `ownerOf`, `tokenURI`, `evolveStage`, `lastEvolvedAt`, `setTokenURI`, `incrementStage`, `PetEvolved` event
- ✅ Cooldown: reads `lastEvolvedAt` from contract, compares to `EVOLVE_COOLDOWN_HOURS` env (default 1h)
- ✅ Webhook server: `GET /` = health check, `POST /` = trigger (body `{"token_id": N}` or `{}` for all)
- ✅ Cron mode: `python pet_evolver_agent.py --cron` runs a single cycle and exits
- ⚠️ Neither OpenAI nor Ollama path has been live-tested against a deployed contract yet — test after Step 2 (deploy)
- ⚠️ Image URL in evolver contains literal `{CID_PLACEHOLDER}` — replace with real root CID after pinata_upload_all.py

---

## ✅ What's Done — Trust These, Don't Redo

| Layer | Status | Notes |
|-------|--------|-------|
| `BROskiPet.sol` | ✅ 22/22 tests | Foundry, not deployed yet |
| `mint-pet-auth` | ✅ v2 live | Correct typehash: `string petId, string ipfsCID` |
| `get-pet-balance` | ✅ v1 live + audited | Returns `{broski_tokens, mint_cost, can_mint}` |
| `mint_nonces` table | ✅ Live with RLS | |
| `next_pet_id()` function | ✅ Live | |
| `useMintPet.ts` hook | ✅ Correct ABI | string types, DO NOT regenerate |
| `wagmi.ts` + RainbowKit | ✅ Wired | DO NOT replace with injected() only |
| `broskiPet.ts` ABI module | ✅ Correct | Minimal ABI, string types |
| `pet_evolver_agent.py` | ✅ Pushed | Audited — see notes above |
| `PINATA_DEPLOY_CHECKLIST.md` | ✅ In repo | Step-by-step deploy guide |
| `SpeciesPicker.tsx` | ✅ Scaffolded | 10 species grid, evo1.png, click-to-select |
| `MintPetButton.tsx` | ✅ Scaffolded | Drives `useMintPet()`, balance gate, step trail |
| `Pets.tsx` | ✅ Scaffolded | 3-step flow, replaces mock data |
| Species images (local) | ✅ Exist | `H:/dNFTpet/BROskiPets-LLM-dNFT/broski_pets/{species}/{species}_evo1-5.png` |

---

## ⏳ What Still Needs Doing (in order)

```
0. Apply pending migration to Supabase:
   supabase/migrations/20260507080000_broskipet_mint_hardening.sql
   → fixes search_path on next_pet_id() + prune_expired_nonces()
   → removes duplicate RLS policy on mint_nonces
   → clears 10 advisor warnings
   → RUN THIS BEFORE any further DB work

1. Upload 10x evo1 images to Pinata BROski_pets_dNFTs group:
   python pinata_upload_all.py
   → outputs pinata_cids.json
   → replace {CID_PLACEHOLDER} in pet_evolver_agent.py with real root CID
   → replace PLACEHOLDER_CID in Pets.tsx with real CID

2. Copy evo1 PNGs to frontend/public/pets/ (for Vercel static serving):
   mkdir -p frontend/public/pets
   for species in apex_dragon blizzard_lizard chaos_cat cyber_fox \
     gigabyte_guinea_pig hyper_beam_bunny hyper_hamster \
     hyperfocus_horse power_pup sonic_spider; do
     mkdir -p "frontend/public/pets/$species"
     cp "H:/dNFTpet/BROskiPets-LLM-dNFT/broski_pets/$species/${species}_evo1.png" \
        "frontend/public/pets/$species/"
   done

3. Generate signer wallet:
   cast wallet new
   → save BACKEND_SIGNER_ADDRESS
   → save BACKEND_SIGNER_PRIVATE_KEY (never commit)

4. Deploy BROskiPet.sol to Base Sepolia:
   cd contracts
   forge script script/DeployBROskiPet.s.sol \
     --rpc-url https://sepolia.base.org \
     --private-key $DEPLOYER_KEY \
     --broadcast --verify
   → save BROSKIPET_CONTRACT_ADDRESS

5. Add 3 secrets to Supabase Edge Functions:
   BACKEND_SIGNER_PRIVATE_KEY  = from step 3
   BROSKIPET_CONTRACT_ADDRESS  = from step 4
   BROSKIPET_CHAIN_ID          = 84532

6. Create broski-pet-evolver agent on Pinata OpenClaw:
   https://agents.pinata.cloud/agents
   See PINATA_DEPLOY_CHECKLIST.md for full config

7. Get free WalletConnect Project ID:
   https://cloud.walletconnect.com (1 min, free)
   → add to frontend .env as VITE_WALLETCONNECT_PROJECT_ID
```

---

## 🚨 Critical Rules (bug traps — encode these, don't forget them)

```
1. ABI types:    string petId, string ipfsCID  (NOT uint256/bytes32 — that was the v1 bug)
2. Typehash:     "MintAuth(address to,string petId,string ipfsCID,uint256 nonce,uint256 expiry)"
3. Hook:         useMintPet.ts — DO NOT regenerate, DO NOT change types
4. Wallet lib:   wagmi.ts + RainbowKit — DO NOT replace with injected() only (regression)
5. Import path:  @/lib/supabase  (NOT @/lib/supabaseClient — that file doesn't exist)
6. Contract:     BROskiPet.sol  (NOT EEPVengers.sol — that's the legacy OG EEPs contract)
7. Chain:        Base Sepolia chainId=84532 (testnet) → Base mainnet chainId=8453 (prod)
8. IPFS_GATEWAY: must include https:// prefix — without it URLs are broken
9. Pinata group: BROski_pets_dNFTs ONLY — never pin new assets to the EEPs group
```

---

## 🗃️ Nonce Functions — Both Exist, Both Needed

Two functions exist in the DB that sound similar but do different jobs:

| Function | What it does | When to call |
|----------|-------------|---------------|
| `cleanup_expired_mint_nonces()` | Deletes **unused** (never submitted) expired nonces | Routine cleanup, prevents table bloat |
| `prune_expired_nonces()` | Deletes **used** expired nonces | After mint activity, archive housekeeping |

Both are correct and complementary. Do NOT merge or delete either.

---

## 📂 Source Paths

```
Contract:          H:/dNFTpet/BROskiPets-LLM-dNFT/contracts/src/BROskiPet.sol
Contract tests:    H:/dNFTpet/BROskiPets-LLM-dNFT/contracts/test/BROskiPet.t.sol
Deploy script:     H:/dNFTpet/BROskiPets-LLM-dNFT/contracts/script/DeployBROskiPet.s.sol
Edge functions:    H:/Hyper-Vibe-Coding-Course/supabase/functions/{mint-pet-auth,get-pet-balance}/index.ts
Hook:              H:/Hyper-Vibe-Coding-Course/frontend/src/hooks/useMintPet.ts
ABI module:        H:/Hyper-Vibe-Coding-Course/frontend/src/lib/contracts/broskiPet.ts
wagmi config:      H:/Hyper-Vibe-Coding-Course/frontend/src/lib/wagmi.ts
SpeciesPicker:     H:/Hyper-Vibe-Coding-Course/frontend/src/components/pets/SpeciesPicker.tsx
MintPetButton:     H:/Hyper-Vibe-Coding-Course/frontend/src/components/pets/MintPetButton.tsx
Pets page:         H:/Hyper-Vibe-Coding-Course/frontend/src/pages/Pets.tsx
Metadata builder:  H:/dNFTpet/BROskiPets-LLM-dNFT/broski_pet_metadata.py
Pinata uploader:   H:/dNFTpet/BROskiPets-LLM-dNFT/pinata_upload_all.py
Species images:    H:/dNFTpet/BROskiPets-LLM-dNFT/broski_pets/{species}/{species}_evo1.png
Migrations:        H:/Hyper-Vibe-Coding-Course/supabase/migrations/2026050700* (3 files)
Evolver agent:     H:/dNFTpet/BROskiPets-LLM-dNFT/pet_evolver_agent.py
Deploy checklist:  H:/dNFTpet/BROskiPets-LLM-dNFT/PINATA_DEPLOY_CHECKLIST.md
```

---

## 🧪 Verify Commands

```bash
# Contract tests (22/22 should pass)
cd contracts && forge test --match-contract BROskiPet -v

# Frontend lint + type check
cd frontend && npx eslint . && npx tsc --noEmit

# Metadata smoke test
python broski_pet_metadata.py --name TestPet --species cyber_fox --rarity uncommon --dry-run

# Evolver agent health (after Pinata deploy)
curl https://your-agent.pinata.cloud/
# Expect: {"status": "ok", "agent": "broski-pet-evolver", "version": "1.0.0"}

# DB nonce check (no orphaned rows)
SELECT COUNT(*) FROM mint_nonces WHERE expires_at < NOW();
```

---

## 🧠 Stack

```
Frontend:  React + Vite + wagmi + RainbowKit + Supabase JS
Contract:  Solidity 0.8.x + Foundry (22/22 tests passing)
Backend:   Supabase Edge Functions (Deno/TypeScript)
IPFS:      Pinata (JWT auth, custom gateway: aqua-few-dolphin-310.mypinata.cloud)
Agent:     Pinata OpenClaw (pet_evolver_agent.py — Python 3.12)
Chain:     Base Sepolia (84532) → Base mainnet (8453)
```

---
*Generated by BROski AI — May 2026 🦅*

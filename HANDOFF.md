# 🦅 BROskiPets — Agent Handoff Doc
> Read this FIRST. Every session. No exceptions.
> Last updated: 2026-05-08 — welshDog / Lyndz Williams, Llanelli 🏴󠁧󠁢󠁷󠁬󠁳󠁿

---

## 📍 Resume Here — 2026-05-08 (afternoon)

**Status:** 🟢 Steps 1, 2, 3 done. 🟢 Path A backend relay shipped (commits `8827d2d`, `fcc1d34`). 🔴 Step 4 deploy blocked on a wallet KEY/ADDRESS mismatch.

**The wallet mess (read this carefully tomorrow):**

Funded wallets on Base Sepolia (we **DO NOT have keys** for them):
- `0xBc548e52e63f31B40101B303Ec9bBFd94a97dFDf` — 0.008 ETH — labelled `DEPLOYER_ADDRESS` in `.env`
- `0x2c241735B3bc7261487B3B9cFdcce27a321B7198` — 0.0037 ETH — labelled `AGENT_ADDRESS` in `.env`

Wallets with keys we **DO have** (no Base Sepolia funding):
- `DEPLOYER_KEY` unlocks `0xb58B8e2E80451CC4Ba8064Cf8a0Ad67aAa88FD41` (was the OG deployer; lost-access per Bro). Has 2.83 ETH on OG Ethereum Sepolia (chain 11155111) but 0 on Base.
- `AGENT_KEY` unlocks `0x2e95e28F49d634393ab07556762a5AA06fC7991d` (old agent wallet, 0 ETH).

Why we can't fix it via Trust Wallet:
- Bro uses **Trust Wallet Extension** for the funded wallets (`0xBc548e...` + `0x2c2417...`).
- Trust Wallet Extension **does not support private key export** — mobile-only feature.
- The "encoded private key download" is an encrypted backup blob (96 bytes after base64 decode, password-encrypted). Decoding alone does not yield a usable raw key.

**`BACKEND_SIGNER_PRIVATE_KEY` was accidentally deleted from local `.env`** during the wallet edits today. The address `0xFF24...2654` is still labelled. Cloud vaults (Pinata agent + Supabase Edge Functions) still have the key per Bro's confirmation 2026-05-07, so live mint flow is unaffected, but local Path A testing won't work until the local `.env` is restored or a fresh signer is generated.

**Recommended next-session unblock — generate fresh wallets + transfer in:**
1. Run `~/.foundry/bin/cast.exe wallet new` — get a fresh deployer wallet whose key we own immediately.
2. Append the new `DEPLOYER_KEY` + `DEPLOYER_ADDRESS` to `.env`.
3. From Trust Wallet Extension, use the normal **Send** button on `0xBc548e...` to transfer ~0.005 ETH to the fresh address (Trust Wallet Extension CAN sign txs even if it can't export keys).
4. Repeat for the agent: generate fresh wallet, transfer 0.001 ETH from `0x2c2417...` to it, update `AGENT_KEY` + `AGENT_ADDRESS`.
5. Optionally regenerate `BACKEND_SIGNER_*` locally and re-add to cloud vaults (or leave the cloud-only setup — local copy is only needed for local relay testing).
6. Then `forge script script/DeployBROskiPet.s.sol --rpc-url https://sepolia.base.org --private-key $DEPLOYER_KEY --broadcast --verify --etherscan-api-key $ETHERSCAN_API_KEY --root H:/dNFTpet/BROskiPets-LLM-dNFT/contracts`.

**Alternative — Trust Wallet Mobile:** Install on phone, import same seed, mobile lets you export raw private keys. Slower but keeps the same `0xBc548e...` and `0x2c2417...` addresses.

**Reminder for future sessions:** `.env` stores config strings — **it does not fund wallets**. Wallet balances live on-chain and only change via real transactions (faucet, bridge, or transfer). Also: a label `DEPLOYER_ADDRESS=0xFoo` in `.env` does **nothing on its own** — only `DEPLOYER_KEY` is what `forge --private-key` actually uses.

**Pre-flight already verified 2026-05-08 (no need to redo):**
- `forge build` clean (one lint hint about keccak256, no errors)
- `forge test --match-contract BROskiPet` → **22 passed / 0 failed**
- Deploy script reads `ADMIN_ADDRESS`, `BACKEND_SIGNER_ADDRESS`, `AGENT_ADDRESS` from env — all currently set and non-zero
- Step 0 (Supabase migration `20260507080000_broskipet_mint_hardening.sql`) status **unconfirmed this session** — verify before further DB work

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
| Pinata evo1 pins (10 species) | ✅ 2026-05-07 | Group `BROski_pets_dNFTs` / `2aedcf70-...` — see `pinata_cids.json`, commit `d5630a6` |
| `species.ts` real CIDs wired | ✅ 2026-05-07 | Hyper-Vibe-Coding-Course commit `ed25c47` — 10 PLACEHOLDERs → real `bafkrei*` |
| Public PNGs in live frontend | ✅ Verified byte-identical | `H:/Hyper-Vibe-Coding-Course/frontend/public/pets/{species}.png` |
| Backend signer wallet | ✅ 2026-05-07 | Address `0xFF24DA010049388b3c9c0eD39F03C88E709b2654` — key in local `.env` + cloud vaults |
| Pinata + Supabase vault secrets | ✅ Per Bro 2026-05-07 | `BACKEND_SIGNER_PRIVATE_KEY` placed in both clouds (still need contract address after Step 4) |
| Path A — backend mint relay | ✅ 2026-05-08 | `mint-pet-auth/index.ts` v3 + `useMintPet.ts` flagged build. Set `VITE_MINT_VIA_RELAY=true` to enable. Users mint without ETH; backend pays gas. |

---

## ⏳ What Still Needs Doing (in order)

```
0. (verify) Apply Supabase migration if not already applied:
   supabase/migrations/20260507080000_broskipet_mint_hardening.sql
   → fixes search_path on next_pet_id() + prune_expired_nonces()
   → removes duplicate RLS policy on mint_nonces
   → clears 10 advisor warnings
   → STATUS UNCONFIRMED 2026-05-08 — check supabase advisor before further DB work

1. ✅ DONE 2026-05-07 — see pinata_cids.json + commits d5630a6, ed25c47

2. ✅ DONE — public/pets/{species}.png byte-identical to source

3. ✅ DONE — BACKEND_SIGNER_ADDRESS = 0xFF24DA010049388b3c9c0eD39F03C88E709b2654

4. 🔴 BLOCKED on Base Sepolia funding (see Resume Here block at top)
   When funded:
     forge script script/DeployBROskiPet.s.sol \
       --rpc-url https://sepolia.base.org \
       --private-key $DEPLOYER_KEY \
       --broadcast --verify --etherscan-api-key $ETHERSCAN_API_KEY \
       --root H:/dNFTpet/BROskiPets-LLM-dNFT/contracts
   → save deployed address as BROSKIPET_CONTRACT_ADDRESS in .env

5. Add to Supabase Edge Functions (BACKEND_SIGNER_PRIVATE_KEY already there per Bro):
   BROSKIPET_CONTRACT_ADDRESS  = from step 4
   BROSKIPET_CHAIN_ID          = 84532

6. Add to broski-pet-evolver Pinata agent vault (PRIVATE_KEY already there per Bro):
   BROSKIPET_CONTRACT_ADDRESS  = from step 4

7. Get free WalletConnect Project ID:
   https://cloud.walletconnect.com (1 min, free)
   → add to frontend .env as VITE_WALLETCONNECT_PROJECT_ID

8. (Path A activation — when Step 4 done and relayer funded)
   Frontend: VITE_MINT_VIA_RELAY=true  (default off — backwards-compatible)
   Edge Function: BACKEND_SIGNER_PRIVATE_KEY already set; optionally add
                  RELAYER_PRIVATE_KEY (separate wallet for the on-chain submit)
                  and MINT_RPC_URL (defaults to https://sepolia.base.org)
   Funding: relayer wallet needs Base Sepolia ETH (defaults to backend signer
            0xFF24DA010049388b3c9c0eD39F03C88E709b2654 — fund this OR override)
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

## 🤖 Pinata OpenClaw Agent — LIVE ✅

> **Updated: May 7 2026** — Agent deployed and context-loaded this session.

| Field | Value |
|-------|-------|
| Name | `broski-pet-evolver` |
| Agent ID | `x2i4f17q` |
| Dashboard | https://agents.pinata.cloud/agents/x2i4f17q |
| AI Provider | **Anthropic (Claude)** ✅ |
| Status | **LIVE** — deployed May 7 2026 |

### Secrets status

| Secret | Status |
|--------|--------|
| `PINATA_JWT` | ✅ Auto-injected by platform |
| `BASE_SEPOLIA_RPC` | ✅ `https://sepolia.base.org` |
| `BROSKIPET_CHAIN_ID` | ✅ `84532` |
| `IPFS_GATEWAY` | ✅ `https://aqua-few-dolphin-310.mypinata.cloud` |
| `BACKEND_SIGNER_PRIVATE_KEY` | ❌ Add after `cast wallet new` |
| `BROSKIPET_CONTRACT_ADDRESS` | ❌ Add after forge deploy |

### 🚨 Action needed before agent is fully operational
1. **Top up Anthropic credits** — console.anthropic.com → Plans & Billing (~£5)
2. **Upgrade Pinata plan** — agents.pinata.cloud → Account (free trial expires)
3. **Run `cast wallet new`** — add `BACKEND_SIGNER_PRIVATE_KEY` to agent Secrets tab
4. **Deploy contract** — add `BROSKIPET_CONTRACT_ADDRESS` to agent Secrets tab

### Agent was loaded with full context
The agent has been sent the vault state URL, HANDOFF.md URL, AutoBuilder plan URL, all Sacred Rules, stack details, and the ordered next-steps list. It will read these on each new session.

**Canonical vault (always read first):**
https://raw.githubusercontent.com/welshDog/BROski-Obsidian-Brain-for-HyperFocus-z0ne/main/HYPERFOCUS_ZONE/State/BROskiPets-2026-05-07.md

**AutoBuilder agent plan:**
https://raw.githubusercontent.com/welshDog/BROski-Obsidian-Brain-for-HyperFocus-z0ne/main/HYPERFOCUS_ZONE/Agents/BROskiPets-AutoBuilder.md

---

*HANDOFF.md last updated: May 7 2026 — BROski AI (Comet/Perplexity) 🐾*

---
*Generated by BROski AI — May 2026 🦅*

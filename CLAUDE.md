# 🐾 BROskiPets-LLM-dNFT — CLAUDE.md

> **Read MASTER first:** [HyperCode-V2.4/CLAUDE.md](https://github.com/welshDog/HyperCode-V2.4/blob/main/CLAUDE.md)
> That file has: who Lyndz is, comms rules, all sacred rules, ecosystem map, AI behaviour.
> This file has: Pets-specific rules only.

---

## 📍 What This Repo Is

- **Purpose:** Web3 NFT pet game — dynamic NFTs (dNFTs) + LLM personality + BROski$ economy
- **Port:** `8098` (broski-pets-bridge in V2.4 stack)
- **Chain:** Base Sepolia testnet — Mint is LIVE 🔥 (May 7)
- **Local path:** `H:\dNFTpet\BROskiPets-LLM-dNFT`
- **Web3 stack:** RainbowKit + wagmi + Base Sepolia

---

## 🔴 Sacred Rules — BROskiPets

| # | Rule | Why | Consequence if broken |
|---|---|---|---|
| 1 | **NEVER import `wagmi`/`rainbowkit` outside `/pets` route** | Shared with Course repo pattern — re-bloats cold funnel by ~900 kB | Reverts Sprint 2 perf win |
| 2 | **`broski-pets-bridge` runs on port `8098` — never reassign** | V2.4 Prometheus + healthchecks hardcoded to 8098 | Monitoring blind spot, health checks fail |
| 3 | **dNFT metadata updates go through bridge — NEVER direct contract write from frontend** | Bridge validates + rate-limits writes | Unvalidated on-chain writes, gas waste |
| 4 | **Supabase schema for Pets is SEPARATE from V2.4 schema — NEVER merge** | Cross-schema coupling causes migration conflicts | Schema drift, broken queries both sides |
| 5 | **Base Sepolia = testnet — NEVER deploy to mainnet without Lyndz explicit sign-off** | Real money, real NFTs | Irreversible mainnet transactions |
| 6 | **`.env` files NEVER committed** | Same as all repos — wallet keys in here | Wallet drained |
| 7 | **Commits: `feat:` `fix:` `docs:` `chore:` only** | Conventional commits | Changelog breaks |

---

## 📂 Key Files

```
contracts/                      — Solidity smart contracts
frontend/src/pages/pets/        — Pets UI (wagmi/rainbowkit isolated here)
backend/                        — broski-pets-bridge FastAPI service
scripts/                        — deploy + mint scripts
.env.example                    — all required env keys
```

---

## 🔍 Current Status

- Mint LIVE on Base Sepolia ✅ May 7
- XP + leaderboard bridge to V2.4 ✅
- E2E mint test on Base Sepolia testnet 🟡 TODO this week
- dNFT dynamic metadata updates 🟡 next sprint

---

> 🐶♾️ Part of the Hyperfocus z0ne — @welshDog

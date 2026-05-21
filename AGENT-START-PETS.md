# 🐾 AGENT-START — BROskiPets-LLM-dNFT Specific
> Repo-specific boot file for `BROskiPets-LLM-dNFT`
> Read AGENT-START.md first, then this file.
> Last updated: May 21, 2026

---

## 🎯 THIS REPO'S MISSION

The **Web3 NFT pet game** — dynamic NFTs (dNFTs) that evolve based on user behaviour. LLM-powered personalities + Base blockchain minting. Lives on port `8098` as `broski-pets-bridge` in the HyperCode stack.

**Mint went LIVE: May 7, 2026** 🔥🐾

---

## 📋 READ ORDER FOR THIS REPO

```
1. AGENT-START.md    → universal rules + skill loader
2. CLAUDE.md         → sacred rules (if exists)
3. WHATS_DONE.md     → what's built (check before every suggestion)
4. README.md         → pet system overview
```

---

## ⚡ KEY FACTS

```
Bridge port:       8098 (broski-pets-bridge in HyperCode stack)
Blockchain:        Base Sepolia (testnet) + Base mainnet
Wallet:            RainbowKit + wagmi + viem
Mint flow:         Edge Function auth → on-chain Base Sepolia tx
LLM providers:     Anthropic (claude-haiku / claude-sonnet) + Ollama fallback
Edge Functions:    mint-pet-auth v9, mint-pet-confirm v6, get-pet-balance v5, pet-evolve-check v1
Pet species:       10 species with images + metadata
```

---

## 📦 WHAT'S BUILT

- ✅ RainbowKit + wagmi + viem Web3 wallet integration
- ✅ Base Sepolia testnet + Base mainnet configured
- ✅ `useMintPet` hook — two-step mint flow
- ✅ Supabase Edge Functions: auth + confirm + balance + evolve
- ✅ 10 pet species images + species catalogue
- ✅ SpeciesPicker + MintPetButton components
- ✅ Pets page rebuilt — three-step mint interface
- ✅ CSP headers updated for WalletConnect + blockchain RPC
- ✅ IDOR hardened on pets endpoints
- ✅ Cosmic Dragon minted + leaderboard live

---

## 🔴 NEXT TASKS

1. **E2E Web3 mint test** on Base Sepolia with real wallet
2. **Pet evolution** — XP → evolve trigger → on-chain metadata update
3. **dNFT metadata** — dynamic traits update based on user activity

---

## 🔗 HOW IT CONNECTS TO THE ECOSYSTEM

```
BROskiPets-LLM-dNFT
    ├── broski-pets-bridge (HyperCode port 8098)
    ├── Supabase Edge Functions (mint flow)
    ├── Base Sepolia / Base mainnet (blockchain)
    ├── Hyper-Vibe-Coding-Course (Pets page UI)
    └── BROski$ economy (XP → evolution triggers)
```

---

## 🧠 SKILLS TO LOAD

```
Working on Web3/blockchain?  → github.com/welshDog/HYPER-SILLs-By-WelshDog/dev/
Working on LLM/agents?       → github.com/welshDog/HYPER-SILLs-By-WelshDog/agents/
Working on BROski$ economy?  → github.com/welshDog/HYPER-SILLs-By-WelshDog/broski/
```

---

> 🐶♾️ BROskiPets-LLM-dNFT — Built by @welshDog
> *"Stop apologising for your brain. Start building."*

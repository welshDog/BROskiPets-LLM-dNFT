# 🧠 AGENTS.md — BROskiPets-LLM-dNFT

> **Dream it. Vibe it. Build it. HYPERFOCUS z0ne ♾️**

---

## 🗺️ What is this repo?

**BROskiPets-LLM-dNFT** is the Web3 NFT layer of the Hyperfocus z0ne ecosystem.

- Hosts the BROskiPets smart contract on Base Sepolia (and Base mainnet).
- All 78 EEP pets have been minted ✅.
- LLM-powered dynamic metadata updates pet traits over time.
- Reads student progress from Hyper-Vibe-Coding-Course to unlock pets.
- Relay minting routes through HyperCode-V2.4 `mint-pet-confirm` edge function.

---

## 🏗️ Ecosystem Architecture

```
HyperCode-V2.4 (backend / wallet authority)
    ↕
Hyper-Vibe-Coding-Course (frontend / earns XP + BROski$)
    ↕
BROskiPets-LLM-dNFT (reads progress → unlocks pets) ⬅️ YOU ARE HERE
    ↕
HyperAgent-SDK (shared agent interface / write once deploy anywhere)
    ↕
BROski-Obsidian-Brain (meta-layer / living knowledge vault)
```

---

## 🎯 Current Sprint (May 2026)

1. Confirm relay minting live via `VITE_MINT_VIA_RELAY=true`
2. Validate all 78 EEP pets metadata on Base Sepolia
3. E2E mint flow passing clean
4. Prepare for mainnet migration when ready

---

## 🛠️ Skills Available (Antigravity)

| Skill | Location | Purpose |
|-------|----------|---------|
| `broskipets-nft-deploy` | `.agents/skills/broskipets-nft-deploy/` | Deploy contracts, mint pets, update LLM metadata |

> Add new skills to `.agents/skills/<skill-name>/SKILL.md`

---

## 🔧 Tools & Connections

- **Hardhat** — Smart contract compile, deploy, verify
- **Base Sepolia** — Testnet for NFT minting
- **Basescan** — Contract verification
- **OpenSea Testnet** — Pet metadata visual check
- **Supabase** — Stores pet metadata + user ownership
- **IPFS / Arweave** — Decentralised metadata storage
- **HyperCode-V2.4** — Provides relay edge function
- **HyperAgent-SDK** — Shared agent interfaces

---

## 📜 Sacred Rules (never break these)

- Short sentences. No walls of text.
- **Bold key info** where it adds clarity.
- PowerShell first for all commands.
- Bullet points over paragraphs.
- Never debate the sacred rules.

---

## 🏆 Major Wins So Far

- BROskiPets Web3 mint LIVE on Base Sepolia ✅
- All 78 EEP pets minted ✅
- LLM metadata pipeline built ✅
- NFT deploy skill ready ✅

---

## 🚀 How to Boot Into Hyperfocus Mode

1. Read `CLAUDE.md` — master brain, sacred rules, architecture.
2. Read `CLAUDE_CONTEXT.md` — current context snapshot.
3. Read `WHATS_DONE.md` — latest wins and sprint state.
4. Check `.agents/skills/` — available skills for this repo.
5. Ask: **"What are we shipping first today?"**

---

*Built with ADHD superpowers by Lyndz @ Hyperfocus Zone, S.Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁿♾️*

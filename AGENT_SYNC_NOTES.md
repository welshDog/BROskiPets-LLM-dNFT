# BROskiPets LLM dNFT — AGENT_SYNC_NOTES

> Last updated: 2026-04-27 | Ecosystem: HyperCode-V2.4 · Hyper-Vibe-Coding-Course · BROskiPets-LLM-dNFT · HyperAgent-SDK

---

## 🏗️ Role in the 4-Repo System

- **Consumes** identity + wallet signals to power pets/dNFT mechanics
- **Does NOT** own earned token state (Course earns; V2.4 stores/spends)
- **Reads** V2.4 wallet balance for spend/unlock decisions

---

## 🔗 Integration Contract

| Key | Value |
|---|---|
| **Primary join key** | `discord_id` |
| **Wallet source** | HyperCode V2.4 economy/wallet (not Supabase Course DB directly) |

---

## 📐 Rules

| Rule | Detail |
|---|---|
| **Wallet authority** | Treat V2.4 wallet balance as authoritative for spend/unlocks |
| **Own rewards** | If this repo triggers rewards, enforce idempotency with stable `source_id` (same pattern as Course→V2.4) |
| **Secret safety** | Never embed Course/Supabase secrets in a client context |
| **Unlinked users** | If no `discord_id` mapping, degrade gracefully — read-only or prompt to link |

---

## 🔑 Shared Vocabulary (All Repos)

| Key | Meaning |
|---|---|
| `source_id` | Idempotency key — always a stable UUID |
| `discord_id` | Cross-repo identity join key |
| `COURSE_SYNC_SECRET` | Auth secret for Course→V2.4 awards (server-only, never browser) |

---

## ⚠️ Security Stance

- `COURSE_SYNC_SECRET` is **server-only** — never expose in client bundles
- Any secret usage is server-side only
- Pets features must degrade gracefully when `discord_id` is missing

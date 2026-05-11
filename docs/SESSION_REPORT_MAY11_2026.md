# 🐶 BROskiPets Session Report — May 11, 2026

> Written by Perplexity AI (BROski Brain mode)
> Repo: welshDog/BROskiPets-LLM-dNFT
> Session: 3:25 PM – 4:05 PM BST

---

## ✅ What We Built This Session

### 1. `shop/items.json` — Master Item Registry
- 30 items created across 7 categories
- Categories: `food`, `toys`, `hygiene`, `boosts`, `cosmetics`, `sacred`, `event`
- Every item has: `id`, `name`, `category`, `cost`, `rarity`, `consumable`, `effect`, `description`
- Optional gates: `faction`, `unlock_level`, `earned_by`
- Sacred items have `cost: 0` and are **earned, never bought**
- Committed: `feat(shop): add master items.json registry` — SHA `8e9935c4`

### 2. `api/shop.py` — FastAPI Router
- 5 endpoints live:
  - `GET /api/shop/items` — all items, filterable by category / faction / rarity
  - `GET /api/shop/items/{item_id}` — single item lookup
  - `GET /api/shop/categories` — list of categories
  - `POST /api/shop/purchase/{item_id}` — purchase with `X-Sync-Secret` header auth
- Sacred item purchase blocked at API level (`400` response)
- `SHOPSYNCSECRET` env var validation on all purchase requests
- TODOs wired in for: `spendtokens`, `unlock_level` check, faction check, on-chain effect

### 3. `shop/seed_shop_items.py` — Supabase Seed Script
- Loops all 30 items from `items.json`
- Upserts via `ON CONFLICT (id)` — safe to re-run
- Uses `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` env vars

### 4. `shop/README.md` — Shop Docs
- Category reference table
- All API endpoints documented
- Seed instructions included

---

## 🔍 Key Findings — Supabase Shop Table

### The `shop_items` table already existed!
It was created in a previous session with **different column names** than expected.

| Our Schema | Actual Supabase Schema |
|------------|------------------------|
| `cost` | `price_tokens` |
| `rarity` (column) | stored in `metadata` JSONB |
| `consumable` (column) | stored in `metadata` JSONB |
| `faction` (column) | stored in `metadata` JSONB |
| `unlock_level` (column) | stored in `metadata` JSONB |
| `id TEXT` | `id UUID` |

### Actual columns in `shop_items`:
```
id UUID PRIMARY KEY
name TEXT
description TEXT
price_tokens INTEGER
price_gbp (exists)
category TEXT
is_available BOOLEAN
created_at TIMESTAMPTZ
metadata JSONB
```

### Items already seeded (38 items across 6 categories):

| Category | Count | Examples |
|----------|-------|----------|
| `frame` | 11 | Dragon Forge, Living Card, Arcade Cab |
| `pet_aura` | 6 | HyperFocus Pulse Rings (2500), Cosmic Swirl |
| `pet_background` | 5 | Reality Fracture (5000!), Nebula Drift |
| `pet_badge` | 6 | Welsh Dragon Badge, Founder Stamp |
| `pet_boost` | 5 | Quantum Shard (10000), Evolution Potion |
| `pet_frame` | 5 | WelshDog Celtic Frame (9999!), Holographic Foil |
| `agent_access` | 1 | Agent Sandbox Access (300) |

---

## 🆕 What Still Needs Seeding

These NEW categories from `items.json` are NOT in Supabase yet:

| Category | Items | Status |
|----------|-------|--------|
| `food` | Markdown Muffin, API Apple, Pixel Sushi, HyperFocus Donut, BROski Burger, Neural Surge Drink | ❌ Not seeded |
| `toys` | Rubber Duck Debugger, Code Ball, Webhook Whistle, Squeaky Deploy Button, Laser Pointer | ❌ Not seeded |
| `hygiene` | Log-File Floss, Cache Clear Shampoo, Dependency Lint Brush | ❌ Not seeded |
| `sacred` | Redemption Core, Vault Immortal Seal | ❌ Not seeded |
| `event` | v3.0 Rift Banner | ❌ Not seeded |

**Action needed:** Seed these using the existing `shop_items` schema (UUID id, price_tokens, metadata JSONB).

---

## ⚠️ Known Issues / Tech Debt

### 1. `seed_shop_items.py` uses wrong column names
- Script uses `cost`, `rarity`, `consumable` etc as top-level columns
- Actual table uses `price_tokens` and `metadata JSONB`
- **Fix needed:** Update seed script to match real schema before running again

### 2. `api/shop.py` loads `items.json` directly
- Currently bypasses Supabase — reads local JSON file
- **Phase 3 TODO:** Wire `/api/shop/items` to query Supabase `shop_items` table instead

### 3. Purchase flow is skeleton only
- `POST /api/shop/purchase/{item_id}` has TODOs for:
  - `spendtokens()` Supabase call
  - `unlock_level` gate check
  - faction alignment check
  - Redis/on-chain metadata update

### 4. `SHOPSYNCSECRET` armed but not wired to shop API yet
- Secret is in `.env` and Supabase Edge Function secrets
- `api/shop.py` reads it via `os.getenv("SHOPSYNCSECRET")`
- Works locally — needs container env injection via `env_file: .env` in compose

---

## 📋 Next Steps (Priority Order)

1. **Fix `seed_shop_items.py`** — update to use `price_tokens` and `metadata` JSONB columns
2. **Seed the 5 new categories** — food, toys, hygiene, sacred, event into Supabase
3. **Wire `api/shop.py` to Supabase** — replace JSON file read with DB query
4. **Implement `spendtokens` call** in purchase endpoint
5. **Add `unlock_level` + faction checks** to purchase flow
6. **Add `env_file: .env`** to shop service in `docker-compose.yml` (same tech debt as hypercode-core)
7. **Phase 3 Merge Roadmap** — Agent Sandbox Access shop item already exists in DB (300 tokens) ✅

---

## 🔑 Key Facts — Never Re-look-up

```
Supabase Project ID : yhtmuibgdnxhbgboajhc
Supabase Region     : eu-west-2
Shop table name     : shop_items
Shop id type        : UUID (gen_random_uuid())
Shop token column   : price_tokens (NOT cost)
Shop extra fields   : metadata JSONB (rarity, consumable, faction, unlock_level, effect)
SHOPSYNCSECRET      : Armed in .env + Supabase Edge Function secrets
GitHub commit       : 8e9935c4 (shop files pushed May 11 2026)
Items in DB now     : 38 (existing) + 0 new (pending seed fix)
Items in JSON       : 30 (items.json)
```

---

## 🏆 Wins This Session

- ✅ Shop architecture designed and committed to GitHub
- ✅ 30-item registry written with full lore + effects
- ✅ FastAPI router built with SHOPSYNCSECRET auth
- ✅ Seed script created (needs schema fix before running)
- ✅ Discovered existing 38-item shop already live in Supabase
- ✅ Sacred item gatekeeping enforced at API level
- ✅ Welsh Dragon Cape added 🏴󠁧󠁢󠁷󠁬󠁳󠁿

---

*Built for ADHD brains. Fast feedback. Real tools. No fluff.*
*by welshDog — Lyndz Williams, Llanelli, Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁿*

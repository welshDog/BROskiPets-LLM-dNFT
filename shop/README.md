# 🛒 BROskiPets Shop

BROski$ powered item shop for the BROskiPets dNFT ecosystem.

## Structure

```
shop/
  items.json          # Master item registry (30 items)
  seed_shop_items.py  # Supabase seed script
  README.md           # This file
api/
  shop.py             # FastAPI router (/api/shop)
```

## Item Categories

| Category | Description |
|----------|-------------|
| `food` | Consumable treats — happiness, energy, XP |
| `toys` | Permanent toys — happiness, agility |
| `hygiene` | Consumable care — memory cleanup, debuff clear |
| `boosts` | XP multipliers, focus buffs, evo accelerators |
| `cosmetics` | Frames, backgrounds, accessories, habitats |
| `sacred` | Earned via milestones — NEVER purchasable |
| `event` | Limited edition — free during events |

## API Endpoints

```
GET  /api/shop/items                     # All items
GET  /api/shop/items?category=food       # Filter by category
GET  /api/shop/items?faction=Architects  # Filter by faction
GET  /api/shop/items/{item_id}           # Single item
GET  /api/shop/categories                # List categories
POST /api/shop/purchase/{item_id}        # Purchase (requires X-Sync-Secret header)
```

## Seeding to Supabase

```bash
export SUPABASE_URL=your_url
export SUPABASE_SERVICE_KEY=your_key
python shop/seed_shop_items.py
```

## Sacred Rules
- Sacred items have `cost: 0` and are **earned**, not bought
- API blocks all POST requests to purchase sacred items
- Faction-gated items require alignment check before purchase
- Level-gated items require `unlock_level` check before purchase

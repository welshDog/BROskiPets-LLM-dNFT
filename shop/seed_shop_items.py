"""
Seed script: inserts NEW categories (food, toys, hygiene, sacred, event)
into the existing Supabase shop_items table.

Real schema:
  id UUID (auto-generated)
  name TEXT
  description TEXT
  price_tokens INTEGER
  category TEXT
  is_available BOOLEAN
  metadata JSONB  <-- rarity, consumable, faction, unlock_level, effect all go here

Run: python3 shop/seed_shop_items.py
"""
import json
import os
from pathlib import Path
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Set SUPABASE_URL and SUPABASE_SERVICE_KEY env vars first!")

client = create_client(SUPABASE_URL, SUPABASE_KEY)

with open(Path(__file__).parent / "items.json", "r") as f:
    data = json.load(f)

# Only seed new categories not already in the DB
NEW_CATEGORIES = {"food", "toys", "hygiene", "sacred", "event"}
new_items = [i for i in data["items"] if i["category"] in NEW_CATEGORIES]

print(f"Seeding {len(new_items)} new items into Supabase shop_items...\n")

for item in new_items:
    # Build metadata JSONB from all non-core fields
    metadata = {
        "item_key": item["id"],  # store our text ID here for reference
        "rarity": item.get("rarity", "Common"),
        "consumable": item.get("consumable", False),
        "effect": item.get("effect", {}),
    }
    if item.get("faction"):
        metadata["faction"] = item["faction"]
    if item.get("unlock_level"):
        metadata["unlock_level"] = item["unlock_level"]
    if item.get("earned_by"):
        metadata["earned_by"] = item["earned_by"]

    result = client.table("shop_items").insert({
        "name": item["name"],
        "category": item["category"],
        "price_tokens": item.get("cost", 0),
        "description": item.get("description", ""),
        "is_available": item["category"] != "sacred",  # sacred = not available to buy
        "metadata": metadata,
    }).execute()

    print(f"  \u2705 {item['name']} ({item['category']}, {item.get('cost', 0)} BROski$)")

print(f"\n\U0001f389 Done! {len(new_items)} new items seeded into Supabase.")

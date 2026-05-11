"""
Seed script: inserts all items from shop/items.json into Supabase shop_items table.
Run once: python shop/seed_shop_items.py
"""
import json
import os
from pathlib import Path
import supabase
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

client = create_client(SUPABASE_URL, SUPABASE_KEY)

with open(Path(__file__).parent / "items.json", "r") as f:
    data = json.load(f)

items = data["items"]

print(f"Seeding {len(items)} items into Supabase shop_items table...")

for item in items:
    result = client.table("shop_items").upsert(
        {
            "id": item["id"],
            "name": item["name"],
            "category": item["category"],
            "cost": item.get("cost", 0),
            "rarity": item.get("rarity", "Common"),
            "consumable": item.get("consumable", False),
            "faction": item.get("faction"),
            "unlock_level": item.get("unlock_level"),
            "effect": item.get("effect", {}),
            "description": item.get("description", ""),
            "earned_by": item.get("earned_by"),
        },
        on_conflict="id"
    ).execute()
    print(f"  ✅ {item['name']} ({item['category']}) seeded.")

print(f"\n🎉 Done! {len(items)} items seeded into Supabase.")

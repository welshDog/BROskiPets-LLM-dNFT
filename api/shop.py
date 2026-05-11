from fastapi import APIRouter, HTTPException, Header
import json
import os
from pathlib import Path

router = APIRouter(prefix="/api/shop", tags=["Shop"])

# Load items registry
_items_path = Path(__file__).parent.parent / "shop" / "items.json"
with open(_items_path, "r") as f:
    SHOP_DATA = json.load(f)

SHOPSYNCSECRET = os.getenv("SHOPSYNCSECRET")


@router.get("/items")
async def get_all_items(category: str = None, faction: str = None, rarity: str = None):
    """Returns shop items, filterable by category, faction, or rarity."""
    items = SHOP_DATA["items"]
    if category:
        items = [i for i in items if i["category"] == category]
    if faction:
        items = [i for i in items if i.get("faction") == faction]
    if rarity:
        items = [i for i in items if i.get("rarity") == rarity]
    return {"total": len(items), "items": items}


@router.get("/items/{item_id}")
async def get_item(item_id: str):
    """Returns a single item by ID."""
    item = next((i for i in SHOP_DATA["items"] if i["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.get("/categories")
async def get_categories():
    """Returns available item categories."""
    return {"categories": SHOP_DATA["categories"]}


@router.post("/purchase/{item_id}")
async def purchase_item(
    item_id: str,
    pet_id: str,
    x_sync_secret: str = Header(...),
):
    """
    Purchase an item for a pet.
    - Validates SHOPSYNCSECRET header
    - Blocks Sacred category items (must be earned)
    - TODO: Validate BROski$ balance via Supabase spendtokens()
    - TODO: Apply effect to pet metadata in Redis/On-Chain
    """
    if x_sync_secret != SHOPSYNCSECRET:
        raise HTTPException(status_code=403, detail="Unauthorized Shop Sync Attempt")

    item = next((i for i in SHOP_DATA["items"] if i["id"] == item_id), None)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found in registry")

    if item["category"] == "sacred":
        raise HTTPException(
            status_code=400,
            detail="Sacred items cannot be bought. Earn it, BROski!"
        )

    if item.get("cost", 0) == 0 and item["category"] != "event":
        raise HTTPException(status_code=400, detail="This item must be earned, not purchased.")

    # TODO: Check unlock_level against user's current level
    # TODO: Check faction alignment for faction-gated items
    # TODO: Call Supabase spendtokens(user_id, item["cost"])
    # TODO: Apply item effect to pet metadata

    return {
        "status": "success",
        "message": f"Successfully purchased {item['name']}.",
        "pet_target": pet_id,
        "item_id": item["id"],
        "cost_deducted": item.get("cost", 0),
        "on_chain_effect": item["effect"],
    }

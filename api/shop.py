from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
import os
from supabase import create_client, Client

router = APIRouter(prefix="/api/shop", tags=["Shop"])

SHOPSYNCSECRET = os.getenv("SHOPSYNCSECRET")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")


def get_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


@router.get("/items")
async def get_all_items(category: str = None, faction: str = None, rarity: str = None):
    """Returns shop items from Supabase, filterable by category, faction, or rarity."""
    sb = get_supabase()
    query = sb.table("shop_items").select("*").eq("is_available", True)

    if category:
        query = query.eq("category", category)

    result = query.execute()
    items = result.data

    # Filter faction/rarity from metadata JSONB (Supabase can't filter nested JSON easily)
    if faction:
        items = [i for i in items if i.get("metadata", {}).get("faction") == faction]
    if rarity:
        items = [i for i in items if i.get("metadata", {}).get("rarity") == rarity]

    return {"total": len(items), "items": items}


@router.get("/items/{item_id}")
async def get_item(item_id: str):
    """Returns a single item by UUID."""
    sb = get_supabase()
    result = sb.table("shop_items").select("*").eq("id", item_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Item not found")
    return result.data


@router.get("/categories")
async def get_categories():
    """Returns distinct categories from shop_items table."""
    sb = get_supabase()
    result = sb.table("shop_items").select("category").execute()
    cats = sorted(set(i["category"] for i in result.data))
    return {"categories": cats}


class PurchaseRequest(BaseModel):
    pet_id: str
    user_id: str


@router.post("/purchase/{item_id}")
async def purchase_item(
    item_id: str,
    body: PurchaseRequest,
    x_sync_secret: str = Header(...),
):
    """
    Purchase an item for a pet.
    - Validates SHOPSYNCSECRET header
    - Blocks sacred/unavailable items
    - Checks unlock_level if set
    - TODO: Call spendtokens(user_id, price_tokens) in Supabase
    - TODO: Apply effect to pet metadata in Redis / on-chain
    """
    if x_sync_secret != SHOPSYNCSECRET:
        raise HTTPException(status_code=403, detail="Unauthorized Shop Sync Attempt")

    sb = get_supabase()
    result = sb.table("shop_items").select("*").eq("id", item_id).single().execute()
    item = result.data

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if not item.get("is_available", False):
        raise HTTPException(
            status_code=400,
            detail="This item must be earned, not purchased. Earn it, BROski!"
        )

    metadata = item.get("metadata", {})

    # Sacred items double-check
    if item["category"] == "sacred":
        raise HTTPException(
            status_code=400,
            detail="Sacred items cannot be bought. Earn it through real cognitive labour!"
        )

    # TODO: Check unlock_level against user's current level
    # unlock_level = metadata.get("unlock_level")
    # if unlock_level and user_level < unlock_level:
    #     raise HTTPException(status_code=403, detail=f"Requires Level {unlock_level}")

    # TODO: Call Supabase spendtokens(body.user_id, item["price_tokens"])
    # TODO: Apply metadata effect to pet via Redis or on-chain update

    return {
        "status": "success",
        "message": f"Purchased {item['name']} for Pet {body.pet_id}!",
        "item_name": item["name"],
        "cost_deducted": item["price_tokens"],
        "pet_target": body.pet_id,
        "effect": metadata.get("effect", {}),
    }

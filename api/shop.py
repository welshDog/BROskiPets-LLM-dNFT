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

    # Filter faction/rarity via metadata JSONB (post-query)
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
    user_id: str  # UUID of the user in public.users


@router.post("/purchase/{item_id}")
async def purchase_item(
    item_id: str,
    body: PurchaseRequest,
    x_sync_secret: str = Header(...),
):
    """
    Purchase a shop item for a pet.

    Flow:
      1. Validate SHOPSYNCSECRET
      2. Fetch item from Supabase
      3. Block sacred + unavailable items
      4. Check unlock_level gate
      5. Call spend_tokens(user_id, price_tokens) -- SECURITY DEFINER, atomic
         - Raises if insufficient balance
         - Writes to token_transactions ledger automatically
         - Returns { spent: true, new_balance: X }
      6. TODO: Apply effect to pet (Redis / on-chain)
    """
    if x_sync_secret != SHOPSYNCSECRET:
        raise HTTPException(status_code=403, detail="Unauthorized Shop Sync Attempt")

    sb = get_supabase()

    # --- 1. Fetch item ---
    item_result = sb.table("shop_items").select("*").eq("id", item_id).single().execute()
    item = item_result.data
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # --- 2. Block unavailable / sacred items ---
    if not item.get("is_available", False):
        raise HTTPException(
            status_code=400,
            detail="This item must be earned, not purchased. Earn it, BROski!"
        )
    if item["category"] == "sacred":
        raise HTTPException(
            status_code=400,
            detail="Sacred items cannot be bought. Real cognitive labour earns these!"
        )

    metadata = item.get("metadata", {})
    price = item.get("price_tokens", 0)

    # --- 3. Unlock level gate ---
    unlock_level = metadata.get("unlock_level")
    if unlock_level:
        # Fetch user's current level from public.users
        user_result = sb.table("users").select("level").eq("id", body.user_id).single().execute()
        user = user_result.data
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user_level = user.get("level", 0)
        if user_level < unlock_level:
            raise HTTPException(
                status_code=403,
                detail=f"'{item['name']}' requires Level {unlock_level}. You're Level {user_level}. Keep grinding!"
            )

    # --- 4. Spend tokens via Supabase SECURITY DEFINER function ---
    # spend_tokens(p_user_id uuid, p_amount int, p_reason text, p_source_id text)
    # Atomically: checks balance, deducts, writes token_transactions ledger
    # Raises Postgres exception if insufficient balance
    try:
        spend_result = sb.rpc(
            "spend_tokens",
            {
                "p_user_id": body.user_id,
                "p_amount": price,
                "p_reason": f"shop_purchase:{item['name']}",
                "p_source_id": item_id,
            }
        ).execute()
    except Exception as e:
        err = str(e)
        if "Insufficient BROski$" in err:
            raise HTTPException(
                status_code=402,
                detail=f"Not enough BROski$! This costs {price} tokens. Top up and come back!"
            )
        raise HTTPException(status_code=500, detail=f"Token spend failed: {err}")

    spend_data = spend_result.data  # { spent: true, new_balance: X }
    new_balance = spend_data.get("new_balance", "?")

    # --- 5. TODO: Apply effect to pet ---
    # e.g. POST to broski-pets-bridge /api/pet/{pet_id}/apply-effect
    # with effect = metadata.get("effect", {})
    # For consumables: one-time effect
    # For cosmetics: persist to pet metadata
    # For sacred: trigger evolution flow

    return {
        "status": "success",
        "message": f"Purchased {item['name']}! BROski$ spent: {price}",
        "item_name": item["name"],
        "category": item["category"],
        "cost_deducted": price,
        "new_balance": new_balance,
        "pet_target": body.pet_id,
        "effect": metadata.get("effect", {}),
        "rarity": metadata.get("rarity", "Common"),
    }

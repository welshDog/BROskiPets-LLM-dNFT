from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import os
from supabase import create_client, Client

router = APIRouter(prefix="/api/shop", tags=["Shop"])

SHOPSYNCSECRET = os.getenv("SHOPSYNCSECRET")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # matches .env

# Effect durations mapped to hours
DURATION_MAP = {
    "1_session": 3,
    "2_hours": 2,
    "3_hours": 3,
    "instant": 0,
}


def get_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def apply_effect_to_pet(sb: Client, pet_id: str, item: dict, metadata: dict) -> dict:
    """
    Applies the purchased item effect to a pet row in Supabase.

    Effect routing by category:
      food / boosts  -> active_effects[]  (timed consumable buff)
      hygiene        -> active_effects[]  (instant one-shot, no expiry)
      cosmetics      -> equipped_cosmetics{slot: item_key}
      toys           -> inventory[]       (persistent toy, happiness buff stored)
      sacred         -> blocked upstream  (never reaches here)
      event          -> equipped_cosmetics{banner: item_key}
    """
    category = item["category"]
    effect = metadata.get("effect", {})
    item_key = metadata.get("item_key", item["id"])
    effect_type = effect.get("type", "none")

    # Fetch current pet
    pet_result = sb.table("pets").select(
        "pet_id, active_effects, equipped_cosmetics, inventory, mood"
    ).eq("pet_id", pet_id).single().execute()

    pet = pet_result.data
    if not pet:
        raise HTTPException(status_code=404, detail=f"Pet {pet_id} not found")

    active_effects = pet.get("active_effects") or []
    equipped_cosmetics = pet.get("equipped_cosmetics") or {}
    inventory = pet.get("inventory") or []
    pet_updates = {}
    effect_summary = {"applied": effect_type, "category": category}

    # --- FOOD & BOOSTS: timed buffs ---
    if category in ("food", "boosts"):
        duration_key = effect.get("duration", "1_session")
        hours = DURATION_MAP.get(duration_key, 3)
        expires_at = None
        if hours > 0:
            expires_at = (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()

        buff = {
            "item_key": item_key,
            "type": effect_type,
            "value": effect.get("value"),
            "expires_at": expires_at,
            "applied_at": datetime.now(timezone.utc).isoformat(),
        }
        active_effects = [e for e in active_effects if e.get("type") != effect_type]
        active_effects.append(buff)
        pet_updates["active_effects"] = active_effects
        effect_summary["buff"] = buff

    # --- HYGIENE: instant effect, clear debuffs or memory cleanup ---
    elif category == "hygiene":
        if effect_type == "status_clear":
            active_effects = [e for e in active_effects if e.get("value", 0) > 0]
            pet_updates["active_effects"] = active_effects
            pet_updates["mood"] = "refreshed"
            effect_summary["cleared_debuffs"] = True
        elif effect_type == "memory_cleanup":
            active_effects = active_effects[-5:]
            pet_updates["active_effects"] = active_effects
            effect_summary["memory_freed"] = True
        elif effect_type == "error_reduction":
            buff = {
                "item_key": item_key,
                "type": effect_type,
                "value": effect.get("value", 15),
                "expires_at": (datetime.now(timezone.utc) + timedelta(hours=6)).isoformat(),
                "applied_at": datetime.now(timezone.utc).isoformat(),
            }
            active_effects = [e for e in active_effects if e.get("type") != effect_type]
            active_effects.append(buff)
            pet_updates["active_effects"] = active_effects
            effect_summary["buff"] = buff

    # --- COSMETICS: equip to slot ---
    elif category == "cosmetics":
        cosmetic_type = metadata.get("type", "accessory")
        slot_map = {
            "background": "background",
            "habitat": "background",
            "accessory": "accessory",
            "frame": "frame",
        }
        slot = slot_map.get(cosmetic_type, "accessory")
        equipped_cosmetics[slot] = item_key
        pet_updates["equipped_cosmetics"] = equipped_cosmetics
        effect_summary["equipped_slot"] = slot
        effect_summary["item_key"] = item_key

    # --- TOYS: add to inventory, apply happiness buff ---
    elif category == "toys":
        owned_keys = [i.get("item_key") for i in inventory]
        if item_key not in owned_keys:
            inventory.append({
                "item_id": item["id"],
                "item_key": item_key,
                "name": item["name"],
                "acquired_at": datetime.now(timezone.utc).isoformat(),
            })
            pet_updates["inventory"] = inventory
        if effect_type == "happiness_boost":
            buff = {
                "item_key": item_key,
                "type": "happiness_boost",
                "value": effect.get("value", 10),
                "expires_at": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
                "applied_at": datetime.now(timezone.utc).isoformat(),
            }
            active_effects = [e for e in active_effects if e.get("type") != "happiness_boost"]
            active_effects.append(buff)
            pet_updates["active_effects"] = active_effects
        effect_summary["added_to_inventory"] = item_key

    # --- EVENT: equip banner ---
    elif category == "event":
        equipped_cosmetics["banner"] = item_key
        pet_updates["equipped_cosmetics"] = equipped_cosmetics
        effect_summary["banner_equipped"] = item_key

    if pet_updates:
        sb.table("pets").update(pet_updates).eq("pet_id", pet_id).execute()

    return effect_summary


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@router.get("/items")
async def get_all_items(category: str = None, faction: str = None, rarity: str = None):
    sb = get_supabase()
    query = sb.table("shop_items").select("*").eq("is_available", True)
    if category:
        query = query.eq("category", category)
    result = query.execute()
    items = result.data
    if faction:
        items = [i for i in items if i.get("metadata", {}).get("faction") == faction]
    if rarity:
        items = [i for i in items if i.get("metadata", {}).get("rarity") == rarity]
    return {"total": len(items), "items": items}


@router.get("/items/{item_id}")
async def get_item(item_id: str):
    sb = get_supabase()
    result = sb.table("shop_items").select("*").eq("id", item_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Item not found")
    return result.data


@router.get("/categories")
async def get_categories():
    sb = get_supabase()
    result = sb.table("shop_items").select("category").execute()
    cats = sorted(set(i["category"] for i in result.data))
    return {"categories": cats}


@router.get("/pet/{pet_id}/inventory")
async def get_pet_inventory(pet_id: str):
    sb = get_supabase()
    result = sb.table("pets").select(
        "pet_id, pet_name, active_effects, equipped_cosmetics, inventory"
    ).eq("pet_id", pet_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Pet not found")
    return result.data


class PurchaseRequest(BaseModel):
    pet_id: str
    user_id: str


@router.post("/purchase/{item_id}")
async def purchase_item(
    item_id: str,
    body: PurchaseRequest,
    x_sync_secret: str = Header(...),
):
    if x_sync_secret != SHOPSYNCSECRET:
        raise HTTPException(status_code=403, detail="Unauthorized Shop Sync Attempt")

    sb = get_supabase()

    item_result = sb.table("shop_items").select("*").eq("id", item_id).single().execute()
    item = item_result.data
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if not item.get("is_available", False):
        raise HTTPException(status_code=400, detail="This item must be earned, not purchased!")
    if item["category"] == "sacred":
        raise HTTPException(status_code=400, detail="Sacred items cannot be bought. Earn it!")

    metadata = item.get("metadata", {})
    price = item.get("price_tokens", 0)

    unlock_level = metadata.get("unlock_level")
    if unlock_level:
        user_result = sb.table("users").select("level").eq("id", body.user_id).single().execute()
        user = user_result.data
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.get("level", 0) < unlock_level:
            raise HTTPException(
                status_code=403,
                detail=f"'{item['name']}' requires Level {unlock_level}. Keep grinding!"
            )

    try:
        spend_result = sb.rpc("spend_tokens", {
            "p_user_id": body.user_id,
            "p_amount": price,
            "p_reason": f"shop_purchase:{item['name']}",
            "p_source_id": item_id,
        }).execute()
    except Exception as e:
        err = str(e)
        if "Insufficient BROski$" in err:
            raise HTTPException(status_code=402, detail=f"Not enough BROski$! Costs {price} tokens.")
        raise HTTPException(status_code=500, detail=f"Token spend failed: {err}")

    new_balance = spend_result.data.get("new_balance", "?")

    effect_summary = apply_effect_to_pet(sb, body.pet_id, item, metadata)

    sb.table("shop_purchases").insert({
        "user_id": body.user_id,
        "pet_id": body.pet_id,
        "item_id": item_id,
        "price_paid": price,
        "item_name": item["name"],
        "category": item["category"],
        "effect_applied": effect_summary,
    }).execute()

    return {
        "status": "success",
        "message": f"Purchased {item['name']}! 🐶",
        "item_name": item["name"],
        "category": item["category"],
        "rarity": metadata.get("rarity", "Common"),
        "cost_deducted": price,
        "new_balance": new_balance,
        "effect_applied": effect_summary,
    }

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


def _utc_day(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d")


RARITY_MULTIPLIER = {
    "Common": 1.0,
    "Uncommon": 1.1,
    "Rare": 1.25,
    "Legendary": 1.5,
    "Quantum": 2.0,
}


@dataclass(frozen=True)
class RewardDecision:
    trigger: str
    amount: int
    multiplier: float
    limit_key: str
    limit_max_per_day: int
    vest_hours: int


def decide_feed_reward(
    *,
    now: datetime,
    rarity: str,
    action: str,
) -> Optional[RewardDecision]:
    action = (action or "feed").lower()
    if action not in {"feed", "like", "comment", "share", "post"}:
        return None

    base = {"feed": 2, "like": 1, "comment": 2, "share": 3, "post": 5}[action]
    mult = float(RARITY_MULTIPLIER.get(rarity, 1.0))
    day = _utc_day(now)
    return RewardDecision(
        trigger=f"feed:{action}",
        amount=base,
        multiplier=mult,
        limit_key=f"feed:{day}",
        limit_max_per_day=50,
        vest_hours=0,
    )


def decide_chat_reward(
    *,
    now: datetime,
    rarity: str,
    message: str,
    blocked: bool,
    is_first_message_today: bool,
) -> Optional[RewardDecision]:
    if blocked:
        return None

    base = 1
    if is_first_message_today:
        base += 5

    if len((message or "").strip()) >= 40:
        base += 1

    mult = float(RARITY_MULTIPLIER.get(rarity, 1.0))
    day = _utc_day(now)
    return RewardDecision(
        trigger="chat:message",
        amount=base,
        multiplier=mult,
        limit_key=f"chat:{day}",
        limit_max_per_day=40,
        vest_hours=0,
    )


def decide_evolve_reward(
    *,
    now: datetime,
    rarity: str,
    previous_level: int,
    new_level: int,
) -> Optional[RewardDecision]:
    if new_level <= previous_level:
        return None

    milestone = {
        2: 10,
        3: 25,
        4: 100,
        5: 250,
        6: 1000,
    }.get(new_level, 0)
    if milestone <= 0:
        return None

    mult = float(RARITY_MULTIPLIER.get(rarity, 1.0))
    day = _utc_day(now)
    vest_hours = 24 if milestone >= 100 else 0
    return RewardDecision(
        trigger=f"evolve:level:{new_level}",
        amount=milestone,
        multiplier=mult,
        limit_key=f"evolve:{day}",
        limit_max_per_day=10,
        vest_hours=vest_hours,
    )


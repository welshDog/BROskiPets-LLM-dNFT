import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from rewards.ledger import RewardsLedger


def test_rewards_ledger_idempotency_single_event(tmp_path: Path):
    db = tmp_path / "rewards.db"
    ledger = RewardsLedger(db_path=str(db))

    r1 = ledger.apply_reward(
        event_id="evt-1",
        user_id="u1",
        pet_id="001",
        endpoint="/pet/{pet_id}/feed",
        trigger="feed:feed",
        amount=2,
        multiplier=1.0,
        metadata={"k": "v"},
        limit_key="feed:day",
        limit_max_per_day=999,
        vest_hours=0,
    )
    r2 = ledger.apply_reward(
        event_id="evt-1",
        user_id="u1",
        pet_id="001",
        endpoint="/pet/{pet_id}/feed",
        trigger="feed:feed",
        amount=2,
        multiplier=1.0,
        metadata={"k": "v"},
        limit_key="feed:day",
        limit_max_per_day=999,
        vest_hours=0,
    )

    assert r1.status == "applied"
    assert r2.status == "duplicate_ignored"
    assert ledger.get_balance("u1") == 2


def test_rewards_ledger_rate_limit_blocks(tmp_path: Path):
    db = tmp_path / "rewards.db"
    now = datetime(2026, 4, 20, 12, 0, 0, tzinfo=timezone.utc)
    ledger = RewardsLedger(db_path=str(db), now_fn=lambda: now)

    for i in range(3):
        r = ledger.apply_reward(
            event_id=f"evt-{i}",
            user_id="u1",
            pet_id="001",
            endpoint="/pet/{pet_id}/chat",
            trigger="chat:message",
            amount=1,
            multiplier=1.0,
            metadata={"i": i},
            limit_key="chat:2026-04-20",
            limit_max_per_day=2,
            vest_hours=0,
        )
        if i < 2:
            assert r.status == "applied"
        else:
            assert r.status == "blocked_rate_limited"
    assert ledger.get_balance("u1") == 2


def test_rewards_ledger_concurrent_duplicates(tmp_path: Path):
    db = tmp_path / "rewards.db"
    ledger = RewardsLedger(db_path=str(db))

    def worker():
        return ledger.apply_reward(
            event_id="evt-concurrent",
            user_id="u1",
            pet_id="001",
            endpoint="/pet/{pet_id}/feed",
            trigger="feed:feed",
            amount=2,
            multiplier=1.0,
            metadata={"t": "x"},
            limit_key="feed:day",
            limit_max_per_day=999,
            vest_hours=0,
        ).status

    with ThreadPoolExecutor(max_workers=10) as ex:
        statuses = list(ex.map(lambda _: worker(), range(20)))

    assert statuses.count("applied") == 1
    assert ledger.get_balance("u1") == 2


def test_rewards_ledger_list_entries(tmp_path: Path):
    db = tmp_path / "rewards.db"
    ledger = RewardsLedger(db_path=str(db))

    ledger.apply_reward(
        event_id="evt-a",
        user_id="u1",
        pet_id="001",
        endpoint="/pet/{pet_id}/feed",
        trigger="feed:feed",
        amount=2,
        multiplier=1.5,
        metadata={"a": 1},
        limit_key="feed:day",
        limit_max_per_day=999,
        vest_hours=0,
    )
    entries = ledger.list_ledger("u1", limit=10)
    assert len(entries) == 1
    assert entries[0]["event_id"] == "evt-a"
    assert entries[0]["final_amount"] == 3
    assert json.dumps(entries[0]["metadata"])


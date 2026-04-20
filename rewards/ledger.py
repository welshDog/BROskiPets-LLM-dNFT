import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Optional


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def _day_bucket(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d")


@dataclass(frozen=True)
class RewardApplyResult:
    status: str
    event_id: str
    final_amount: int
    balance: int
    available_at: str


class RewardsLedger:
    def __init__(self, db_path: Optional[str] = None, now_fn: Callable[[], datetime] = _utc_now):
        self._now_fn = now_fn
        default_path = os.getenv("REWARDS_DB_PATH", "data/rewards.db")
        self._db_path = Path(db_path or default_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path.as_posix(), timeout=30, isolation_level=None)
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self) -> None:
        conn = self._connect()
        try:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS ledger_entries ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "event_id TEXT NOT NULL UNIQUE,"
                "user_id TEXT NOT NULL,"
                "pet_id TEXT,"
                "endpoint TEXT NOT NULL,"
                "trigger TEXT NOT NULL,"
                "amount INTEGER NOT NULL,"
                "multiplier REAL NOT NULL DEFAULT 1.0,"
                "final_amount INTEGER NOT NULL,"
                "status TEXT NOT NULL,"
                "created_at TEXT NOT NULL,"
                "available_at TEXT NOT NULL,"
                "metadata_json TEXT NOT NULL"
                ")"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS user_balances ("
                "user_id TEXT PRIMARY KEY,"
                "balance INTEGER NOT NULL,"
                "updated_at TEXT NOT NULL"
                ")"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS rate_limit_counters ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "user_id TEXT NOT NULL,"
                "limit_key TEXT NOT NULL,"
                "window_start TEXT NOT NULL,"
                "count INTEGER NOT NULL,"
                "updated_at TEXT NOT NULL,"
                "UNIQUE(user_id, limit_key, window_start)"
                ")"
            )
        finally:
            conn.close()

    def get_balance(self, user_id: str) -> int:
        conn = self._connect()
        try:
            row = conn.execute("SELECT balance FROM user_balances WHERE user_id = ?", (user_id,)).fetchone()
            return int(row[0]) if row else 0
        finally:
            conn.close()

    def list_ledger(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT event_id, pet_id, endpoint, trigger, amount, multiplier, final_amount, status, created_at, available_at, metadata_json "
                "FROM ledger_entries WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
            out: list[dict[str, Any]] = []
            for r in rows:
                out.append(
                    {
                        "event_id": r[0],
                        "pet_id": r[1],
                        "endpoint": r[2],
                        "trigger": r[3],
                        "amount": int(r[4]),
                        "multiplier": float(r[5]),
                        "final_amount": int(r[6]),
                        "status": r[7],
                        "created_at": r[8],
                        "available_at": r[9],
                        "metadata": json.loads(r[10]) if r[10] else {},
                    }
                )
            return out
        finally:
            conn.close()

    def apply_reward(
        self,
        *,
        event_id: str,
        user_id: str,
        pet_id: Optional[str],
        endpoint: str,
        trigger: str,
        amount: int,
        multiplier: float,
        metadata: dict[str, Any],
        limit_key: Optional[str] = None,
        limit_max_per_day: Optional[int] = None,
        vest_hours: int = 0,
    ) -> RewardApplyResult:
        now = self._now_fn()
        created_at = _iso(now)
        available_at = _iso(now + timedelta(hours=vest_hours))
        final_amount = int(round(amount * multiplier))
        meta_json = json.dumps(metadata, sort_keys=True)

        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")

            if limit_key and limit_max_per_day is not None:
                window_start = _day_bucket(now)
                row = conn.execute(
                    "SELECT count FROM rate_limit_counters WHERE user_id = ? AND limit_key = ? AND window_start = ?",
                    (user_id, limit_key, window_start),
                ).fetchone()
                current = int(row[0]) if row else 0
                if current >= int(limit_max_per_day):
                    conn.execute("ROLLBACK")
                    return RewardApplyResult(
                        status="blocked_rate_limited",
                        event_id=event_id,
                        final_amount=0,
                        balance=self.get_balance(user_id),
                        available_at=available_at,
                    )

                if row:
                    conn.execute(
                        "UPDATE rate_limit_counters SET count = count + 1, updated_at = ? "
                        "WHERE user_id = ? AND limit_key = ? AND window_start = ?",
                        (created_at, user_id, limit_key, window_start),
                    )
                else:
                    conn.execute(
                        "INSERT INTO rate_limit_counters(user_id, limit_key, window_start, count, updated_at) "
                        "VALUES(?, ?, ?, 1, ?)",
                        (user_id, limit_key, window_start, created_at),
                    )

            try:
                conn.execute(
                    "INSERT INTO ledger_entries(event_id, user_id, pet_id, endpoint, trigger, amount, multiplier, final_amount, status, created_at, available_at, metadata_json) "
                    "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        event_id,
                        user_id,
                        pet_id,
                        endpoint,
                        trigger,
                        int(amount),
                        float(multiplier),
                        int(final_amount),
                        "posted",
                        created_at,
                        available_at,
                        meta_json,
                    ),
                )
            except sqlite3.IntegrityError:
                existing = conn.execute(
                    "SELECT final_amount, available_at FROM ledger_entries WHERE event_id = ?",
                    (event_id,),
                ).fetchone()
                conn.execute("COMMIT")
                return RewardApplyResult(
                    status="duplicate_ignored",
                    event_id=event_id,
                    final_amount=int(existing[0]) if existing else 0,
                    balance=self.get_balance(user_id),
                    available_at=str(existing[1]) if existing else available_at,
                )

            row = conn.execute("SELECT balance FROM user_balances WHERE user_id = ?", (user_id,)).fetchone()
            balance_before = int(row[0]) if row else 0
            balance_after = balance_before + int(final_amount)

            if row:
                conn.execute(
                    "UPDATE user_balances SET balance = ?, updated_at = ? WHERE user_id = ?",
                    (balance_after, created_at, user_id),
                )
            else:
                conn.execute(
                    "INSERT INTO user_balances(user_id, balance, updated_at) VALUES(?, ?, ?)",
                    (user_id, balance_after, created_at),
                )

            conn.execute("COMMIT")
            return RewardApplyResult(
                status="applied",
                event_id=event_id,
                final_amount=int(final_amount),
                balance=int(balance_after),
                available_at=available_at,
            )
        except Exception:
            conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()


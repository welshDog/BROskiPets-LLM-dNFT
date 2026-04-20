CREATE TABLE IF NOT EXISTS ledger_entries (
  id BIGSERIAL PRIMARY KEY,
  event_id TEXT NOT NULL UNIQUE,
  user_id TEXT NOT NULL,
  pet_id TEXT,
  endpoint TEXT NOT NULL,
  trigger TEXT NOT NULL,
  amount INTEGER NOT NULL,
  multiplier DOUBLE PRECISION NOT NULL DEFAULT 1.0,
  final_amount INTEGER NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  available_at TIMESTAMPTZ NOT NULL,
  metadata_json JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ledger_entries_user_created
  ON ledger_entries(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ledger_entries_user_trigger_created
  ON ledger_entries(user_id, trigger, created_at DESC);

CREATE TABLE IF NOT EXISTS user_balances (
  user_id TEXT PRIMARY KEY,
  balance BIGINT NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS rate_limit_counters (
  id BIGSERIAL PRIMARY KEY,
  user_id TEXT NOT NULL,
  limit_key TEXT NOT NULL,
  window_start TIMESTAMPTZ NOT NULL,
  count INTEGER NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL,
  UNIQUE(user_id, limit_key, window_start)
);

CREATE INDEX IF NOT EXISTS idx_rate_limit_user_key_window
  ON rate_limit_counters(user_id, limit_key, window_start);

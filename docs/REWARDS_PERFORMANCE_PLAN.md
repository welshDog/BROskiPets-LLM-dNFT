# Rewards Performance Plan (10,000+ concurrent ops)

Goal: validate the reward ledger can handle 10,000+ concurrent reward operations with correct idempotency.

## Phase 1 — Local Functional Load (SQLite)

Purpose: confirm correctness under concurrency; not absolute throughput.

Plan:
- Spin up API locally.
- Drive `/pet/001/feed` with:
  - constant `X-User-Id`
  - unique `X-Idempotency-Key` per request
- Validate:
  - balances match expected sums
  - no duplicate event_ids
  - rate limits kick in deterministically

Expected:
- SQLite will bottleneck under heavy write concurrency.
- Correctness should remain (unique constraints + transactions).

## Phase 2 — Production Load (Postgres)

Purpose: meet the 10k concurrency target.

Requirements:
- Postgres 15+ with connection pool (e.g. PgBouncer)
- API worker model: multiple processes
- Ledger uses transaction isolation + unique `event_id`

Benchmarks:
- p95 latency for reward apply: < 50ms at 5k RPS (cluster target)
- 0 duplicate ledger rows for the same `event_id`
- 0 balance drift (sum of final_amounts equals balance snapshot)

## Phase 3 — Failure + Retry Testing

Inject failures:
- simulate 5xx after ledger commit but before response
- client retries with same idempotency key

Acceptance:
- second request returns `duplicate_ignored`
- balance unchanged

## Tooling Options

- k6: HTTP scenario + shared-arrival-rate executor
- Locust: user-behavior simulation
- Custom asyncio driver for deterministic idempotency-key control


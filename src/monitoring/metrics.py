#!/usr/bin/env python3
"""
BROskiPets — Prometheus Metrics
All observable events in the system emit here.
Author: welshDog (Lyndon Williams)
"""

from prometheus_client import Counter, Histogram, Gauge, Info

# ── Chat metrics ──────────────────────────────────────────────────────────────
pet_chats_total = Counter(
    "bropets_chats_total",
    "Total chat interactions per pet",
    ["pet_id", "species"],
)

chat_latency = Histogram(
    "bropets_chat_duration_seconds",
    "End-to-end chat latency including LLM inference",
    ["pet_id"],
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# ── State metrics ─────────────────────────────────────────────────────────────
pet_xp_gauge = Gauge(
    "bropets_xp_total",
    "Current XP per pet",
    ["pet_id"],
)

pet_hunger_gauge = Gauge(
    "bropets_hunger_level",
    "Current hunger level per pet (0-100)",
    ["pet_id"],
)

pet_happiness_gauge = Gauge(
    "bropets_happiness_level",
    "Current happiness level per pet (0-100)",
    ["pet_id"],
)

# ── Evolution metrics ─────────────────────────────────────────────────────────
evolution_events_total = Counter(
    "bropets_evolutions_total",
    "Evolution events fired",
    ["from_level", "to_level"],
)

# ── Security metrics ──────────────────────────────────────────────────────────
blocked_injections_total = Counter(
    "bropets_blocked_injections_total",
    "Count of blocked prompt injection attempts",
)

rate_limit_hits_total = Counter(
    "bropets_rate_limit_hits_total",
    "Count of rate limit triggers",
    ["pet_id"],
)

# ── LLM metrics ───────────────────────────────────────────────────────────────
llm_fallbacks_total = Counter(
    "bropets_llm_fallbacks_total",
    "Times LLM fallback response was used",
)

llm_errors_total = Counter(
    "bropets_llm_errors_total",
    "LLM call errors by type",
    ["error_type"],
)

# ── System info ───────────────────────────────────────────────────────────────
bropets_info = Info(
    "bropets_build",
    "Build metadata for BROskiPets",
)
bropets_info.info({"version": "1.1.0", "author": "welshDog", "phase": "1"})

#!/usr/bin/env python3
"""
BROskiPets — Shared Redis Connection Pool
Fix: replaces raw redis.Redis() per-instance with a single shared pool.
Author: welshDog (Lyndon Williams)
"""

import os
import redis
import structlog

log = structlog.get_logger()

_pool: redis.ConnectionPool | None = None


def get_redis_pool() -> redis.ConnectionPool:
    """Return singleton connection pool. Thread-safe lazy init."""
    global _pool
    if _pool is None:
        password = os.getenv("REDIS_PASSWORD")
        if not password:
            log.warning("redis_pool.no_password", msg="REDIS_PASSWORD not set — running without auth!")
        _pool = redis.ConnectionPool(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            password=password,
            max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", 50)),
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
        )
        log.info("redis_pool.created", max_connections=_pool.max_connections)
    return _pool


def get_redis() -> redis.Redis:
    """Get a Redis client from the shared pool."""
    return redis.Redis(connection_pool=get_redis_pool())


def health_check() -> bool:
    """Ping Redis — returns True if healthy."""
    try:
        return get_redis().ping()
    except redis.RedisError as e:
        log.error("redis_pool.health_check_failed", error=str(e))
        return False

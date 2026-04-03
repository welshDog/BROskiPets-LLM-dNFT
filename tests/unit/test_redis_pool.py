#!/usr/bin/env python3
"""
Unit tests — Redis connection pool singleton + health check.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestRedisPool:
    def test_singleton_pool_returned_same_instance(self):
        """get_redis_pool() must return the same pool object on repeated calls."""
        with patch("src.core.redis_pool._pool", None):
            with patch("redis.ConnectionPool") as MockPool:
                MockPool.return_value = MagicMock()
                from src.core.redis_pool import get_redis_pool
                p1 = get_redis_pool()
                p2 = get_redis_pool()
                # Called only once despite two calls
                assert p1 is p2

    def test_health_check_returns_true_on_ping(self):
        with patch("src.core.redis_pool.get_redis") as mock_redis:
            mock_r = MagicMock()
            mock_r.ping.return_value = True
            mock_redis.return_value = mock_r

            from src.core.redis_pool import health_check
            assert health_check() is True

    def test_health_check_returns_false_on_error(self):
        import redis
        with patch("src.core.redis_pool.get_redis") as mock_redis:
            mock_r = MagicMock()
            mock_r.ping.side_effect = redis.RedisError("Connection refused")
            mock_redis.return_value = mock_r

            from src.core.redis_pool import health_check
            assert health_check() is False

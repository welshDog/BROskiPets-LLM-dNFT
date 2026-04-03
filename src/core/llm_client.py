#!/usr/bin/env python3
"""
BROskiPets — Async LLM Client
Fix: replaces placeholder stub with real Ollama/OpenAI calls + retry + fallback.
Author: welshDog (Lyndon Williams)
"""

import os
import asyncio
import httpx
import structlog
from typing import Optional

log = structlog.get_logger()

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://ollama:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:7b")
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT_SECONDS", 10.0))
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", 3))

# Fallback responses when LLM is unavailable
FALLBACK_RESPONSES = [
    "*yawns and stretches* Zzz... my brain is napping, try again soon! 🐾",
    "*tilts head* Something feels fuzzy... poke me again in a sec! 🐾",
    "*spins in circles* Whoops, got dizzy! Come back in a moment! 🐾",
]

_fallback_index = 0


async def call_llm(
    system_prompt: str,
    user_message: str,
    model: Optional[str] = None,
    max_tokens: int = 150,
) -> str:
    """
    Call Ollama LLM with retry logic and graceful fallback.
    Returns pet response string.
    """
    global _fallback_index
    target_model = model or LLM_MODEL

    payload = {
        "model": target_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "stream": False,
        "options": {"num_predict": max_tokens, "temperature": 0.8},
    }

    for attempt in range(1, LLM_MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
                resp = await client.post(
                    f"{LLM_BASE_URL}/api/chat", json=payload
                )
                resp.raise_for_status()
                data = resp.json()
                content = data["message"]["content"].strip()
                log.info("llm_client.success", model=target_model, attempt=attempt)
                return content

        except httpx.TimeoutException:
            log.warning("llm_client.timeout", attempt=attempt, model=target_model)
        except httpx.HTTPStatusError as e:
            log.error("llm_client.http_error", status=e.response.status_code, attempt=attempt)
        except Exception as e:
            log.error("llm_client.unexpected_error", error=str(e), attempt=attempt)

        if attempt < LLM_MAX_RETRIES:
            await asyncio.sleep(0.5 * attempt)  # exponential backoff

    # All retries exhausted — use fallback
    log.warning("llm_client.fallback_used", model=target_model)
    fallback = FALLBACK_RESPONSES[_fallback_index % len(FALLBACK_RESPONSES)]
    _fallback_index += 1
    return fallback


async def health_check() -> bool:
    """Check if Ollama is reachable."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{LLM_BASE_URL}/api/tags")
            return resp.status_code == 200
    except Exception as e:
        log.error("llm_client.health_check_failed", error=str(e))
        return False

"""
chain.py — web3.py integration for calling EEPVengers.evolve() on-chain.

Loaded lazily so the API starts without CONTRACT_ADDRESS set (useful for
local dev / tests that don't touch the on-chain path).
"""

import json
import os
import re
from pathlib import Path

from web3 import Web3
try:
    from web3.middleware import ExtraDataToPOAMiddleware
except ImportError:
    # web3.py 7.0+ moved middleware; define a no-op for compatibility
    class ExtraDataToPOAMiddleware:
        pass

# ── ABI (only the functions we call) ──────────────────────────────────────────

_ABI = [
    {
        "type": "function",
        "name": "evolve",
        "inputs": [
            {"name": "tokenId", "type": "uint256"},
            {"name": "newCID",   "type": "string"},
            {"name": "newStage", "type": "uint8"},
        ],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
    {
        "type": "function",
        "name": "evolveCooldownRemaining",
        "inputs": [{"name": "tokenId", "type": "uint256"}],
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
    },
    {
        "type": "function",
        "name": "evolutionStage",
        "inputs": [{"name": "", "type": "uint256"}],
        "outputs": [{"name": "", "type": "uint8"}],
        "stateMutability": "view",
    },
    {
        "type": "event",
        "name": "PetEvolved",
        "inputs": [
            {"name": "tokenId",  "type": "uint256", "indexed": True},
            {"name": "newStage", "type": "uint8",   "indexed": False},
            {"name": "newCID",   "type": "string",  "indexed": False},
            {"name": "timestamp","type": "uint256",  "indexed": False},
        ],
        "anonymous": False,
    },
]


def _load_env() -> tuple[str, str, str]:
    """Load and validate required env vars. Raises EnvironmentError if missing."""
    rpc  = os.getenv("SEPOLIA_RPC", "").strip()
    addr = os.getenv("CONTRACT_ADDRESS", "").strip()
    key  = os.getenv("AGENT_KEY", "").strip()

    missing = [n for n, v in [("SEPOLIA_RPC", rpc), ("CONTRACT_ADDRESS", addr), ("AGENT_KEY", key)] if not v]
    if missing:
        raise EnvironmentError(f"Missing env vars for on-chain evolve: {', '.join(missing)}")

    if not Web3.is_address(addr):
        raise EnvironmentError("CONTRACT_ADDRESS is set but invalid (expected 0x-prefixed 20-byte hex address).")

    key_stripped = key[2:] if key.lower().startswith("0x") else key
    if not re.fullmatch(r"[0-9a-fA-F]{64}", key_stripped or ""):
        raise EnvironmentError("AGENT_KEY is set but invalid (expected 32-byte hex private key).")

    return rpc, addr, key


def call_evolve_onchain(token_id: int, metadata_cid: str, new_stage: int) -> str:
    """
    Build, sign, and broadcast EEPVengers.evolve(tokenId, newCID, newStage).

    Returns the transaction hash (hex string, 0x-prefixed).

    Raises:
        EnvironmentError  — missing env vars (caller maps to HTTP 503)
        RuntimeError      — on-chain call rejected / chain error (caller maps to HTTP 502)
    """
    rpc, contract_addr, agent_key = _load_env()

    w3 = Web3(Web3.HTTPProvider(rpc))
    # Sepolia uses PoA-style extra data in some client configs
    try:
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    except (TypeError, AttributeError):
        pass  # web3.py version doesn't support this middleware

    if not w3.is_connected():
        raise RuntimeError(f"Cannot connect to RPC endpoint: {rpc}")

    checksum_addr = Web3.to_checksum_address(contract_addr)
    contract = w3.eth.contract(address=checksum_addr, abi=_ABI)

    agent_account = w3.eth.account.from_key(agent_key)
    agent_addr    = agent_account.address

    # Check cooldown before sending (saves gas on revert)
    cooldown = contract.functions.evolveCooldownRemaining(token_id).call()
    if cooldown > 0:
        raise RuntimeError(
            f"Token {token_id} is still on cooldown — {cooldown}s remaining. "
            "Wait before calling evolve again."
        )

    # Build transaction
    nonce = w3.eth.get_transaction_count(agent_addr)
    gas_price = w3.eth.gas_price

    tx = contract.functions.evolve(
        token_id,
        metadata_cid,
        new_stage,
    ).build_transaction({
        "from":     agent_addr,
        "nonce":    nonce,
        "gasPrice": gas_price,
        # Let web3.py estimate gas; add 20% buffer
        "gas":      int(
            contract.functions.evolve(token_id, metadata_cid, new_stage)
            .estimate_gas({"from": agent_addr}) * 1.2
        ),
    })

    signed = w3.eth.account.sign_transaction(tx, private_key=agent_key)

    try:
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    except Exception as exc:
        raise RuntimeError(f"Transaction broadcast failed: {exc}") from exc

    # Wait up to 120 s for receipt
    try:
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    except Exception as exc:
        # Broadcast succeeded — return hash even if receipt times out
        return tx_hash.hex()

    if receipt.status != 1:
        raise RuntimeError(
            f"evolve() transaction reverted. tx={tx_hash.hex()}"
        )

    return tx_hash.hex()

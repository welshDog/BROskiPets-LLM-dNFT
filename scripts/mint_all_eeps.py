"""Batch-mint every EEP from eeps/squad.json onto Sepolia.

Idempotent: reads on-chain petId(tokenId) to detect pets already minted, then
skips them. Safe to re-run after a crash, RPC blip, or out-of-gas — it picks
up where it left off.

Env required (loaded from contracts/../.env):
  SEPOLIA_RPC, CONTRACT_ADDRESS, DEPLOYER_KEY, PINATA_JWT
Optional:
  IMAGES_ROOT_CID   - if set, baby.png URLs resolve under this folder CID
  RECIPIENT_ADDRESS - defaults to deployer address
  MINT_LIMIT        - cap how many to mint this run (e.g. test with 1)
  TX_DELAY_SECONDS  - sleep between submitted txs (default 1.0)
"""

import json
import os
import sys
import time
from pathlib import Path

from web3 import Web3

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))

from agent import load_squad
from metadata import EEPMetadata, upload_to_ipfs


MANIFEST_PATH = _REPO_ROOT / "scripts" / "mint_all_manifest.json"


def _require_env(key: str) -> str:
    value = os.getenv(key, "").strip()
    if not value:
        raise SystemExit(f"Missing required env var: {key}")
    return value


def _load_local_env_file(repo_root: Path) -> None:
    env_path = repo_root / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def _load_contract_abi(repo_root: Path) -> list:
    abi_path = repo_root / "contracts" / "out" / "EEPVengers.sol" / "EEPVengers.json"
    if not abi_path.exists():
        raise SystemExit("Missing contracts/out ABI. Run: cd contracts; forge build")
    return json.loads(abi_path.read_text(encoding="utf-8"))["abi"]


def _load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        return {"minted": {}}
    try:
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"minted": {}}


def _save_manifest(manifest: dict) -> None:
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _already_minted_pet_ids(contract) -> dict:
    """Return {pet_id: token_id} for every EEP already on-chain."""
    total = int(contract.functions.totalMinted().call())
    out = {}
    for token_id in range(1, total + 1):
        try:
            pid = contract.functions.petId(token_id).call()
        except Exception:
            continue
        if pid:
            out[str(pid)] = token_id
    return out


def _build_eip1559_fees(w3: Web3) -> tuple[int, int]:
    base_fee = w3.eth.get_block("latest").get("baseFeePerGas")
    if base_fee is None:
        # Sepolia is 1559, but if we ever swap RPC keep a fallback.
        gp = w3.eth.gas_price
        return gp, gp
    priority = w3.to_wei(1, "gwei")
    return priority, base_fee * 2 + priority


def _mint_one(
    w3: Web3,
    contract,
    account,
    recipient: str,
    pet_id: str,
    eep: dict,
    nonce: int,
    chain_id: int,
) -> dict:
    images_root_cid = os.getenv("IMAGES_ROOT_CID", "").strip()
    image_cid = f"{images_root_cid}/EEPVengers/{pet_id}/baby.png" if images_root_cid else None

    eep_meta = EEPMetadata(
        pet_id=pet_id,
        name=eep["name"],
        species=eep["species"],
        rarity=eep.get("rarity", "Common"),
        token_id=0,  # placeholder; final token_id read post-receipt
    )
    state = {"xp": 0, "happiness": 70, "hunger": 50, "energy": 80, "last_interaction": ""}
    metadata = eep_meta.generate_metadata(state, image_cid=image_cid)
    content = json.dumps(metadata, indent=2).encode("utf-8")
    metadata_cid = upload_to_ipfs(content, f"{pet_id}_mint.json", "application/json")

    priority_fee, max_fee = _build_eip1559_fees(w3)
    tx = contract.functions.mint(recipient, pet_id, metadata_cid).build_transaction({
        "from": account.address,
        "nonce": nonce,
        "chainId": chain_id,
        "maxPriorityFeePerGas": priority_fee,
        "maxFeePerGas": max_fee,
    })
    tx["gas"] = int(w3.eth.estimate_gas(tx) * 12 // 10)  # +20% buffer

    signed = w3.eth.account.sign_transaction(tx, private_key=account.key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)

    if receipt.status != 1:
        raise RuntimeError(f"Mint reverted for pet_id={pet_id} tx={tx_hash.hex()}")

    token_id = int(contract.functions.totalMinted().call())
    return {
        "pet_id": pet_id,
        "token_id": token_id,
        "metadata_cid": metadata_cid,
        "tx_hash": "0x" + tx_hash.hex(),
        "block": receipt.blockNumber,
        "gas_used": receipt.gasUsed,
    }


def main() -> None:
    repo_root = _REPO_ROOT
    _load_local_env_file(repo_root)
    sepolia_rpc = _require_env("SEPOLIA_RPC")
    contract_address = _require_env("CONTRACT_ADDRESS")
    deployer_key = _require_env("DEPLOYER_KEY")
    _require_env("PINATA_JWT")

    tx_delay = float(os.getenv("TX_DELAY_SECONDS", "1.0"))
    mint_limit_raw = os.getenv("MINT_LIMIT", "").strip()
    mint_limit = int(mint_limit_raw) if mint_limit_raw else None

    w3 = Web3(Web3.HTTPProvider(sepolia_rpc))
    if not w3.is_connected():
        raise SystemExit("Web3 provider not connected. Check SEPOLIA_RPC.")
    chain_id = w3.eth.chain_id

    account = w3.eth.account.from_key(deployer_key)
    recipient = os.getenv("RECIPIENT_ADDRESS", "").strip() or account.address

    abi = _load_contract_abi(repo_root)
    contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=abi)

    squad = load_squad(str(repo_root / "eeps" / "squad.json"))
    onchain_minted = _already_minted_pet_ids(contract)
    manifest = _load_manifest()
    manifest["minted"].update({k: {"token_id": v} for k, v in onchain_minted.items() if k not in manifest["minted"]})

    pending = [eep for eep in squad if str(eep["id"]) not in onchain_minted]

    print(f"Squad size:        {len(squad)}")
    print(f"Already on-chain:  {len(onchain_minted)}")
    print(f"Pending to mint:   {len(pending)}")
    if mint_limit is not None:
        pending = pending[:mint_limit]
        print(f"MINT_LIMIT cap:    {mint_limit} (will mint {len(pending)} this run)")
    if not pending:
        print("Nothing to do — all 78 EEPs already minted.")
        _save_manifest(manifest)
        return

    nonce = w3.eth.get_transaction_count(account.address)
    failures: list[dict] = []

    for idx, eep in enumerate(pending, start=1):
        pet_id = str(eep["id"])
        print(f"\n[{idx}/{len(pending)}] minting pet_id={pet_id} name={eep['name']} nonce={nonce}")
        try:
            result = _mint_one(w3, contract, account, recipient, pet_id, eep, nonce, chain_id)
            manifest["minted"][pet_id] = result
            _save_manifest(manifest)
            print(f"  ok token_id={result['token_id']} tx={result['tx_hash']} block={result['block']} gas={result['gas_used']}")
            nonce += 1
            time.sleep(tx_delay)
        except Exception as exc:
            print(f"  FAILED pet_id={pet_id}: {exc}")
            failures.append({"pet_id": pet_id, "error": str(exc)})
            # Resync nonce in case the tx silently landed or the RPC drifted.
            nonce = w3.eth.get_transaction_count(account.address)
            time.sleep(tx_delay * 3)

    print("\n--- Summary ---")
    print(f"Total minted in this run: {len(pending) - len(failures)}")
    print(f"Failures:                 {len(failures)}")
    print(f"Manifest:                 {MANIFEST_PATH}")
    if failures:
        print(json.dumps(failures, indent=2))
        raise SystemExit(1)


if __name__ == "__main__":
    main()

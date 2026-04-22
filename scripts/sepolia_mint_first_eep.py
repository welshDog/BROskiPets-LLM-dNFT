import json
import os
import sys
from pathlib import Path

from web3 import Web3

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))

from agent import load_squad
from metadata import EEPMetadata, upload_to_ipfs


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
    payload = json.loads(abi_path.read_text(encoding="utf-8"))
    return payload["abi"]


def _get_eep(repo_root: Path, pet_id: str) -> dict:
    squad = load_squad(str(repo_root / "eeps" / "squad.json"))
    for eep in squad:
        if str(eep["id"]) == pet_id:
            return eep
    raise SystemExit(f"pet_id not found in eeps/squad.json: {pet_id}")


def main() -> None:
    repo_root = _REPO_ROOT
    _load_local_env_file(repo_root)
    sepolia_rpc = _require_env("SEPOLIA_RPC")
    contract_address = _require_env("CONTRACT_ADDRESS")
    deployer_key = _require_env("DEPLOYER_KEY")
    _require_env("PINATA_JWT")

    pet_id = os.getenv("PET_ID", "001").strip() or "001"
    eep = _get_eep(repo_root, pet_id)

    w3 = Web3(Web3.HTTPProvider(sepolia_rpc))
    if not w3.is_connected():
        raise SystemExit("Web3 provider not connected. Check SEPOLIA_RPC.")

    account = w3.eth.account.from_key(deployer_key)
    recipient = os.getenv("RECIPIENT_ADDRESS", "").strip() or account.address

    abi = _load_contract_abi(repo_root)
    contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=abi)

    state = {
        "xp": 0,
        "happiness": 70,
        "hunger": 50,
        "energy": 80,
        "last_interaction": "",
    }

    images_root_cid = os.getenv("IMAGES_ROOT_CID", "").strip()
    if images_root_cid:
        image_cid = f"{images_root_cid}/EEPVengers/{pet_id}/baby.png"
    else:
        image_cid = None

    eep_meta = EEPMetadata(
        pet_id=pet_id,
        name=eep["name"],
        species=eep["species"],
        rarity=eep.get("rarity", "Common"),
        token_id=1,
    )

    metadata = eep_meta.generate_metadata(state, image_cid=image_cid)
    content = json.dumps(metadata, indent=2).encode("utf-8")
    filename = f"{pet_id}_mint.json"
    metadata_cid = upload_to_ipfs(content, filename, content_type="application/json")

    tx = contract.functions.mint(recipient, pet_id, metadata_cid).build_transaction(
        {
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
        }
    )

    tx["gas"] = w3.eth.estimate_gas(tx)
    tx["chainId"] = w3.eth.chain_id

    latest_block = w3.eth.get_block("latest")
    base_fee = latest_block.get("baseFeePerGas")
    if base_fee is not None:
        priority_fee = w3.to_wei(1, "gwei")
        tx["maxPriorityFeePerGas"] = priority_fee
        tx["maxFeePerGas"] = base_fee * 2 + priority_fee
        tx.pop("gasPrice", None)
    else:
        tx["gasPrice"] = w3.eth.gas_price

    signed = w3.eth.account.sign_transaction(tx, private_key=deployer_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    token_id = int(contract.functions.totalMinted().call())
    if token_id > 0:
        owner = contract.functions.ownerOf(token_id).call()
        if owner.lower() != recipient.lower():
            raise SystemExit(f"Mint tx confirmed but owner mismatch. token_id={token_id} owner={owner} recipient={recipient}")

    print(json.dumps(
        {
            "contract": contract_address,
            "recipient": recipient,
            "pet_id": pet_id,
            "metadata_cid": metadata_cid,
            "tx_hash": "0x" + tx_hash.hex(),
            "token_id": token_id if token_id > 0 else None,
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()

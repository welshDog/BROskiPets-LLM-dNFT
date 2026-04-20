import json
import os
from pathlib import Path

from web3 import Web3

from agent import load_squad
from metadata import EEPMetadata, upload_to_ipfs


def _require_env(key: str) -> str:
    value = os.getenv(key, "").strip()
    if not value:
        raise SystemExit(f"Missing required env var: {key}")
    return value


def _load_contract_abi(repo_root: Path) -> list:
    abi_path = repo_root / "contracts" / "out" / "EEPVengers.sol" / "EEPVengers.json"
    if not abi_path.exists():
        raise SystemExit("Missing contracts/out ABI. Run: cd contracts; forge build")
    payload = json.loads(abi_path.read_text(encoding="utf-8"))
    return payload["abi"]


def _get_eep(pet_id: str) -> dict:
    squad = load_squad("eeps/squad.json")
    for eep in squad:
        if str(eep["id"]) == pet_id:
            return eep
    raise SystemExit(f"pet_id not found in eeps/squad.json: {pet_id}")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    sepolia_rpc = _require_env("SEPOLIA_RPC")
    contract_address = _require_env("CONTRACT_ADDRESS")
    deployer_key = _require_env("DEPLOYER_KEY")
    _require_env("PINATA_JWT")

    pet_id = os.getenv("PET_ID", "001").strip() or "001"
    eep = _get_eep(pet_id)

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
        image_cid = f"{images_root_cid}/{pet_id}/baby.png"
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
    tx["gasPrice"] = w3.eth.gas_price

    signed = w3.eth.account.sign_transaction(tx, private_key=deployer_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    minted = contract.events.PetMinted().process_receipt(receipt)
    token_id = minted[0]["args"]["tokenId"] if minted else None

    print(json.dumps(
        {
            "contract": contract_address,
            "recipient": recipient,
            "pet_id": pet_id,
            "metadata_cid": metadata_cid,
            "tx_hash": tx_hash.hex(),
            "token_id": int(token_id) if token_id is not None else None,
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()


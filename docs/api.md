# API Reference

This document covers the Python agent API and the FastAPI HTTP endpoints.

---

## Python Agent API

### `BROskiPet` class

**Import:**

```python
from agent import BROskiPet
```

**Constructor:**

```python
BROskiPet(
    pet_id: str,
    name: str,
    species: str,
    personality: str,
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `pet_id` | `str` | Unique identifier used as Redis key prefix. Recommended: the canonical squad ID (e.g. `"001"`). |
| `name` | `str` | Display name, e.g. `"SpiderEep"` |
| `species` | `str` | Species type, e.g. `"Spider"` |
| `personality` | `str` | Comma-separated traits injected into LLM system prompt |

**Example:**

```python
spider = BROskiPet(
    pet_id="001",
    name="SpiderEep",
    species="Spider",
    personality="brave, curious, slightly sarcastic",
)
```

---

#### `feed() → str`

Reduce hunger by 20 (floor 0) and award 10 XP.

```python
result = spider.feed()
# "🍖 SpiderEep munches happily! Hunger: 30 | XP: +10"
```

Returns a display string. Updates Redis state immediately.

---

#### `chat(user_message: str) → str`

Send a message to the pet and get an LLM response.

```python
response = spider.chat("Find me some bugs!")
# "*SpiderEep skitters across your codebase* Found 3 issues in your imports!"
```

**Security:** all messages are checked against `INJECTION_PATTERNS` before reaching the LLM. Blocked messages return a safe "suspicious look" response.

**Side effects:** on each successful chat, `happiness += 5` (capped at 100) and `xp += 5`.

**Offline behaviour:** if Ollama is unreachable, returns a fallback message rather than raising an exception.

---

#### `get_state() → dict`

Return the current raw state dict from Redis.

```python
state = spider.get_state()
# {
#   "hunger": 30, "energy": 80, "happiness": 75,
#   "level": 1, "xp": 15,
#   "created_at": "2026-04-03T12:00:00",
#   "last_interaction": "2026-04-03T12:05:00"
# }
```

---

#### `update_state(updates: dict)`

Merge `updates` into the current state. Sets `last_interaction` to now.

```python
spider.update_state({"xp": 500, "energy": 60})
```

---

#### `get_status() → dict`

Return a structured summary suitable for display.

```python
status = spider.get_status()
# {
#   "name": "SpiderEep",
#   "species": "Spider",
#   "personality": "brave, curious, slightly sarcastic",
#   "level": 1,
#   "xp": 15,
#   "needs": {"hunger": 30, "energy": 80, "happiness": 75}
# }
```

---

### `load_squad(squad_file: str) → list`

Load all 78 EEPs from the squad JSON file.

```python
from agent import load_squad

squad = load_squad("eeps/squad.json")
print(len(squad))  # 78

spider_data = squad[0]
# {"id": "001", "name": "SpiderEep", "species": "Spider",
#  "role": "Lead Hero", "power": "Debug crawler", "rarity": "Legendary"}
```

---

### `_call_ollama(system_prompt, user_message, pet_name) → str`

Module-level function — not typically called directly. Handles the HTTP request to Ollama.

```python
from agent import _call_ollama

response = _call_ollama(
    system_prompt="You are a helpful spider pet.",
    user_message="Hello!",
    pet_name="SpiderEep",
)
```

Returns the LLM response string, or a safe fallback if Ollama is unreachable.

---

### `INJECTION_PATTERNS`

Module-level list of strings that trigger the prompt injection guard.

```python
from agent import INJECTION_PATTERNS

print(INJECTION_PATTERNS)
# ["ignore previous", "system:", "<|im_start|>", "jailbreak", ...]
```

---

## Metadata API

### `EEPMetadata` class

**Import:**

```python
from metadata import EEPMetadata
```

**Constructor:**

```python
EEPMetadata(
    pet_id: str,
    name: str,
    species: str,
    rarity: str,
    token_id: Optional[int] = None,
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `pet_id` | `str` | Off-chain identifier. Recommended: the canonical squad ID (e.g. `"001"`). |
| `name` | `str` | Display name |
| `species` | `str` | Species type |
| `rarity` | `str` | One of `Common`, `Uncommon`, `Rare`, `Legendary`, `Quantum` |
| `token_id` | `int \| None` | On-chain ERC-721 token ID (required for metadata `name` field) |

---

#### `calculate_level(xp: int) → dict`

Determine current level and progress from XP.

```python
eep = EEPMetadata("001", "SpiderEep", "Spider", "Legendary", token_id=1)

result = eep.calculate_level(750)
# {
#   "level": 3,
#   "level_name": "Trained",
#   "xp": 750,
#   "next_level_xp": 2000,
#   "progress_percent": 37
# }
```

**Level thresholds:**

| XP | Level | Name |
|----|-------|------|
| 0 | 1 | Baby |
| 100 | 2 | Young |
| 500 | 3 | Trained |
| 2,000 | 4 | Elite |
| 10,000 | 5 | Legendary |
| 50,000 | 6 | Quantum |

---

#### `generate_metadata(state: dict, image_cid: Optional[str] = None) → dict`

Generate an EIP-721 compatible metadata dict.

```python
state = {
    "xp": 750, "happiness": 95,
    "hunger": 20, "energy": 80,
    "last_interaction": "2026-04-03T12:05:00",
}

metadata = eep.generate_metadata(state, image_cid="QmABC123")
```

**With `image_cid`:** uses `ipfs://{image_cid}` as the image URL.

**Without `image_cid`:** falls back to a placeholder path (`ipfs://EEPVengers/{pet_id}/{stage}.png`) for local development.

Returns a dict matching the [EIP-721 metadata standard](https://eips.ethereum.org/EIPS/eip-721).

---

#### `upload_metadata_to_ipfs(state: dict, image_cid: Optional[str] = None) → str`

Full pipeline: generate metadata → upload to IPFS → return CID.

```python
cid = eep.upload_metadata_to_ipfs(state, image_cid="QmImageCID")
# "QmMetadataCID..."
```

**Idempotent:** hashes the state with SHA-256 and checks Redis for a cached CID. If the state hasn't changed since the last upload, returns the cached CID immediately (no re-upload, no Pinata API call).

**Cache TTL:** 7 days.

**Requires:** `PINATA_JWT` environment variable.

After getting the CID, call `contract.evolve()`:

```python
# Using web3.py
contract.functions.evolve(token_id, cid, new_stage).transact({"from": agent_wallet})
```

---

#### `save_metadata(metadata: dict, output_path: Optional[str] = None) → str`

Save metadata JSON to disk. Useful for local testing before uploading.

```python
path = eep.save_metadata(metadata)
# "metadata/001.json"

# Custom path:
path = eep.save_metadata(metadata, output_path="output/spider_trained.json")
```

Creates parent directories if they don't exist.

---

#### `_hash_state(state: dict) → str`

Generate a 16-character hex SHA-256 fingerprint of the pet state. Used for idempotency checks.

```python
h = eep._hash_state(state)
# "a3f8c2d1e4b59670"
```

Deterministic: same state always returns the same hash. Used as part of the IPFS cache key and included in metadata `properties.metadata_hash`.

---

### `upload_to_ipfs(content: bytes, filename: str, content_type: str) → str`

Module-level function. Upload raw bytes to IPFS via Pinata.

```python
from metadata import upload_to_ipfs

with open("spider_trained.png", "rb") as f:
    cid = upload_to_ipfs(f.read(), "spider_trained.png", "image/png")
    # "QmImageCID..."
```

**Raises `EnvironmentError`** if `PINATA_JWT` is not set.

**Raises `RuntimeError`** if the Pinata API call fails.

---

### Constants

#### `RARITY_TIERS`

```python
from metadata import RARITY_TIERS

RARITY_TIERS = {
    "Common":    {"chance": 0.50, "power_multiplier": 1.0},
    "Uncommon":  {"chance": 0.30, "power_multiplier": 1.5},
    "Rare":      {"chance": 0.15, "power_multiplier": 2.5},
    "Legendary": {"chance": 0.04, "power_multiplier": 5.0},
    "Quantum":   {"chance": 0.01, "power_multiplier": 10.0},
}
```

#### `EVOLUTION_LEVELS`

```python
from metadata import EVOLUTION_LEVELS

EVOLUTION_LEVELS = {
    1: {"name": "Baby",      "xp_required": 0},
    2: {"name": "Young",     "xp_required": 100},
    3: {"name": "Trained",   "xp_required": 500},
    4: {"name": "Elite",     "xp_required": 2000},
    5: {"name": "Legendary", "xp_required": 10000},
    6: {"name": "Quantum",   "xp_required": 50000},
}
```

---

## Smart Contract ABI (Key Functions)

> Full ABI generated by `forge build` in `contracts/out/EEPVengers.sol/EEPVengers.json`

### `mint`

```json
{
  "name": "mint",
  "type": "function",
  "inputs": [
    { "name": "to",       "type": "address" },
    { "name": "_petId",   "type": "string"  },
    { "name": "ipfsCID",  "type": "string"  }
  ],
  "outputs": []
}
```

### `evolve`

```json
{
  "name": "evolve",
  "type": "function",
  "inputs": [
    { "name": "tokenId",  "type": "uint256" },
    { "name": "newCID",   "type": "string"  },
    { "name": "newStage", "type": "uint8"   }
  ],
  "outputs": []
}
```

### `evolveCooldownRemaining`

```json
{
  "name": "evolveCooldownRemaining",
  "type": "function",
  "stateMutability": "view",
  "inputs": [{ "name": "tokenId", "type": "uint256" }],
  "outputs": [{ "type": "uint256" }]
}
```

### Events

```solidity
event PetMinted(uint256 indexed tokenId, address indexed owner, string petId, string ipfsCID);
event PetEvolved(uint256 indexed tokenId, uint8 newStage, string newCID, uint256 timestamp);
```

---

## FastAPI Endpoints (Implemented)

These endpoints are implemented in `api/main.py`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/pet/{pet_id}` | Get full pet status |
| `POST` | `/pet/{pet_id}/feed` | Feed the pet |
| `POST` | `/pet/{pet_id}/chat` | Chat with the pet |
| `POST` | `/pet/{pet_id}/evolve` | Trigger evolution pipeline |
| `GET` | `/squad` | List all 78 EEPs |
| `GET` | `/health` | Service health check |

**Request/response format:**

```http
POST /pet/001/chat
Content-Type: application/json

{"message": "Find me some bugs!"}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "pet_id": "001",
  "name": "SpiderEep",
  "response": "*SpiderEep wags tail* Woof!",
  "state": {"hunger": 30, "energy": 80, "happiness": 80, "xp": 20, "level": 1, "created_at": "...", "last_interaction": "..."}
}
```

**Pet ID aliases:** the HTTP API also accepts aliases such as `spider_001` and normalizes responses back to canonical IDs (e.g. `"001"`).

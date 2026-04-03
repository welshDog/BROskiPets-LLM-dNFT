# Code Style Guide

Consistency makes the codebase easier to read, review, and contribute to. Follow these guidelines for all new code.

---

## Python

### General

- **PEP 8** — the baseline. Use `black` for auto-formatting and `ruff` for linting.
- **Line length** — 100 characters maximum
- **Python version** — 3.10+ syntax is fine; no walrus operator abuse

```bash
# Auto-format before committing
black agent.py metadata.py tests/

# Lint check
ruff check agent.py metadata.py tests/
```

### Naming

| Thing | Convention | Example |
|-------|-----------|---------|
| Module-level constants | `UPPER_SNAKE_CASE` | `INJECTION_PATTERNS`, `REDIS_HOST` |
| Classes | `PascalCase` | `BROskiPet`, `EEPMetadata` |
| Functions / methods | `snake_case` | `calculate_level()`, `upload_to_ipfs()` |
| Private functions | `_snake_case` | `_call_ollama()`, `_hash_state()` |
| Variables | `snake_case` | `pet_id`, `state_hash` |
| Test functions | `test_<what_it_tests>` | `test_feed_gives_xp` |

### Type Hints

Use type hints on all public functions and methods:

```python
# Good
def calculate_level(self, xp: int) -> dict:
    ...

def upload_to_ipfs(content: bytes, filename: str, content_type: str = "application/json") -> str:
    ...

# Avoid — no type hints
def calculate_level(self, xp):
    ...
```

Use `Optional[X]` (or `X | None` in 3.10+) for nullable parameters:

```python
from typing import Optional

def generate_metadata(self, state: dict, image_cid: Optional[str] = None) -> dict:
    ...
```

### Docstrings

Add docstrings to all public classes and methods. Keep them short — one line for simple functions, a few lines for complex ones:

```python
def feed(self) -> str:
    """Feed the pet — reduces hunger by 20 (floor 0) and awards 10 XP."""
    ...

def upload_metadata_to_ipfs(self, state: dict, image_cid: Optional[str] = None) -> str:
    """
    Full pipeline: generate ERC-721 metadata JSON → upload to IPFS → return CID.

    Idempotent: checks Redis cache before uploading. Same state = same CID returned.
    Requires: PINATA_JWT environment variable.
    """
    ...
```

**Do not** add docstrings to private functions or test functions — they're self-explanatory from the name.

### Comments

Comments explain *why*, not *what*. The code already says what.

```python
# Good — explains non-obvious reasoning
# lastEvolved == 0 means the pet has never evolved — first evolution is always allowed.
if lastEvolved[tokenId] == 0:
    ...

# Bad — restates the code
# Check if the pet has never evolved
if lastEvolved[tokenId] == 0:
    ...
```

### Error Handling

Only handle errors at system boundaries (external APIs, user input). Trust internal code.

```python
# Good — handling Ollama being offline (external service)
try:
    resp = httpx.post(...)
    resp.raise_for_status()
    return resp.json()["message"]["content"]
except httpx.HTTPError:
    return f"*{pet_name} tilts head* (LLM offline) 🐾"

# Avoid — wrapping internal logic in try/except
try:
    state = self.get_state()
    state.update(updates)
except Exception:
    pass  # never silently swallow errors
```

### Imports

Group imports in this order, separated by a blank line:

```python
# 1. Standard library
import json
import os
from datetime import datetime
from typing import Optional

# 2. Third-party
import httpx
import redis

# 3. Local (if any)
from metadata import EEPMetadata
```

---

## Solidity

### General

Follow the [OpenZeppelin Solidity style](https://docs.openzeppelin.com/contracts/5.x/governance) and Solidity official style guide.

### Layout Order

```solidity
// SPDX-License-Identifier
// pragma
// imports
// contract {
//   type declarations
//   state variables
//   events
//   errors
//   constructor
//   external functions
//   public functions
//   internal functions
//   private functions
// }
```

### Naming

| Thing | Convention | Example |
|-------|-----------|---------|
| Contracts | `PascalCase` | `EEPVengers` |
| Functions | `camelCase` | `evolve()`, `totalMinted()` |
| State variables | `camelCase` | `evolutionStage`, `lastEvolved` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_SUPPLY`, `EVOLVE_COOLDOWN` |
| Events | `PascalCase` | `PetEvolved`, `PetMinted` |
| Errors | `PascalCase` | `MaxSupplyReached` |
| Roles | `UPPER_SNAKE_CASE` | `MINTER_ROLE`, `AGENT_ROLE` |

### NatSpec Comments

All public and external functions need NatSpec documentation:

```solidity
/**
 * @notice Update a pet's metadata CID when it evolves.
 * @dev Only callable by AGENT_ROLE. Rate-limited by EVOLVE_COOLDOWN.
 * @param tokenId   The NFT token to evolve.
 * @param newCID    New IPFS CID of the updated metadata JSON.
 * @param newStage  New evolution stage (1-6). Must be >= current stage.
 */
function evolve(uint256 tokenId, string calldata newCID, uint8 newStage) external { ... }
```

Single-line `///` comments for simple view functions:

```solidity
/// @notice Total EEPs minted so far.
function totalMinted() external view returns (uint256) {
    return _nextTokenId - 1;
}
```

### Error Messages

Use `require()` with descriptive string messages (matches test assertions):

```solidity
// Good — test can assert exact string
require(_nextTokenId <= MAX_SUPPLY, "EEPVengers: All 78 EEPs minted");
require(newStage <= 6, "EEPVengers: Max stage is 6 (Quantum)");

// Avoid in this codebase — harder to test with string matching
revert MaxSupplyReached(); // custom errors are fine for new contracts, but match existing style
```

### Access Modifiers Order

```solidity
function myFunction(uint256 arg)
    external           // visibility first
    onlyRole(MY_ROLE)  // access control
    whenNotPaused      // state checks
    nonReentrant       // guards last
{
    ...
}
```

---

## Tests (Python)

### Naming

```python
def test_<what_is_being_tested>():
    ...

# For parametrised tests:
@pytest.mark.parametrize("xp,expected_level", [...])
def test_level_thresholds(spider, xp, expected_level):
    ...

# For fuzz/property tests:
def testFuzz_<what_is_being_tested>(random_input):
    ...
```

### Structure (AAA)

Arrange → Act → Assert — keep them visually separated:

```python
def test_feed_reduces_hunger(spider):
    # Arrange
    before = spider.get_state()["hunger"]

    # Act
    spider.feed()

    # Assert
    assert spider.get_state()["hunger"] == max(0, before - 20)
```

For very simple tests, inline is fine:

```python
def test_initial_xp_is_zero(spider):
    assert spider.get_state()["xp"] == 0
```

### No Magic Numbers

Use named constants or fixtures instead of bare numbers:

```python
# Good
LEGENDARY_POWER_MULTIPLIER = 5.0

def test_metadata_power_multiplier_matches_rarity(spider, base_state):
    meta = spider.generate_metadata(base_state)
    mults = [a["value"] for a in meta["attributes"] if a["trait_type"] == "Power Multiplier"]
    assert mults == [LEGENDARY_POWER_MULTIPLIER]

# Avoid
assert mults == [5.0]  # where does 5.0 come from?
```

---

## Tests (Solidity)

### Naming

```solidity
// Unit tests
function test_<WhatIsBeingTested>() public { ... }

// Fuzz tests
function testFuzz_<WhatIsBeingTested>(Type fuzzInput) public { ... }

// Failure tests (expected reverts)
function test_<Feature>Reverts<Reason>() public { ... }
```

### setUp pattern

```solidity
function setUp() public {
    vm.startPrank(admin);
    nft = new EEPVengers(admin);
    nft.grantRole(nft.MINTER_ROLE(), minter);
    nft.grantRole(nft.AGENT_ROLE(),  agent);
    vm.stopPrank();
}
```

All test state created in `setUp()`, not inline in tests.

---

## Documentation (Markdown)

- Use GitHub-Flavored Markdown
- Code blocks always have a language tag: ` ```python `, ` ```solidity `, ` ```bash `
- One blank line before and after headings
- Tables for structured comparisons (not bullet lists)
- Active voice: "Run the tests" not "Tests should be run"
- No emojis in code-facing docs (API reference, architecture) — fine in user-facing docs (README, EEP powers)

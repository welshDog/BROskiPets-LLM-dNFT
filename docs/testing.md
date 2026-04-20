# Testing Guide

BROskiPets has two test suites: Python (pytest) and Solidity (Foundry). Both must pass before any merge.

**Current status: 89/89 tests passing**

---

## Quick Run

```bash
# Python tests only (73 tests, ~1 second)
python -m pytest tests/ -v

# Solidity tests only (16 tests + 10k fuzz, ~10 seconds)
cd contracts && forge test -v

# Full suite
python -m pytest tests/ -v && cd contracts && forge test
```

---

## Python Tests

### Prerequisites

```bash
pip install pytest fakeredis httpx pytest-cov
```

`fakeredis` replaces Redis with an in-memory fake — no Docker needed for unit tests.

### Running

```bash
# All tests with verbose output
python -m pytest tests/ -v

# Single file
python -m pytest tests/test_agent.py -v
python -m pytest tests/test_metadata.py -v

# Single test
python -m pytest tests/test_agent.py::test_feed_gives_xp -v

# With coverage report
python -m pytest tests/ --cov=agent --cov=metadata --cov-report=term-missing
```

### Test Files

#### `tests/test_agent.py` — 37 tests

Covers `BROskiPet` class behaviour without requiring real Redis or Ollama.

| Test Group | Count | What it covers |
|------------|-------|----------------|
| Init state | 6 | Default hunger/energy/happiness/xp/level; state not reset on second instantiation |
| `feed()` | 4 | Hunger reduction, XP award, floor at 0, return string format |
| `chat()` / injection guard | 15 | Blocks 15 different injection patterns |
| `chat()` side effects | 3 | Happiness increases, XP increases, happiness capped at 100 |
| `get_status()` | 2 | Structure and name field |
| `update_state()` | 2 | Partial updates, sets `last_interaction` |
| `INJECTION_PATTERNS` | 2 | Non-empty, all are matchable |
| `load_squad()` | 3 | Returns 78 EEPs, all have required fields, WelshDogEep is Quantum |

**Key technique — fakeredis:**

```python
@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    import fakeredis
    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr("agent.r", fake)
    return fake
```

This replaces the module-level Redis connection before any test runs — no Docker required.

#### `tests/test_metadata.py` — 36 tests

Covers `EEPMetadata` and the `upload_to_ipfs` function.

| Test Group | Count | What it covers |
|------------|-------|----------------|
| `RARITY_TIERS` | 4 | All five tiers exist, chances sum to 1.0, Quantum is rarest, Quantum has highest multiplier |
| `calculate_level()` | 12 | Level at 0/100/500/50000 XP, progress capped at 100, parametrised thresholds |
| `generate_metadata()` | 11 | EIP-721 required fields, name has token ID, image URL format, CID vs placeholder, rarity in attributes, power multiplier, can_evolve flag, JSON serialisable |
| `_hash_state()` | 4 | Deterministic, changes with state, 16 chars, valid hex |
| `upload_to_ipfs()` | 1 | Raises `EnvironmentError` without JWT |

**The `can_evolve` edge case:**

`can_evolve` is `True` only when `progress_percent >= 100`. This only occurs at the Quantum level (XP ≥ 50,000), because `calculate_level()` advances the level as soon as XP hits the threshold — so `next_xp` always refers to the *next* tier.

```python
# This is correct — can_evolve=True only at Quantum
def test_metadata_can_evolve_flag(spider):
    state = {"xp": 50000, ...}
    meta = spider.generate_metadata(state)
    assert meta["properties"]["can_evolve"] is True
```

### Adding Python Tests

1. Create a test function in the appropriate file (`test_agent.py` or `test_metadata.py`)
2. Follow the naming convention: `test_{what_it_tests}`
3. Use parametrize for multiple input scenarios:

```python
@pytest.mark.parametrize("xp,expected_level", [
    (0, 1), (99, 1), (100, 2), (500, 3),
])
def test_level_thresholds(spider, xp, expected_level):
    assert spider.calculate_level(xp)["level"] == expected_level
```

4. Patch external services with `monkeypatch`:

```python
def test_chat_increases_xp(spider):
    import agent as ag
    ag._call_ollama = lambda s, u, n: "Woof!"  # bypass Ollama
    spider.chat("Hello!")
    assert spider.get_state()["xp"] > 0
```

---

## Solidity Tests (Foundry)

### Prerequisites

```bash
# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Install contract dependencies (run once)
cd contracts
forge install
```

### Running

```bash
cd contracts

# All tests
forge test

# Verbose (shows test names)
forge test -v

# Very verbose (shows logs, traces)
forge test -vvv

# Single test
forge test --match-test test_MintSucceeds -v

# Single contract
forge test --match-contract EEPVengersTest -v

# Gas report
forge test --gas-report

# Custom fuzz runs
forge test --fuzz-runs 50000
```

### Test File: `contracts/test/EEPVengers.t.sol`

16 tests across 5 groups:

#### Minting (4 tests)

| Test | What it checks |
|------|---------------|
| `test_MintSucceeds` | Owner, stage=1, petId stored, tokenURI = `ipfs://{CID}`, totalMinted=1 |
| `test_MintEmitsEvent` | `PetMinted(tokenId, owner, petId, cid)` event emitted correctly |
| `test_MintRevertsIfNotMinter` | Reverts when caller lacks `MINTER_ROLE` |
| `test_MintRevertsAfterMaxSupply` | Reverts with `"EEPVengers: All 78 EEPs minted"` after token 78 |

#### Evolution (6 tests)

| Test | What it checks |
|------|---------------|
| `test_EvolveSucceeds` | Stage updated, tokenURI updated, event emitted |
| `test_EvolveEmitsEvent` | `PetEvolved(tokenId, stage, cid, timestamp)` matches |
| `test_EvolveRevertsIfNotAgent` | Reverts when caller lacks `AGENT_ROLE` |
| `test_EvolveRevertsOnCooldown` | Second `evolve()` in same block reverts |
| `test_EvolveSucceedsAfterCooldown` | `evolve()` works after `vm.warp(+1 hour)` |
| `test_EvolveRevertsDeEvolution` | Reverts when `newStage < currentStage` |
| `test_EvolveRevertsAboveMaxStage` | Reverts when `newStage > 6` |

#### Cooldown View (2 tests)

| Test | What it checks |
|------|---------------|
| `test_CooldownRemainingIsZeroBeforeFirstEvolve` | Returns 0 for never-evolved token |
| `test_CooldownRemainingAfterEvolve` | Returns >0 and ≤ 1 hour after evolve |

#### Pause (2 tests)

| Test | What it checks |
|------|---------------|
| `test_PauseBlocksMint` | `mint()` reverts when paused |
| `test_UnpauseRestoresMint` | `mint()` works after unpause |

#### Fuzz (1 test)

| Test | What it checks |
|------|---------------|
| `testFuzz_EvolveStageRange(uint8 stage)` | All valid stages (1-6) succeed on first evolution; runs 10,001 times |

### Foundry Cheatcodes Used

```solidity
vm.prank(address)          // Next call comes from `address`
vm.startPrank(address)     // All calls until stopPrank come from `address`
vm.stopPrank()             // End prank
vm.warp(uint256 timestamp) // Set block.timestamp
vm.expectRevert(bytes)     // Expect next call to revert with message
vm.expectEmit(...)         // Expect next call to emit an event
makeAddr("label")          // Create deterministic test address from label
vm.assume(bool)            // Fuzz: skip inputs where condition is false
```

### Adding Solidity Tests

Follow the existing pattern in `EEPVengers.t.sol`:

```solidity
function test_NewFeature() public {
    // Arrange
    vm.prank(minter);
    nft.mint(user1, PET_ID, BASE_CID);

    // Act
    vm.prank(agent);
    nft.evolve(1, EVOLVED_CID, 2);

    // Assert
    assertEq(nft.evolutionStage(1), 2);
}

// Fuzz test
function testFuzz_Example(uint256 value) public {
    vm.assume(value > 0 && value < 100);
    // test body
}
```

---

## CI / CD

A GitHub Actions workflow runs on every push and PR:

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  python-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install pytest pytest-asyncio fakeredis httpx fastapi pydantic redis web3
      - run: python -m pytest tests -q

  solidity-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { submodules: recursive }
      - uses: foundry-rs/foundry-toolchain@v1
      - run: cd contracts && forge test --fuzz-runs 1000
```

---

## Test Coverage

```bash
# Python coverage report
python -m pytest tests/ --cov=agent --cov=metadata --cov-report=html
open htmlcov/index.html

# Solidity coverage (requires lcov)
cd contracts && forge coverage --report lcov
```

**Coverage targets:**

| Module | Target |
|--------|--------|
| `agent.py` | > 90% |
| `metadata.py` | > 90% |
| `EEPVengers.sol` | 100% branch coverage |

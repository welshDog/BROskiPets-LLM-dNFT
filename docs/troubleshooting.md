# Troubleshooting

Common issues and how to fix them.

---

## Docker / Stack Issues

### Docker Desktop is paused

**Symptom:** `Error response from daemon: Docker Desktop is manually paused.`

**Fix:** Unpause Docker Desktop from the whale menu or Dashboard, then restart the stack:

```bash
docker compose up -d
docker compose ps
```

---

### Ollama is not responding

**Symptom:** `chat()` returns `"(LLM offline — check Ollama is running) 🐾"` or connection refused on port 11434.

**Cause:** Model is still downloading (first run takes 5-10 min for 4 GB).

**Fix:**

```bash
docker compose logs ollama
# Look for: "successfully pulled model qwen2.5:7b"
```

Wait until you see the model pull complete. If it's stuck:

```bash
docker compose restart ollama
```

If Ollama starts but the model is missing:

```bash
docker compose exec ollama ollama pull qwen2.5:7b
```

---

### Redis connection refused

**Symptom:** `redis.exceptions.ConnectionError: Error 111 connecting to redis:6379`

**Cause 1:** Redis container isn't running.

```bash
docker compose ps  # check redis status
docker compose up redis -d
```

**Cause 2:** Wrong password in `.env`.

```bash
# Check your .env
cat .env | grep REDIS_PASSWORD

# Test the connection manually
docker compose exec redis redis-cli -a "YOUR_PASSWORD" PING
# Expected: PONG
```

### Redis authentication error

**Symptom:** `redis.exceptions.AuthenticationError: invalid username-password pair or user is disabled.`

**Cause:** The API container is not receiving `REDIS_PASSWORD`, or `.env` doesn’t match the Redis `--requirepass` value.

**Fix:**

```bash
docker compose up -d
docker compose logs --tail 80 bropets-api
docker compose exec redis redis-cli -a "$REDIS_PASSWORD" PING
```

**Cause 3:** Running Python locally but pointing at Docker Redis without the right host.

```bash
export REDIS_HOST=localhost  # not 'redis' when running outside Docker
python agent.py
```

---

### Port conflict (8080 already in use)

**Symptom:** `Error starting userland proxy: listen tcp 0.0.0.0:8080: bind: address already in use`

**Fix:** Find and stop the conflicting process:

```bash
# Find what's on port 8080
lsof -i :8080    # macOS/Linux
netstat -ano | findstr :8080  # Windows

# Or change the port in docker-compose.yml:
ports:
  - "8081:8080"  # use 8081 externally
```

---

### Docker Compose `version` warning

**Symptom:** `WARN[0000] /path/to/docker-compose.yml: 'version' is obsolete`

**This is harmless.** Docker Compose v2 deprecated the `version` key. The stack runs correctly.

---

## Python Issues

### `ModuleNotFoundError: No module named 'redis'`

```bash
# Activate your virtual environment first
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Then install
pip install redis httpx
```

### `ModuleNotFoundError: No module named 'fakeredis'`

Only needed for tests:

```bash
pip install fakeredis
```

### `EnvironmentError: PINATA_JWT not set`

**Symptom:** Raised by `upload_to_ipfs()` or `upload_metadata_to_ipfs()`.

**Fix:** Set the environment variable before running:

```bash
export PINATA_JWT=your_jwt_here
# or add to .env and reload
```

Get a free JWT at [app.pinata.cloud/developers/api-keys](https://app.pinata.cloud/developers/api-keys).

For development without IPFS, use `generate_metadata()` and `save_metadata()` instead of `upload_metadata_to_ipfs()` — they don't require Pinata.

### IPFS upload fails with 403 Forbidden

**Symptom:** `Client error '403 Forbidden' for url 'https://api.pinata.cloud/pinning/pinFileToIPFS'`

**Cause:** `PINATA_JWT` is missing inside the API container, revoked, or lacks permission for `pinFileToIPFS`.

**Fix:**

```bash
# Confirm the API container sees the JWT (prints 'set' or empty)
docker compose exec bropets-api sh -lc 'python -c "import os; print(\"set\" if os.getenv(\"PINATA_JWT\") else \"missing\")"'
```

### `NameError: name 'RARITY_TIERS' is not defined`

This was a bug in the original codebase (`RAREITY_TIERS` typo) — it has been fixed. Make sure you have the latest code:

```bash
git pull origin main
```

### Tests fail with `redis.exceptions.ConnectionError`

Tests use `fakeredis` and should never connect to real Redis. If you see this error in tests, the `fake_redis` fixture isn't applying.

Check that `autouse=True` is set on the fixture in `test_agent.py`:

```python
@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    ...
```

---

## Solidity / Foundry Issues

### `forge: command not found`

Foundry isn't in your PATH.

```bash
# Re-run foundryup
foundryup

# Add to PATH manually
export PATH="$PATH:$HOME/.foundry/bin"

# Make permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export PATH="$PATH:$HOME/.foundry/bin"' >> ~/.bashrc
source ~/.bashrc
```

### `cast: The term 'cast' is not recognized` (Windows)

**Fix:**

```powershell
$env:PATH += ";$env:USERPROFILE\.foundry\bin"
cast --version
```

### `--rpc-url` / `--fork-url` value missing in PowerShell

**Symptom:** `a value is required for '--rpc-url <URL>' but none was supplied`

**Cause:** `$env:SEPOLIA_RPC` is not set in the current terminal.

**Fix:** Load `.env` into your session, or set `$env:SEPOLIA_RPC` directly:

```powershell
cd H:\dNFTpet\BROskiPets-LLM-dNFT
Get-Content .env | ForEach-Object {
  $line = $_.Trim()
  if (-not $line -or $line.StartsWith('#') -or $line -notmatch '=') { return }
  $k,$v = $line.Split('=',2)
  $k=$k.Trim()
  $v=$v.Trim().Trim('"').Trim("'")
  if ($k) { [Environment]::SetEnvironmentVariable($k, $v, 'Process') }
}
```

### `forge install` fails

```bash
# Run from the contracts/ directory, not root
cd contracts
forge install
```

If submodule clone fails (network issue):

```bash
forge install --no-git OpenZeppelin/openzeppelin-contracts
```

### `Unable to resolve imports: @openzeppelin/contracts/...`

OpenZeppelin isn't installed or the remapping isn't picking it up.

```bash
cd contracts
forge install OpenZeppelin/openzeppelin-contracts
forge remappings  # verify @openzeppelin/contracts/ is in the list
```

### `Encountered invalid solc version: ^0.8.26`

This error comes from OpenZeppelin's internal `fv/` harnesses, which require a newer compiler. The `foundry.toml` already has a skip rule for these — if you see this, verify:

```toml
# contracts/foundry.toml
skip = [
    "lib/openzeppelin-contracts/fv/**",
    "lib/openzeppelin-contracts/test/**",
]
```

### `EEPVengers: Evolution on cooldown` in tests

If `evolve()` is failing in a Foundry test with this message on the **first** evolve call, the token was just minted and `lastEvolved == 0`. This is handled correctly by the contract (`lastEvolved == 0` is treated as "never evolved → allow immediately"), but if you're writing a new test that skips past the normal flow, ensure the token was actually minted via `nft.mint(...)` first.

---

## Metadata Issues

### `generate_metadata()` returns placeholder IPFS paths

**Symptom:** `image` field is `ipfs://EEPVengers/001/baby.png` instead of a real CID.

**This is expected behaviour** for local development when images are not pinned yet. You can either pass a CID path explicitly, or set `IMAGES_ROOT_CID` so metadata generation becomes resolvable automatically:

```python
metadata = eep.generate_metadata(state, image_cid="QmYourRealCID")
```

For development without Pinata, the placeholder paths are intentional and safe.

### Metadata JSON fails to serialise

**Symptom:** `TypeError: Object of type ... is not JSON serializable`

The `state` dict must contain only JSON-serialisable values (strings, numbers, booleans, None). The `last_interaction` field must be a string (ISO format), not a `datetime` object:

```python
# Good
state = {"xp": 100, "last_interaction": datetime.now().isoformat()}

# Will fail
state = {"xp": 100, "last_interaction": datetime.now()}  # datetime is not JSON serialisable
```

---

## Git Issues

### Merge conflicts after `git pull`

The repository had a merge with `757cdb4` that introduced conflicts in `EEPVengers.sol`, `metadata.py`, `agent.py`, and `foundry.toml`. These are all resolved. If you see fresh conflicts, it means you have local changes — resolve them by taking the remote version:

```bash
git checkout --theirs path/to/conflicting/file
git add path/to/conflicting/file
git commit
```

Or see the full resolution in [CHANGELOG.md](../CHANGELOG.md).

### Submodule issues (`contracts/lib/` is empty)

After cloning, initialise submodules:

```bash
git submodule update --init --recursive
```

---

## Getting More Help

- Open a [GitHub Issue](https://github.com/welshDog/BROskiPets-LLM-dNFT/issues) with your error output
- Include: OS, Python version (`python --version`), Docker version (`docker --version`), and the full error traceback
- Tag with `bug` or `question` as appropriate

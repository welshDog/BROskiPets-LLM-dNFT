from pathlib import Path


def _parse_env_file(path: Path) -> dict[str, str]:
    raw = path.read_text(encoding="utf-8")
    env: dict[str, str] = {}
    for raw_line in raw.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if key in env:
            raise AssertionError(f"Duplicate key in {path.name}: {key}")
        env[key] = value
    return env


def test_env_example_has_required_keys():
    env = _parse_env_file(Path(__file__).parent.parent / ".env.example")
    required = {
        "REDIS_HOST",
        "REDIS_PORT",
        "REDIS_PASSWORD",
        "LLM_MODEL",
        "LLM_BASE_URL",
        "PINATA_JWT",
        "IPFS_GATEWAY",
        "SEPOLIA_RPC",
        "CONTRACT_ADDRESS",
        "AGENT_KEY",
    }
    missing = sorted(required - set(env.keys()))
    assert not missing, f"Missing required keys in .env.example: {missing}"


def test_env_example_has_sane_defaults():
    env = _parse_env_file(Path(__file__).parent.parent / ".env.example")
    must_be_non_empty = {
        "REDIS_HOST",
        "REDIS_PORT",
        "REDIS_PASSWORD",
        "LLM_MODEL",
        "LLM_BASE_URL",
        "IPFS_GATEWAY",
    }
    empty = sorted([k for k in must_be_non_empty if not env.get(k, "").strip()])
    assert not empty, f"These keys must not be empty in .env.example: {empty}"

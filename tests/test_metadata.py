"""
Tests for BROskiPets dNFT metadata engine.
Runs without Redis, Ollama, or Pinata — pure unit tests.
"""
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from metadata import EEPMetadata, EVOLUTION_LEVELS, RARITY_TIERS, upload_to_ipfs


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def spider():
    return EEPMetadata(
        pet_id="spider_001",
        name="SpiderEep",
        species="Spider",
        rarity="Legendary",
        token_id=1,
    )

@pytest.fixture
def base_state():
    return {
        "xp": 750,
        "happiness": 95,
        "hunger": 20,
        "energy": 80,
        "last_interaction": "2026-04-03T12:00:00",
    }


# ── RARITY_TIERS ─────────────────────────────────────────────────────────────

def test_rarity_tiers_has_all_five_tiers():
    assert set(RARITY_TIERS.keys()) == {"Common", "Uncommon", "Rare", "Legendary", "Quantum"}

def test_rarity_chances_sum_to_one():
    total = sum(t["chance"] for t in RARITY_TIERS.values())
    assert abs(total - 1.0) < 1e-9

def test_quantum_is_rarest():
    assert RARITY_TIERS["Quantum"]["chance"] == 0.01

def test_quantum_has_highest_multiplier():
    multipliers = [t["power_multiplier"] for t in RARITY_TIERS.values()]
    assert RARITY_TIERS["Quantum"]["power_multiplier"] == max(multipliers)


# ── calculate_level ───────────────────────────────────────────────────────────

def test_level_1_at_zero_xp(spider):
    result = spider.calculate_level(0)
    assert result["level"] == 1
    assert result["level_name"] == "Baby"

def test_level_2_at_100_xp(spider):
    result = spider.calculate_level(100)
    assert result["level"] == 2
    assert result["level_name"] == "Young"

def test_level_3_at_500_xp(spider):
    result = spider.calculate_level(500)
    assert result["level"] == 3
    assert result["level_name"] == "Trained"

def test_level_6_at_50000_xp(spider):
    result = spider.calculate_level(50000)
    assert result["level"] == 6
    assert result["level_name"] == "Quantum"

def test_progress_percent_is_capped_at_100(spider):
    result = spider.calculate_level(999999)
    assert result["progress_percent"] == 100

def test_xp_in_result_matches_input(spider):
    result = spider.calculate_level(750)
    assert result["xp"] == 750

@pytest.mark.parametrize("xp,expected_level", [
    (0, 1), (99, 1), (100, 2), (499, 2),
    (500, 3), (1999, 3), (2000, 4), (9999, 4),
    (10000, 5), (49999, 5), (50000, 6),
])
def test_level_thresholds(spider, xp, expected_level):
    assert spider.calculate_level(xp)["level"] == expected_level


# ── generate_metadata ─────────────────────────────────────────────────────────

def test_metadata_has_required_eip721_fields(spider, base_state):
    meta = spider.generate_metadata(base_state)
    for field in ("name", "description", "image", "external_url", "attributes"):
        assert field in meta, f"Missing EIP-721 field: {field}"

def test_metadata_name_includes_token_id(spider, base_state):
    meta = spider.generate_metadata(base_state)
    assert "#1" in meta["name"]

def test_metadata_image_is_ipfs_url(spider, base_state):
    meta = spider.generate_metadata(base_state)
    assert meta["image"].startswith("ipfs://")

def test_metadata_image_uses_provided_cid(spider, base_state):
    meta = spider.generate_metadata(base_state, image_cid="QmTestCID123")
    assert meta["image"] == "ipfs://QmTestCID123"

def test_metadata_image_falls_back_to_placeholder(spider, base_state):
    meta = spider.generate_metadata(base_state, image_cid=None)
    assert "EEPVengers" in meta["image"]

def test_metadata_attributes_include_rarity(spider, base_state):
    meta = spider.generate_metadata(base_state)
    rarities = [a["value"] for a in meta["attributes"] if a["trait_type"] == "Rarity"]
    assert rarities == ["Legendary"]

def test_metadata_power_multiplier_matches_rarity(spider, base_state):
    meta = spider.generate_metadata(base_state)
    mults = [a["value"] for a in meta["attributes"] if a["trait_type"] == "Power Multiplier"]
    assert mults == [5.0]  # Legendary = 5x

def test_metadata_can_evolve_flag(spider):
    # can_evolve is True only at Quantum level (xp >= 50000, progress forced to 100%)
    # because calculate_level advances the level as soon as XP hits the threshold —
    # so next_xp always refers to the *next* tier, keeping progress < 100 until max.
    state = {"xp": 50000, "happiness": 80, "hunger": 30, "energy": 70, "last_interaction": "2026-04-03T12:00:00"}
    meta = spider.generate_metadata(state)
    assert meta["properties"]["can_evolve"] is True

def test_metadata_cannot_evolve_mid_level(spider, base_state):
    # XP 750 is partway through Trained (500-2000)
    meta = spider.generate_metadata(base_state)
    assert meta["properties"]["can_evolve"] is False

def test_metadata_is_json_serialisable(spider, base_state):
    meta = spider.generate_metadata(base_state)
    dumped = json.dumps(meta)
    assert isinstance(dumped, str)


# ── _hash_state ───────────────────────────────────────────────────────────────

def test_hash_is_deterministic(spider, base_state):
    h1 = spider._hash_state(base_state)
    h2 = spider._hash_state(base_state)
    assert h1 == h2

def test_hash_changes_with_state(spider, base_state):
    h1 = spider._hash_state(base_state)
    changed = {**base_state, "xp": 9999}
    h2 = spider._hash_state(changed)
    assert h1 != h2

def test_hash_is_16_chars(spider, base_state):
    h = spider._hash_state(base_state)
    assert len(h) == 16

def test_hash_is_hex(spider, base_state):
    h = spider._hash_state(base_state)
    int(h, 16)  # raises if not valid hex


# ── upload_to_ipfs (no JWT → graceful error) ─────────────────────────────────

def test_upload_raises_without_jwt(monkeypatch):
    monkeypatch.setenv("PINATA_JWT", "")
    with pytest.raises(EnvironmentError, match="PINATA_JWT"):
        upload_to_ipfs(b"test", "test.json")

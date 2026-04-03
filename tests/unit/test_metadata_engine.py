#!/usr/bin/env python3
"""
Unit tests — EEPMetadata engine
Covers: level calc, boundary XP, hash integrity, token_id guard, rarity validation.
"""

import pytest
from src.metadata.engine import EEPMetadata


@pytest.fixture
def spider_eep():
    return EEPMetadata(
        pet_id="spider_001",
        name="SpiderEep",
        species="Spider",
        rarity="Legendary",
        token_id=1,
    )


class TestCalculateLevel:
    def test_baby_at_zero_xp(self, spider_eep):
        result = spider_eep.calculate_level(0)
        assert result["level"] == 1
        assert result["level_name"] == "Baby"

    def test_young_at_100_xp(self, spider_eep):
        result = spider_eep.calculate_level(100)
        assert result["level"] == 2
        assert result["level_name"] == "Young"

    def test_boundary_99_xp_still_baby(self, spider_eep):
        result = spider_eep.calculate_level(99)
        assert result["level"] == 1

    def test_legendary_at_10000_xp(self, spider_eep):
        result = spider_eep.calculate_level(10000)
        assert result["level"] == 5
        assert result["level_name"] == "Legendary"

    def test_quantum_at_50000_xp(self, spider_eep):
        result = spider_eep.calculate_level(50000)
        assert result["level"] == 6
        assert result["level_name"] == "Quantum"

    def test_negative_xp_clamped_to_zero(self, spider_eep):
        result = spider_eep.calculate_level(-999)
        assert result["level"] == 1
        assert result["xp"] == 0

    def test_progress_percent_never_exceeds_100(self, spider_eep):
        result = spider_eep.calculate_level(999999)
        assert result["progress_percent"] <= 100


class TestGenerateMetadata:
    def test_generates_valid_eip721(self, spider_eep):
        state = {"xp": 750, "happiness": 95, "hunger": 20, "energy": 80,
                 "last_interaction": "2026-04-03T00:00:00"}
        meta = spider_eep.generate_metadata(state)
        assert meta["name"] == "SpiderEep #1"
        assert "attributes" in meta
        assert "ipfs://" in meta["image"]

    def test_raises_without_token_id(self):
        eep = EEPMetadata(pet_id="x", name="X", species="X", rarity="Common", token_id=None)
        with pytest.raises(ValueError, match="token_id must be set"):
            eep.generate_metadata({"xp": 0})

    def test_metadata_hash_is_full_64_chars(self, spider_eep):
        state = {"xp": 100, "happiness": 80}
        meta = spider_eep.generate_metadata(state)
        assert len(meta["properties"]["metadata_hash"]) == 64

    def test_happiness_clamped_to_100(self, spider_eep):
        state = {"xp": 0, "happiness": 9999}
        meta = spider_eep.generate_metadata(state)
        happiness_attr = next(a for a in meta["attributes"] if a["trait_type"] == "Happiness")
        assert happiness_attr["value"] <= 100


class TestRarityValidation:
    def test_invalid_rarity_raises(self):
        with pytest.raises(ValueError, match="Invalid rarity"):
            EEPMetadata(pet_id="x", name="X", species="X", rarity="SuperMegaRare")

    def test_valid_rarities_all_pass(self):
        for rarity in ["Common", "Uncommon", "Rare", "Legendary", "Quantum"]:
            eep = EEPMetadata(pet_id="x", name="X", species="X", rarity=rarity, token_id=1)
            assert eep.rarity == rarity


class TestHashIntegrity:
    def test_same_state_same_hash(self, spider_eep):
        state = {"xp": 100, "happiness": 80, "hunger": 30}
        h1 = spider_eep._hash_state(state)
        h2 = spider_eep._hash_state(state)
        assert h1 == h2

    def test_different_state_different_hash(self, spider_eep):
        h1 = spider_eep._hash_state({"xp": 100})
        h2 = spider_eep._hash_state({"xp": 101})
        assert h1 != h2

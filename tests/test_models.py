"""Tests for data models."""

import pytest
from pydantic import ValidationError

from pypoolchem.models.pool import Pool, PoolSurface, PoolType
from pypoolchem.models.targets import (
    ParameterRange,
    get_target_ranges,
)
from pypoolchem.models.water import WaterChemistry


class TestWaterChemistry:
    """Tests for WaterChemistry model."""

    def test_create_basic(self):
        """Test creating basic water chemistry."""
        water = WaterChemistry(
            ph=7.5,
            temperature_f=84,
            calcium_hardness=300,
            total_alkalinity=80,
        )
        assert water.ph == 7.5
        assert water.temperature_f == 84

    def test_defaults(self):
        """Test default values."""
        water = WaterChemistry(
            ph=7.5,
            temperature_f=84,
            calcium_hardness=300,
            total_alkalinity=80,
        )
        assert water.free_chlorine == 0
        assert water.cyanuric_acid == 0
        assert water.salt == 0
        assert water.borates == 0
        assert water.tds == 1000

    def test_total_chlorine_property(self):
        """Test total chlorine calculation."""
        water = WaterChemistry(
            ph=7.5,
            temperature_f=84,
            calcium_hardness=300,
            total_alkalinity=80,
            free_chlorine=3.0,
            combined_chlorine=0.5,
        )
        assert water.total_chlorine == 3.5

    def test_temperature_celsius_property(self):
        """Test temperature conversion property."""
        water = WaterChemistry(
            ph=7.5,
            temperature_f=77,  # 25°C
            calcium_hardness=300,
            total_alkalinity=80,
        )
        assert abs(water.temperature_c - 25) < 0.1

    def test_ph_validation(self):
        """Test pH range validation."""
        with pytest.raises(ValidationError):
            WaterChemistry(
                ph=15,  # Invalid
                temperature_f=84,
                calcium_hardness=300,
                total_alkalinity=80,
            )

    def test_frozen_model(self):
        """Test that model is immutable."""
        water = WaterChemistry(
            ph=7.5,
            temperature_f=84,
            calcium_hardness=300,
            total_alkalinity=80,
        )
        with pytest.raises(ValidationError):
            water.ph = 7.6


class TestPool:
    """Tests for Pool model."""

    def test_create_pool(self):
        """Test creating a pool."""
        pool = Pool(
            name="Backyard Pool",
            volume_gallons=15000,
            pool_type=PoolType.SWG,
            surface=PoolSurface.PLASTER,
        )
        assert pool.name == "Backyard Pool"
        assert pool.volume_gallons == 15000
        assert pool.pool_type == PoolType.SWG

    def test_volume_liters_property(self):
        """Test volume conversion property."""
        pool = Pool(volume_gallons=1000)
        assert abs(pool.volume_liters - 3785.41) < 1

    def test_defaults(self):
        """Test default values."""
        pool = Pool(volume_gallons=15000)
        assert pool.pool_type == PoolType.TRADITIONAL
        assert pool.surface == PoolSurface.PLASTER
        assert pool.has_heater is False
        assert pool.has_swg is False


class TestParameterRange:
    """Tests for ParameterRange model."""

    def test_is_in_range(self):
        """Test range checking."""
        ph_range = ParameterRange(minimum=7.2, target=7.5, maximum=7.8)
        assert ph_range.is_in_range(7.5) is True
        assert ph_range.is_in_range(7.0) is False
        assert ph_range.is_in_range(8.0) is False

    def test_is_low(self):
        """Test low value detection."""
        ph_range = ParameterRange(minimum=7.2, target=7.5, maximum=7.8)
        assert ph_range.is_low(7.0) is True
        assert ph_range.is_low(7.5) is False

    def test_is_high(self):
        """Test high value detection."""
        ph_range = ParameterRange(minimum=7.2, target=7.5, maximum=7.8)
        assert ph_range.is_high(8.0) is True
        assert ph_range.is_high(7.5) is False


class TestTargetRanges:
    """Tests for target range presets."""

    def test_traditional_pool_targets(self):
        """Test traditional pool targets."""
        targets = get_target_ranges(PoolType.TRADITIONAL)
        assert targets.ph.target == 7.5
        assert targets.cyanuric_acid.target == 50

    def test_swg_pool_targets(self):
        """Test SWG pool targets."""
        targets = get_target_ranges(PoolType.SWG)
        assert targets.ph.target == 7.6
        assert targets.salt is not None
        assert targets.salt.target == 3200

    def test_spa_targets(self):
        """Test spa targets."""
        targets = get_target_ranges(PoolType.SPA)
        assert targets.cyanuric_acid.maximum == 40  # Lower for spas

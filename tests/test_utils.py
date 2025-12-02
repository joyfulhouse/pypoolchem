"""Tests for utility functions."""

from pypoolchem.utils.conversions import (
    celsius_to_fahrenheit,
    fahrenheit_to_celsius,
    fl_oz_to_ml,
    gallons_to_liters,
    grams_to_oz,
    lbs_to_oz,
    liters_to_gallons,
    ml_to_fl_oz,
    oz_to_grams,
    oz_to_lbs,
)
from pypoolchem.utils.volume import (
    PoolShape,
    calculate_pool_volume,
    estimate_volume_from_dimensions,
)


class TestTemperatureConversions:
    """Tests for temperature conversions."""

    def test_fahrenheit_to_celsius(self):
        """Test F to C conversion."""
        assert abs(fahrenheit_to_celsius(32) - 0) < 0.01
        assert abs(fahrenheit_to_celsius(212) - 100) < 0.01
        assert abs(fahrenheit_to_celsius(77) - 25) < 0.01

    def test_celsius_to_fahrenheit(self):
        """Test C to F conversion."""
        assert abs(celsius_to_fahrenheit(0) - 32) < 0.01
        assert abs(celsius_to_fahrenheit(100) - 212) < 0.01
        assert abs(celsius_to_fahrenheit(25) - 77) < 0.01

    def test_roundtrip(self):
        """Test roundtrip conversion."""
        original = 84
        converted = celsius_to_fahrenheit(fahrenheit_to_celsius(original))
        assert abs(converted - original) < 0.01


class TestVolumeConversions:
    """Tests for volume conversions."""

    def test_gallons_to_liters(self):
        """Test gallons to liters."""
        assert abs(gallons_to_liters(1) - 3.78541) < 0.001

    def test_liters_to_gallons(self):
        """Test liters to gallons."""
        assert abs(liters_to_gallons(3.78541) - 1) < 0.001

    def test_roundtrip(self):
        """Test roundtrip conversion."""
        original = 15000
        converted = liters_to_gallons(gallons_to_liters(original))
        assert abs(converted - original) < 0.01


class TestWeightConversions:
    """Tests for weight conversions."""

    def test_oz_to_grams(self):
        """Test oz to grams."""
        assert abs(oz_to_grams(1) - 28.3495) < 0.001

    def test_grams_to_oz(self):
        """Test grams to oz."""
        assert abs(grams_to_oz(28.3495) - 1) < 0.001

    def test_oz_to_lbs(self):
        """Test oz to lbs."""
        assert oz_to_lbs(16) == 1.0

    def test_lbs_to_oz(self):
        """Test lbs to oz."""
        assert lbs_to_oz(1) == 16.0


class TestFluidConversions:
    """Tests for fluid volume conversions."""

    def test_fl_oz_to_ml(self):
        """Test fl oz to ml."""
        assert abs(fl_oz_to_ml(1) - 29.5735) < 0.001

    def test_ml_to_fl_oz(self):
        """Test ml to fl oz."""
        assert abs(ml_to_fl_oz(29.5735) - 1) < 0.001


class TestPoolVolume:
    """Tests for pool volume calculations."""

    def test_rectangular_pool(self):
        """Test rectangular pool volume."""
        volume = calculate_pool_volume(
            PoolShape.RECTANGULAR,
            length_ft=30,
            width_ft=15,
            avg_depth_ft=5,
        )
        # 30 * 15 * 5 * 7.48052 ~ 16831 gallons
        assert abs(volume - 16831) < 15

    def test_round_pool(self):
        """Test round pool volume."""
        volume = calculate_pool_volume(
            PoolShape.ROUND,
            length_ft=18,  # diameter
            width_ft=18,  # ignored for round
            avg_depth_ft=4,
        )
        # 18 * 18 * 4 * 7.48052 ~ 9695 gallons
        assert abs(volume - 9695) < 15

    def test_oval_pool(self):
        """Test oval pool volume."""
        volume = calculate_pool_volume(
            PoolShape.OVAL,
            length_ft=30,
            width_ft=15,
            avg_depth_ft=5,
        )
        # Oval is smaller than rectangular
        rect_volume = calculate_pool_volume(PoolShape.RECTANGULAR, 30, 15, 5)
        assert volume < rect_volume

    def test_kidney_pool(self):
        """Test kidney pool volume (75% of rectangular)."""
        volume = calculate_pool_volume(
            PoolShape.KIDNEY,
            length_ft=30,
            width_ft=15,
            avg_depth_ft=5,
        )
        rect_volume = calculate_pool_volume(PoolShape.RECTANGULAR, 30, 15, 5)
        assert abs(volume - rect_volume * 0.75) < 1

    def test_variable_depth(self):
        """Test with shallow and deep ends."""
        volume = calculate_pool_volume(
            PoolShape.RECTANGULAR,
            length_ft=30,
            width_ft=15,
            avg_depth_ft=0,  # Will be calculated
            shallow_depth_ft=3,
            deep_depth_ft=8,
        )
        # Average depth = (3 + 8) / 2 = 5.5
        expected = 30 * 15 * 5.5 * 7.48052
        assert abs(volume - expected) < 1

    def test_estimate_convenience_function(self):
        """Test the convenience function."""
        volume = estimate_volume_from_dimensions(30, 15, 5)
        expected = 30 * 15 * 5 * 7.48052
        assert abs(volume - expected) < 1

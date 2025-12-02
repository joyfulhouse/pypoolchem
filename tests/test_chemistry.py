"""Tests for chemistry calculations (CSI, LSI, factors)."""

import pytest

from pypoolchem.chemistry.csi import calculate_csi, interpret_csi
from pypoolchem.chemistry.factors import (
    calculate_carbonate_alkalinity,
    calculate_ionic_strength,
    calculate_temperature_factor,
)
from pypoolchem.chemistry.fc_cya import (
    calculate_min_fc,
    calculate_mustard_algae_shock_fc,
    calculate_shock_fc,
    calculate_target_fc,
    is_fc_adequate,
)
from pypoolchem.chemistry.lsi import calculate_lsi, interpret_lsi
from pypoolchem.exceptions import CalculationError
from pypoolchem.models.water import WaterChemistry


class TestCarbonatAlkalinity:
    """Tests for carbonate alkalinity calculation."""

    def test_no_cya_no_borates(self):
        """With no CYA or borates, carbonate alk equals total alk."""
        result = calculate_carbonate_alkalinity(100, 0, 7.5, 0)
        assert result == 100

    def test_cya_correction(self):
        """CYA reduces carbonate alkalinity."""
        result = calculate_carbonate_alkalinity(80, 50, 7.5)
        # CYA correction at pH 7.5 is approximately 0.38772 * 50 / (1 + 10^(6.83-7.5))
        # = 19.386 / (1 + 10^(-0.67)) = 19.386 / (1 + 0.214) = 15.97
        assert 60 < result < 80

    def test_borate_correction(self):
        """Borates reduce carbonate alkalinity."""
        result_no_borate = calculate_carbonate_alkalinity(100, 0, 7.5, 0)
        result_with_borate = calculate_carbonate_alkalinity(100, 0, 7.5, 50)
        assert result_with_borate < result_no_borate

    def test_minimum_zero(self):
        """Carbonate alkalinity cannot go negative."""
        # Very high CYA should not result in negative
        result = calculate_carbonate_alkalinity(20, 200, 7.5, 0)
        assert result >= 0


class TestIonicStrength:
    """Tests for ionic strength calculation."""

    def test_basic_calculation(self):
        """Test basic ionic strength calculation."""
        result = calculate_ionic_strength(300, 80, 0)
        assert result > 0

    def test_salt_effect(self):
        """Salt increases ionic strength."""
        result_no_salt = calculate_ionic_strength(300, 80, 0)
        result_with_salt = calculate_ionic_strength(300, 80, 3200)
        assert result_with_salt > result_no_salt

    def test_excess_nacl(self):
        """Salt bound to calcium is not counted, but CH adds to ionic strength."""
        # Higher calcium binds more NaCl, but also contributes 1.5*CH to ionic
        # So higher CH still means higher overall ionic strength
        result_low_ca = calculate_ionic_strength(100, 80, 3200)
        result_high_ca = calculate_ionic_strength(400, 80, 3200)
        # Higher calcium means higher ionic strength due to 1.5*CH contribution
        assert result_high_ca > result_low_ca


class TestTemperatureFactor:
    """Tests for temperature factor calculation."""

    def test_known_values(self):
        """Test known temperature factor values from table."""
        assert calculate_temperature_factor(32) == 0.0
        assert calculate_temperature_factor(84) == 0.7

    def test_interpolation(self):
        """Test interpolation between table values."""
        result = calculate_temperature_factor(80)
        # Should be between 0.6 (76°F) and 0.7 (84°F)
        assert 0.6 < result < 0.7

    def test_extremes(self):
        """Test extreme temperatures."""
        assert calculate_temperature_factor(20) == 0.0  # Below minimum
        assert calculate_temperature_factor(120) == 0.9  # Above maximum


class TestCSI:
    """Tests for Calcium Saturation Index calculation."""

    def test_balanced_water(self):
        """Test typical balanced pool water."""
        water = WaterChemistry(
            ph=7.5,
            temperature_f=84,
            free_chlorine=3.0,
            calcium_hardness=300,
            total_alkalinity=80,
            cyanuric_acid=50,
        )
        csi = calculate_csi(water)
        # Balanced water should have CSI close to 0
        assert -0.5 < csi < 0.5

    def test_with_individual_params(self):
        """Test CSI with individual parameters."""
        csi = calculate_csi(
            ph=7.5,
            temperature_f=84,
            calcium_hardness=300,
            total_alkalinity=80,
            cyanuric_acid=50,
        )
        assert -0.5 < csi < 0.5

    def test_low_calcium_corrosive(self):
        """Low calcium water should be corrosive (negative CSI)."""
        csi = calculate_csi(
            ph=7.2,
            temperature_f=84,
            calcium_hardness=100,
            total_alkalinity=60,
        )
        assert csi < 0

    def test_high_calcium_scaling(self):
        """High calcium water should be scale-forming (positive CSI)."""
        csi = calculate_csi(
            ph=8.0,
            temperature_f=100,
            calcium_hardness=500,
            total_alkalinity=150,
        )
        assert csi > 0

    def test_missing_params_raises_error(self):
        """Missing required params should raise error."""
        with pytest.raises(CalculationError):
            calculate_csi(ph=7.5)

    def test_zero_calcium_raises_error(self):
        """Zero calcium should raise error."""
        with pytest.raises(CalculationError):
            calculate_csi(
                ph=7.5,
                temperature_f=84,
                calcium_hardness=0,
                total_alkalinity=80,
            )


class TestLSI:
    """Tests for Langelier Saturation Index calculation."""

    def test_balanced_water(self):
        """Test typical balanced pool water."""
        water = WaterChemistry(
            ph=7.5,
            temperature_f=84,
            free_chlorine=3.0,
            calcium_hardness=300,
            total_alkalinity=80,
            cyanuric_acid=30,
        )
        lsi = calculate_lsi(water)
        # Balanced water should have LSI close to 0
        assert -0.5 < lsi < 0.5

    def test_with_individual_params(self):
        """Test LSI with individual parameters."""
        lsi = calculate_lsi(
            ph=7.5,
            temperature_f=84,
            calcium_hardness=300,
            total_alkalinity=100,
        )
        # LSI with higher alkalinity (100) will be more positive (scale forming)
        assert -0.6 < lsi < 0.7


class TestFCCYA:
    """Tests for FC/CYA relationship calculations."""

    def test_min_fc_non_swg(self):
        """Test minimum FC for non-SWG pools."""
        # At CYA 50, min FC = max(1, floor(50 * 0.075 + 0.7)) = 4
        assert calculate_min_fc(50, is_swg=False) == 4

    def test_min_fc_swg(self):
        """Test minimum FC for SWG pools."""
        # At CYA 70, min FC = max(1, floor(70 * 0.045 + 0.7)) = 3
        assert calculate_min_fc(70, is_swg=True) == 3

    def test_target_fc_non_swg(self):
        """Test target FC range for non-SWG pools."""
        low, high = calculate_target_fc(50, is_swg=False)
        assert low >= 3
        assert high >= low

    def test_shock_fc(self):
        """Test shock FC level."""
        # At CYA 50, shock = max(10, floor(50 * 0.393 + 0.5)) = 20
        assert calculate_shock_fc(50) == 20

    def test_mustard_algae_shock(self):
        """Test mustard algae shock FC level."""
        # At CYA 50, mustard = max(12, floor(50/2 + 4.5)) = 29
        assert calculate_mustard_algae_shock_fc(50) == 29

    def test_fc_adequate(self):
        """Test FC adequacy check."""
        assert is_fc_adequate(5, 50, is_swg=False) is True
        assert is_fc_adequate(2, 50, is_swg=False) is False


class TestInterpretations:
    """Tests for CSI/LSI interpretation functions."""

    def test_interpret_csi(self):
        """Test CSI interpretation."""
        assert "Balanced" in interpret_csi(0.0)
        assert "Corrosive" in interpret_csi(-0.8)
        assert "Scale" in interpret_csi(0.8)

    def test_interpret_lsi(self):
        """Test LSI interpretation."""
        assert "Ideal" in interpret_lsi(0.15)
        assert "Aggressive" in interpret_lsi(-0.5)
        assert "Over-saturated" in interpret_lsi(0.5)

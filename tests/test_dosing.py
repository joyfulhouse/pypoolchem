"""Tests for chemical dosing calculations."""

from pypoolchem.dosing.calculator import (
    calculate_alkalinity_dose,
    calculate_calcium_dose,
    calculate_chlorine_dose,
    calculate_cya_dose,
    calculate_ph_dose,
    calculate_salt_dose,
    calculate_water_replacement,
)
from pypoolchem.dosing.chemicals import ChemicalType, get_chemical


class TestChlorineDosing:
    """Tests for chlorine dosing calculations."""

    def test_bleach_dose(self):
        """Test bleach dosing calculation."""
        result = calculate_chlorine_dose(
            current_fc=2.0,
            target_fc=5.0,
            pool_gallons=15000,
            chemical_type=ChemicalType.BLEACH_12_5,
        )
        assert result.amount > 0
        assert result.unit == "fl_oz"

    def test_trichlor_dose(self):
        """Test trichlor dosing calculation."""
        result = calculate_chlorine_dose(
            current_fc=2.0,
            target_fc=5.0,
            pool_gallons=15000,
            chemical_type=ChemicalType.TRICHLOR,
        )
        assert result.amount > 0
        assert result.unit == "oz"

    def test_no_dose_needed(self):
        """Test when FC is already at target."""
        result = calculate_chlorine_dose(
            current_fc=5.0,
            target_fc=5.0,
            pool_gallons=15000,
        )
        assert result.amount == 0

    def test_larger_pool_needs_more(self):
        """Larger pools need more chemical."""
        result_small = calculate_chlorine_dose(current_fc=2.0, target_fc=5.0, pool_gallons=10000)
        result_large = calculate_chlorine_dose(current_fc=2.0, target_fc=5.0, pool_gallons=20000)
        assert result_large.amount > result_small.amount


class TestPHDosing:
    """Tests for pH dosing calculations."""

    def test_lower_ph_with_acid(self):
        """Test lowering pH with muriatic acid."""
        result = calculate_ph_dose(
            current_ph=7.8,
            target_ph=7.5,
            pool_gallons=15000,
            total_alkalinity=80,
            temperature_f=84,
        )
        assert result.amount > 0
        assert "acid" in result.chemical.name.lower()

    def test_raise_ph_with_soda_ash(self):
        """Test raising pH with soda ash."""
        result = calculate_ph_dose(
            current_ph=7.2,
            target_ph=7.5,
            pool_gallons=15000,
            total_alkalinity=80,
            temperature_f=84,
        )
        assert result.amount > 0
        assert "soda" in result.chemical.name.lower()

    def test_ph_at_target(self):
        """Test when pH is at target."""
        result = calculate_ph_dose(
            current_ph=7.5,
            target_ph=7.5,
            pool_gallons=15000,
            total_alkalinity=80,
        )
        assert result.amount == 0

    def test_higher_ta_needs_more_acid(self):
        """Higher TA requires more acid to lower pH."""
        result_low_ta = calculate_ph_dose(
            current_ph=7.8,
            target_ph=7.5,
            pool_gallons=15000,
            total_alkalinity=60,
        )
        result_high_ta = calculate_ph_dose(
            current_ph=7.8,
            target_ph=7.5,
            pool_gallons=15000,
            total_alkalinity=120,
        )
        assert result_high_ta.amount > result_low_ta.amount


class TestAlkalinityDosing:
    """Tests for alkalinity dosing calculations."""

    def test_raise_ta(self):
        """Test raising TA with baking soda."""
        result = calculate_alkalinity_dose(
            current_ta=60,
            target_ta=80,
            pool_gallons=15000,
        )
        assert result.amount > 0
        assert "baking soda" in result.chemical.name.lower()

    def test_ta_at_target(self):
        """Test when TA is at target."""
        result = calculate_alkalinity_dose(
            current_ta=80,
            target_ta=80,
            pool_gallons=15000,
        )
        assert result.amount == 0


class TestCalciumDosing:
    """Tests for calcium hardness dosing calculations."""

    def test_raise_ch(self):
        """Test raising CH with calcium chloride."""
        result = calculate_calcium_dose(
            current_ch=200,
            target_ch=300,
            pool_gallons=15000,
        )
        assert result.amount > 0
        assert "calcium" in result.chemical.name.lower()


class TestCYADosing:
    """Tests for CYA dosing calculations."""

    def test_raise_cya(self):
        """Test raising CYA with stabilizer."""
        result = calculate_cya_dose(
            current_cya=30,
            target_cya=50,
            pool_gallons=15000,
        )
        assert result.amount > 0


class TestSaltDosing:
    """Tests for salt dosing calculations."""

    def test_raise_salt(self):
        """Test raising salt level."""
        result = calculate_salt_dose(
            current_salt=2800,
            target_salt=3200,
            pool_gallons=15000,
        )
        assert result.amount > 0
        assert result.unit == "lbs"


class TestWaterReplacement:
    """Tests for water replacement calculations."""

    def test_cya_replacement(self):
        """Test CYA water replacement calculation."""
        # To go from 80 to 50 ppm, need to replace 37.5%
        percent = calculate_water_replacement(80, 50)
        assert 35 < percent < 40

    def test_ch_replacement_with_fill_water(self):
        """Test CH water replacement with fill water CH."""
        # Current 400, target 300, fill water 100
        percent = calculate_water_replacement(400, 300, fill_water_value=100)
        # (400-300) / (400-100) = 100/300 = 33.3%
        assert 30 < percent < 37

    def test_already_at_target(self):
        """Test when already at target."""
        percent = calculate_water_replacement(50, 50)
        assert percent == 0


class TestChemicalLookup:
    """Tests for chemical lookup."""

    def test_get_existing_chemical(self):
        """Test getting an existing chemical."""
        chemical = get_chemical(ChemicalType.TRICHLOR)
        assert chemical.name == "Trichlor (90%)"
        assert chemical.multiplier == 6854.95

    def test_chemical_has_secondary_effects(self):
        """Test that some chemicals have secondary effects."""
        trichlor = get_chemical(ChemicalType.TRICHLOR)
        assert "cyanuric_acid" in trichlor.secondary_effects
        assert "ph" in trichlor.secondary_effects

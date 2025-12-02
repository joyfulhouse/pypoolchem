"""Calcium Saturation Index (CSI) calculation.

CSI is the PoolMath/TroubleFreePool formula that improves upon traditional LSI
by accounting for ionic strength, cyanuric acid, and borate effects on alkalinity.

Formula:
    CSI = pH - 11.677 + log10(CH) + log10(CarbAlk)
          - (2.56 * sqrt(Ionic)) / (1 + 1.65 * sqrt(Ionic))
          - 1412.5 / (T_celsius + 273.15) + 4.7375

Where:
    CarbAlk = TA - CYA correction - Borate correction
    Ionic = ionic strength based on CH, TA, and Salt

CSI Interpretation:
    ≤ -0.6: Corrosive (aggressive water, will etch surfaces)
    -0.6 to -0.3: Slightly corrosive
    -0.3 to +0.3: Balanced (ideal)
    +0.3 to +0.6: Slightly scale-forming
    ≥ +0.6: Scale-forming
"""

import math

from pypoolchem.chemistry.constants import (
    CSI_FINAL_CONSTANT,
    CSI_IONIC_COEFFICIENT,
    CSI_IONIC_DENOMINATOR_COEFFICIENT,
    CSI_PH_CONSTANT,
    CSI_TEMP_NUMERATOR,
)
from pypoolchem.chemistry.factors import (
    calculate_carbonate_alkalinity,
    calculate_ionic_strength,
)
from pypoolchem.exceptions import CalculationError
from pypoolchem.models.water import WaterChemistry


def calculate_csi(
    water: WaterChemistry | None = None,
    *,
    ph: float | None = None,
    temperature_f: float | None = None,
    calcium_hardness: float | None = None,
    total_alkalinity: float | None = None,
    cyanuric_acid: float = 0,
    salt: float = 0,
    borates: float = 0,
) -> float:
    """Calculate the Calcium Saturation Index (CSI).

    CSI indicates whether water is corrosive (negative), balanced (zero),
    or scale-forming (positive). It accounts for cyanuric acid and borate
    effects on alkalinity, as well as ionic strength from salt.

    Can be called with a WaterChemistry object or individual parameters.

    Args:
        water: WaterChemistry object with all parameters.
        ph: Water pH (7.0-8.0 typical for pools).
        temperature_f: Water temperature in Fahrenheit.
        calcium_hardness: Calcium hardness in ppm as CaCO3.
        total_alkalinity: Total alkalinity in ppm as CaCO3.
        cyanuric_acid: Cyanuric acid in ppm (default 0).
        salt: Salt level in ppm (default 0).
        borates: Borate level in ppm (default 0).

    Returns:
        CSI value. Ideal range is -0.3 to +0.3.

    Raises:
        CalculationError: If required parameters are missing or invalid.

    Example:
        >>> water = WaterChemistry(
        ...     ph=7.5, temperature_f=84, calcium_hardness=300,
        ...     total_alkalinity=80, cyanuric_acid=50
        ... )
        >>> csi = calculate_csi(water)
        >>> print(f"CSI: {csi:.2f}")

        >>> # Or with individual parameters:
        >>> csi = calculate_csi(
        ...     ph=7.5, temperature_f=84, calcium_hardness=300,
        ...     total_alkalinity=80, cyanuric_acid=50
        ... )
    """
    # Extract values from WaterChemistry or use individual parameters
    if water is not None:
        ph = water.ph
        temperature_f = water.temperature_f
        calcium_hardness = water.calcium_hardness
        total_alkalinity = water.total_alkalinity
        cyanuric_acid = water.cyanuric_acid
        salt = water.salt
        borates = water.borates

    # Validate required parameters
    if ph is None:
        raise CalculationError("pH is required for CSI calculation")
    if temperature_f is None:
        raise CalculationError("Temperature is required for CSI calculation")
    if calcium_hardness is None:
        raise CalculationError("Calcium hardness is required for CSI calculation")
    if total_alkalinity is None:
        raise CalculationError("Total alkalinity is required for CSI calculation")

    # Validate ranges
    if calcium_hardness <= 0:
        raise CalculationError("Calcium hardness must be greater than 0")

    # Calculate carbonate alkalinity
    carbonate_alk = calculate_carbonate_alkalinity(total_alkalinity, cyanuric_acid, ph, borates)

    if carbonate_alk <= 0:
        raise CalculationError("Carbonate alkalinity is too low (CYA/Borate correction exceeds TA)")

    # Calculate ionic strength
    ionic = calculate_ionic_strength(calcium_hardness, total_alkalinity, salt)

    # Calculate ionic strength correction term
    sqrt_ionic = math.sqrt(ionic)
    ionic_correction = (CSI_IONIC_COEFFICIENT * sqrt_ionic) / (
        1 + CSI_IONIC_DENOMINATOR_COEFFICIENT * sqrt_ionic
    )

    # Calculate temperature correction term
    temp_celsius = (temperature_f - 32) * 5 / 9
    temp_correction = CSI_TEMP_NUMERATOR / (temp_celsius + 273.15)

    # Calculate CSI
    return (
        ph
        - CSI_PH_CONSTANT
        + math.log10(calcium_hardness)
        + math.log10(carbonate_alk)
        - ionic_correction
        - temp_correction
        + CSI_FINAL_CONSTANT
    )


def interpret_csi(csi: float) -> str:
    """Interpret a CSI value.

    Args:
        csi: The CSI value to interpret.

    Returns:
        Human-readable interpretation of the CSI value.

    Example:
        >>> interpret_csi(-0.15)
        'Balanced (ideal)'
    """
    if csi <= -0.6:
        return "Corrosive (aggressive water, will etch surfaces)"
    if csi <= -0.3:
        return "Slightly corrosive (may cause slow corrosion)"
    if csi <= 0.3:
        return "Balanced (ideal)"
    if csi <= 0.6:
        return "Slightly scale-forming (may form light scale)"
    return "Scale-forming (scale formation likely)"

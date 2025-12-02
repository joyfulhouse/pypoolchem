"""Langelier Saturation Index (LSI) calculation.

LSI is the traditional water balance formula used by Orenda and others.
It uses a simpler approach than CSI but is still widely used.

Formula:
    LSI = pH + TF + CF + AF - 12.1

Where:
    pH = measured pH value
    TF = Temperature Factor (from lookup table)
    CF = Calcium Factor = log10(CH as CaCO3)
    AF = Alkalinity Factor = log10(Carbonate Alkalinity)

LSI Interpretation:
    ≤ -0.31: Aggressive (corrosive water)
    -0.30 to -0.01: Acceptable (close to balanced)
    0.00 to +0.30: Ideal (perfectly balanced)
    ≥ +0.31: Over-saturated (scale-forming)
"""

import math

from pypoolchem.chemistry.constants import (
    LSI_CONSTANT,
    get_cya_correction_factor,
)
from pypoolchem.chemistry.factors import calculate_temperature_factor
from pypoolchem.exceptions import CalculationError
from pypoolchem.models.water import WaterChemistry


def calculate_lsi(
    water: WaterChemistry | None = None,
    *,
    ph: float | None = None,
    temperature_f: float | None = None,
    calcium_hardness: float | None = None,
    total_alkalinity: float | None = None,
    cyanuric_acid: float = 0,
    tds: float = 1000,  # noqa: ARG001 - Reserved for future TDS correction
) -> float:
    """Calculate the Langelier Saturation Index (LSI).

    LSI indicates whether water is corrosive (negative), balanced (zero),
    or scale-forming (positive). This is the traditional formula used by
    Orenda and many pool professionals.

    Can be called with a WaterChemistry object or individual parameters.

    Args:
        water: WaterChemistry object with all parameters.
        ph: Water pH (7.0-8.0 typical for pools).
        temperature_f: Water temperature in Fahrenheit.
        calcium_hardness: Calcium hardness in ppm as CaCO3.
        total_alkalinity: Total alkalinity in ppm as CaCO3.
        cyanuric_acid: Cyanuric acid in ppm (default 0, used for alkalinity correction).
        tds: Total dissolved solids in ppm (default 1000, currently not used).

    Returns:
        LSI value. Ideal range is -0.3 to +0.3.

    Raises:
        CalculationError: If required parameters are missing or invalid.

    Example:
        >>> water = WaterChemistry(
        ...     ph=7.5, temperature_f=84, calcium_hardness=300,
        ...     total_alkalinity=80, cyanuric_acid=50
        ... )
        >>> lsi = calculate_lsi(water)
        >>> print(f"LSI: {lsi:.2f}")

        >>> # Or with individual parameters:
        >>> lsi = calculate_lsi(
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

    # Validate required parameters
    if ph is None:
        raise CalculationError("pH is required for LSI calculation")
    if temperature_f is None:
        raise CalculationError("Temperature is required for LSI calculation")
    if calcium_hardness is None:
        raise CalculationError("Calcium hardness is required for LSI calculation")
    if total_alkalinity is None:
        raise CalculationError("Total alkalinity is required for LSI calculation")

    # Validate ranges
    if calcium_hardness <= 0:
        raise CalculationError("Calcium hardness must be greater than 0")

    # Calculate carbonate alkalinity using CYA correction
    # Orenda uses a simpler correction: TA - (CYA * correction_factor)
    cya_correction_factor = get_cya_correction_factor(ph)
    carbonate_alk = total_alkalinity - (cyanuric_acid * cya_correction_factor)

    if carbonate_alk <= 0:
        raise CalculationError("Carbonate alkalinity is too low (CYA correction exceeds TA)")

    # Calculate factors
    tf = calculate_temperature_factor(temperature_f)  # Temperature factor
    cf = math.log10(calcium_hardness)  # Calcium factor
    af = math.log10(carbonate_alk)  # Alkalinity factor

    # Calculate LSI
    return ph + tf + cf + af - LSI_CONSTANT


def interpret_lsi(lsi: float) -> str:
    """Interpret an LSI value using Orenda-style color coding.

    Args:
        lsi: The LSI value to interpret.

    Returns:
        Human-readable interpretation of the LSI value with color indicator.

    Example:
        >>> interpret_lsi(0.15)
        'Green - Ideal (perfectly balanced)'
    """
    if lsi <= -0.31:
        return "Red - Aggressive (corrosive, will etch surfaces)"
    if lsi < 0:
        return "Yellow - Acceptable (close to balanced)"
    if lsi <= 0.30:
        return "Green - Ideal (perfectly balanced)"
    return "Purple - Over-saturated (scale-forming)"

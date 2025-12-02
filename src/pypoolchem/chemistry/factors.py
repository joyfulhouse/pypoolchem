"""Factor calculations for water balance indices.

These functions calculate the intermediate factors used in LSI and CSI calculations.
"""

import math

from pypoolchem.chemistry.constants import (
    BORATE_COEFFICIENT,
    BORATE_PH_CONSTANT,
    CH_TO_NACL_RATIO,
    CYA_COEFFICIENT,
    CYA_PH_CONSTANT,
    IONIC_CH_COEFFICIENT,
    IONIC_DIVISOR,
    IONIC_NACL_DIVISOR,
    IONIC_TA_COEFFICIENT,
    interpolate_temperature_factor,
)


def calculate_carbonate_alkalinity(
    total_alkalinity: float,
    cyanuric_acid: float,
    ph: float,
    borates: float = 0,
) -> float:
    """Calculate carbonate alkalinity corrected for CYA and borates.

    Cyanuric acid and borates contribute to total alkalinity but not to
    the carbonate alkalinity that affects water balance.

    Formula:
        CarbAlk = TA - (0.38772 * CYA) / (1 + 10^(6.83 - pH))
                     - (4.63 * Borate) / (1 + 10^(9.11 - pH))

    Args:
        total_alkalinity: Total alkalinity in ppm as CaCO3.
        cyanuric_acid: Cyanuric acid in ppm.
        ph: Water pH level.
        borates: Borate level in ppm (default 0).

    Returns:
        Carbonate alkalinity in ppm as CaCO3.

    Example:
        >>> calculate_carbonate_alkalinity(80, 50, 7.5)
        73.77...
    """
    # CYA correction
    cya_correction = (CYA_COEFFICIENT * cyanuric_acid) / (1 + 10 ** (CYA_PH_CONSTANT - ph))

    # Borate correction
    borate_correction = 0.0
    if borates > 0:
        borate_correction = (BORATE_COEFFICIENT * borates) / (1 + 10 ** (BORATE_PH_CONSTANT - ph))

    carbonate_alk = total_alkalinity - cya_correction - borate_correction

    # Carbonate alkalinity cannot be negative
    return max(0.0, carbonate_alk)


def calculate_ionic_strength(
    calcium_hardness: float,
    total_alkalinity: float,
    salt: float = 0,
) -> float:
    """Calculate ionic strength for CSI calculation.

    Formula:
        extra_NaCl = max(0, Salt - 1.1678 * CH)
        Ionic = (1.5 * CH + TA) / 50045 + extra_NaCl / 58440

    Args:
        calcium_hardness: Calcium hardness in ppm as CaCO3.
        total_alkalinity: Total alkalinity in ppm as CaCO3.
        salt: Salt level in ppm (default 0).

    Returns:
        Ionic strength value (dimensionless).

    Example:
        >>> calculate_ionic_strength(300, 80, 3200)
        0.0545...
    """
    # Calculate excess NaCl (salt not bound to calcium)
    extra_nacl = max(0.0, salt - CH_TO_NACL_RATIO * calcium_hardness)

    # Calculate ionic strength
    return (
        IONIC_CH_COEFFICIENT * calcium_hardness + IONIC_TA_COEFFICIENT * total_alkalinity
    ) / IONIC_DIVISOR + extra_nacl / IONIC_NACL_DIVISOR


def calculate_temperature_factor(temperature_f: float) -> float:
    """Calculate temperature factor for LSI calculation.

    Uses a lookup table with linear interpolation between values.

    Args:
        temperature_f: Water temperature in Fahrenheit.

    Returns:
        Temperature factor (TF) for LSI calculation.

    Example:
        >>> calculate_temperature_factor(84)
        0.7
    """
    return interpolate_temperature_factor(temperature_f)


def calculate_calcium_factor(calcium_hardness: float) -> float:
    """Calculate calcium hardness factor for LSI calculation.

    Formula: CF = log10(CH as CaCO3)

    Args:
        calcium_hardness: Calcium hardness in ppm as CaCO3.

    Returns:
        Calcium factor (CF) for LSI calculation.

    Raises:
        ValueError: If calcium_hardness is <= 0.

    Example:
        >>> calculate_calcium_factor(300)
        2.477...
    """
    if calcium_hardness <= 0:
        raise ValueError("Calcium hardness must be greater than 0")
    return math.log10(calcium_hardness)


def calculate_alkalinity_factor(alkalinity: float) -> float:
    """Calculate alkalinity factor for LSI calculation.

    Formula: AF = log10(Alkalinity as CaCO3)

    Args:
        alkalinity: Alkalinity in ppm as CaCO3 (should be carbonate alkalinity).

    Returns:
        Alkalinity factor (AF) for LSI calculation.

    Raises:
        ValueError: If alkalinity is <= 0.

    Example:
        >>> calculate_alkalinity_factor(80)
        1.903...
    """
    if alkalinity <= 0:
        raise ValueError("Alkalinity must be greater than 0")
    return math.log10(alkalinity)

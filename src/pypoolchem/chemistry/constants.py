"""Chemical constants and conversion factors for pool chemistry calculations.

All formulas are derived from the TroubleFreePool PoolMath calculator
and validated against the Orenda LSI calculator.

References:
    - https://www.troublefreepool.com/calc.html
    - Wojtowicz, J.A. (2001). "The Carbonate System in Swimming Pool Water"
    - Langelier, W.F. (1936). "The Analytical Control of Anti-Corrosion Water Treatment"
"""

# CSI Formula Constants
# CSI = pH - 11.677 + log(CH) + log(CarbAlk) - ionic_correction - temp_correction + 4.7375  # noqa: ERA001
CSI_PH_CONSTANT = 11.677
CSI_FINAL_CONSTANT = 4.7375
CSI_TEMP_NUMERATOR = 1412.5  # 1412.5 / (T_celsius + 273.15)
CSI_IONIC_COEFFICIENT = 2.56
CSI_IONIC_DENOMINATOR_COEFFICIENT = 1.65

# LSI Formula Constants
# LSI = pH + TF + CF + AF - 12.1  # noqa: ERA001
LSI_CONSTANT = 12.1

# Carbonate Alkalinity Correction Constants
# CarbAlk = TA - (0.38772 * CYA) / (1 + 10^(6.83 - pH)) - (4.63 * Borate) / (1 + 10^(9.11 - pH))  # noqa: ERA001
CYA_COEFFICIENT = 0.38772
CYA_PH_CONSTANT = 6.83
BORATE_COEFFICIENT = 4.63
BORATE_PH_CONSTANT = 9.11

# Ionic Strength Constants
# Ionic = (1.5 * CH + TA) / 50045 + extra_NaCl / 58440  # noqa: ERA001
IONIC_CH_COEFFICIENT = 1.5
IONIC_TA_COEFFICIENT = 1.0
IONIC_DIVISOR = 50045
IONIC_NACL_DIVISOR = 58440
CH_TO_NACL_RATIO = 1.1678  # Salt - 1.1678 * CH = excess NaCl

# Temperature Factor Table for LSI (Orenda-style)
# Maps temperature (°F) to temperature factor
TEMPERATURE_FACTOR_TABLE: dict[int, float] = {
    32: 0.0,
    37: 0.1,
    46: 0.2,
    53: 0.3,
    60: 0.4,
    66: 0.5,
    76: 0.6,
    84: 0.7,
    94: 0.8,
    105: 0.9,
}

# pH-dependent CYA correction factors (simplified table for LSI)
# Used when calculating carbonate alkalinity for LSI
CYA_CORRECTION_TABLE: dict[float, float] = {
    7.0: 0.22,
    7.2: 0.27,
    7.4: 0.31,
    7.5: 0.33,
    7.6: 0.33,
    7.8: 0.35,
    8.0: 0.38,
}

# Unit Conversion Constants
GALLONS_TO_LITERS = 3.78541
LITERS_TO_GALLONS = 1 / GALLONS_TO_LITERS
CUBIC_FEET_TO_GALLONS = 7.48052
OZ_TO_GRAMS = 28.3495
GRAMS_TO_OZ = 1 / OZ_TO_GRAMS
OZ_TO_LBS = 0.0625
LBS_TO_OZ = 16
FL_OZ_TO_ML = 29.5735
IMPERIAL_GALLON_TO_US_GALLON = 1.20095


def interpolate_temperature_factor(temp_f: float) -> float:
    """Interpolate temperature factor from lookup table.

    Args:
        temp_f: Water temperature in Fahrenheit.

    Returns:
        Temperature factor for LSI calculation.

    Example:
        >>> interpolate_temperature_factor(80)
        0.65
    """
    temps = sorted(TEMPERATURE_FACTOR_TABLE.keys())

    if temp_f <= temps[0]:
        return TEMPERATURE_FACTOR_TABLE[temps[0]]
    if temp_f >= temps[-1]:
        return TEMPERATURE_FACTOR_TABLE[temps[-1]]

    # Find bracketing temperatures
    for i, t in enumerate(temps[:-1]):
        if t <= temp_f < temps[i + 1]:
            t1, t2 = t, temps[i + 1]
            f1, f2 = TEMPERATURE_FACTOR_TABLE[t1], TEMPERATURE_FACTOR_TABLE[t2]
            # Linear interpolation
            return f1 + (f2 - f1) * (temp_f - t1) / (t2 - t1)

    return TEMPERATURE_FACTOR_TABLE[temps[-1]]


def get_cya_correction_factor(ph: float) -> float:
    """Get CYA correction factor for a given pH.

    Uses linear interpolation between table values.

    Args:
        ph: Water pH value.

    Returns:
        CYA correction factor for carbonate alkalinity calculation.

    Example:
        >>> get_cya_correction_factor(7.5)
        0.33
    """
    ph_values = sorted(CYA_CORRECTION_TABLE.keys())

    if ph <= ph_values[0]:
        return CYA_CORRECTION_TABLE[ph_values[0]]
    if ph >= ph_values[-1]:
        return CYA_CORRECTION_TABLE[ph_values[-1]]

    # Find bracketing pH values
    for i, p in enumerate(ph_values[:-1]):
        if p <= ph < ph_values[i + 1]:
            p1, p2 = p, ph_values[i + 1]
            f1, f2 = CYA_CORRECTION_TABLE[p1], CYA_CORRECTION_TABLE[p2]
            # Linear interpolation
            return f1 + (f2 - f1) * (ph - p1) / (p2 - p1)

    return CYA_CORRECTION_TABLE[ph_values[-1]]

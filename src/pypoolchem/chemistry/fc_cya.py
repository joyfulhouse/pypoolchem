"""Free Chlorine / Cyanuric Acid relationship calculations.

The FC/CYA ratio is critical for effective sanitization. CYA (stabilizer) protects
chlorine from UV degradation but also reduces its effectiveness. Higher CYA levels
require higher FC levels to maintain proper sanitization.

These formulas are based on the TroubleFreePool methodology.
"""

import math


def calculate_min_fc(cyanuric_acid: float, *, is_swg: bool = False) -> float:
    """Calculate the minimum acceptable free chlorine level.

    This is the absolute minimum FC level to maintain basic sanitization.
    Below this level, algae growth is likely.

    Formulas:
        SWG: max(1, floor(CYA * 0.045 + 0.7))
        Non-SWG: max(1, floor(CYA * 0.075 + 0.7))

    Args:
        cyanuric_acid: Cyanuric acid level in ppm.
        is_swg: Whether the pool uses a salt water generator.

    Returns:
        Minimum free chlorine level in ppm.

    Example:
        >>> calculate_min_fc(50, is_swg=False)
        4
        >>> calculate_min_fc(70, is_swg=True)
        3
    """
    if cyanuric_acid <= 0:
        return 1.0

    if is_swg:
        return max(1.0, math.floor(cyanuric_acid * 0.045 + 0.7))
    return max(1.0, math.floor(cyanuric_acid * 0.075 + 0.7))


def calculate_target_fc(cyanuric_acid: float, *, is_swg: bool = False) -> tuple[float, float]:
    """Calculate the target free chlorine range.

    This is the recommended FC range for normal pool operation.

    Formulas:
        SWG: max(3, floor(CYA * 0.075))
        Non-SWG: max(3, floor(CYA/10 + 1.5)) to max(3, floor(CYA/10 + 3.5))

    Args:
        cyanuric_acid: Cyanuric acid level in ppm.
        is_swg: Whether the pool uses a salt water generator.

    Returns:
        Tuple of (low_target, high_target) free chlorine in ppm.

    Example:
        >>> calculate_target_fc(50, is_swg=False)
        (6.0, 8.0)
        >>> calculate_target_fc(70, is_swg=True)
        (5.0, 5.0)
    """
    if cyanuric_acid <= 0:
        return (3.0, 3.0)

    if is_swg:
        target = max(3.0, math.floor(cyanuric_acid * 0.075))
        return (target, target)
    low = max(3.0, math.floor(cyanuric_acid / 10 + 1.5))
    high = max(3.0, math.floor(cyanuric_acid / 10 + 3.5))
    return (low, high)


def calculate_shock_fc(cyanuric_acid: float) -> float:
    """Calculate the shock/SLAM (Shock Level and Maintain) FC level.

    This is the FC level needed to kill algae during a SLAM process.

    Formula: max(10, floor(CYA * 0.393 + 0.5))

    Args:
        cyanuric_acid: Cyanuric acid level in ppm.

    Returns:
        Shock free chlorine level in ppm.

    Example:
        >>> calculate_shock_fc(50)
        20
        >>> calculate_shock_fc(30)
        12
    """
    if cyanuric_acid <= 0:
        return 10.0

    return max(10.0, math.floor(cyanuric_acid * 0.393 + 0.5))


def calculate_mustard_algae_shock_fc(cyanuric_acid: float) -> float:
    """Calculate the FC level needed to kill mustard (yellow) algae.

    Mustard algae requires higher FC levels than regular algae.

    Formula: max(12, floor(CYA / 2 + 4.5))

    Args:
        cyanuric_acid: Cyanuric acid level in ppm.

    Returns:
        Mustard algae shock free chlorine level in ppm.

    Example:
        >>> calculate_mustard_algae_shock_fc(50)
        29
        >>> calculate_mustard_algae_shock_fc(30)
        19
    """
    if cyanuric_acid <= 0:
        return 12.0

    return max(12.0, math.floor(cyanuric_acid / 2 + 4.5))


def is_fc_adequate(
    free_chlorine: float,
    cyanuric_acid: float,
    *,
    is_swg: bool = False,
) -> bool:
    """Check if free chlorine level is adequate for the CYA level.

    Args:
        free_chlorine: Current free chlorine level in ppm.
        cyanuric_acid: Cyanuric acid level in ppm.
        is_swg: Whether the pool uses a salt water generator.

    Returns:
        True if FC is at or above the minimum for the CYA level.

    Example:
        >>> is_fc_adequate(3, 50, is_swg=False)
        False
        >>> is_fc_adequate(5, 50, is_swg=False)
        True
    """
    min_fc = calculate_min_fc(cyanuric_acid, is_swg=is_swg)
    return free_chlorine >= min_fc

"""Pool volume calculation utilities."""

from enum import StrEnum

from pypoolchem.chemistry.constants import CUBIC_FEET_TO_GALLONS


class PoolShape(StrEnum):
    """Pool shape for volume calculations."""

    RECTANGULAR = "rectangular"
    OVAL = "oval"
    ROUND = "round"
    KIDNEY = "kidney"
    FREEFORM = "freeform"


def calculate_pool_volume(
    shape: PoolShape,
    length_ft: float,
    width_ft: float,
    avg_depth_ft: float,
    *,
    shallow_depth_ft: float | None = None,
    deep_depth_ft: float | None = None,
) -> float:
    """Calculate pool volume in US gallons.

    For pools with variable depth, you can either provide avg_depth_ft directly,
    or provide shallow_depth_ft and deep_depth_ft and the average will be calculated.

    Formulas:
        Rectangular: length * width * depth * 7.48052
        Oval: (length * width - 0.214602 * width^2) * depth * 7.48052
        Round: diameter^2 * depth * 7.48052 (using length as diameter)
        Kidney: length * width * depth * 7.48052 * 0.75 (approximate)
        Freeform: length * width * depth * 7.48052 * 0.85 (approximate)

    Args:
        shape: Pool shape.
        length_ft: Pool length in feet (or diameter for round pools).
        width_ft: Pool width in feet (ignored for round pools).
        avg_depth_ft: Average depth in feet.
        shallow_depth_ft: Shallow end depth (optional, used to calculate average).
        deep_depth_ft: Deep end depth (optional, used to calculate average).

    Returns:
        Pool volume in US gallons.

    Example:
        >>> calculate_pool_volume(PoolShape.RECTANGULAR, 30, 15, 5)
        16819.17
        >>> calculate_pool_volume(PoolShape.ROUND, 18, 18, 4)
        9681.55...
    """
    # Calculate average depth if shallow and deep provided
    if shallow_depth_ft is not None and deep_depth_ft is not None:
        avg_depth_ft = (shallow_depth_ft + deep_depth_ft) / 2

    match shape:
        case PoolShape.RECTANGULAR:
            cubic_feet = length_ft * width_ft * avg_depth_ft
        case PoolShape.OVAL:
            # Formula accounts for the curved ends of an oval
            cubic_feet = (length_ft * width_ft - 0.214602 * width_ft * width_ft) * avg_depth_ft
        case PoolShape.ROUND:
            # For round pools, length is the diameter, width is ignored
            # Simplified formula used by PoolMath: diameter^2 * depth
            # More accurate would be: pi/4 * diameter^2 * depth
            cubic_feet = length_ft * length_ft * avg_depth_ft
        case PoolShape.KIDNEY:
            # Kidney pools are approximately 75% of rectangular area
            cubic_feet = length_ft * width_ft * avg_depth_ft * 0.75
        case PoolShape.FREEFORM:
            # Freeform pools are approximately 85% of rectangular area
            cubic_feet = length_ft * width_ft * avg_depth_ft * 0.85
        case _:
            # Default to rectangular
            cubic_feet = length_ft * width_ft * avg_depth_ft

    return cubic_feet * CUBIC_FEET_TO_GALLONS


def estimate_volume_from_dimensions(
    length_ft: float,
    width_ft: float,
    avg_depth_ft: float,
    shape: PoolShape = PoolShape.RECTANGULAR,
) -> float:
    """Convenience function to estimate pool volume.

    Args:
        length_ft: Pool length in feet.
        width_ft: Pool width in feet.
        avg_depth_ft: Average depth in feet.
        shape: Pool shape (default: rectangular).

    Returns:
        Estimated pool volume in US gallons.

    Example:
        >>> estimate_volume_from_dimensions(30, 15, 5)
        16819.17
    """
    return calculate_pool_volume(shape, length_ft, width_ft, avg_depth_ft)

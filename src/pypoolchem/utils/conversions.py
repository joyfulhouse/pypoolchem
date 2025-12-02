"""Unit conversion utilities for pool chemistry calculations."""

from pypoolchem.chemistry.constants import (
    GALLONS_TO_LITERS,
    GRAMS_TO_OZ,
    LBS_TO_OZ,
    LITERS_TO_GALLONS,
    OZ_TO_GRAMS,
    OZ_TO_LBS,
)


def fahrenheit_to_celsius(temp_f: float) -> float:
    """Convert temperature from Fahrenheit to Celsius.

    Args:
        temp_f: Temperature in Fahrenheit.

    Returns:
        Temperature in Celsius.

    Example:
        >>> fahrenheit_to_celsius(84)
        28.888...
    """
    return (temp_f - 32) * 5 / 9


def celsius_to_fahrenheit(temp_c: float) -> float:
    """Convert temperature from Celsius to Fahrenheit.

    Args:
        temp_c: Temperature in Celsius.

    Returns:
        Temperature in Fahrenheit.

    Example:
        >>> celsius_to_fahrenheit(28)
        82.4
    """
    return temp_c * 9 / 5 + 32


def gallons_to_liters(gallons: float) -> float:
    """Convert US gallons to liters.

    Args:
        gallons: Volume in US gallons.

    Returns:
        Volume in liters.

    Example:
        >>> gallons_to_liters(1000)
        3785.41
    """
    return gallons * GALLONS_TO_LITERS


def liters_to_gallons(liters: float) -> float:
    """Convert liters to US gallons.

    Args:
        liters: Volume in liters.

    Returns:
        Volume in US gallons.

    Example:
        >>> liters_to_gallons(3785.41)
        1000.0...
    """
    return liters * LITERS_TO_GALLONS


def oz_to_grams(oz: float) -> float:
    """Convert ounces to grams.

    Args:
        oz: Weight in ounces.

    Returns:
        Weight in grams.

    Example:
        >>> oz_to_grams(1)
        28.3495
    """
    return oz * OZ_TO_GRAMS


def grams_to_oz(grams: float) -> float:
    """Convert grams to ounces.

    Args:
        grams: Weight in grams.

    Returns:
        Weight in ounces.

    Example:
        >>> grams_to_oz(28.3495)
        1.0
    """
    return grams * GRAMS_TO_OZ


def oz_to_lbs(oz: float) -> float:
    """Convert ounces to pounds.

    Args:
        oz: Weight in ounces.

    Returns:
        Weight in pounds.

    Example:
        >>> oz_to_lbs(16)
        1.0
    """
    return oz * OZ_TO_LBS


def lbs_to_oz(lbs: float) -> float:
    """Convert pounds to ounces.

    Args:
        lbs: Weight in pounds.

    Returns:
        Weight in ounces.

    Example:
        >>> lbs_to_oz(1)
        16.0
    """
    return lbs * LBS_TO_OZ


def fl_oz_to_ml(fl_oz: float) -> float:
    """Convert fluid ounces to milliliters.

    Args:
        fl_oz: Volume in fluid ounces.

    Returns:
        Volume in milliliters.

    Example:
        >>> fl_oz_to_ml(1)
        29.5735
    """
    return fl_oz * 29.5735


def ml_to_fl_oz(ml: float) -> float:
    """Convert milliliters to fluid ounces.

    Args:
        ml: Volume in milliliters.

    Returns:
        Volume in fluid ounces.

    Example:
        >>> ml_to_fl_oz(29.5735)
        1.0
    """
    return ml / 29.5735

"""Configuration for pypoolchem library.

This module provides a way to customize the library's behavior without
modifying source code. Users can override default constants, add custom
chemicals, or adjust calculation parameters.

Example:
    >>> from pypoolchem.config import get_config, set_config, PyPoolChemConfig
    >>> config = get_config()
    >>> # Customize temperature factor table
    >>> config.temperature_factors[90] = 0.75
    >>> set_config(config)

    >>> # Or create a completely new config
    >>> custom_config = PyPoolChemConfig(
    ...     lsi_constant=12.14,  # Different LSI constant
    ... )
    >>> set_config(custom_config)

    >>> # Reset to defaults
    >>> from pypoolchem.config import reset_config
    >>> reset_config()
"""

from copy import deepcopy

from pydantic import BaseModel, ConfigDict, Field


class PyPoolChemConfig(BaseModel):
    """Global configuration for pypoolchem calculations.

    All values have sensible defaults based on TroubleFreePool formulas.
    Override individual values as needed for your use case.

    Attributes:
        lsi_constant: Constant subtracted in LSI formula (default 12.1).
        csi_ph_constant: pH constant for CSI formula (default 11.677).
        csi_final_constant: Final additive constant for CSI (default 4.7375).
        csi_temp_numerator: Temperature numerator for CSI (default 1412.5).
        csi_ionic_coefficient: Ionic strength coefficient (default 2.56).
        cya_coefficient: CYA correction coefficient (default 0.38772).
        cya_ph_constant: CYA pH constant (default 6.83).
        borate_coefficient: Borate correction coefficient (default 4.63).
        borate_ph_constant: Borate pH constant (default 9.11).
        temperature_factors: Temperature to factor mapping for LSI.
    """

    # LSI constants
    lsi_constant: float = Field(default=12.1, description="LSI subtraction constant")

    # CSI constants
    csi_ph_constant: float = Field(default=11.677, description="CSI pH constant")
    csi_final_constant: float = Field(default=4.7375, description="CSI final constant")
    csi_temp_numerator: float = Field(default=1412.5, description="CSI temperature numerator")
    csi_ionic_coefficient: float = Field(default=2.56, description="Ionic strength coefficient")
    csi_ionic_denominator_coefficient: float = Field(
        default=1.65, description="Ionic denominator coefficient"
    )

    # Carbonate alkalinity correction constants
    cya_coefficient: float = Field(default=0.38772, description="CYA correction coefficient")
    cya_ph_constant: float = Field(default=6.83, description="CYA pH constant")
    borate_coefficient: float = Field(default=4.63, description="Borate correction coefficient")
    borate_ph_constant: float = Field(default=9.11, description="Borate pH constant")

    # Ionic strength constants
    ionic_ch_coefficient: float = Field(default=1.5, description="CH coefficient for ionic")
    ionic_ta_coefficient: float = Field(default=1.0, description="TA coefficient for ionic")
    ionic_divisor: float = Field(default=50045, description="Ionic strength divisor")
    ionic_nacl_divisor: float = Field(default=58440, description="NaCl divisor")
    ch_to_nacl_ratio: float = Field(default=1.1678, description="CH to NaCl binding ratio")

    # Temperature factor lookup table (Fahrenheit -> factor)
    temperature_factors: dict[int, float] = Field(
        default_factory=lambda: {
            32: 0.0,
            37: 0.1,
            45: 0.2,
            53: 0.3,
            60: 0.4,
            66: 0.5,
            76: 0.6,
            84: 0.7,
            94: 0.8,
            105: 0.9,
        },
        description="Temperature (°F) to factor mapping for LSI",
    )

    # CYA correction factors by pH (for LSI)
    cya_correction_factors: dict[float, float] = Field(
        default_factory=lambda: {
            7.0: 0.22,
            7.2: 0.27,
            7.4: 0.31,
            7.5: 0.33,
            7.6: 0.33,
            7.8: 0.35,
            8.0: 0.38,
        },
        description="pH to CYA correction factor mapping",
    )

    # Unit conversions
    gallons_to_liters: float = Field(default=3.78541, description="Gallons to liters")
    cubic_feet_to_gallons: float = Field(default=7.48052, description="Cubic feet to gallons")
    oz_to_grams: float = Field(default=28.3495, description="Ounces to grams")
    fl_oz_to_ml: float = Field(default=29.5735, description="Fluid ounces to milliliters")

    model_config = ConfigDict(validate_assignment=True)


# Global configuration instance
_config: PyPoolChemConfig | None = None


def get_config() -> PyPoolChemConfig:
    """Get the current configuration.

    Returns a copy to prevent accidental modification.
    Use set_config() to apply changes.

    Returns:
        Current PyPoolChemConfig instance.

    Example:
        >>> config = get_config()
        >>> print(f"LSI constant: {config.lsi_constant}")
        LSI constant: 12.1
    """
    global _config
    if _config is None:
        _config = PyPoolChemConfig()
    return deepcopy(_config)


def set_config(config: PyPoolChemConfig) -> None:
    """Set the global configuration.

    Args:
        config: New configuration to use.

    Example:
        >>> config = get_config()
        >>> config.lsi_constant = 12.14
        >>> set_config(config)
    """
    global _config
    _config = deepcopy(config)


def reset_config() -> None:
    """Reset configuration to defaults.

    Example:
        >>> reset_config()
        >>> config = get_config()
        >>> config.lsi_constant
        12.1
    """
    global _config
    _config = PyPoolChemConfig()


def update_config(**kwargs: float | dict[int, float] | dict[float, float]) -> None:
    """Update specific configuration values.

    Args:
        **kwargs: Configuration values to update.

    Example:
        >>> update_config(lsi_constant=12.14)
        >>> get_config().lsi_constant
        12.14
    """
    global _config
    if _config is None:
        _config = PyPoolChemConfig()
    for key, value in kwargs.items():
        setattr(_config, key, value)

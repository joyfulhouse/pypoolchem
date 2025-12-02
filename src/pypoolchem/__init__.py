"""pypoolchem - Pool and spa water chemistry calculations library.

This library provides accurate, well-documented pool chemistry calculations
including water balance indices (LSI, CSI), chemical dosing recommendations,
target range validation, and pool volume calculations.

Example:
    >>> from pypoolchem import WaterChemistry, calculate_csi, calculate_chlorine_dose
    >>> water = WaterChemistry(
    ...     ph=7.5,
    ...     temperature_f=84,
    ...     free_chlorine=3.0,
    ...     calcium_hardness=300,
    ...     total_alkalinity=80,
    ...     cyanuric_acid=50,
    ... )
    >>> csi = calculate_csi(water)
    >>> print(f"CSI: {csi:.2f}")
"""

from pypoolchem.chemistry.csi import calculate_csi
from pypoolchem.chemistry.factors import (
    calculate_carbonate_alkalinity,
    calculate_ionic_strength,
    calculate_temperature_factor,
)
from pypoolchem.chemistry.lsi import calculate_lsi
from pypoolchem.config import (
    PyPoolChemConfig,
    get_config,
    reset_config,
    set_config,
    update_config,
)
from pypoolchem.dosing.calculator import (
    calculate_alkalinity_dose,
    calculate_borate_dose,
    calculate_calcium_dose,
    calculate_chlorine_dose,
    calculate_cya_dose,
    calculate_ph_dose,
    calculate_salt_dose,
)
from pypoolchem.dosing.chemicals import Chemical, ChemicalType
from pypoolchem.effects.predictions import predict_effect
from pypoolchem.exceptions import (
    CalculationError,
    ChemicalNotFoundError,
    PyPoolChemError,
    ValidationError,
)
from pypoolchem.models.pool import Pool, PoolSurface, PoolType
from pypoolchem.models.targets import TargetRanges, get_target_ranges
from pypoolchem.models.water import WaterChemistry
from pypoolchem.utils.conversions import (
    celsius_to_fahrenheit,
    fahrenheit_to_celsius,
    gallons_to_liters,
    grams_to_oz,
    lbs_to_oz,
    liters_to_gallons,
    oz_to_grams,
    oz_to_lbs,
)
from pypoolchem.utils.volume import PoolShape, calculate_pool_volume

__version__ = "0.1.1"

__all__ = [
    # Version
    "__version__",
    # Configuration
    "PyPoolChemConfig",
    "get_config",
    "reset_config",
    "set_config",
    "update_config",
    # Models
    "Chemical",
    "ChemicalType",
    "Pool",
    "PoolShape",
    "PoolSurface",
    "PoolType",
    "TargetRanges",
    "WaterChemistry",
    # Exceptions
    "CalculationError",
    "ChemicalNotFoundError",
    "PyPoolChemError",
    "ValidationError",
    # Chemistry calculations
    "calculate_carbonate_alkalinity",
    "calculate_csi",
    "calculate_ionic_strength",
    "calculate_lsi",
    "calculate_temperature_factor",
    # Dosing calculations
    "calculate_alkalinity_dose",
    "calculate_borate_dose",
    "calculate_calcium_dose",
    "calculate_chlorine_dose",
    "calculate_cya_dose",
    "calculate_ph_dose",
    "calculate_salt_dose",
    # Effects
    "predict_effect",
    # Target ranges
    "get_target_ranges",
    # Utilities - volume
    "calculate_pool_volume",
    # Utilities - conversions
    "celsius_to_fahrenheit",
    "fahrenheit_to_celsius",
    "gallons_to_liters",
    "grams_to_oz",
    "lbs_to_oz",
    "liters_to_gallons",
    "oz_to_grams",
    "oz_to_lbs",
]

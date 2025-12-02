"""Chemical dosing calculations for pool chemistry."""

from pypoolchem.dosing.calculator import (
    calculate_alkalinity_dose,
    calculate_borate_dose,
    calculate_calcium_dose,
    calculate_chlorine_dose,
    calculate_cya_dose,
    calculate_ph_dose,
    calculate_salt_dose,
)
from pypoolchem.dosing.chemicals import (
    CHEMICALS,
    Chemical,
    ChemicalType,
    get_chemical,
)

__all__ = [
    "CHEMICALS",
    "Chemical",
    "ChemicalType",
    "calculate_alkalinity_dose",
    "calculate_borate_dose",
    "calculate_calcium_dose",
    "calculate_chlorine_dose",
    "calculate_cya_dose",
    "calculate_ph_dose",
    "calculate_salt_dose",
    "get_chemical",
]

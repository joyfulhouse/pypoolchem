"""Chemical definitions and properties for pool dosing calculations.

All multipliers are derived from the TroubleFreePool PoolMath calculator.
Formula: dose_oz = (target - current) * pool_gallons / multiplier
"""

from enum import StrEnum

from pydantic import BaseModel, Field

from pypoolchem.exceptions import ChemicalNotFoundError


class ChemicalType(StrEnum):
    """Type of pool chemical."""

    # Chlorine sources
    BLEACH_6 = "bleach_6"
    BLEACH_8_25 = "bleach_8.25"
    BLEACH_10 = "bleach_10"
    BLEACH_12_5 = "bleach_12.5"
    TRICHLOR = "trichlor"
    DICHLOR = "dichlor"
    CAL_HYPO_48 = "cal_hypo_48"
    CAL_HYPO_53 = "cal_hypo_53"
    CAL_HYPO_65 = "cal_hypo_65"
    CAL_HYPO_73 = "cal_hypo_73"
    LITHIUM_HYPO = "lithium_hypo"
    CHLORINE_GAS = "chlorine_gas"

    # pH adjustment
    MURIATIC_ACID_14_5 = "muriatic_acid_14.5"
    MURIATIC_ACID_15_7 = "muriatic_acid_15.7"
    MURIATIC_ACID_20 = "muriatic_acid_20"
    MURIATIC_ACID_28_3 = "muriatic_acid_28.3"
    MURIATIC_ACID_31_45 = "muriatic_acid_31.45"
    MURIATIC_ACID_34_6 = "muriatic_acid_34.6"
    DRY_ACID = "dry_acid"
    SODA_ASH = "soda_ash"
    BORAX = "borax"

    # Alkalinity
    BAKING_SODA = "baking_soda"

    # Calcium
    CALCIUM_CHLORIDE_ANHYDROUS = "calcium_chloride_anhydrous"
    CALCIUM_CHLORIDE_DIHYDRATE = "calcium_chloride_dihydrate"

    # Stabilizer
    CYA_GRANULAR = "cya_granular"
    CYA_LIQUID = "cya_liquid"

    # Salt
    POOL_SALT = "pool_salt"

    # Borates
    BORAX_BORATE = "borax_borate"
    BORIC_ACID = "boric_acid"
    SODIUM_TETRABORATE_PENTAHYDRATE = "sodium_tetraborate_pentahydrate"


class Chemical(BaseModel, frozen=True):
    """Definition of a pool chemical with dosing properties.

    Attributes:
        chemical_type: The type identifier for this chemical.
        name: Human-readable name.
        multiplier: Dosing multiplier for primary effect.
        unit: Unit of measurement (oz, fl_oz, lbs).
        volume_factor: Factor to convert weight to volume (if applicable).
        affects: What parameter this chemical primarily affects.
        secondary_effects: Dictionary of secondary effects {parameter: multiplier}.
    """

    chemical_type: ChemicalType
    name: str
    multiplier: float = Field(description="Primary effect multiplier")
    unit: str = Field(default="oz", description="Unit of measurement")
    volume_factor: float | None = Field(
        default=None,
        description="Factor to convert weight to volume",
    )
    affects: str = Field(description="Primary parameter affected")
    secondary_effects: dict[str, float] = Field(
        default_factory=dict,
        description="Secondary effects {parameter: multiplier}",
    )


# Define all chemicals with their properties
CHEMICALS: dict[ChemicalType, Chemical] = {
    # Chlorine - Liquid
    ChemicalType.BLEACH_6: Chemical(
        chemical_type=ChemicalType.BLEACH_6,
        name="Bleach 6%",
        multiplier=600.0,  # Calculated from formula
        unit="fl_oz",
        affects="free_chlorine",
    ),
    ChemicalType.BLEACH_8_25: Chemical(
        chemical_type=ChemicalType.BLEACH_8_25,
        name="Bleach 8.25%",
        multiplier=825.0,
        unit="fl_oz",
        affects="free_chlorine",
    ),
    ChemicalType.BLEACH_10: Chemical(
        chemical_type=ChemicalType.BLEACH_10,
        name="Bleach 10%",
        multiplier=1000.0,
        unit="fl_oz",
        affects="free_chlorine",
    ),
    ChemicalType.BLEACH_12_5: Chemical(
        chemical_type=ChemicalType.BLEACH_12_5,
        name="Bleach 12.5%",
        multiplier=1250.0,
        unit="fl_oz",
        affects="free_chlorine",
    ),
    # Chlorine - Solid
    ChemicalType.TRICHLOR: Chemical(
        chemical_type=ChemicalType.TRICHLOR,
        name="Trichlor (90%)",
        multiplier=6854.95,
        unit="oz",
        volume_factor=0.9351,
        affects="free_chlorine",
        secondary_effects={
            "cyanuric_acid": 4159.41,
            "ph": -367.0,  # Lowers pH
            "salt": 5600.0,
        },
    ),
    ChemicalType.DICHLOR: Chemical(
        chemical_type=ChemicalType.DICHLOR,
        name="Dichlor (56%)",
        multiplier=4149.03,
        unit="oz",
        volume_factor=0.9352,
        affects="free_chlorine",
        secondary_effects={
            "cyanuric_acid": 3776.46,
            "ph": -158.0,  # Lowers pH
            "salt": 3384.0,
        },
    ),
    ChemicalType.CAL_HYPO_48: Chemical(
        chemical_type=ChemicalType.CAL_HYPO_48,
        name="Cal-Hypo 48%",
        multiplier=3565.44,
        unit="oz",
        volume_factor=0.9352,
        affects="free_chlorine",
        secondary_effects={
            "calcium_hardness": 2938.56,
        },
    ),
    ChemicalType.CAL_HYPO_53: Chemical(
        chemical_type=ChemicalType.CAL_HYPO_53,
        name="Cal-Hypo 53%",
        multiplier=3936.84,
        unit="oz",
        volume_factor=0.9352,
        affects="free_chlorine",
        secondary_effects={
            "calcium_hardness": 3245.92,
        },
    ),
    ChemicalType.CAL_HYPO_65: Chemical(
        chemical_type=ChemicalType.CAL_HYPO_65,
        name="Cal-Hypo 65%",
        multiplier=5422.41,
        unit="oz",
        volume_factor=0.9352,
        affects="free_chlorine",
        secondary_effects={
            "calcium_hardness": 3827.09,
            "salt": 5500.0,
        },
    ),
    ChemicalType.CAL_HYPO_73: Chemical(
        chemical_type=ChemicalType.CAL_HYPO_73,
        name="Cal-Hypo 73%",
        multiplier=6092.62,
        unit="oz",
        volume_factor=0.9352,
        affects="free_chlorine",
        secondary_effects={
            "calcium_hardness": 4295.56,
            "salt": 6175.0,
        },
    ),
    ChemicalType.LITHIUM_HYPO: Chemical(
        chemical_type=ChemicalType.LITHIUM_HYPO,
        name="Lithium Hypochlorite (35%)",
        multiplier=2637.5,
        unit="oz",
        volume_factor=0.978,
        affects="free_chlorine",
        secondary_effects={
            "salt": 2711.0,
        },
    ),
    ChemicalType.CHLORINE_GAS: Chemical(
        chemical_type=ChemicalType.CHLORINE_GAS,
        name="Chlorine Gas",
        multiplier=7489.4,
        unit="oz",
        affects="free_chlorine",
        secondary_effects={
            "ph": -625.0,  # Lowers pH significantly
            "salt": 6140.0,
        },
    ),
    # pH - Lowering (Acids)  # noqa: ERA001
    ChemicalType.MURIATIC_ACID_14_5: Chemical(
        chemical_type=ChemicalType.MURIATIC_ACID_14_5,
        name="Muriatic Acid 14.5% (10° Baumé)",
        multiplier=240.15 / 2.16897,  # Base multiplier / concentration factor
        unit="fl_oz",
        affects="ph",
        secondary_effects={"total_alkalinity": -3911.47 / 2.16897},
    ),
    ChemicalType.MURIATIC_ACID_15_7: Chemical(
        chemical_type=ChemicalType.MURIATIC_ACID_15_7,
        name="Muriatic Acid 15.7%",
        multiplier=240.15 / 2.0,
        unit="fl_oz",
        affects="ph",
        secondary_effects={"total_alkalinity": -3911.47 / 2.0},
    ),
    ChemicalType.MURIATIC_ACID_20: Chemical(
        chemical_type=ChemicalType.MURIATIC_ACID_20,
        name="Muriatic Acid 20% (22° Baumé)",
        multiplier=240.15 / 1.5725,
        unit="fl_oz",
        affects="ph",
        secondary_effects={"total_alkalinity": -3911.47 / 1.5725},
    ),
    ChemicalType.MURIATIC_ACID_28_3: Chemical(
        chemical_type=ChemicalType.MURIATIC_ACID_28_3,
        name="Muriatic Acid 28.3%",
        multiplier=240.15 / 1.11111,
        unit="fl_oz",
        affects="ph",
        secondary_effects={"total_alkalinity": -3911.47 / 1.11111},
    ),
    ChemicalType.MURIATIC_ACID_31_45: Chemical(
        chemical_type=ChemicalType.MURIATIC_ACID_31_45,
        name="Muriatic Acid 31.45% (20° Baumé)",
        multiplier=240.15,  # Reference concentration
        unit="fl_oz",
        affects="ph",
        secondary_effects={"total_alkalinity": -3911.47},
    ),
    ChemicalType.MURIATIC_ACID_34_6: Chemical(
        chemical_type=ChemicalType.MURIATIC_ACID_34_6,
        name="Muriatic Acid 34.6%",
        multiplier=240.15 / 0.909091,
        unit="fl_oz",
        affects="ph",
        secondary_effects={"total_alkalinity": -3911.47 / 0.909091},
    ),
    ChemicalType.DRY_ACID: Chemical(
        chemical_type=ChemicalType.DRY_ACID,
        name="Dry Acid (Sodium Bisulfate)",
        multiplier=178.66,
        unit="oz",
        volume_factor=0.6657,
        affects="ph",
        secondary_effects={"total_alkalinity": -2909.47},
    ),
    # pH - Raising
    ChemicalType.SODA_ASH: Chemical(
        chemical_type=ChemicalType.SODA_ASH,
        name="Soda Ash (Sodium Carbonate)",
        multiplier=218.68,
        unit="oz",
        volume_factor=0.8715,
        affects="ph",
        secondary_effects={"total_alkalinity": 7072.46},
    ),
    ChemicalType.BORAX: Chemical(
        chemical_type=ChemicalType.BORAX,
        name="Borax (20 Mule Team)",
        multiplier=110.05,
        unit="oz",
        volume_factor=0.9586,
        affects="ph",
        secondary_effects={"borates": 849.271},  # Also raises borates
    ),
    # Alkalinity
    ChemicalType.BAKING_SODA: Chemical(
        chemical_type=ChemicalType.BAKING_SODA,
        name="Baking Soda (Sodium Bicarbonate)",
        multiplier=4259.15,
        unit="oz",
        volume_factor=0.7988,
        affects="total_alkalinity",
        secondary_effects={"ph": 9.091},  # Slight pH increase
    ),
    # Calcium
    ChemicalType.CALCIUM_CHLORIDE_ANHYDROUS: Chemical(
        chemical_type=ChemicalType.CALCIUM_CHLORIDE_ANHYDROUS,
        name="Calcium Chloride Anhydrous (94-97%)",
        multiplier=6754.11,
        unit="oz",
        volume_factor=0.7988,
        affects="calcium_hardness",
    ),
    ChemicalType.CALCIUM_CHLORIDE_DIHYDRATE: Chemical(
        chemical_type=ChemicalType.CALCIUM_CHLORIDE_DIHYDRATE,
        name="Calcium Chloride Dihydrate/Flake (77-80%)",
        multiplier=5098.82,
        unit="oz",
        volume_factor=1.148,
        affects="calcium_hardness",
    ),
    # Stabilizer (CYA)  # noqa: ERA001
    ChemicalType.CYA_GRANULAR: Chemical(
        chemical_type=ChemicalType.CYA_GRANULAR,
        name="Cyanuric Acid Granular",
        multiplier=7489.51,
        unit="oz",
        volume_factor=1.042,
        affects="cyanuric_acid",
        secondary_effects={"ph": -138.8},  # Slight pH decrease
    ),
    ChemicalType.CYA_LIQUID: Chemical(
        chemical_type=ChemicalType.CYA_LIQUID,
        name="Cyanuric Acid Liquid",
        multiplier=2890.0,
        unit="fl_oz",
        affects="cyanuric_acid",
    ),
    # Salt
    ChemicalType.POOL_SALT: Chemical(
        chemical_type=ChemicalType.POOL_SALT,
        name="Pool Salt (Sodium Chloride)",
        multiplier=7468.64,
        unit="oz",
        affects="salt",
    ),
    # Borates
    ChemicalType.BORAX_BORATE: Chemical(
        chemical_type=ChemicalType.BORAX_BORATE,
        name="Borax (for borate level)",
        multiplier=849.271,
        unit="oz",
        volume_factor=1.075,
        affects="borates",
        secondary_effects={"ph": 110.05},  # Raises pH
    ),
    ChemicalType.BORIC_ACID: Chemical(
        chemical_type=ChemicalType.BORIC_ACID,
        name="Boric Acid",
        multiplier=1309.52,
        unit="oz",
        volume_factor=0.5296,
        affects="borates",
        # Requires muriatic acid to neutralize (0.624 oz per oz boric acid)
    ),
    ChemicalType.SODIUM_TETRABORATE_PENTAHYDRATE: Chemical(
        chemical_type=ChemicalType.SODIUM_TETRABORATE_PENTAHYDRATE,
        name="Sodium Tetraborate Pentahydrate (ProTeam Supreme)",
        multiplier=1111.69,
        unit="oz",
        volume_factor=0.9586,
        affects="borates",
        # Requires muriatic acid to neutralize (0.4765 oz per oz)
    ),
}


def get_chemical(chemical_type: ChemicalType) -> Chemical:
    """Get a chemical definition by type.

    Args:
        chemical_type: The type of chemical to retrieve.

    Returns:
        Chemical definition.

    Raises:
        ChemicalNotFoundError: If chemical type is not found.
    """
    if chemical_type not in CHEMICALS:
        raise ChemicalNotFoundError(f"Chemical type not found: {chemical_type}")
    return CHEMICALS[chemical_type]

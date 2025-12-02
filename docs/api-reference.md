# API Reference

Complete reference for all public functions, classes, and constants in pypoolchem.

## Models

### WaterChemistry

```python
class WaterChemistry(BaseModel, frozen=True):
    """Water chemistry measurements."""

    ph: float                      # pH level (0-14)
    temperature_f: float           # Temperature in Fahrenheit (32-120)
    free_chlorine: float = 0       # Free chlorine in ppm
    combined_chlorine: float = 0   # Combined chlorine in ppm
    calcium_hardness: float        # Calcium hardness in ppm
    total_alkalinity: float        # Total alkalinity in ppm
    cyanuric_acid: float = 0       # CYA in ppm
    salt: float = 0                # Salt in ppm
    borates: float = 0             # Borates in ppm
    tds: float = 1000              # Total dissolved solids in ppm

    @property
    def total_chlorine(self) -> float: ...
    @property
    def temperature_c(self) -> float: ...
```

### Pool

```python
class Pool(BaseModel, frozen=True):
    """Pool configuration."""

    name: str                             # Pool identifier
    volume_gallons: float                 # Volume in US gallons
    pool_type: PoolType = TRADITIONAL     # Pool type
    surface: PoolSurface = PLASTER        # Surface material

    @property
    def volume_liters(self) -> float: ...
```

### PoolType

```python
class PoolType(StrEnum):
    TRADITIONAL = "traditional"
    SWG = "swg"
    SPA = "spa"
```

### PoolSurface

```python
class PoolSurface(StrEnum):
    PLASTER = "plaster"
    PEBBLE = "pebble"
    TILE = "tile"
    FIBERGLASS = "fiberglass"
    VINYL = "vinyl"
```

### PoolShape

```python
class PoolShape(StrEnum):
    RECTANGULAR = "rectangular"
    OVAL = "oval"
    ROUND = "round"
    KIDNEY = "kidney"
    FREEFORM = "freeform"
```

### ChemicalType

```python
class ChemicalType(StrEnum):
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
```

### Chemical

```python
class Chemical(BaseModel, frozen=True):
    """Pool chemical with dosing properties."""

    chemical_type: ChemicalType
    name: str
    multiplier: float                        # Dosing multiplier
    unit: str = "oz"                         # Unit of measurement
    volume_factor: float | None = None       # Weight to volume conversion
    affects: str                             # Primary parameter affected
    secondary_effects: dict[str, float] = {} # Secondary effects
```

### DosingResult

```python
class DosingResult(BaseModel, frozen=True):
    """Result of a dosing calculation."""

    chemical: Chemical
    amount: float                            # Amount to add
    unit: str                                # Unit of measurement
    amount_volume: float | None = None       # Volume equivalent
    volume_unit: str | None = None           # Volume unit
    notes: str | None = None                 # Additional information
```

### TargetRanges

```python
class TargetRanges(BaseModel, frozen=True):
    """Target ranges for water chemistry parameters."""

    ph: ParameterRange
    total_alkalinity: ParameterRange
    calcium_hardness: ParameterRange
    cyanuric_acid: ParameterRange
    salt: ParameterRange | None = None
    borates: ParameterRange | None = None
    csi: ParameterRange = ParameterRange(-0.3, 0.0, 0.3)
    fc_min_factor: float = 0.075
    fc_target_factor: float = 0.10
```

### ParameterRange

```python
class ParameterRange(BaseModel, frozen=True):
    """Range for a water chemistry parameter."""

    minimum: float
    target: float
    maximum: float

    def is_in_range(self, value: float) -> bool: ...
    def is_low(self, value: float) -> bool: ...
    def is_high(self, value: float) -> bool: ...
```

## Chemistry Functions

### calculate_csi

```python
def calculate_csi(
    water: WaterChemistry | None = None,
    *,
    ph: float | None = None,
    temperature_f: float | None = None,
    calcium_hardness: float | None = None,
    total_alkalinity: float | None = None,
    cyanuric_acid: float = 0,
    salt: float = 0,
    borates: float = 0,
) -> float:
    """Calculate the Calcium Saturation Index (CSI).

    Args:
        water: WaterChemistry object, or use individual parameters.
        ph: Water pH (7.0-8.0 typical).
        temperature_f: Temperature in Fahrenheit.
        calcium_hardness: CH in ppm as CaCO3.
        total_alkalinity: TA in ppm as CaCO3.
        cyanuric_acid: CYA in ppm.
        salt: Salt in ppm.
        borates: Borates in ppm.

    Returns:
        CSI value. Ideal range is -0.3 to +0.3.

    Raises:
        CalculationError: If parameters are invalid.
    """
```

### calculate_lsi

```python
def calculate_lsi(
    water: WaterChemistry | None = None,
    *,
    ph: float | None = None,
    temperature_f: float | None = None,
    calcium_hardness: float | None = None,
    total_alkalinity: float | None = None,
    cyanuric_acid: float = 0,
    tds: float = 1000,
) -> float:
    """Calculate the Langelier Saturation Index (LSI).

    Args:
        water: WaterChemistry object, or use individual parameters.
        ph: Water pH.
        temperature_f: Temperature in Fahrenheit.
        calcium_hardness: CH in ppm.
        total_alkalinity: TA in ppm.
        cyanuric_acid: CYA in ppm.
        tds: Total dissolved solids in ppm.

    Returns:
        LSI value. Ideal range is -0.3 to +0.3.

    Raises:
        CalculationError: If parameters are invalid.
    """
```

### interpret_csi

```python
def interpret_csi(csi: float) -> str:
    """Interpret a CSI value.

    Returns:
        Human-readable interpretation.
    """
```

### interpret_lsi

```python
def interpret_lsi(lsi: float) -> str:
    """Interpret an LSI value with color coding.

    Returns:
        Human-readable interpretation with color indicator.
    """
```

### calculate_carbonate_alkalinity

```python
def calculate_carbonate_alkalinity(
    total_alkalinity: float,
    cyanuric_acid: float,
    ph: float,
    borates: float = 0,
) -> float:
    """Calculate carbonate alkalinity corrected for CYA and borates.

    Returns:
        Carbonate alkalinity in ppm.
    """
```

### calculate_ionic_strength

```python
def calculate_ionic_strength(
    calcium_hardness: float,
    total_alkalinity: float,
    salt: float = 0,
) -> float:
    """Calculate ionic strength for CSI calculation.

    Returns:
        Ionic strength value (dimensionless).
    """
```

### calculate_temperature_factor

```python
def calculate_temperature_factor(temperature_f: float) -> float:
    """Calculate temperature factor for LSI.

    Returns:
        Temperature factor from lookup table.
    """
```

## Dosing Functions

### calculate_chlorine_dose

```python
def calculate_chlorine_dose(
    current_fc: float,
    target_fc: float,
    pool_gallons: float,
    chemical_type: ChemicalType = ChemicalType.BLEACH_12_5,
) -> DosingResult:
    """Calculate chlorine dose to reach target FC."""
```

### calculate_ph_dose

```python
def calculate_ph_dose(
    current_ph: float,
    target_ph: float,
    pool_gallons: float,
    total_alkalinity: float,
    temperature_f: float = 80,
    borates: float = 0,
    *,
    raise_ph: bool | None = None,
    chemical_type: ChemicalType | None = None,
) -> DosingResult:
    """Calculate pH adjustment dose."""
```

### calculate_alkalinity_dose

```python
def calculate_alkalinity_dose(
    current_ta: float,
    target_ta: float,
    pool_gallons: float,
    chemical_type: ChemicalType = ChemicalType.BAKING_SODA,
) -> DosingResult:
    """Calculate alkalinity adjustment dose."""
```

### calculate_calcium_dose

```python
def calculate_calcium_dose(
    current_ch: float,
    target_ch: float,
    pool_gallons: float,
    chemical_type: ChemicalType = ChemicalType.CALCIUM_CHLORIDE_DIHYDRATE,
) -> DosingResult:
    """Calculate calcium hardness adjustment dose."""
```

### calculate_cya_dose

```python
def calculate_cya_dose(
    current_cya: float,
    target_cya: float,
    pool_gallons: float,
    chemical_type: ChemicalType = ChemicalType.CYA_GRANULAR,
) -> DosingResult:
    """Calculate cyanuric acid dose."""
```

### calculate_salt_dose

```python
def calculate_salt_dose(
    current_salt: float,
    target_salt: float,
    pool_gallons: float,
) -> DosingResult:
    """Calculate salt dose for SWG pools.

    Note: Returns amount in lbs, not oz.
    """
```

### calculate_borate_dose

```python
def calculate_borate_dose(
    current_borates: float,
    target_borates: float,
    pool_gallons: float,
    chemical_type: ChemicalType = ChemicalType.BORAX_BORATE,
) -> DosingResult:
    """Calculate borate dose."""
```

### calculate_water_replacement

```python
def calculate_water_replacement(
    current_value: float,
    target_value: float,
    fill_water_value: float = 0,
) -> float:
    """Calculate percentage of water to replace.

    Used for lowering CYA, CH, or Salt.

    Returns:
        Percentage of water to replace.
    """
```

## Effect Functions

### predict_effect

```python
def predict_effect(
    water: WaterChemistry,
    chemical_type: ChemicalType,
    amount_oz: float,
    pool_gallons: float,
) -> WaterChemistry:
    """Predict water chemistry after adding a chemical.

    Returns:
        New WaterChemistry with predicted values.
    """
```

### predict_multiple_effects

```python
def predict_multiple_effects(
    water: WaterChemistry,
    additions: list[tuple[ChemicalType, float]],
    pool_gallons: float,
) -> WaterChemistry:
    """Predict water chemistry after adding multiple chemicals.

    Args:
        additions: List of (chemical_type, amount_oz) tuples.

    Returns:
        New WaterChemistry with predicted values.
    """
```

## Utility Functions

### calculate_pool_volume

```python
def calculate_pool_volume(
    shape: PoolShape,
    length_ft: float,
    width_ft: float,
    avg_depth_ft: float,
    *,
    shallow_depth_ft: float | None = None,
    deep_depth_ft: float | None = None,
) -> float:
    """Calculate pool volume in US gallons."""
```

### get_target_ranges

```python
def get_target_ranges(pool_type: PoolType) -> TargetRanges:
    """Get target ranges for a specific pool type."""
```

### Unit Conversions

```python
def fahrenheit_to_celsius(temp_f: float) -> float: ...
def celsius_to_fahrenheit(temp_c: float) -> float: ...
def gallons_to_liters(gallons: float) -> float: ...
def liters_to_gallons(liters: float) -> float: ...
def oz_to_grams(oz: float) -> float: ...
def grams_to_oz(grams: float) -> float: ...
def oz_to_lbs(oz: float) -> float: ...
def lbs_to_oz(lbs: float) -> float: ...
```

## Configuration Functions

### get_config

```python
def get_config() -> PyPoolChemConfig:
    """Get the current configuration (copy)."""
```

### set_config

```python
def set_config(config: PyPoolChemConfig) -> None:
    """Set the global configuration."""
```

### update_config

```python
def update_config(**kwargs) -> None:
    """Update specific configuration values."""
```

### reset_config

```python
def reset_config() -> None:
    """Reset configuration to defaults."""
```

## Exceptions

### PyPoolChemError

Base exception for all pypoolchem errors.

### CalculationError

Raised when a calculation cannot be completed (invalid parameters).

### ValidationError

Raised when input validation fails.

### ChemicalNotFoundError

Raised when a chemical type is not found.

## FC/CYA Functions

```python
from pypoolchem.chemistry.fc_cya import (
    calculate_min_fc,
    calculate_target_fc,
    calculate_shock_fc,
    calculate_mustard_algae_shock_fc,
    is_fc_adequate,
)

def calculate_min_fc(cyanuric_acid: float, *, is_swg: bool = False) -> float: ...
def calculate_target_fc(cyanuric_acid: float, *, is_swg: bool = False) -> tuple[float, float]: ...
def calculate_shock_fc(cyanuric_acid: float) -> float: ...
def calculate_mustard_algae_shock_fc(cyanuric_acid: float) -> float: ...
def is_fc_adequate(free_chlorine: float, cyanuric_acid: float, *, is_swg: bool = False) -> bool: ...
```

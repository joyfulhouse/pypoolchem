# Water Chemistry Models

pypoolchem uses Pydantic models to represent water chemistry data. All models are immutable (frozen) to ensure data integrity.

## WaterChemistry

The primary model representing the current state of pool or spa water.

```python
from pypoolchem import WaterChemistry

water = WaterChemistry(
    ph=7.5,
    temperature_f=84,
    free_chlorine=3.0,
    combined_chlorine=0.0,
    calcium_hardness=300,
    total_alkalinity=80,
    cyanuric_acid=50,
    salt=0,
    borates=0,
    tds=1000,
)
```

### Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `ph` | float | required | 0-14 | Water pH level |
| `temperature_f` | float | required | 32-120 | Temperature in Fahrenheit |
| `free_chlorine` | float | 0 | ≥0 | Free chlorine in ppm |
| `combined_chlorine` | float | 0 | ≥0 | Combined chlorine (chloramines) in ppm |
| `calcium_hardness` | float | required | ≥0 | Calcium hardness in ppm as CaCO3 |
| `total_alkalinity` | float | required | ≥0 | Total alkalinity in ppm as CaCO3 |
| `cyanuric_acid` | float | 0 | ≥0 | Cyanuric acid (stabilizer) in ppm |
| `salt` | float | 0 | ≥0 | Salt level in ppm |
| `borates` | float | 0 | ≥0 | Borate level in ppm |
| `tds` | float | 1000 | ≥0 | Total dissolved solids in ppm |

### Computed Properties

```python
# Total chlorine (FC + CC)
water.total_chlorine  # 3.0

# Temperature in Celsius
water.temperature_c  # 28.89
```

### Validation

The model validates input ranges:

```python
# This will raise a ValidationError
water = WaterChemistry(ph=15.0, ...)  # pH must be 0-14
```

### Immutability

Models are frozen - you cannot modify them after creation:

```python
water = WaterChemistry(ph=7.5, ...)
water.ph = 7.6  # Raises an error!

# Instead, create a new instance
new_water = WaterChemistry(
    ph=7.6,
    temperature_f=water.temperature_f,
    # ... copy other fields
)
```

## Pool

Represents pool configuration including volume and type.

```python
from pypoolchem import Pool, PoolType, PoolSurface

pool = Pool(
    name="Backyard Pool",
    volume_gallons=15000,
    pool_type=PoolType.SWG,
    surface=PoolSurface.PLASTER,
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | required | Pool name/identifier |
| `volume_gallons` | float | required | Volume in US gallons |
| `pool_type` | PoolType | TRADITIONAL | Type of pool |
| `surface` | PoolSurface | PLASTER | Pool surface material |

### Pool Types

```python
from pypoolchem import PoolType

PoolType.TRADITIONAL  # Standard chlorine pool
PoolType.SWG          # Salt water generator pool
PoolType.SPA          # Hot tub or spa
```

### Pool Surfaces

```python
from pypoolchem import PoolSurface

PoolSurface.PLASTER     # Traditional plaster
PoolSurface.PEBBLE      # Pebble/aggregate finish
PoolSurface.TILE        # Tile surface
PoolSurface.FIBERGLASS  # Fiberglass shell
PoolSurface.VINYL       # Vinyl liner
```

### Computed Properties

```python
pool.volume_liters  # 56781.15
```

## TargetRanges

Defines acceptable ranges for all water chemistry parameters.

```python
from pypoolchem import get_target_ranges, PoolType

# Get pre-configured targets
targets = get_target_ranges(PoolType.TRADITIONAL)

# Access individual ranges
targets.ph.minimum   # 7.2
targets.ph.target    # 7.5
targets.ph.maximum   # 7.8

# Check if value is in range
targets.ph.is_in_range(7.6)  # True
targets.ph.is_low(7.0)       # True
targets.ph.is_high(8.0)      # True
```

### Pre-configured Target Ranges

#### Traditional Pool

| Parameter | Min | Target | Max |
|-----------|-----|--------|-----|
| pH | 7.2 | 7.5 | 7.8 |
| Total Alkalinity | 80 | 100 | 120 |
| Calcium Hardness | 200 | 300 | 400 |
| Cyanuric Acid | 30 | 50 | 80 |
| FC/CYA Ratio | 7.5% | 10% | - |

#### SWG Pool

| Parameter | Min | Target | Max |
|-----------|-----|--------|-----|
| pH | 7.4 | 7.6 | 7.8 |
| Total Alkalinity | 50 | 70 | 90 |
| Calcium Hardness | 200 | 350 | 450 |
| Cyanuric Acid | 60 | 70 | 90 |
| Salt | 2700 | 3200 | 3400 |
| FC/CYA Ratio | 4.5% | 7.5% | - |

#### Spa

| Parameter | Min | Target | Max |
|-----------|-----|--------|-----|
| pH | 7.4 | 7.6 | 7.8 |
| Total Alkalinity | 50 | 60 | 80 |
| Calcium Hardness | 120 | 150 | 200 |
| Cyanuric Acid | 20 | 30 | 40 |
| FC/CYA Ratio | 7.5% | 10% | - |

### Custom Target Ranges

Create custom targets for specific needs:

```python
from pypoolchem.models.targets import TargetRanges, ParameterRange

custom_targets = TargetRanges(
    ph=ParameterRange(minimum=7.4, target=7.6, maximum=7.8),
    total_alkalinity=ParameterRange(minimum=60, target=80, maximum=100),
    calcium_hardness=ParameterRange(minimum=250, target=350, maximum=450),
    cyanuric_acid=ParameterRange(minimum=40, target=60, maximum=80),
    salt=ParameterRange(minimum=3000, target=3400, maximum=3800),
    fc_min_factor=0.05,
    fc_target_factor=0.08,
)
```

## ParameterRange

Represents a range with minimum, target, and maximum values.

```python
from pypoolchem.models.targets import ParameterRange

ph_range = ParameterRange(minimum=7.2, target=7.5, maximum=7.8)

# Check values
ph_range.is_in_range(7.5)  # True
ph_range.is_low(7.0)       # True (below minimum)
ph_range.is_high(8.0)      # True (above maximum)
```

## Chemical

Represents a pool chemical with dosing properties.

```python
from pypoolchem import ChemicalType
from pypoolchem.dosing.chemicals import get_chemical

chemical = get_chemical(ChemicalType.BLEACH_12_5)

chemical.name           # "Bleach 12.5%"
chemical.multiplier     # 1250.0
chemical.unit           # "fl_oz"
chemical.affects        # "free_chlorine"
chemical.secondary_effects  # {} (none for bleach)
```

### Chemical Types

See [Chemical Dosing](dosing.md) for the complete list of 32 supported chemicals.

## DosingResult

Returned by dosing calculation functions.

```python
from pypoolchem import calculate_chlorine_dose, ChemicalType

result = calculate_chlorine_dose(
    current_fc=2.0,
    target_fc=5.0,
    pool_gallons=15000,
    chemical_type=ChemicalType.BLEACH_12_5,
)

result.chemical        # Chemical object
result.amount          # 36.0
result.unit            # "fl_oz"
result.amount_volume   # Volume equivalent (if applicable)
result.volume_unit     # "cups" (if applicable)
result.notes           # Additional information
```

## PoolShape

Enum for pool volume calculations.

```python
from pypoolchem import PoolShape, calculate_pool_volume

volume = calculate_pool_volume(
    shape=PoolShape.RECTANGULAR,
    length_ft=30,
    width_ft=15,
    avg_depth_ft=5,
)
# 16831.17 gallons
```

### Available Shapes

| Shape | Description |
|-------|-------------|
| `RECTANGULAR` | Standard rectangular pool |
| `OVAL` | Oval/elliptical pool |
| `ROUND` | Circular pool (use length as diameter) |
| `KIDNEY` | Kidney-shaped pool (~75% of rectangular) |
| `FREEFORM` | Irregular shape (~85% of rectangular) |

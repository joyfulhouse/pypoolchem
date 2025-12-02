# pypoolchem

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Type Checked](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)

A Python library for swimming pool and spa water chemistry calculations. Calculate water balance indices, chemical dosing recommendations, and predict chemistry changes with precision.

## Features

- **Water Balance Indices**: Calculate CSI (Calcium Saturation Index) and LSI (Langelier Saturation Index) to determine if water is corrosive, balanced, or scale-forming
- **Chemical Dosing**: Calculate precise doses for 32 different chemicals including chlorine, pH adjusters, alkalinity, calcium, stabilizer, salt, and borates
- **Effect Predictions**: Predict how adding chemicals will affect water chemistry before you add them
- **FC/CYA Relationships**: Calculate minimum, target, and shock chlorine levels based on cyanuric acid
- **Target Ranges**: Pre-configured targets for traditional pools, SWG pools, and spas
- **Pool Volume**: Calculate pool volume from dimensions for rectangular, oval, round, kidney, and freeform shapes
- **Fully Configurable**: Customize all formula constants and parameters
- **Type Safe**: Full type hints with mypy strict mode compliance
- **Immutable Models**: All data models are frozen for thread safety

## Installation

```bash
pip install pypoolchem
```

Or with uv:

```bash
uv add pypoolchem
```

## Quick Start

```python
from pypoolchem import (
    WaterChemistry,
    calculate_csi,
    interpret_csi,
    calculate_chlorine_dose,
    ChemicalType,
)

# Define current water chemistry
water = WaterChemistry(
    ph=7.5,
    temperature_f=84,
    free_chlorine=2.0,
    calcium_hardness=300,
    total_alkalinity=80,
    cyanuric_acid=50,
)

# Calculate water balance index
csi = calculate_csi(water)
print(f"CSI: {csi:.2f}")
print(interpret_csi(csi))
# CSI: -0.12
# Balanced (ideal)

# Calculate chlorine dose
result = calculate_chlorine_dose(
    current_fc=2.0,
    target_fc=5.0,
    pool_gallons=15000,
    chemical_type=ChemicalType.BLEACH_12_5,
)
print(f"Add {result.amount:.1f} {result.unit} of {result.chemical.name}")
# Add 36.0 fl_oz of Bleach 12.5%
```

## Water Balance

The CSI tells you if your water is corrosive (negative), balanced (ideal), or scale-forming (positive):

| CSI Range | Condition |
|-----------|-----------|
| ≤ -0.6 | Corrosive |
| -0.6 to -0.3 | Slightly corrosive |
| **-0.3 to +0.3** | **Balanced (ideal)** |
| +0.3 to +0.6 | Slightly scale-forming |
| ≥ +0.6 | Scale-forming |

```python
from pypoolchem import calculate_csi

# Using individual parameters
csi = calculate_csi(
    ph=7.5,
    temperature_f=84,
    calcium_hardness=300,
    total_alkalinity=80,
    cyanuric_acid=50,
    salt=3200,    # For SWG pools
    borates=30,   # If using borates
)
```

## Chemical Dosing

Calculate doses for any supported chemical:

```python
from pypoolchem import (
    calculate_ph_dose,
    calculate_alkalinity_dose,
    calculate_calcium_dose,
    calculate_cya_dose,
    calculate_salt_dose,
    ChemicalType,
)

# Lower pH with muriatic acid
ph_result = calculate_ph_dose(
    current_ph=7.8,
    target_ph=7.5,
    pool_gallons=15000,
    total_alkalinity=80,
)

# Raise alkalinity with baking soda
ta_result = calculate_alkalinity_dose(60, 80, 15000)

# Raise calcium with calcium chloride
ch_result = calculate_calcium_dose(200, 350, 15000)

# Raise stabilizer
cya_result = calculate_cya_dose(30, 50, 15000)

# Raise salt for SWG
salt_result = calculate_salt_dose(2800, 3200, 15000)
```

## Effect Predictions

See what will happen before adding chemicals:

```python
from pypoolchem import predict_effect, ChemicalType

# Predict effect of adding trichlor
new_water = predict_effect(
    water=water,
    chemical_type=ChemicalType.TRICHLOR,
    amount_oz=8,
    pool_gallons=15000,
)

print(f"FC: {water.free_chlorine} -> {new_water.free_chlorine}")
print(f"CYA: {water.cyanuric_acid} -> {new_water.cyanuric_acid}")
# Trichlor raises both FC and CYA
```

## Target Ranges

Get recommended targets by pool type:

```python
from pypoolchem import get_target_ranges, PoolType

targets = get_target_ranges(PoolType.SWG)

print(f"pH: {targets.ph.minimum} - {targets.ph.maximum}")
print(f"Salt: {targets.salt.minimum} - {targets.salt.maximum}")

# Check if value is in range
if targets.ph.is_in_range(7.6):
    print("pH is good!")
```

## FC/CYA Relationship

Calculate chlorine levels based on stabilizer:

```python
from pypoolchem.chemistry.fc_cya import (
    calculate_min_fc,
    calculate_target_fc,
    calculate_shock_fc,
)

cya = 50

min_fc = calculate_min_fc(cya)           # Minimum to prevent algae
low, high = calculate_target_fc(cya)     # Normal operating range
shock_fc = calculate_shock_fc(cya)       # SLAM level

print(f"Min FC: {min_fc}, Target: {low}-{high}, Shock: {shock_fc}")
# Min FC: 4, Target: 6-8, Shock: 20
```

## Pool Volume

Calculate volume from dimensions:

```python
from pypoolchem import calculate_pool_volume, PoolShape

volume = calculate_pool_volume(
    shape=PoolShape.RECTANGULAR,
    length_ft=30,
    width_ft=15,
    avg_depth_ft=5,
)
print(f"Pool volume: {volume:,.0f} gallons")
# Pool volume: 16,831 gallons
```

## Configuration

Customize calculation parameters:

```python
from pypoolchem import get_config, update_config, reset_config

# View current config
config = get_config()
print(f"LSI constant: {config.lsi_constant}")

# Update specific values
update_config(lsi_constant=12.14)

# Reset to defaults
reset_config()
```

## Supported Chemicals

pypoolchem supports 32 chemicals across these categories:

- **Chlorine**: Bleach (6%, 8.25%, 10%, 12.5%), Trichlor, Dichlor, Cal-Hypo (48-73%), Lithium Hypo
- **pH Down**: Muriatic Acid (14.5-34.6%), Dry Acid
- **pH Up**: Soda Ash, Borax
- **Alkalinity**: Baking Soda
- **Calcium**: Calcium Chloride (Anhydrous, Dihydrate)
- **Stabilizer**: CYA Granular, CYA Liquid
- **Salt**: Pool Salt
- **Borates**: Borax, Boric Acid, Sodium Tetraborate Pentahydrate

## Documentation

Full documentation is available in the [docs](docs/) directory:

- [Getting Started](docs/getting-started.md)
- [Water Chemistry Models](docs/models.md)
- [Chemistry Calculations](docs/chemistry.md)
- [Chemical Dosing](docs/dosing.md)
- [Effect Predictions](docs/effects.md)
- [Configuration](docs/configuration.md)
- [API Reference](docs/api-reference.md)

## Requirements

- Python 3.13+
- pydantic >= 2.12.5

## Development

```bash
# Clone repository
git clone https://github.com/joyfulhouse/pypoolchem.git
cd pypoolchem

# Install with dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Run linting
uv run ruff check src/pypoolchem

# Run type checking
uv run mypy src/pypoolchem --strict
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

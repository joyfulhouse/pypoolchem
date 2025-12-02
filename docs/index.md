# pypoolchem Documentation

**pypoolchem** is a Python library for swimming pool and spa water chemistry calculations. It provides accurate, well-documented calculations for water balance indices, chemical dosing recommendations, and target range validation.

## Features

- **Water Balance Indices**: Calculate CSI (Calcium Saturation Index) and LSI (Langelier Saturation Index) to determine if water is corrosive, balanced, or scale-forming
- **Chemical Dosing**: Calculate precise doses for chlorine, pH adjusters, alkalinity, calcium, stabilizer, salt, and borates
- **Effect Predictions**: Predict how adding chemicals will affect water chemistry before you add them
- **Target Ranges**: Pre-configured target ranges for traditional pools, salt water generator (SWG) pools, and spas
- **Fully Configurable**: Customize all formula constants and parameters
- **Type Safe**: Full type hints with mypy strict mode compliance
- **Async Compatible**: Pure functions suitable for async applications

## Quick Example

```python
from pypoolchem import (
    WaterChemistry,
    calculate_csi,
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

# Calculate water balance
csi = calculate_csi(water)
print(f"CSI: {csi:.2f}")  # CSI: -0.12 (balanced)

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

## Installation

```bash
pip install pypoolchem
```

Or with uv:

```bash
uv add pypoolchem
```

## Requirements

- Python 3.13 or higher
- pydantic >= 2.12.5

## Documentation Contents

- [Getting Started](getting-started.md) - Installation and basic usage
- [Water Chemistry Models](models.md) - Data models for water chemistry, pools, and targets
- [Chemistry Calculations](chemistry.md) - CSI, LSI, and factor calculations
- [Chemical Dosing](dosing.md) - Dosing calculations for all supported chemicals
- [Effect Predictions](effects.md) - Predicting chemistry changes
- [Configuration](configuration.md) - Customizing library behavior
- [API Reference](api-reference.md) - Complete API documentation

## Use Cases

### Home Automation Integration

pypoolchem is designed to integrate with home automation platforms like Home Assistant:

```python
from pypoolchem import WaterChemistry, calculate_csi, interpret_csi

# Get readings from sensors
water = WaterChemistry(
    ph=sensor_ph,
    temperature_f=sensor_temp,
    free_chlorine=sensor_fc,
    calcium_hardness=last_test_ch,
    total_alkalinity=last_test_ta,
    cyanuric_acid=last_test_cya,
)

# Calculate and interpret
csi = calculate_csi(water)
status = interpret_csi(csi)
# "Balanced (ideal)"
```

### Pool Service Applications

Calculate dosing for multiple pools:

```python
from pypoolchem import (
    calculate_chlorine_dose,
    calculate_ph_dose,
    calculate_alkalinity_dose,
    ChemicalType,
)

def generate_service_report(pool_gallons, current, target):
    doses = []

    if current.fc < target.fc:
        doses.append(calculate_chlorine_dose(
            current.fc, target.fc, pool_gallons
        ))

    if current.ph != target.ph:
        doses.append(calculate_ph_dose(
            current.ph, target.ph, pool_gallons, current.ta
        ))

    return doses
```

### Water Testing Applications

Validate test results against targets:

```python
from pypoolchem import get_target_ranges, PoolType, WaterChemistry

targets = get_target_ranges(PoolType.SWG)

water = WaterChemistry(ph=7.8, ...)

if targets.ph.is_high(water.ph):
    print("pH is above target range")
elif targets.ph.is_low(water.ph):
    print("pH is below target range")
else:
    print("pH is within target range")
```

## License

MIT License - see LICENSE file for details.

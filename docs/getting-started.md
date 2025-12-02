# Getting Started

This guide will help you install pypoolchem and start using it for pool chemistry calculations.

## Installation

### Using pip

```bash
pip install pypoolchem
```

### Using uv (recommended)

```bash
uv add pypoolchem
```

### From source

```bash
git clone https://github.com/joyfulhouse/pypoolchem.git
cd pypoolchem
uv sync --dev
```

## Requirements

- **Python 3.13+** - pypoolchem uses modern Python features like match statements and StrEnum
- **pydantic >= 2.12.5** - For data validation and models

## Basic Usage

### 1. Create a Water Chemistry Profile

The `WaterChemistry` model holds all the parameters that describe your pool water:

```python
from pypoolchem import WaterChemistry

water = WaterChemistry(
    ph=7.5,                    # pH level (0-14)
    temperature_f=84,          # Water temperature in Fahrenheit
    free_chlorine=3.0,         # Free chlorine in ppm
    calcium_hardness=300,      # Calcium hardness in ppm
    total_alkalinity=80,       # Total alkalinity in ppm
    cyanuric_acid=50,          # Stabilizer (CYA) in ppm
    salt=3200,                 # Salt level in ppm (for SWG pools)
    borates=30,                # Borate level in ppm (optional)
)
```

### 2. Calculate Water Balance Index

The CSI (Calcium Saturation Index) tells you if your water is corrosive, balanced, or scale-forming:

```python
from pypoolchem import calculate_csi, interpret_csi

csi = calculate_csi(water)
print(f"CSI: {csi:.2f}")
# CSI: -0.12

interpretation = interpret_csi(csi)
print(interpretation)
# "Balanced (ideal)"
```

**CSI Interpretation:**
| CSI Value | Condition |
|-----------|-----------|
| ≤ -0.6 | Corrosive (aggressive water) |
| -0.6 to -0.3 | Slightly corrosive |
| -0.3 to +0.3 | Balanced (ideal) |
| +0.3 to +0.6 | Slightly scale-forming |
| ≥ +0.6 | Scale-forming |

### 3. Calculate Chemical Doses

When you need to adjust your water chemistry, use the dosing calculators:

```python
from pypoolchem import (
    calculate_chlorine_dose,
    calculate_ph_dose,
    calculate_alkalinity_dose,
    ChemicalType,
)

# Raise chlorine from 2 ppm to 5 ppm
chlorine_dose = calculate_chlorine_dose(
    current_fc=2.0,
    target_fc=5.0,
    pool_gallons=15000,
    chemical_type=ChemicalType.BLEACH_12_5,
)
print(f"Add {chlorine_dose.amount:.1f} {chlorine_dose.unit}")
# Add 36.0 fl_oz

# Lower pH from 7.8 to 7.5
ph_dose = calculate_ph_dose(
    current_ph=7.8,
    target_ph=7.5,
    pool_gallons=15000,
    total_alkalinity=80,
    temperature_f=84,
)
print(f"Add {ph_dose.amount:.1f} {ph_dose.unit} of {ph_dose.chemical.name}")
# Add 12.5 fl_oz of Muriatic Acid 31.45%

# Raise alkalinity from 60 to 80 ppm
ta_dose = calculate_alkalinity_dose(
    current_ta=60,
    target_ta=80,
    pool_gallons=15000,
)
print(f"Add {ta_dose.amount:.1f} {ta_dose.unit}")
# Add 70.4 oz
```

### 4. Use Target Ranges

Get recommended target ranges based on pool type:

```python
from pypoolchem import get_target_ranges, PoolType

# For a salt water generator pool
targets = get_target_ranges(PoolType.SWG)

print(f"Target pH: {targets.ph.minimum} - {targets.ph.maximum}")
# Target pH: 7.4 - 7.8

print(f"Target Salt: {targets.salt.minimum} - {targets.salt.maximum}")
# Target Salt: 2700 - 3400

# Check if current value is in range
if targets.ph.is_in_range(water.ph):
    print("pH is good!")
```

**Available Pool Types:**
- `PoolType.TRADITIONAL` - Standard chlorine pools
- `PoolType.SWG` - Salt water generator pools
- `PoolType.SPA` - Hot tubs and spas

### 5. Predict Chemical Effects

Before adding chemicals, predict how they'll affect your water:

```python
from pypoolchem import predict_effect, ChemicalType

# Predict effect of adding 8 oz trichlor
new_water = predict_effect(
    water=water,
    chemical_type=ChemicalType.TRICHLOR,
    amount_oz=8,
    pool_gallons=15000,
)

print(f"Current FC: {water.free_chlorine} -> New FC: {new_water.free_chlorine}")
print(f"Current CYA: {water.cyanuric_acid} -> New CYA: {new_water.cyanuric_acid}")
# Trichlor raises both FC and CYA
```

## Common Workflows

### Weekly Maintenance Check

```python
from pypoolchem import (
    WaterChemistry,
    calculate_csi,
    get_target_ranges,
    PoolType,
    calculate_chlorine_dose,
    ChemicalType,
)

# Your test results
water = WaterChemistry(
    ph=7.6,
    temperature_f=82,
    free_chlorine=2.5,
    calcium_hardness=280,
    total_alkalinity=75,
    cyanuric_acid=45,
)

# Check water balance
csi = calculate_csi(water)
print(f"Water Balance (CSI): {csi:.2f}")

# Get targets for traditional pool
targets = get_target_ranges(PoolType.TRADITIONAL)

# Check what needs adjustment
issues = []

if targets.ph.is_high(water.ph):
    issues.append("pH is high - add acid")
elif targets.ph.is_low(water.ph):
    issues.append("pH is low - add soda ash")

# Calculate FC target based on CYA
min_fc = water.cyanuric_acid * targets.fc_min_factor
if water.free_chlorine < min_fc:
    dose = calculate_chlorine_dose(
        water.free_chlorine,
        min_fc,
        15000,  # your pool gallons
        ChemicalType.BLEACH_12_5,
    )
    issues.append(f"FC is low - add {dose.amount:.1f} {dose.unit} bleach")

if issues:
    print("Actions needed:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("Water chemistry looks good!")
```

### SLAM (Shock Level and Maintain)

```python
from pypoolchem.chemistry.fc_cya import calculate_shock_fc
from pypoolchem import calculate_chlorine_dose, ChemicalType

# Calculate shock level based on CYA
cya = 50
shock_fc = calculate_shock_fc(cya)
print(f"SLAM FC level: {shock_fc} ppm")
# SLAM FC level: 20 ppm

# Calculate how much bleach to reach shock level
current_fc = 3.0
dose = calculate_chlorine_dose(
    current_fc=current_fc,
    target_fc=shock_fc,
    pool_gallons=15000,
    chemical_type=ChemicalType.BLEACH_12_5,
)
print(f"Add {dose.amount:.1f} {dose.unit} to reach shock level")
```

## Next Steps

- [Water Chemistry Models](models.md) - Learn about all available data models
- [Chemistry Calculations](chemistry.md) - Deep dive into CSI, LSI, and factor calculations
- [Chemical Dosing](dosing.md) - Complete guide to dosing calculations
- [Configuration](configuration.md) - Customize library behavior

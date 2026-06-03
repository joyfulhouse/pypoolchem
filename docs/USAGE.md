# Usage Guide

Detailed usage for pypoolchem. See the [README](../README.md) for a quick
start.

## Core Workflows

### Water Balance

Calculate CSI (Calcium Saturation Index) and LSI (Langelier Saturation Index):

```python
from pypoolchem import WaterChemistry, calculate_csi, calculate_lsi, interpret_csi

water = WaterChemistry(
    ph=7.5,
    temperature_f=84,
    free_chlorine=2.0,
    calcium_hardness=300,
    total_alkalinity=80,
    cyanuric_acid=50,
)

csi = calculate_csi(water)
print(f"CSI: {csi:.2f} — {interpret_csi(csi)}")
```

### Chemical Dosing

```python
from pypoolchem import (
    calculate_chlorine_dose,
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

# Raise chlorine with 12.5% bleach
cl_result = calculate_chlorine_dose(
    current_fc=2.0,
    target_fc=5.0,
    pool_gallons=15000,
    chemical_type=ChemicalType.BLEACH_12_5,
)
```

### Effect Predictions

```python
from pypoolchem import predict_effect, ChemicalType

new_water = predict_effect(
    water=water,
    chemical_type=ChemicalType.TRICHLOR,
    amount_oz=8,
    pool_gallons=15000,
)
print(f"FC: {water.free_chlorine} -> {new_water.free_chlorine}")
print(f"CYA: {water.cyanuric_acid} -> {new_water.cyanuric_acid}")
```

### FC/CYA Relationship

```python
from pypoolchem.chemistry.fc_cya import (
    calculate_min_fc,
    calculate_target_fc,
    calculate_shock_fc,
)

cya = 50
min_fc = calculate_min_fc(cya)
low, high = calculate_target_fc(cya)
shock_fc = calculate_shock_fc(cya)
```

### Target Ranges

```python
from pypoolchem import get_target_ranges, PoolType

targets = get_target_ranges(PoolType.SWG)
if targets.ph.is_in_range(7.6):
    print("pH is good!")
```

### Pool Volume

```python
from pypoolchem import calculate_pool_volume, PoolShape

volume = calculate_pool_volume(
    shape=PoolShape.RECTANGULAR,
    length_ft=30,
    width_ft=15,
    avg_depth_ft=5,
)
```

## Error Handling

pypoolchem raises standard Python exceptions for invalid inputs. Pydantic
validation errors are raised for invalid `WaterChemistry` fields. No custom
exception hierarchy is required.

## Advanced

### Global Configuration

Override formula constants for specialized use cases:

```python
from pypoolchem import get_config, update_config, reset_config

update_config(lsi_constant=12.14)
# ... calculations ...
reset_config()  # restore defaults
```

See [configuration.md](configuration.md) for all available constants.

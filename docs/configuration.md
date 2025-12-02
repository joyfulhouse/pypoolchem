# Configuration

pypoolchem allows you to customize all formula constants and parameters without modifying the source code.

## Basic Usage

```python
from pypoolchem import get_config, set_config, update_config, reset_config

# Get current configuration
config = get_config()
print(f"LSI constant: {config.lsi_constant}")  # 12.1

# Update a specific value
update_config(lsi_constant=12.14)

# Verify change
config = get_config()
print(f"LSI constant: {config.lsi_constant}")  # 12.14

# Reset to defaults
reset_config()
```

## Configuration Object

The `PyPoolChemConfig` class contains all configurable parameters:

```python
from pypoolchem import PyPoolChemConfig

config = PyPoolChemConfig(
    # LSI constants
    lsi_constant=12.1,

    # CSI constants
    csi_ph_constant=11.677,
    csi_final_constant=4.7375,
    csi_temp_numerator=1412.5,
    csi_ionic_coefficient=2.56,
    csi_ionic_denominator_coefficient=1.65,

    # Carbonate alkalinity correction
    cya_coefficient=0.38772,
    cya_ph_constant=6.83,
    borate_coefficient=4.63,
    borate_ph_constant=9.11,

    # Ionic strength
    ionic_ch_coefficient=1.5,
    ionic_ta_coefficient=1.0,
    ionic_divisor=50045,
    ionic_nacl_divisor=58440,
    ch_to_nacl_ratio=1.1678,

    # Temperature factors (Fahrenheit -> factor)
    temperature_factors={
        32: 0.0, 37: 0.1, 45: 0.2, 53: 0.3,
        60: 0.4, 66: 0.5, 76: 0.6, 84: 0.7,
        94: 0.8, 105: 0.9,
    },

    # CYA correction factors by pH
    cya_correction_factors={
        7.0: 0.22, 7.2: 0.27, 7.4: 0.31, 7.5: 0.33,
        7.6: 0.33, 7.8: 0.35, 8.0: 0.38,
    },

    # Unit conversions
    gallons_to_liters=3.78541,
    cubic_feet_to_gallons=7.48052,
    oz_to_grams=28.3495,
    fl_oz_to_ml=29.5735,
)
```

## Configurable Parameters

### LSI Constants

| Parameter | Default | Description |
|-----------|---------|-------------|
| `lsi_constant` | 12.1 | Constant subtracted in LSI formula |

### CSI Constants

| Parameter | Default | Description |
|-----------|---------|-------------|
| `csi_ph_constant` | 11.677 | pH constant in CSI formula |
| `csi_final_constant` | 4.7375 | Final additive constant |
| `csi_temp_numerator` | 1412.5 | Temperature correction numerator |
| `csi_ionic_coefficient` | 2.56 | Ionic strength coefficient |
| `csi_ionic_denominator_coefficient` | 1.65 | Ionic denominator coefficient |

### Carbonate Alkalinity Correction

| Parameter | Default | Description |
|-----------|---------|-------------|
| `cya_coefficient` | 0.38772 | CYA correction coefficient |
| `cya_ph_constant` | 6.83 | CYA pH constant |
| `borate_coefficient` | 4.63 | Borate correction coefficient |
| `borate_ph_constant` | 9.11 | Borate pH constant |

### Ionic Strength

| Parameter | Default | Description |
|-----------|---------|-------------|
| `ionic_ch_coefficient` | 1.5 | CH coefficient for ionic strength |
| `ionic_ta_coefficient` | 1.0 | TA coefficient for ionic strength |
| `ionic_divisor` | 50045 | Ionic strength divisor |
| `ionic_nacl_divisor` | 58440 | NaCl divisor |
| `ch_to_nacl_ratio` | 1.1678 | CH to NaCl binding ratio |

### Temperature Factor Table

The `temperature_factors` dictionary maps temperature (°F) to factor values used in LSI calculation:

```python
config.temperature_factors = {
    32: 0.0,   # Freezing
    37: 0.1,
    45: 0.2,
    53: 0.3,
    60: 0.4,
    66: 0.5,
    76: 0.6,
    84: 0.7,   # Common pool temp
    94: 0.8,
    105: 0.9,  # Hot spa
}
```

Values between table entries are linearly interpolated.

### CYA Correction Factors

The `cya_correction_factors` dictionary maps pH to CYA correction factors used in LSI:

```python
config.cya_correction_factors = {
    7.0: 0.22,
    7.2: 0.27,
    7.4: 0.31,
    7.5: 0.33,
    7.6: 0.33,
    7.8: 0.35,
    8.0: 0.38,
}
```

### Unit Conversions

| Parameter | Default | Description |
|-----------|---------|-------------|
| `gallons_to_liters` | 3.78541 | US gallons to liters |
| `cubic_feet_to_gallons` | 7.48052 | Cubic feet to US gallons |
| `oz_to_grams` | 28.3495 | Ounces to grams |
| `fl_oz_to_ml` | 29.5735 | Fluid ounces to milliliters |

## Use Cases

### Regional Variations

Some regions use slightly different constants:

```python
from pypoolchem import update_config

# Use a different LSI constant
update_config(lsi_constant=12.14)
```

### Extended Temperature Range

Add temperature factors for extreme conditions:

```python
from pypoolchem import get_config, set_config

config = get_config()
config.temperature_factors[110] = 0.95  # Very hot spa
config.temperature_factors[25] = -0.1   # Near freezing
set_config(config)
```

### Custom Calculation Parameters

Adjust formula constants based on your specific water chemistry:

```python
from pypoolchem import PyPoolChemConfig, set_config

# Custom config for high-TDS water
custom = PyPoolChemConfig(
    ionic_divisor=48000,  # Adjusted for high TDS
    ionic_nacl_divisor=56000,
)
set_config(custom)
```

## Thread Safety

Configuration is stored in a global variable. If you're using pypoolchem in a multi-threaded application, be aware that configuration changes affect all threads.

For thread-safe usage, set configuration once at application startup before spawning threads:

```python
import pypoolchem

def main():
    # Configure once at startup
    pypoolchem.update_config(lsi_constant=12.14)

    # Now safe to use from multiple threads
    ...
```

## Persistence

Configuration is not automatically persisted. To maintain configuration across restarts:

```python
import json
from pypoolchem import PyPoolChemConfig, get_config, set_config

# Save configuration
def save_config(filepath: str):
    config = get_config()
    with open(filepath, 'w') as f:
        json.dump(config.model_dump(), f)

# Load configuration
def load_config(filepath: str):
    with open(filepath) as f:
        data = json.load(f)
    config = PyPoolChemConfig(**data)
    set_config(config)
```

## Validation

The configuration uses Pydantic validation. Invalid values will raise errors:

```python
from pypoolchem import update_config
from pydantic import ValidationError

try:
    update_config(lsi_constant="not a number")
except ValidationError as e:
    print("Invalid configuration value")
```

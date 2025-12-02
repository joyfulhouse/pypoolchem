# Effect Predictions

pypoolchem can predict how adding chemicals will affect your water chemistry before you actually add them.

## Basic Usage

```python
from pypoolchem import WaterChemistry, predict_effect, ChemicalType

# Current water chemistry
water = WaterChemistry(
    ph=7.5,
    temperature_f=84,
    free_chlorine=2.0,
    calcium_hardness=300,
    total_alkalinity=80,
    cyanuric_acid=50,
)

# Predict effect of adding 8 oz trichlor
new_water = predict_effect(
    water=water,
    chemical_type=ChemicalType.TRICHLOR,
    amount_oz=8,
    pool_gallons=15000,
)

print(f"FC: {water.free_chlorine} -> {new_water.free_chlorine}")
print(f"CYA: {water.cyanuric_acid} -> {new_water.cyanuric_acid}")
print(f"pH: {water.ph} -> {new_water.ph}")
```

Output:
```
FC: 2.0 -> 2.8
CYA: 50.0 -> 50.5
pH: 7.5 -> 7.48
```

## How It Works

The prediction uses each chemical's effect multipliers:

```
new_value = current_value + (amount_oz / pool_gallons) * multiplier
```

For chemicals with secondary effects (like trichlor which raises CYA while adding chlorine), all effects are calculated.

## Multiple Chemical Additions

Predict the cumulative effect of adding multiple chemicals:

```python
from pypoolchem.effects.predictions import predict_multiple_effects

additions = [
    (ChemicalType.MURIATIC_ACID_31_45, 16),  # Lower pH
    (ChemicalType.BLEACH_12_5, 64),           # Raise FC
]

new_water = predict_multiple_effects(
    water=water,
    additions=additions,
    pool_gallons=15000,
)

print(f"pH: {water.ph} -> {new_water.ph}")
print(f"FC: {water.free_chlorine} -> {new_water.free_chlorine}")
```

Chemicals are applied in sequence, so order can matter for accurate predictions.

## Use Cases

### Planning Chemical Additions

Before a service visit, predict what levels will be after treatment:

```python
from pypoolchem import calculate_chlorine_dose, predict_effect

# Calculate needed dose
dose = calculate_chlorine_dose(
    current_fc=2.0,
    target_fc=5.0,
    pool_gallons=15000,
    chemical_type=ChemicalType.BLEACH_12_5,
)

# Predict result
predicted = predict_effect(
    water=water,
    chemical_type=ChemicalType.BLEACH_12_5,
    amount_oz=dose.amount,
    pool_gallons=15000,
)

print(f"Predicted FC after treatment: {predicted.free_chlorine}")
```

### Avoiding Unwanted Side Effects

Check if a chemical will push other parameters out of range:

```python
from pypoolchem import get_target_ranges, PoolType

targets = get_target_ranges(PoolType.TRADITIONAL)

# Want to add trichlor for chlorine
predicted = predict_effect(
    water=water,
    chemical_type=ChemicalType.TRICHLOR,
    amount_oz=16,
    pool_gallons=15000,
)

# Check if CYA will go too high
if targets.cyanuric_acid.is_high(predicted.cyanuric_acid):
    print("Warning: CYA will exceed target range!")
    print("Consider using liquid chlorine instead.")
```

### Comparing Chemical Options

Compare different chemicals to see which has fewer side effects:

```python
options = [
    ChemicalType.BLEACH_12_5,
    ChemicalType.TRICHLOR,
    ChemicalType.CAL_HYPO_73,
]

for chemical_type in options:
    predicted = predict_effect(
        water=water,
        chemical_type=chemical_type,
        amount_oz=8,
        pool_gallons=15000,
    )

    print(f"\n{chemical_type.value}:")
    print(f"  FC: {water.free_chlorine} -> {predicted.free_chlorine}")
    print(f"  CYA: {water.cyanuric_acid} -> {predicted.cyanuric_acid}")
    print(f"  CH: {water.calcium_hardness} -> {predicted.calcium_hardness}")
    print(f"  pH: {water.ph} -> {predicted.ph}")
```

## Chemical Effects Reference

### Chlorine Sources

| Chemical | Primary | Secondary Effects |
|----------|---------|-------------------|
| Bleach (all %) | +FC | None |
| Trichlor | +FC | +CYA, -pH |
| Dichlor | +FC | +CYA, -pH |
| Cal-Hypo | +FC | +CH |
| Lithium Hypo | +FC | None |
| Chlorine Gas | +FC | -pH |

### pH Adjusters

| Chemical | Primary | Secondary Effects |
|----------|---------|-------------------|
| Muriatic Acid | -pH | -TA |
| Dry Acid | -pH | -TA |
| Soda Ash | +pH | +TA |
| Borax | +pH | +Borates |

### Other Chemicals

| Chemical | Primary | Secondary Effects |
|----------|---------|-------------------|
| Baking Soda | +TA | Slight +pH |
| Calcium Chloride | +CH | None |
| CYA (Granular/Liquid) | +CYA | Slight -pH |
| Pool Salt | +Salt | None |
| Boric Acid | +Borates | None* |
| Borax (for borates) | +Borates | +pH |

*Boric acid requires acid to neutralize

## Limitations

1. **Simplified pH model** - pH effects are linearized approximations. Actual pH changes depend on complex buffering interactions.

2. **No time factor** - Predictions assume instantaneous mixing. Real pools take time to circulate.

3. **No temperature effects** - Predictions don't account for temperature-dependent solubility.

4. **No loss factors** - Chlorine loss from sunlight, bather load, etc. is not modeled.

For best results, use predictions as estimates and verify with actual testing.

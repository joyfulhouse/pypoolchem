# Chemical Dosing

pypoolchem calculates precise chemical doses based on pool volume, current levels, and target levels.

## Basic Dosing Formula

Most chemicals follow this formula:

```
dose_oz = (target - current) * pool_gallons / multiplier
```

Where `multiplier` is specific to each chemical and accounts for concentration and purity.

## Chlorine Dosing

### Liquid Chlorine (Bleach)

```python
from pypoolchem import calculate_chlorine_dose, ChemicalType

result = calculate_chlorine_dose(
    current_fc=2.0,
    target_fc=5.0,
    pool_gallons=15000,
    chemical_type=ChemicalType.BLEACH_12_5,
)

print(f"Add {result.amount:.1f} {result.unit}")
# Add 36.0 fl_oz
```

### Available Chlorine Types

| ChemicalType | Name | Primary Effect | Secondary Effects |
|--------------|------|----------------|-------------------|
| `BLEACH_6` | Bleach 6% | FC | None |
| `BLEACH_8_25` | Bleach 8.25% | FC | None |
| `BLEACH_10` | Bleach 10% | FC | None |
| `BLEACH_12_5` | Bleach 12.5% | FC | None |
| `TRICHLOR` | Trichlor 90% | FC | Raises CYA, lowers pH |
| `DICHLOR` | Dichlor 56% | FC | Raises CYA, lowers pH |
| `CAL_HYPO_48` | Cal-Hypo 48% | FC | Raises CH |
| `CAL_HYPO_53` | Cal-Hypo 53% | FC | Raises CH |
| `CAL_HYPO_65` | Cal-Hypo 65% | FC | Raises CH |
| `CAL_HYPO_73` | Cal-Hypo 73% | FC | Raises CH |
| `LITHIUM_HYPO` | Lithium Hypochlorite 35% | FC | None |
| `CHLORINE_GAS` | Chlorine Gas | FC | Lowers pH |

### Chlorine Comparison

For raising FC by 3 ppm in a 15,000 gallon pool:

| Chemical | Amount | Unit | Notes |
|----------|--------|------|-------|
| Bleach 6% | 75.0 | fl_oz | Cheapest, no side effects |
| Bleach 12.5% | 36.0 | fl_oz | Most common |
| Trichlor | 6.6 | oz | Also adds CYA |
| Cal-Hypo 73% | 7.4 | oz | Also adds calcium |

## pH Dosing

pH adjustment is complex because it depends on temperature, total alkalinity, and borates.

### Lowering pH

```python
from pypoolchem import calculate_ph_dose, ChemicalType

result = calculate_ph_dose(
    current_ph=7.8,
    target_ph=7.5,
    pool_gallons=15000,
    total_alkalinity=80,
    temperature_f=84,
    borates=0,
)

print(f"Add {result.amount:.1f} {result.unit} of {result.chemical.name}")
# Add 12.5 fl_oz of Muriatic Acid 31.45%
```

### Raising pH

```python
result = calculate_ph_dose(
    current_ph=7.2,
    target_ph=7.5,
    pool_gallons=15000,
    total_alkalinity=80,
    temperature_f=84,
)

print(f"Add {result.amount:.1f} {result.unit} of {result.chemical.name}")
# Add 8.3 oz of Soda Ash
```

### Available pH Adjusters

**Acids (Lower pH):**

| ChemicalType | Name | Notes |
|--------------|------|-------|
| `MURIATIC_ACID_14_5` | Muriatic Acid 14.5% | 10° Baumé |
| `MURIATIC_ACID_15_7` | Muriatic Acid 15.7% | |
| `MURIATIC_ACID_20` | Muriatic Acid 20% | 22° Baumé |
| `MURIATIC_ACID_28_3` | Muriatic Acid 28.3% | |
| `MURIATIC_ACID_31_45` | Muriatic Acid 31.45% | 20° Baumé (most common) |
| `MURIATIC_ACID_34_6` | Muriatic Acid 34.6% | |
| `DRY_ACID` | Sodium Bisulfate | Granular, easier to handle |

**Bases (Raise pH):**

| ChemicalType | Name | Notes |
|--------------|------|-------|
| `SODA_ASH` | Sodium Carbonate | Primary pH increaser |
| `BORAX` | 20 Mule Team Borax | Also raises borates |

### pH Dosing Factors

Higher alkalinity requires more acid/base to change pH:

```python
# Same pH change, different TA levels
low_ta = calculate_ph_dose(7.8, 7.5, 15000, total_alkalinity=60)
high_ta = calculate_ph_dose(7.8, 7.5, 15000, total_alkalinity=120)

print(f"TA 60: {low_ta.amount:.1f} fl_oz")   # ~9 fl_oz
print(f"TA 120: {high_ta.amount:.1f} fl_oz") # ~18 fl_oz
```

## Alkalinity Dosing

### Raising Alkalinity

```python
from pypoolchem import calculate_alkalinity_dose

result = calculate_alkalinity_dose(
    current_ta=60,
    target_ta=80,
    pool_gallons=15000,
)

print(f"Add {result.amount:.1f} {result.unit}")
# Add 70.4 oz of baking soda
```

### Lowering Alkalinity

Alkalinity can only be lowered with acid + aeration. The function returns a note explaining this:

```python
result = calculate_alkalinity_dose(
    current_ta=120,
    target_ta=80,
    pool_gallons=15000,
)

print(result.notes)
# "TA is already at or above target. Lower TA with acid + aeration."
```

To lower TA:
1. Add acid to lower pH to ~7.0
2. Aerate to raise pH back up (drives off CO2)
3. Repeat until TA reaches target

## Calcium Hardness Dosing

### Raising Calcium

```python
from pypoolchem import calculate_calcium_dose, ChemicalType

result = calculate_calcium_dose(
    current_ch=200,
    target_ch=350,
    pool_gallons=15000,
    chemical_type=ChemicalType.CALCIUM_CHLORIDE_DIHYDRATE,
)

print(f"Add {result.amount:.1f} {result.unit}")
# Add 44.2 oz
```

### Available Calcium Products

| ChemicalType | Name | Notes |
|--------------|------|-------|
| `CALCIUM_CHLORIDE_ANHYDROUS` | Calcium Chloride 94-97% | More concentrated |
| `CALCIUM_CHLORIDE_DIHYDRATE` | Calcium Chloride 77-80% | Common "flake" form |

### Lowering Calcium

Calcium can only be lowered by water replacement:

```python
from pypoolchem.dosing.calculator import calculate_water_replacement

replacement_pct = calculate_water_replacement(
    current_value=500,  # Current CH
    target_value=350,   # Target CH
    fill_water_value=100,  # CH in your fill water
)

print(f"Replace {replacement_pct:.1f}% of pool water")
# Replace 37.5% of pool water
```

## Cyanuric Acid (Stabilizer) Dosing

### Raising CYA

```python
from pypoolchem import calculate_cya_dose

result = calculate_cya_dose(
    current_cya=30,
    target_cya=50,
    pool_gallons=15000,
)

print(f"Add {result.amount:.1f} {result.unit}")
# Add 40.1 oz
```

### Available CYA Products

| ChemicalType | Name | Notes |
|--------------|------|-------|
| `CYA_GRANULAR` | Cyanuric Acid Granular | Dissolve in sock/bucket |
| `CYA_LIQUID` | Cyanuric Acid Liquid | Easier to dose |

### Lowering CYA

CYA can only be lowered by water replacement:

```python
replacement_pct = calculate_water_replacement(
    current_value=80,
    target_value=50,
)

print(f"Replace {replacement_pct:.1f}% of pool water")
# Replace 37.5% of pool water
```

## Salt Dosing

For salt water generator (SWG) pools.

```python
from pypoolchem import calculate_salt_dose

result = calculate_salt_dose(
    current_salt=2800,
    target_salt=3200,
    pool_gallons=15000,
)

print(f"Add {result.amount:.1f} {result.unit}")
# Add 50.1 lbs
```

**Note:** Salt dose is returned in pounds (lbs), not ounces.

## Borate Dosing

Borates improve water feel and help stabilize pH.

```python
from pypoolchem import calculate_borate_dose, ChemicalType

result = calculate_borate_dose(
    current_borates=0,
    target_borates=30,
    pool_gallons=15000,
    chemical_type=ChemicalType.BORAX_BORATE,
)

print(f"Add {result.amount:.1f} {result.unit}")
# Add 529.5 oz
if result.notes:
    print(result.notes)
```

### Available Borate Products

| ChemicalType | Name | Notes |
|--------------|------|-------|
| `BORAX_BORATE` | 20 Mule Team Borax | Also raises pH |
| `BORIC_ACID` | Boric Acid | Requires acid to neutralize |
| `SODIUM_TETRABORATE_PENTAHYDRATE` | ProTeam Supreme Plus | Requires acid to neutralize |

When using boric acid or sodium tetraborate, the result includes a note about required acid:

```python
result = calculate_borate_dose(0, 30, 15000, ChemicalType.BORIC_ACID)
print(result.notes)
# "Requires 206.4 fl oz muriatic acid (31.45%) to neutralize"
```

## DosingResult Object

All dosing functions return a `DosingResult` with consistent properties:

```python
result = calculate_chlorine_dose(2.0, 5.0, 15000)

result.chemical        # Chemical object with full details
result.chemical.name   # "Bleach 12.5%"
result.amount          # 36.0 (primary amount)
result.unit            # "fl_oz"
result.amount_volume   # 4.5 (volume equivalent, if applicable)
result.volume_unit     # "cups"
result.notes           # Additional information (if any)
```

## Water Replacement Calculator

For parameters that can only be lowered by dilution:

```python
from pypoolchem.dosing.calculator import calculate_water_replacement

# CYA from 80 to 50 (no CYA in fill water)
pct = calculate_water_replacement(80, 50, fill_water_value=0)
# 37.5%

# CH from 500 to 350 (fill water has 100 ppm CH)
pct = calculate_water_replacement(500, 350, fill_water_value=100)
# 37.5%
```

## Best Practices

1. **Add chemicals gradually** - Don't add more than the recommended amount at once
2. **Wait between additions** - Allow 30 minutes to 1 hour for circulation
3. **Test after adding** - Verify levels before adding more
4. **Consider secondary effects** - Trichlor adds CYA, Cal-Hypo adds calcium
5. **Pre-dissolve when needed** - CYA and calcium chloride should be pre-dissolved
6. **Add acid slowly** - Add in front of a return jet with pump running

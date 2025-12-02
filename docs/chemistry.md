# Chemistry Calculations

pypoolchem provides calculations for water balance indices and the underlying factors that determine water chemistry behavior.

## Water Balance Indices

Water balance indices indicate whether your pool water is corrosive (will dissolve surfaces), balanced (ideal), or scale-forming (will deposit calcium scale).

### Calcium Saturation Index (CSI)

CSI is the more comprehensive water balance calculation that accounts for:
- Cyanuric acid's effect on alkalinity
- Borate's effect on alkalinity
- Ionic strength from salt
- Temperature effects

```python
from pypoolchem import WaterChemistry, calculate_csi, interpret_csi

water = WaterChemistry(
    ph=7.5,
    temperature_f=84,
    calcium_hardness=300,
    total_alkalinity=80,
    cyanuric_acid=50,
    salt=3200,
    borates=30,
)

csi = calculate_csi(water)
print(f"CSI: {csi:.2f}")  # CSI: -0.08

interpretation = interpret_csi(csi)
print(interpretation)  # "Balanced (ideal)"
```

#### CSI Formula

```
CSI = pH - 11.677 + log10(CH) + log10(CarbAlk)
      - (2.56 * sqrt(Ionic)) / (1 + 1.65 * sqrt(Ionic))
      - 1412.5 / (T_celsius + 273.15) + 4.7375
```

Where:
- `CarbAlk` = Carbonate alkalinity (TA corrected for CYA and borates)
- `Ionic` = Ionic strength based on CH, TA, and salt
- `T_celsius` = Temperature in Celsius

#### CSI Interpretation

| CSI Range | Condition | Description |
|-----------|-----------|-------------|
| ≤ -0.6 | Corrosive | Aggressive water, will etch plaster and corrode metal |
| -0.6 to -0.3 | Slightly corrosive | May cause slow corrosion over time |
| -0.3 to +0.3 | Balanced | Ideal range, water is stable |
| +0.3 to +0.6 | Slightly scale-forming | May form light scale deposits |
| ≥ +0.6 | Scale-forming | Scale formation likely on surfaces and equipment |

#### Using Individual Parameters

You can also calculate CSI without creating a WaterChemistry object:

```python
csi = calculate_csi(
    ph=7.5,
    temperature_f=84,
    calcium_hardness=300,
    total_alkalinity=80,
    cyanuric_acid=50,
    salt=3200,
    borates=30,
)
```

### Langelier Saturation Index (LSI)

LSI is the traditional water balance formula. It's simpler than CSI but doesn't account for as many factors.

```python
from pypoolchem import calculate_lsi
from pypoolchem.chemistry.lsi import interpret_lsi

water = WaterChemistry(
    ph=7.5,
    temperature_f=84,
    calcium_hardness=300,
    total_alkalinity=80,
    cyanuric_acid=50,
)

lsi = calculate_lsi(water)
print(f"LSI: {lsi:.2f}")

interpretation = interpret_lsi(lsi)
print(interpretation)  # "Green - Ideal (perfectly balanced)"
```

#### LSI Formula

```
LSI = pH + TF + CF + AF - 12.1
```

Where:
- `TF` = Temperature Factor (from lookup table)
- `CF` = Calcium Factor = log10(CH)
- `AF` = Alkalinity Factor = log10(Carbonate Alkalinity)

#### LSI Interpretation

| LSI Range | Color | Condition |
|-----------|-------|-----------|
| ≤ -0.31 | Red | Aggressive (corrosive) |
| -0.30 to -0.01 | Yellow | Acceptable (close to balanced) |
| 0.00 to +0.30 | Green | Ideal (perfectly balanced) |
| ≥ +0.31 | Purple | Over-saturated (scale-forming) |

### CSI vs LSI: When to Use Each

| Factor | CSI | LSI |
|--------|-----|-----|
| Accounts for CYA | Yes (detailed formula) | Yes (simplified) |
| Accounts for borates | Yes | No |
| Accounts for salt | Yes | No |
| Ionic strength correction | Yes | No |
| Best for | Pools with CYA/salt/borates | Simple pools without additives |

**Recommendation:** Use CSI for most modern pools, especially SWG pools. Use LSI for simple pools without stabilizer or salt.

## Factor Calculations

These underlying calculations are used by CSI and LSI but can also be called directly.

### Carbonate Alkalinity

Total alkalinity includes contributions from cyanuric acid and borates that don't affect water balance. Carbonate alkalinity is the corrected value.

```python
from pypoolchem import calculate_carbonate_alkalinity

carb_alk = calculate_carbonate_alkalinity(
    total_alkalinity=80,
    cyanuric_acid=50,
    ph=7.5,
    borates=30,
)
print(f"Carbonate Alkalinity: {carb_alk:.1f} ppm")
# Carbonate Alkalinity: 72.3 ppm
```

#### Formula

```
CarbAlk = TA - (0.38772 * CYA) / (1 + 10^(6.83 - pH))
             - (4.63 * Borate) / (1 + 10^(9.11 - pH))
```

### Ionic Strength

Ionic strength affects the activity of calcium and carbonate ions, which is important for accurate CSI calculation.

```python
from pypoolchem import calculate_ionic_strength

ionic = calculate_ionic_strength(
    calcium_hardness=300,
    total_alkalinity=80,
    salt=3200,
)
print(f"Ionic Strength: {ionic:.4f}")
# Ionic Strength: 0.0545
```

#### Formula

```
extra_NaCl = max(0, Salt - 1.1678 * CH)
Ionic = (1.5 * CH + TA) / 50045 + extra_NaCl / 58440
```

### Temperature Factor

Used in LSI calculation. Warmer water holds less CO2, affecting the saturation index.

```python
from pypoolchem import calculate_temperature_factor

tf = calculate_temperature_factor(84)  # 84°F
print(f"Temperature Factor: {tf}")
# Temperature Factor: 0.7
```

#### Temperature Factor Table

| Temperature (°F) | Factor |
|-----------------|--------|
| 32 | 0.0 |
| 37 | 0.1 |
| 45 | 0.2 |
| 53 | 0.3 |
| 60 | 0.4 |
| 66 | 0.5 |
| 76 | 0.6 |
| 84 | 0.7 |
| 94 | 0.8 |
| 105 | 0.9 |

Values between table entries are linearly interpolated.

## FC/CYA Relationship

The relationship between free chlorine and cyanuric acid is critical for effective sanitization. Higher CYA levels require higher FC levels.

### Minimum FC

The absolute minimum FC level to prevent algae growth:

```python
from pypoolchem.chemistry.fc_cya import calculate_min_fc

# Non-SWG pool
min_fc = calculate_min_fc(cyanuric_acid=50, is_swg=False)
print(f"Minimum FC: {min_fc} ppm")  # 4 ppm

# SWG pool (can run lower FC)
min_fc_swg = calculate_min_fc(cyanuric_acid=70, is_swg=True)
print(f"Minimum FC (SWG): {min_fc_swg} ppm")  # 3 ppm
```

### Target FC

The recommended FC range for normal operation:

```python
from pypoolchem.chemistry.fc_cya import calculate_target_fc

low, high = calculate_target_fc(cyanuric_acid=50, is_swg=False)
print(f"Target FC: {low} - {high} ppm")  # 6 - 8 ppm
```

### Shock FC (SLAM Level)

The FC level needed to kill algae during a SLAM (Shock Level and Maintain) process:

```python
from pypoolchem.chemistry.fc_cya import calculate_shock_fc

shock = calculate_shock_fc(cyanuric_acid=50)
print(f"Shock FC: {shock} ppm")  # 20 ppm
```

### Mustard Algae Shock FC

Mustard (yellow) algae requires even higher FC levels:

```python
from pypoolchem.chemistry.fc_cya import calculate_mustard_algae_shock_fc

mustard_shock = calculate_mustard_algae_shock_fc(cyanuric_acid=50)
print(f"Mustard Algae Shock: {mustard_shock} ppm")  # 29 ppm
```

### FC Adequacy Check

Quick check if current FC is sufficient:

```python
from pypoolchem.chemistry.fc_cya import is_fc_adequate

adequate = is_fc_adequate(
    free_chlorine=5.0,
    cyanuric_acid=50,
    is_swg=False,
)
print(f"FC adequate: {adequate}")  # True
```

### FC/CYA Guidelines Table

| CYA (ppm) | Min FC | Target FC | Shock FC |
|-----------|--------|-----------|----------|
| 0 | 1 | 3 | 10 |
| 30 | 3 | 4-6 | 12 |
| 40 | 4 | 5-7 | 16 |
| 50 | 4 | 6-8 | 20 |
| 60 | 5 | 7-9 | 24 |
| 70 | 6 | 8-10 | 28 |
| 80 | 7 | 9-11 | 32 |

## Error Handling

Chemistry calculations can fail if parameters are invalid:

```python
from pypoolchem import calculate_csi
from pypoolchem.exceptions import CalculationError

try:
    csi = calculate_csi(
        ph=7.5,
        temperature_f=84,
        calcium_hardness=0,  # Invalid!
        total_alkalinity=80,
    )
except CalculationError as e:
    print(f"Calculation failed: {e}")
    # "Calcium hardness must be greater than 0"
```

Common errors:
- Calcium hardness ≤ 0
- Carbonate alkalinity ≤ 0 (CYA correction exceeds TA)
- Missing required parameters

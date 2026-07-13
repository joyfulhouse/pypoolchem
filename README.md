# pypoolchem

Python library for swimming pool and spa water chemistry calculations.

[![PyPI Version][pypi-shield]][pypi]
[![Python Versions][pyversions-shield]][pypi]
[![License][license-shield]](LICENSE)
[![CI][ci-shield]][ci]
[![GitHub Sponsors][sponsors-shield]][sponsors]
[![Ko-fi][kofi-shield]][kofi]

## What It Does

pypoolchem provides precise water chemistry calculations for swimming pools and
spas. It calculates water balance indices (CSI and LSI), generates accurate
chemical dosing recommendations for 32 supported chemicals, and predicts how
adding a chemical will change your water before you add it.

## Features

- **Water Balance Indices**: Calculate CSI (Calcium Saturation Index) and LSI
  (Langelier Saturation Index) to determine if water is corrosive, balanced, or
  scale-forming.
- **Chemical Dosing**: Precise doses for 32 chemicals including chlorine, pH
  adjusters, alkalinity, calcium, stabilizer, salt, and borates.
- **Effect Predictions**: Predict how adding a chemical will affect water
  chemistry before you add it.
- **FC/CYA Relationships**: Calculate minimum, target, and shock chlorine levels
  based on cyanuric acid concentration.
- **Target Ranges**: Pre-configured targets for traditional pools, SWG pools,
  and spas.
- **Pool Volume**: Calculate pool volume from dimensions for rectangular, oval,
  round, kidney, and freeform shapes.
- **Fully Configurable**: Customize all formula constants and parameters.
- **Type Safe**: Full type hints with mypy strict-mode compliance and immutable
  frozen models for thread safety.

## Installation

See **[INSTALL.md](INSTALL.md)** for the complete guide.

```bash
pip install pypoolchem
# or
uv add pypoolchem
```

Requires Python 3.13+.

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

## Usage

See [docs/USAGE.md](docs/USAGE.md) for the full usage guide with examples for
each feature. Key workflows:

- **Water balance** — CSI/LSI calculation and interpretation
- **Chemical dosing** — doses for chlorine, pH, alkalinity, calcium, CYA, salt, borates
- **Effect predictions** — simulate chemistry changes before adding a chemical
- **FC/CYA relationships** — minimum, target, and shock FC levels
- **Pool volume** — volume from dimensions for five pool shapes
- **Configuration** — customize formula constants globally

## API Reference

Full API reference lives in [docs/](docs/). Key entry points:

| Symbol | Description |
|---|---|
| `WaterChemistry` | Immutable water chemistry measurement model |
| `calculate_csi(water)` | Calcium Saturation Index |
| `calculate_lsi(water)` | Langelier Saturation Index |
| `calculate_chlorine_dose(...)` | Chlorine dosing |
| `calculate_ph_dose(...)` | pH dosing |
| `calculate_alkalinity_dose(...)` | Alkalinity dosing |
| `predict_effect(water, chemical_type, ...)` | Predict chemistry change |
| `get_target_ranges(pool_type)` | Target ranges by pool type |
| `calculate_pool_volume(shape, ...)` | Pool volume from dimensions |
| `ChemicalType` | Enum of all 32 supported chemicals |

## Development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md). In short:

```bash
git clone https://github.com/joyfulhouse/pypoolchem.git
cd pypoolchem
uv sync
uv run pytest
uv run ruff check
uv run mypy
```

## Support

- Join the [JoyfulHouse Discord](https://discord.gg/gc4eTPwxjJ) for support and discussion across all JoyfulHouse Home Assistant integrations and libraries.
- **Issues:** <https://github.com/joyfulhouse/pypoolchem/issues>
- **PyPI:** <https://pypi.org/project/pypoolchem/>

## Support Development

If this library is useful to you, please consider supporting its development:

- [GitHub Sponsors][sponsors]
- [Ko-fi][kofi]

## License

This project is licensed under the **MIT** License — see [LICENSE](LICENSE) for
details.

## Related Projects

- [Pool Chem](https://github.com/joyfulhouse/ha-poolchem) — the Home Assistant
  integration built on this library.

<!-- Badge links -->
[pypi-shield]: https://img.shields.io/pypi/v/pypoolchem.svg?style=for-the-badge
[pypi]: https://pypi.org/project/pypoolchem/
[pyversions-shield]: https://img.shields.io/pypi/pyversions/pypoolchem.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/joyfulhouse/pypoolchem.svg?style=for-the-badge
[ci-shield]: https://img.shields.io/github/actions/workflow/status/joyfulhouse/pypoolchem/ci.yml?style=for-the-badge&label=CI
[ci]: https://github.com/joyfulhouse/pypoolchem/actions
[sponsors-shield]: https://img.shields.io/badge/sponsor-GitHub-EA4AAA.svg?style=for-the-badge&logo=githubsponsors&logoColor=white
[sponsors]: https://github.com/sponsors/btli
[kofi-shield]: https://img.shields.io/badge/Ko--fi-donate-FF5E5B.svg?style=for-the-badge&logo=ko-fi&logoColor=white
[kofi]: https://ko-fi.com/bryanli

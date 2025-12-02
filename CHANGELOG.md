# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-12-02

### Added

- Initial release of pypoolchem
- **Water Balance Indices**
  - Calcium Saturation Index (CSI) calculation with interpretation
  - Langelier Saturation Index (LSI) calculation with interpretation
  - Carbonate alkalinity correction for CYA and borates
  - Ionic strength calculations
- **Chemical Dosing**
  - Support for 32 different pool chemicals
  - Chlorine: Bleach (6%, 8.25%, 10%, 12.5%), Trichlor, Dichlor, Cal-Hypo (48-73%), Lithium Hypo
  - pH adjustment: Muriatic Acid (various strengths), Dry Acid, Soda Ash, Borax
  - Alkalinity: Baking Soda
  - Calcium: Calcium Chloride (Anhydrous, Dihydrate)
  - Stabilizer: CYA Granular, CYA Liquid
  - Salt: Pool Salt
  - Borates: Borax, Boric Acid, Sodium Tetraborate Pentahydrate
- **Effect Predictions**
  - Predict water chemistry changes before adding chemicals
  - Support for single and multiple chemical additions
- **FC/CYA Relationship**
  - Calculate minimum, target, and shock FC levels based on CYA
  - Support for SWG pools with adjusted recommendations
- **Target Ranges**
  - Pre-configured targets for Traditional, SWG, and Spa pools
  - Parameter range validation helpers
- **Pool Volume Calculator**
  - Support for Rectangular, Oval, Round, Kidney, and Freeform shapes
- **Configuration System**
  - Fully configurable formula constants
  - Global configuration with get/set/update/reset functions
- **Data Models**
  - WaterChemistry: Immutable water chemistry measurements
  - Pool: Pool configuration with volume and type
  - Chemical: Chemical definitions with dosing properties
  - DosingResult: Dosing calculation results with units
  - TargetRanges: Target ranges for water parameters
- **Utilities**
  - Unit conversions (F/C, gallons/liters, oz/grams, etc.)
  - Water replacement calculations for lowering parameters
- Full type hints with mypy strict mode compliance
- PEP 561 py.typed marker for type checker support
- Comprehensive documentation

[Unreleased]: https://github.com/joyfulhouse/pypoolchem/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/joyfulhouse/pypoolchem/releases/tag/v0.1.0

# Architecture

How pypoolchem is structured and why.

## Overview

pypoolchem is a pure-Python calculation library with no network I/O. All public
functions are synchronous and stateless (except the optional global configuration
object), making the library safe to use in async applications and multi-threaded
contexts.

## Components

| Module | Responsibility |
|---|---|
| `pypoolchem.models` | Immutable Pydantic data models (`WaterChemistry`, `Pool`, `Chemical`, `DosingResult`, `TargetRanges`) |
| `pypoolchem.chemistry` | Water balance calculations (CSI, LSI, ionic strength, carbonate alkalinity corrections) |
| `pypoolchem.chemistry.fc_cya` | FC/CYA relationship calculations (min, target, shock FC) |
| `pypoolchem.dosing` | Chemical dosing calculations for all 32 supported chemicals |
| `pypoolchem.effects` | Effect prediction (simulate chemistry change before adding a chemical) |
| `pypoolchem.targets` | Pre-configured target ranges by pool type (Traditional, SWG, Spa) |
| `pypoolchem.volume` | Pool volume calculation from shape and dimensions |
| `pypoolchem.config` | Global configuration (formula constants, get/update/reset) |
| `pypoolchem.units` | Unit conversion helpers (F/C, gallons/liters, oz/grams) |

## Data Flow

All calculations take immutable input models and return new values or new
immutable models — no in-place mutation occurs. Effect predictions create a new
`WaterChemistry` instance reflecting the predicted state after a chemical
addition.

## Key Design Decisions

- **Frozen Pydantic models** — `WaterChemistry` and other data models are
  frozen for thread safety and to prevent accidental mutation.
- **Pure functions** — every calculation function is stateless; only
  `get_config` / `update_config` / `reset_config` touch global state.
- **No network I/O** — the library is a pure calculation engine. Sensor
  readings and device communication are the responsibility of the caller
  (e.g., the [Pool Chem](https://github.com/joyfulhouse/ha-poolchem) Home
  Assistant integration).
- **32 chemicals** — the `ChemicalType` enum enumerates all supported
  chemicals with their active-ingredient concentrations and unit weights baked
  in, so callers never need to supply chemical constants.

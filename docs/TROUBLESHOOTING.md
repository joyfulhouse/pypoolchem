# Troubleshooting

Common problems with pypoolchem and how to resolve them.

## Common Issues

### Import error after installation

**Symptom:** `ModuleNotFoundError: No module named 'pypoolchem'`

**Cause:** The package is not installed in the active Python environment.

**Fix:** Install the package or activate the correct virtual environment:

```bash
pip install pypoolchem
# or, if using uv:
uv add pypoolchem
```

### Pydantic validation error on WaterChemistry

**Symptom:** `pydantic.ValidationError` when constructing `WaterChemistry`.

**Cause:** A field value is outside its accepted range (e.g., negative pH or
temperature).

**Fix:** Check the field constraints in [models.md](models.md) and ensure your
sensor readings are within valid ranges before constructing the model.

### Unexpected dosing results

**Symptom:** Calculated dose is much higher or lower than expected.

**Cause:** Pool volume, current reading, or target value is incorrect; or the
wrong `ChemicalType` was selected.

**Fix:** Verify your pool volume (see `calculate_pool_volume`), confirm the
correct chemical strength (e.g., `BLEACH_10` vs `BLEACH_12_5`), and check
current vs target values.

## Enabling Debug Logging

pypoolchem is a pure calculation library and does not emit log output. To debug
integration issues, log the inputs and outputs of calculation calls in your
application.

## Getting Help

If you are still stuck, open an issue at
<https://github.com/joyfulhouse/pypoolchem/issues> with a minimal reproduction
example and the output of `python -c "import pypoolchem; print(pypoolchem.__version__)"`.

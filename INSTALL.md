# Installing pypoolchem

## Requirements

- Python 3.13 or newer.

## Install from PyPI

```bash
pip install pypoolchem
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add pypoolchem
```

## Install from Source

```bash
git clone https://github.com/joyfulhouse/pypoolchem.git
cd pypoolchem
uv sync
```

This installs the package with its development dependencies into a local virtual
environment.

## Verify the Installation

```bash
python -c "import pypoolchem; print(pypoolchem.__version__)"
```

You should see the installed version printed with no import errors.

## Next Steps

See the [README](README.md#quick-start) for a quick-start example and usage
guide.

# Development

How to set up a development environment for pypoolchem.

## Prerequisites

- Python 3.13+ and [`uv`](https://docs.astral.sh/uv/).

## Setup

```bash
git clone https://github.com/joyfulhouse/pypoolchem.git
cd pypoolchem
uv sync
```

## Quality Checks

```bash
uv run pytest          # tests
uv run ruff check      # lint
uv run ruff format     # format
uv run mypy            # type check
```

Run all of these before opening a pull request. See
[CONTRIBUTING](https://github.com/joyfulhouse/.github/blob/main/CONTRIBUTING.md)
for the contribution workflow.

## Releasing

1. Update `CHANGELOG.md` — move items from `[Unreleased]` to a new versioned
   section with today's date.
2. Bump `version` in `pyproject.toml` and `src/pypoolchem/__init__.py`.
3. Commit: `chore: release vX.Y.Z`.
4. Tag: `git tag vX.Y.Z`.
5. Push tag to trigger the release workflow, which publishes to PyPI.

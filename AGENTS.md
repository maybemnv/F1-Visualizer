# Repository Guidelines

## Project Structure & Module Organization
`app.py` starts the Dash server and `config.py` holds runtime settings. UI code lives in `dashboard/` with `callbacks/`, `components/`, `layout.py`, and `graphs.py`. Core processing lives in `f1_visualization/`, including `cache/`, `helpers/`, `plots/`, `schemas/`, `session/`, and `ml/`. Test coverage sits in `tests/` and follows the package layout. Static assets are under `Assets/`, example visuals and notes are in `Docs/` and `Comments/`, and CSV/TOML race data lives in `Data/`.

## Build, Test, and Development Commands
Prefer `uv` because `uv.lock` is committed.

```bash
uv sync --extra dev        # install app + dev tools
uv run python app.py       # run the dashboard locally
uv run pytest              # run the full test suite
uv run pytest --cov=f1_visualization --cov=dashboard
uv run ruff check .        # lint
uv run ruff format .       # format
uv run mypy f1_visualization dashboard
docker-compose up --build  # containerized local run
```

If `uv` is unavailable, use `pip install -e .[dev]`.

## Coding Style & Naming Conventions
Use Python 3.10+ with 4-space indentation, double quotes, and a 96-character line limit. Ruff is the formatter and primary linter; do not hand-format around it. Keep module names lowercase with underscores, tests in `test_*.py`, and prefer explicit, typed functions because the repo enforces broad annotation and docstring lint rules. Keep Dash callbacks grouped by concern inside `dashboard/callbacks/`.

## Testing Guidelines
Pytest is configured in `pyproject.toml`; place new tests in `tests/` and mirror the module under test, for example `tests/test_cache.py`. Add focused unit tests for data transforms, schemas, cache behavior, and callback helpers when logic changes. Run coverage when touching shared processing code, but there is no hard minimum currently checked in repo config.

## Commit & Pull Request Guidelines
Recent history uses short, feature-first subjects such as `ADD: ...`, `add:docs`, and concise modularization notes. Keep commits small, imperative, and under roughly 72 characters; use an optional prefix when it adds clarity. PRs should explain the user-facing change, list validation commands run, link any issue, and include screenshots for dashboard or visual output changes.

## Configuration & Data Notes
Runtime settings use the `F1_` prefix, for example `F1_HOST`, `F1_PORT`, and `F1_DATA_DIR`. Do not commit secrets or local-only overrides. Large generated CSV updates in `Data/` should be intentional and called out in the PR because they materially affect repository size and downstream visuals.

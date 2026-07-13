# F1 Visualizer Production Readiness Checklist

Use this checklist to track the work required to deploy the dashboard reliably. Add the date, owner, and evidence link beside completed items.

## 1. Fix Confirmed Blockers

- [ ] Fix package discovery in `pyproject.toml`; verify the built wheel contains `f1_visualization.ml`, `plots`, `helpers`, `schemas`, and `session`.
- [ ] Fix boolean parsing in `f1_visualization/preprocess.py`; confirm the string `"False"` becomes `False`, not `True`.
- [ ] Define one contract for `Time` and `GapTo*` columns: either float seconds or timedeltas. Update `add_gap()` and its tests accordingly.
- [ ] Stop mutating caller-owned DataFrames in `dashboard/utils.py`; use `.copy()` before transformations.
- [ ] Replace import-time loading of all data with explicit, lazy loading and a clear missing-data error.
- [ ] Resolve the Python version mismatch between `pyproject.toml`, README, Docker, and CI.

## 2. Automated Quality Gates

- [ ] Make `uv run pytest` pass with zero failures.
- [ ] Add regression tests for boolean parsing, package imports, missing data, empty sessions, and gap calculations.
- [ ] Reduce `uv run ruff check .` from the current 401 violations to zero, or narrow the configured rules intentionally.
- [ ] Run `uv run mypy f1_visualization dashboard` and resolve or document remaining errors.
- [ ] Add CI for tests, Ruff, mypy, and wheel-build validation on every pull request.
- [ ] Run `pre-commit run --all-files` successfully.

## 3. Build and Deployment Validation

- [ ] Build a clean artifact with `uv build`.
- [ ] Install the wheel in a fresh environment and run `python app.py`.
- [ ] Verify the Docker image builds from a clean checkout with `docker compose build`.
- [ ] Run `docker compose up -d f1-visualizer` and confirm the healthcheck returns HTTP 200.
- [ ] Test the dashboard using a read-only `Data/` mount and persistent cache/log volumes.
- [ ] Confirm assets, TOML configuration, nested Python packages, and application entry points exist inside the image.

## 4. Production Configuration

- [ ] Set `F1_HOST=0.0.0.0` and an explicit production `F1_PORT`.
- [ ] Set `F1_LOG_LEVEL=INFO`; do not enable debug mode in production.
- [ ] Confirm `F1_DATA_DIR` points to a complete, readable dataset.
- [ ] Do not commit secrets, credentials, or local cache files.
- [ ] Add a reverse proxy with TLS, request limits, and access logging if exposed publicly.
- [ ] Define a backup and refresh process for `Data/` and cache invalidation.

## 5. Go-Live Sign-Off

- [ ] Perform a smoke test: load a race, sprint, strategy plot, lap plot, compound plot, and ML analysis.
- [ ] Test an unavailable event, empty data, malformed data, and a failed FastF1 request.
- [ ] Verify logs contain useful errors without secrets or excessive stack traces.
- [ ] Record the deployed image/version, dataset date, environment, and rollback target.
- [ ] Assign an owner for incident response and data refreshes.
- [ ] Mark launch approved only after all blocker and deployment items are complete.

## Useful Commands

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run mypy f1_visualization dashboard
uv build
docker compose build
docker compose up -d f1-visualizer
docker compose ps
docker compose logs --tail=100 f1-visualizer
```

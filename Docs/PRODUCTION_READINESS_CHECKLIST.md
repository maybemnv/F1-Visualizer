# F1 Visualizer Production Readiness Checklist

Use this checklist to track the work required to deploy the dashboard reliably. Add the date, owner, and evidence link beside completed items.

Last updated: 2026-07-13.

## 1. Fix Confirmed Blocker

- [x] Fix package discovery in `pyproject.toml`; verified with `uv run mypy src/f1_visualization src/dashboard` and `uv run pytest` after `src/` layout migration on 2026-07-13.
- [x] Fix boolean parsing in `preprocess.py`; string booleans are normalized explicitly instead of relying on `astype(bool)`.
- [x] Define one contract for `Time` and `GapTo*` columns in dashboard data: `Time` is serialized as float seconds and `GapTo*` is float seconds. Verified by gap tests on 2026-07-13.
- [x] Adopt `src/` layout — all importable packages live under `src/`, tests mirror the hierarchy. Verified with `uv run pytest` (49 passed) on 2026-07-13.
- [x] Fix Docker path resolution — `_resolve_project_root()` in `schemas/settings.py` walks up to `pyproject.toml` sentinel, works in both source tree and wheel-installed (Docker) deployments. Environment keys `F1_DATA_DIR` and `F1_CACHE_DIR` added to Dockerfile + docker-compose.yml for defense-in-depth on 2026-07-13.
- [x] Fix `Automation/data-refresh.sh` ERR trap — pattern widened from `*preprocess.py*` to `*preprocess*` to cover both direct-file and `-m` invocation on 2026-07-13.
- [ ] Stop mutating caller-owned DataFrames in `dashboard/utils.py`; use `.copy()` before transformations.
- [x] Replace import-time loading of all data with explicit, lazy loading and a clear missing-data warning. `DF_DICT` now defers CSV reads until first mapping access and can be reloaded explicitly.
- [x] Resolve the Python version mismatch between `pyproject.toml`, README, Docker, and CI. Project metadata and README now target Python 3.11+.

## 2. Automated Quality Gates

- [x] Make `uv run pytest` pass with zero failures. Evidence: `49 passed` on 2026-07-13.
- [ ] Add regression tests for boolean parsing, package imports, missing data, empty sessions, and gap calculations. Missing-data and lazy-loading regressions are covered.
- [x] Reduce `uv run ruff check .` from the current 401 violations to zero, or narrow the configured rules intentionally. Evidence: `All checks passed!` on 2026-07-24.
- [ ] Run `uv run mypy src/f1_visualization src/dashboard` and resolve or document remaining errors. (27 errors in 13 files remain — all pre-existing, none related to import resolution or path discovery.)
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

- [x] Set `F1_HOST=0.0.0.0` and `F1_PORT=8050` in Docker environment.
- [x] Set `F1_LOG_LEVEL=INFO` in Docker environment; debug mode is disabled.
- [x] `F1_DATA_DIR=/app/Data` and `F1_CACHE_DIR=/app/.cache` set in Docker environment; sentinel-based fallback works without env vars.
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
uv run mypy src/f1_visualization src/dashboard
uv build
docker compose build
docker compose up -d f1-visualizer
docker compose ps
docker compose logs --tail=100 f1-visualizer
```

# F1 Visualizer Product Requirements Document

**Status:** Draft for production hardening  
**Owner:** F1 Visualizer maintainers  
**Last updated:** 2026-07-13

## 1. Product Summary

F1 Visualizer is a web dashboard for exploring Formula 1 race and sprint data from 2018 onward. It combines FastF1 timing data, validated transformations, interactive Plotly visualizations, and optional machine-learning analysis in one analyst-friendly interface.

## 2. Problem Statement

Race data is technically rich but difficult to compare consistently across drivers, stints, compounds, and sessions. Users need a fast way to select a session, inspect pace and strategy, calculate driver gaps, and understand anomalous or consistently strong performance without writing analysis code.

## 3. Users and Primary Outcomes

- **F1 analysts:** compare pace, position, tyre strategy, and teammate performance.
- **F1 fans:** explore a race through approachable visual controls rather than raw CSV files.
- **Project maintainers:** refresh data and deploy the dashboard reproducibly with clear operational checks.

Success means a user can load a supported session, understand the selected data, produce the main plots without errors, and repeat the workflow after a data refresh.

## 4. Scope

### In Scope

- Race and sprint session selection by season and event.
- Driver filtering, teammate comparison, and gap-to-driver calculations.
- Strategy, scatter, line, distribution, compound, and legend views.
- Clustering, anomaly detection, and driver ranking analysis where sufficient data exists.
- Cached local datasets with Docker deployment and health checks.

### Out of Scope

- Live timing during an active session.
- Editing or manually correcting official timing data in the UI.
- User accounts, saved dashboards, collaboration, or public API access.
- Replacing FastF1 as the upstream data provider.

## 5. Core User Journey

1. Open the dashboard and choose a season, event, and session type.
2. Load the session and wait for the data-ready state.
3. Select drivers, optional teammate comparison, and an optional reference driver.
4. Move between visualization tabs and adjust lap, compound, and y-axis controls.
5. Open Analysis to run a supported ML view and interpret its limitations.

The UI must show clear empty, loading, unavailable-data, and failure states. A failed upstream request must not leave stale results presented as the newly selected session.

## 6. Functional Requirements

- **FR-01:** Validate season, session type, event, driver, lap, and compound inputs before processing.
- **FR-02:** Load only the selected session into browser state and serialize time-based columns safely.
- **FR-03:** Preserve source data while deriving gaps, deltas, tyre metrics, and filtered views.
- **FR-04:** Keep plot legends, units, driver labels, and compound colors consistent across tabs.
- **FR-05:** Disable controls that have no eligible data and explain why.
- **FR-06:** Return useful user-facing errors for missing files, invalid sessions, malformed rows, and upstream failures.
- **FR-07:** Ensure ML results identify the input session and expose enough context to avoid misleading comparisons.

## 7. Technical Requirements

- Python 3.11, `uv`, Dash, Plotly, Pandas, Pydantic, FastF1, and scikit-learn.
- Runtime configuration through `F1_` environment variables; production binds to `0.0.0.0`.
- Package builds must include every nested `f1_visualization` and `dashboard` module.
- Docker images run as a non-root user and exclude tests, development scripts, repository docs, and local caches.
- Data files remain externally mounted or managed as a deliberate release artifact.
- Cache keys must include session identity and relevant analysis parameters; stale cache entries must expire or be invalidated.

## 8. Quality and Acceptance Criteria

- `uv run pytest` passes with zero failures.
- Ruff, mypy, and pre-commit checks are either clean or have documented, intentional exceptions.
- A clean wheel installation can import the dashboard and all nested runtime packages.
- `docker compose build` succeeds from a clean checkout.
- The production health check returns HTTP 200 after startup.
- Smoke testing covers one race, one sprint, empty data, unavailable data, malformed data, and an upstream failure.
- No secrets, user credentials, test fixtures, or development-only files are present in the production image.
- A release records image version, dataset revision, configuration, owner, and rollback target.

## 9. Observability and Operations

Log startup, data-load duration, selected session, cache hit/miss, processing failures, and shutdown at appropriate levels. Do not log raw secrets or unnecessarily large dataframes. Define an owner for data refreshes, cache invalidation, incident response, and rollback.

## 10. Delivery Plan

1. **Stabilize:** resolve failing tests, data-type contracts, package/build issues, and clear error states.
2. **Harden:** add CI, coverage for data transformations and callbacks, structured logs, and deployment smoke tests.
3. **Launch:** deploy the pinned image, run the production checklist, monitor the first refresh, and document rollback.
4. **Improve:** add exportable views, richer ML explanations, performance profiling, and user feedback only after core reliability is proven.

## 11. Key Risks

- FastF1 availability, rate limits, or upstream schema changes.
- Large datasets causing slow startup or browser-store pressure.
- ML outputs being interpreted as objective driver rankings without sufficient context.
- Data refreshes changing historical results without a recorded dataset revision.

Mitigations are schema validation, explicit data revisions, bounded caching, clear UI caveats, automated regression tests, and a tested rollback path.

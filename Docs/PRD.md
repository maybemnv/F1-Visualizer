# F1 Strategy Intelligence Agent — Product Requirements Document

## 1. Document metadata and version history

| Field | Value |
| --- | --- |
| Status | Proposed implementation specification |
| Owner | F1 Visualizer maintainers |
| Last updated | 2026-07-27 |
| Scope labels | Current = audited repository state; Approved = this PRD; Planned = phased work; Future = not MVP scope. |

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-07-13 | Descriptive F1 Visualizer dashboard PRD. |
| 2.0 | 2026-07-27 | Model-driven, agent-orchestrated F1 race-strategy intelligence product. |

A decision-time prediction, actual history, and simulated counterfactual are separate artifact types and must never be conflated.

## 2. Executive summary

F1 Visualizer will evolve into **F1 Strategy Intelligence Agent**: a historical, model-driven system that reconstructs race state lap by lap, estimates strategic signals, simulates bounded alternatives, and stores an auditable recommendation or abstention.

Quantitative models and the simulator produce all numerical estimates. The agent orchestrates typed tools, compares results, applies a deterministic policy, and may generate grounded explanation prose. An LLM must not invent tyre degradation, pit loss, confidence, expected delta, or simulation output.

The MVP is historical-only: selected dry races from 2023–2024, a small driver set, green-flag decisions, limited-horizon Monte Carlo simulation, replay, Strategy Receipts, and walk-forward backtests. It prioritizes leakage prevention, calibration, reproducibility, and limitations over coverage or live support.

## 3. Existing product assessment

Current repository foundations:

- Python 3.11, `uv`, Dash, Plotly, Pandas, NumPy, Pydantic, FastF1, scikit-learn, Docker, Pytest, Ruff, and mypy.
- `src/dashboard/` provides Dash controls, callbacks, async loading, and strategy/pace/compound/analysis charts.
- `src/f1_visualization/` provides FastF1 preprocessing, loaders, helpers, schemas, cache, plots, and retrospective ML.
- Existing CSV loading is lazy through `LapDataStore`.
- `Data/` currently contains configuration TOML files, not committed race datasets.

| Decision | Existing assets |
| --- | --- |
| Retain | Dash/Plotly UI, FastF1 adapter, typed settings, cache, existing charts, gap/SC helpers, tests, Docker workflow. |
| Extend | Raw ingestion, preprocessing, data quality checks, dashboard charts, cache identity, schemas, observability. |
| Redesign | Data storage, race-state construction, feature pipeline, model registry, simulation, recommendations, backtesting. |
| Isolate | Existing clustering, anomaly detection, and driver ranking remain retrospective analytics only. |
| Exclude from decision features | `DeltaToRep`, `DeltaToFastest`, final positions/results, full-session features, future stints, and post-race annotations. |

The current transformed CSV pipeline is useful for retrospective visualizations but is unsafe as a decision-time strategy dataset because several fields use completed-race information. New strategy datasets must be immutable complete event bundles, not append-derived race-wide aggregates.

## 4. Product vision

Answer:

> Given only what was observable at this point in the race, which bounded action had the highest estimated outcome under the stated assumptions, objective function, and uncertainty?

The system records its recommendation before later race data is revealed. Afterward, it compares the actual team action with decision-time prediction and conditional simulated alternatives without claiming the counterfactual is historical fact.

## 5. Problem statement

Public F1 timing data is rich enough to describe a completed race but not inherently suitable for evaluating strategy decisions without hindsight. Users need a reproducible, uncertainty-aware system that estimates pit windows, tyre degradation, traffic, and rival threats using only contemporaneous information.

## 6. Product positioning

**Model-driven, agent-orchestrated F1 race strategy intelligence.**

Use framing such as:

> Under the system's observable race state, uncertainty assumptions, objective function, and simulation model, this action had a higher estimated outcome.

Do not claim:

- Perfect strategy prediction.
- Superiority to professional F1 teams.
- Proof that a team made a wrong decision.
- Fully autonomous race engineering.

## 7. Goals

1. Construct immutable, availability-bounded race states.
2. Estimate tyre degradation, pit-cycle loss, rejoin traffic, and undercut/overcut risk.
3. Compare candidate actions with distributions, not falsely precise single values.
4. Support abstention where evidence is insufficient.
5. Store typed, versioned recommendations, traces, simulations, and receipts.
6. Backtest chronologically against interpretable baselines.
7. Preserve useful descriptive dashboard functionality.
8. Produce portfolio-quality methodology, model cards, evaluation, and case studies.

## 8. Non-goals

- Live race support in MVP.
- Private telemetry, tyre temperatures, true fuel load, internal damage, or full radio context.
- Wet-race, red-flag, every-season, or every-driver coverage in MVP.
- Reinforcement learning or full game-theoretic multi-agent strategy.
- Mobile, voice, accounts, social publishing, or public write APIs.
- Claims of real-team-grade accuracy or causal proof of team mistakes.

## 9. Users and use cases

| User | Need |
| --- | --- |
| F1 strategy enthusiasts | Replay a historical decision and understand pit-window reasoning. |
| Applied ML/data-science audiences | Inspect features, models, intervals, baselines, and leakage controls. |
| Motorsport analysts/content creators | Create caveated strategy narratives and receipts. |
| Engineering recruiters | Evaluate architecture, tests, reproducibility, and scope judgment. |
| Sequential-decision researchers | Compare frozen decision policies under partial observability. |

## 10. Product modes

### Historical Race Replay — MVP

The user selects season, event, race, driver, and lap. The UI reconstructs only data available at the end of that driver's lap.

### Historical Backtesting — MVP

The system evaluates decisions sequentially and stores recommendations before later outcomes are attached.

### Counterfactual Strategy Analysis — MVP

Compare:

- Pit now.
- Stay out one or two laps.
- Medium versus hard.
- Cover a rival.
- Attempt undercut or overcut.
- Abstain and reassess.

Results are distributions with assumptions and uncertainty.

### Near-Live Strategy Mode — Future

Only after historical replay, calibration, and leakage controls are proven reliable.

## 11. Functional requirements

- Build `RaceState` at a declared `available_at` boundary and reject future observations.
- Persist schema, source manifest, configuration, model version, seed, and commit provenance.
- Show data quality and ineligibility rather than silently substituting data.
- Return prediction intervals, support, uncertainty causes, and model versions.
- Distinguish observed pit measurements from estimated pit/rejoin outputs.
- Select relevant rivals from the boundary state, never final classification.
- Generate bounded candidate actions including `ABSTAIN`.
- Persist seeded simulation inputs and outputs.
- Validate every numerical recommendation claim against tool/model evidence.
- Visibly distinguish observed state, prediction, actual history, and simulation.
- Persist recommendations before actual actions or outcomes are attached.
- Remain functional with LLM explanation disabled.

## 12. Race-state schema

The MVP decision boundary is **end of target driver lap N**. `available_at` is the target driver's lap-completion timestamp, not row N of a completed dataframe.

```json
{
  "schema_version": "race_state.v1",
  "race_state_id": "rs_...",
  "event": {
    "season": 2024,
    "round": 10,
    "event_name": "string",
    "circuit_id": "string",
    "session_id": "2024-10-R"
  },
  "subject": {
    "driver": "NOR",
    "team": "string"
  },
  "boundary": {
    "decision_lap": 22,
    "generated_at_state": "end_of_target_driver_lap_22",
    "available_at_session_seconds": 2234.531,
    "availability_policy_version": "availability.v1"
  },
  "race_progress": {
    "scheduled_laps": 66,
    "position": 5,
    "gap_to_leader_seconds": 18.4,
    "gap_to_ahead_seconds": 1.2,
    "gap_to_behind_seconds": 2.8
  },
  "tyre_state": {
    "compound": "MEDIUM",
    "absolute_compound": "C3",
    "tyre_age_laps": 22,
    "stint_number": 1
  },
  "pace_state": {
    "recent_clean_median": 79.23,
    "trend_seconds_per_lap": 0.11,
    "fuel_corrected_interval": [79.42, 80.08]
  },
  "track_state": {
    "status": "GREEN",
    "weather": {},
    "track_evolution_index": 0.38
  },
  "strategy_context": {
    "expected_rejoin": {},
    "nearby_traffic_ids": [],
    "relevant_rival_ids": []
  },
  "data_quality": {
    "flags": [],
    "source_manifest_id": "dataset_..."
  },
  "provenance": {
    "feature_schema_version": "features.v1",
    "config_hash": "sha256:...",
    "commit_sha": "..."
  }
}
```

Supporting lap, timing, stint, weather, status, pit, and race-control observations must include source time, source identifier, data-quality flags, and source-manifest ID.

## 13. Data sources and limitations

Expected sources:

- FastF1 lap and sector timing.
- Compounds, tyre age, stint data, positions, intervals, and pit markers.
- Weather and track-status data.
- Race-control messages where available.
- Public pit-stop records where validated.
- Historical circuit, driver, and team context.

Public sources do not provide:

- Private telemetry.
- Exact tyre temperatures or fuel loads.
- Internal damage, mechanical issues, or radio intent.
- Team orders, tyre inventory, or championship objectives.

Missing variables must become uncertainty or a limitation, never fabricated data.

## 14. Data pipeline

1. Acquire raw FastF1 session extract.
2. Write immutable `DatasetManifest` with checksums and source metadata.
3. Normalize typed, timestamped event tables.
4. Validate schema, identity, duplicates, timing order, stints, and plausibility.
5. Store complete event bundles as partitioned Parquet.
6. Build race states in availability order.
7. Materialize versioned feature snapshots.
8. Train/infer, simulate, and persist recommendation before reveal.
9. Attach actual history separately for evaluation.

Legacy CSVs remain for retrospective charts until migration tests pass. They are not automatically strategy-training data.

## 15. Feature engineering

Features must declare unit, source, transformation, availability rule, missing policy, version, and tests.

Feature groups:

- Circuit/season context.
- Compound, tyre age, stint length, fresh tyre.
- Rolling clean-lap pace, sector trend, variability.
- Scheduled-distance fuel-burn prior with uncertainty.
- Traffic and dirty-air proxies from gaps, closure, and following duration.
- Weather, track status, and track evolution.
- Relevant rival state.
- Data quality and sample support.

Exclude or explicitly model pit-in/out, invalid, safety-car, VSC, red-flag, warm-up, and outlier laps.

Forbidden decision-time features include final position, points, final fastest lap, full-race representative pace, later pit stops, future weather/status messages, penalties, and post-race annotations.

## 16. Quantitative models

Every model requires a model card, artifact ID, training manifests, feature schema, configuration, chronological validation, calibration report, support limits, and failure analysis.

### Tyre degradation model

Predict next clean-lap residual and short-horizon degradation trajectory.

Benchmark:

1. Constant pace.
2. Robust per-stint linear regression.
3. Contextual robust regression.
4. Hierarchical or mixed-effects/Bayesian model.
5. Quantile-capable gradient boosting if justified.

Evaluate MAE, median absolute error, pinball loss, 50/80/90% coverage, interval width, and segmented errors by circuit, compound, tyre age, and traffic regime.

### Pit-loss and rejoin model

Estimate total pit-cycle loss, out-lap warm-up, rejoin rank, rejoin traffic, and clean-air probability.

Only separate pit transit from stationary time when reliable source data supports that decomposition.

### Undercut and overcut model

For each relevant rival, calculate current pace, fresh-tyre pace, pit loss, traffic risk, required gap, expected delta, success probability, and uncertainty.

### Required baselines

1. Fixed tyre-age rule.
2. Fixed degradation threshold.
3. Rule-based undercut cover.
4. Rule-based clean-air optimization.
5. Actual historical action.
6. Learned model without agent layer.
7. Full model-driven agent system.

## 17. Strategy simulator

`StrategySimulator.v1` receives frozen state, typed action, model artifacts, scenario configuration, horizon, and seed.

MVP actions:

- Pit now.
- Pit next lap.
- Stay out one/two laps.
- Medium/hard where eligible.
- Cover relevant rival.
- Abstain/reassess.

Default horizon: shorter of 12 green-flag-equivalent laps or next decision opportunity.

Model uncertainty in degradation, pit duration, warm-up, traffic, rival reactions, pace variation, weather forecast, safety-car/VSC hazard, and track evolution.

Never use later actual safety cars or rival stops in recommendation-time simulation.

Return:

- p10/p50/p90 time delta.
- Position and rejoin distributions.
- Clean-air and traffic outcomes.
- Probability of gain/loss.
- Risk metrics.
- Scenario assumptions.
- Seeds, sample count, model versions, and quality flags.

## 18. Agent architecture

`StrategyCoordinator` executes:

1. Read state.
2. Select relevant rivals.
3. Call degradation, pit, rejoin, threat, and compound tools.
4. Generate bounded candidates.
5. Simulate candidates.
6. Compare outcome distributions.
7. Apply deterministic recommendation/abstention policy.
8. Store recommendation and evidence.
9. Optionally render validated explanation prose.

The LLM cannot change action, targets, confidence, values, evidence, or versions.

## 19. Tool contracts

Every tool uses Pydantic input/output and returns:

```text
ToolResult.v1(
  tool_call_id,
  race_state_id,
  available_at,
  feature_snapshot_hash,
  status,
  payload,
  model_versions,
  data_quality,
  warnings,
  evidence_ids,
  latency_ms
)
```

Required tools:

- get_race_state
- get_driver_stint
- estimate_tyre_degradation
- estimate_pit_loss
- project_rejoin_traffic
- detect_undercut_threat
- detect_overcut_opportunity
- compare_compounds
- simulate_strategy
- compare_strategy_options
- retrieve_similar_historical_scenarios
- get_actual_team_action
- generate_strategy_receipt

Typed errors: INPUT_INVALID, DATA_INCOMPLETE, OUT_OF_SCOPE, MODEL_INELIGIBLE, SIMULATION_FAILED, TIMEOUT.

## 20. Structured recommendation schema

```json
{
  "schema_version": "strategy_recommendation.v1",
  "recommendation_id": "rec_...",
  "event_id": "2024-10-R",
  "driver": "NOR",
  "race_state_id": "rs_...",
  "decision_lap": 22,
  "generated_at_state": "end_of_target_driver_lap_22",
  "action": "PIT",
  "target_lap": 23,
  "target_compound": "HARD",
  "covered_rival": "VER",
  "decision_status": "RECOMMEND",
  "confidence": 0.71,
  "expected_delta_seconds": {
    "reference_action": "STAY_OUT_AND_REASSESS",
    "p10": -0.8,
    "median": 2.3,
    "p90": 5.1
  },
  "expected_position_delta": {
    "median": 1,
    "range": [-1, 2]
  },
  "primary_reason": {
    "code": "UNDERCUT_THREAT",
    "evidence_ids": ["tool_..."]
  },
  "supporting_factors": [],
  "risks": [],
  "assumptions": [],
  "evidence": ["tool_...", "sim_..."],
  "model_versions": {},
  "data_quality": {},
  "provenance": {},
  "abstention_reason": null
}
```

Actions: PIT, STAY_OUT, COVER_RIVAL, EXTEND, ABSTAIN.

Every numeric claim must map to boundary-valid evidence. ABSTAIN requires an abstention reason.

## 21. Historical replay design

Keep Dash as the primary UI.

Required replay panels:

- Season/event/driver/lap selector.
- Decision-eligible lap timeline.
- Track order and current gaps.
- Tyre and stint timeline.
- Pace and degradation chart.
- Pit-window and rejoin-traffic view.
- Rival-threat panel.
- Recommendation/abstention card.
- Outcome distribution.
- Actual versus recommendation versus simulation comparison.
- Expandable evidence, assumptions, quality, model, manifest, feature hash, and trace.

Do not preload future race data into decision-time browser state. Keep legacy charts as a clearly labeled Retrospective Explorer until migrated.

## 22. Backtesting framework

For each eligible decision point:

1. Reconstruct state.
2. Freeze state and feature snapshot.
3. Load only chronologically valid models.
4. Generate tools, simulations, and recommendation.
5. Persist recommendation.
6. Reveal actual action/outcomes afterward.
7. Record model, policy, and uncertainty error.

Split by complete races/seasons, never random laps. Fit preprocessing, feature selection, and calibration only inside training folds.

## 23. Evaluation methodology

Evaluate:

- Tyre degradation: MAE, pinball loss, coverage, sharpness.
- Fuel correction: next-clean-lap error and sensitivity.
- Pit loss: error and interval coverage.
- Rejoin traffic: position error, clean-air calibration, traffic-loss error.
- Undercut/overcut: Brier score, calibration, success/failure rate.
- Policy: expected/simulated delta, position delta, unnecessary-stop rate, regret, confidence calibration, abstention quality.

Break down by circuit, compound, tyre age, track status, weather eligibility, driver/team, traffic, and data support.

Use paired decision states and race-clustered bootstrap confidence intervals. Publish failures and baseline-winning contexts.

## 24. Leakage-prevention strategy

Leakage is a release-blocking correctness failure.

Controls:

- Source-time filtering at state-query level.
- Explicit feature availability contracts.
- Complete-race chronological splits.
- Fold-local preprocessing.
- Immutable, content-hashed state/features/recommendations.
- Frozen preprocessing/model versions.
- Trace hash compatibility checks.
- Tests injecting future lap/result/status/annotation sentinels.
- Tests asserting recommendation persistence before outcome attachment.

## 25. Strategy Receipt specification

StrategyReceipt.v1 is read-only JSON plus HTML/Plotly rendering.

It includes event, driver, decision lap, boundary state, recommendation, actual action after reveal, strategic reason, candidate distribution, selected simulation, risks, assumptions, confidence/status, quality warnings, provenance, and evidence appendix.

Persistent labels:

- Observed at decision time
- Predicted at decision time
- Simulated estimate
- Observed after decision time

## 26. User experience

The product should feel like an analytical cockpit, not a chat screen.

Reading order:

1. Current state.
2. Candidate actions.
3. Outcome distribution.
4. Recommendation.
5. Evidence and caveats.
6. Post-reveal actual comparison.

Use accessible controls, explicit units, color-independent summaries, loading/error states, and visible assumptions.

## 27. System architecture

```
FastF1/public adapters
  -> ingestion + source manifests
  -> normalized Parquet event bundles
  -> availability-bounded race-state engine
  -> feature snapshots
  -> versioned quantitative models
  -> seeded strategy simulator
  -> deterministic policy + typed tools
  -> recommendations, receipts, backtests, traces
  -> typed read API
  -> Dash replay UI
```

Add packages incrementally:

- ingestion
- normalization
- race_state
- features
- strategy/models
- strategy/simulation
- strategy/agent
- backtesting
- evaluation
- experiments
- storage
- services

Keep Dash; do not replace it with React/Next.js for MVP.

## 28. Storage and data models

| Store | MVP technology | Purpose |
| --- | --- | --- |
| Raw archive | Filesystem | Immutable source extracts/manifests. |
| Event store | Partitioned Parquet | Normalized laps, timing, sectors, stints, weather, status, pit, quality. |
| Artifact store | Filesystem | Models, transforms, calibration, configs, reports. |
| Metadata | SQLite | Manifests, states, features, runs, tools, simulations, recommendations, receipts, evaluations. |
| Cache | Existing cache with redesigned keys | Disposable derived read models only. |

Use append-only decision artifacts and foreign-key/version compatibility checks.

## 29. API requirements

MVP uses typed in-process services. Phase 6 may add FastAPI read endpoints:

- GET /api/v1/events
- GET /api/v1/events/{event_id}/drivers
- GET /api/v1/replay/.../state?driver=&lap=
- GET /api/v1/recommendations/{id}
- GET /api/v1/simulations/{id}
- GET /api/v1/receipts/{id}
- GET /api/v1/models/{id}
- GET /api/v1/manifests/{id}

Ingestion, model training, and backtests remain trusted local CLI jobs in MVP.

## 30. Observability

Log every decision:

- Race-state ID and boundary.
- Manifest and feature hash.
- Tool calls/results/errors.
- Model versions and outputs.
- Candidate actions.
- Simulation seed, samples, assumptions.
- Final action/abstention/confidence.
- Latency, quality flags, configuration, commit SHA.

Track cache rate, validation failures, leakage failures, tool failures, latency, abstention rate, schema errors, and calibration drift.

## 31. Testing strategy

Require:

- Unit tests for normalization, fuel prior, tyre age, pit loss, traffic, state reconstruction, quality flags.
- Tool/schema/property tests.
- Leakage sentinel tests.
- Simulator fixed-seed reproducibility tests.
- Agent evidence/abstention/LLM-off tests.
- Backtest integrity tests.
- API and Dash integration tests.
- Existing graph/cache/schema regression tests.
- Golden scenarios with frozen state, expected tool ranges, valid action/abstention range, limitations, seed, and evaluation criteria.

## 32. Reproducibility

Persist source checksums, manifests, schemas/hashes, model/calibration artifacts, parameters, seeds, simulation configuration, objective/policy thresholds, commit SHA, lockfile hash, command, timestamps, and hardware metadata.

Never overwrite an artifact. Source, code, configuration, or feature changes create a new run.

## 33. Security and privacy

The MVP uses public data and no accounts. Keep secrets in environment configuration; validate IDs, paths, and frame sizes; use read-only data mounts; restrict refresh jobs.

If exposed publicly, add authentication, rate limits, CORS allowlist, request limits, TLS proxy, and audit logs. Send LLMs only minimum validated evidence.

## 34. Delivery phases

| Phase | Objective | Exit criteria |
| --- | --- | --- |
| 0. Existing-System Audit | Audit code, data, docs, debt, and leakage risks. | Required sources classified available, approximate, or unsupported. |
| 1. Historical Race-State Engine | Manifests, normalized Parquet, quality checks, state builder. | Same manifest/state key is reproducible; future sentinel cannot alter earlier state. |
| 2. Quantitative Models | Degradation, pit, rejoin, threats, compounds, baselines. | Selected models pass declared held-out accuracy/calibration gates or scope narrows. |
| 3. Counterfactual Simulator | Typed actions, scenarios, seeded Monte Carlo. | Golden runs replay with uncertainty and stored seed/configuration. |
| 4. Strategy Agent | Tools, deterministic policy, abstention, receipt. | Every numeric output resolves to evidence. |
| 5. Historical Backtesting | Walk-forward runner, baselines, metrics, error reports. | Leakage suite and segmented evaluation report pass. |
| 6. Replay UI and Receipts | Dash replay, comparison, export, read API. | User can replay, compare, and export without LLM. |
| 7. Near-Live Mode | Polling, watermarks, latency display. | Historical replay equivalence at watermark. |

## 35. Acceptance criteria

- Golden state values match validated sources.
- No known future-data leakage.
- Features/models/simulations reproduce from artifacts.
- Learned models are compared against named baselines on held-out races.
- Prediction intervals report calibration.
- Recommendations validate, trace correctly, and abstain under insufficient evidence.
- Replay, comparison, and Strategy Receipt work with LLM disabled.
- Portfolio includes architecture, methodology, model cards, benchmark report, demo, and case studies.

## 36. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Missing private telemetry/objectives | Explicit limitations, uncertainty, no optimal-team claims. |
| Future leakage | Availability timestamps, immutable artifacts, chronological folds, sentinel tests. |
| Timing gaps/schema changes | Manifest, validation, quality flags, fail-closed eligibility. |
| Sparse pit data | Model total pit-cycle loss only. |
| Regulation/tyre drift | Narrow recent scope and context-specific evaluation. |
| Safety-car/weather randomness | Forecast scenarios, risk distributions, abstention. |
| Traffic proxy error | Separate error analysis and conservative thresholds. |
| Overfitting | Simple baselines, race-level splits, bootstrap intervals. |
| LLM hallucination | Typed tools, deterministic policy, evidence validation, LLM-off path. |
| One-engineer scope | Narrow MVP and phase gates. |

## 37. Future roadmap

Potential future work:

- More dry races.
- Validated VSC/SC and wet-race support.
- Improved rival-response models.
- Full-horizon simulator.
- PostgreSQL/MLflow deployment upgrades.
- Hierarchical Bayesian models if benchmarks justify them.
- Cautious near-live public-data beta.

RL, full game theory, team-specific objectives, mobile, voice, and autonomy require separate PRDs.

## 38. Open technical decisions

| Decision | MVP default | Evidence needed |
| --- | --- | --- |
| Supported races | Selected dry 2023–2024 events | FastF1 data-quality audit. |
| Pit target | Total pit-cycle loss | Reliable stationary/transit data. |
| Degradation model | Contextual robust baseline with intervals | Held-out benchmark/calibration improvement. |
| Extra ML dependencies | Defer initially | Material value over simpler model. |
| Experiment registry | SQLite/filesystem | Operational need for MLflow. |
| Confidence semantics | Probability only if calibrated | Reliability report. |
| Horizon | 12 green-equivalent laps/next decision | Latency and sensitivity evidence. |

Largest unresolved risk: whether public FastF1 timing/pit/event timestamps can support sufficiently faithful, availability-bounded pit-cycle, rejoin, traffic, and rival estimates. If not, narrow MVP to conservative pace/pit-window analysis with stronger abstention.

## 39. Repository migration plan

1. Preserve app.py, config, dashboard, tests, and legacy interfaces.
2. Add Pydantic strategy contracts and new domain packages beside existing code.
3. Add version-pinned ingestion and immutable event bundles while retaining preprocess.py/CSV compatibility.
4. Keep generated Parquet out of Git except intentional fixtures/release artifacts.
5. Add version-aware cache identity.
6. Extract strategy-safe services from callbacks.
7. Relabel existing ML as retrospective and enforce import barriers.
8. Do not promote full-race deltas/results into decision features.
9. Migrate charts incrementally with regression tests.
10. Update README, architecture/schema/readiness docs, and model cards as implementation ships.

## 40. Final prioritized implementation backlog

### Recommended MVP

Historical dry 2023–2024 replay with immutable event bundles, end-of-lap state, tyre/total-pit/rejoin/undercut models, 12-lap seeded simulation, deterministic recommendation/abstention, Dash replay, three golden scenarios, walk-forward report, and Strategy Receipts.

### First three historical races or scenarios

1. 2023 Bahrain Grand Prix — Fernando Alonso, first green-flag pit window.
2. 2023 Hungarian Grand Prix — Lando Norris, mid-race undercut/overcut decision.
3. 2024 Spanish Grand Prix — Lando Norris versus Max Verstappen, mid-race compound/pit-window decision.

These are candidate golden scenarios, not optimality claims. Replace any that fail Phase 0 data-quality audit with a documented equivalent dry 2023–2024 scenario.

### First ten engineering tasks in dependency order

1. Capture current test/lint/type baseline and audit the three source events.
2. Add ADRs plus manifest, race-state, feature snapshot, and availability schemas.
3. Implement version-pinned FastF1 ingestion and checksummed manifests.
4. Implement normalized Parquet event tables and quality reports.
5. Implement state builder, frozen fixtures, and future-sentinel tests.
6. Add SQLite metadata and version-aware cache keys.
7. Implement strategy-safe features, clean-lap/fuel policy, and legacy-ML import barrier.
8. Implement baseline degradation and total pit-cycle models with chronological calibration.
9. Implement rejoin/undercut tools, typed actions, and seeded simulator.
10. Implement coordinator, policy, recommendations, receipts, first replay card, and golden end-to-end test.

### Exact evidence required before claiming superiority to a baseline

Publish:

1. Immutable held-out chronological manifests, checksums, and eligibility list.
2. Passing future-lap, final-result, annotation, fold-isolation, and persistence-order leakage tests.
3. Frozen configurations, features, models, calibration, seeds, horizon, objective, commit, and lockfile IDs.
4. Paired results for every baseline on identical eligible states, including abstentions and failures.
5. Predeclared primary risk-adjusted simulated metric plus observed secondary metrics with race-clustered bootstrap confidence intervals.
6. Improvement over the strongest simple eligible baseline by a predeclared practical margin, with interval excluding no improvement; otherwise report "no demonstrated improvement."
7. Calibration, segmented errors, and ablation against the learned-model-without-agent baseline.
8. A clear statement that results are conditional on public data, supported contexts, objective, and simulator assumptions—not proof of real-world strategic superiority.
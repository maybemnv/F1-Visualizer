# Architecture

## Package Dependency Diagram

```mermaid
flowchart TB
    subgraph EXT["External Dependencies"]
        FAST["fastf1<br/>F1 Timing API"]
        PLOT["plotly"]
        DASH["dash<br/>dash-bootstrap-components"]
        ML_LIB["scikit-learn<br/>KMeans, IsolationForest,<br/>GradientBoosting"]
        PD["pandas / numpy"]
        PYD["pydantic<br/>pydantic-settings"]
    end

    subgraph ROOT["Root"]
        APP["app.py"]
        CFG["config.py"]
    end

    subgraph DASHBOARD["src/dashboard/ — UI Layer"]
        LAY["layout.py<br/>Component Tree"]
        GR["graphs.py<br/>Plotly Figure Builders"]
        UT["utils.py<br/>Slider Config, Timedelta,<br/>Compound Styling"]
        CB["callbacks/<br/>6 Modules"]
        CO["components/<br/>Session Picker, Tabs,<br/>Gap Controls, Legends"]
        AL["async_loader.py<br/>ThreadPool-based<br/>Async Loading"]
    end

    subgraph CORE["src/f1_visualization/ — Core Layer"]
        DL["data_loader.py<br/>DF_DICT = load_laps()"]
        PP["preprocess.py<br/>FastF1 Fetch →<br/>Transform → CSV"]
        HP["helpers/<br/>gap.py, filters.py"]
        SS["session/<br/>info.py"]
        ML["ml/<br/>clustering.py, anomaly.py,<br/>ranking.py, features.py"]
        SC["schemas/<br/>lap_data.py, session_info.py,<br/>settings.py"]
        CA["cache/<br/>manager.py, decorators.py"]
        CO2["consts.py<br/>Seasons, Compounds,<br/>TOML Config"]
        AN["annotations.py<br/>Type Aliases"]
        EX["exceptions.py<br/>Error Hierarchy"]
        LG["logging_config.py<br/>setup_logging()"]
        VS["visualization.py<br/>Backward-compat Re-exports"]
    end

    APP --> CFG
    APP --> LAY
    APP --> CB
    CFG --> SC

    CB --> DL
    CB --> GR
    CB --> ML
    CB --> SS
    CB --> AL
    GR --> HP
    GR --> SC
    GR --> AN
    UT --> CO2
    UT --> HP

    DL --> CO2
    PP --> FAST
    SS --> FAST
    VS --> DL
    VS --> HP
    VS --> SS

    DASH --> LAY
    DASH --> CO
    PLOT --> GR
    ML_LIB --> ML
    PYD --> SC

    style ROOT fill:#1a1a2e,color:#eee,stroke:#e94560
    style DASHBOARD fill:#16213e,color:#eee,stroke:#0f3460
    style CORE fill:#1a1a2e,color:#eee,stroke:#533483
    style EXT fill:#0f3460,color:#eee,stroke:#e94560
```

---

## Data Flow

```mermaid
flowchart LR
    subgraph INGEST["Data Ingestion (preprocess.py)"]
        F1["FastF1 API<br/>f.get_session()"]
        RAW["Raw Laps<br/>DataFrame"]
        TRANS["transform()<br/>▶ add_is_slick()<br/>▶ add_compound_name()<br/>▶ add_fastest_deltas()<br/>▶ add_fuel_adjusted_time()"]
        CSV["Data/**/<br/>transformed_*.csv"]
    end

    subgraph LOAD["Dashboard Startup"]
        MLOAD["load_laps()<br/>Read all CSVs"]
        DFDICT["DF_DICT<br/>{season: {type: DataFrame}}"]
    end

    subgraph SESSION["User Loads Session"]
        SESS["FastF1<br/>Session Metadata"]
        FLTR["Filter by EventName<br/>+ Correct Dtypes"]
        STORE["dcc.Store('laps')<br/>(dict)"]
    end

    subgraph PLOTS["Plot Rendering"]
        GAP["add_gap()<br/>GapTo{driver} col"]
        PLT["dashboard.graphs.*<br/>Plotly Figure"]
        OUT["Browser<br/>Interactive Dashboard"]
    end

    F1 --> RAW
    RAW --> TRANS
    TRANS --> CSV

    CSV --> MLOAD
    MLOAD --> DFDICT

    DFDICT --> FLTR
    SESS --> FLTR
    FLTR --> STORE

    STORE --> GAP
    STORE --> PLT
    GAP --> PLT
    PLT --> OUT

    style INGEST fill:#1a1a2e,color:#eee,stroke:#e94560
    style LOAD fill:#16213e,color:#eee,stroke:#0f3460
    style SESSION fill:#1a1a2e,color:#eee,stroke:#533483
    style PLOTS fill:#0f3460,color:#eee,stroke:#e94560
```

---

## Initialization Sequence

```mermaid
sequenceDiagram
    participant app as app.py
    participant cfg as config.py
    participant settings as schemas/settings.py
    participant dl as data_loader.py
    participant log as logging_config.py
    participant dash as Dash App
    participant layout as dashboard/layout.py
    participant cb_reg as callbacks/registry.py
    participant cb_mod as callbacks/*.py

    app->>cfg: import config
    cfg->>settings: from schemas.settings import settings
    settings->>settings: AppSettings() reads F1_* env vars / .env
    settings->>settings: CacheSettings()
    settings-->>cfg: settings instance
    cfg-->>app: HOST, PORT, DATA_DIR, etc.

    app->>log: from f1_visualization.logging_config import setup_logging
    log->>settings: import settings
    log-->>app: setup_logging() ready
    app->>app: setup_logging() — configures console + file handlers

    app->>dash: Dash(__name__, ...)
    app->>layout: from dashboard.layout import app_layout
    layout->>layout: Build component tree (Header, Tabs, Stores, Footer)
    layout-->>app: app_layout
    app->>dash: app.layout = app_layout

    app->>cb_reg: register_callbacks(app)
    cb_reg->>cb_mod: import session.py
    cb_mod->>dl: import f1_visualization.data_loader
    Note over dl: DF_DICT = load_laps() — reads all CSVs at module level
    cb_mod->>cb_mod: @callback decorated functions defined
    cb_reg->>cb_mod: import data.py, drivers.py, plots.py, analysis.py, sliders.py
    cb_reg-->>app: All callbacks registered

    app->>app: app.run(host=HOST, port=PORT)
```

---

## Callback Dependency Graph

```mermaid
flowchart TD
    SEASON["Season Dropdown"] --> EVENT["Event Dropdown"]
    EVENT --> SESSION["Session Dropdown (R/S)"]
    SESSION --> LOAD_BTN["Load Session Button Enabled"]

    LOAD_BTN --> META["get_session_metadata()"]
    LOAD_BTN --> LAPS["get_session_laps()"]

    META --> DRIVERS["set_driver_dropdowns()"]
    META --> SESS_STORE["session-info store"]

    LAPS --> Y_AXIS["set_y_axis_dropdowns()"]
    LAPS --> COMPOUNDS["set_compounds_dropdown()"]
    LAPS --> SEQ["after_laps_data_callback()"]
    LAPS --> SCAT_SLIDER["set_scatterplot_slider()"]
    LAPS --> LINE_SLIDER["set_lineplot_slider()"]

    SEQ --> PLOT_TRIGGER["laps-data-sequencer (hidden span)"]

    DRIVERS --> GAP_ENABLE["enable_add_gap()"]
    GAP_ENABLE --> GAP_DRIVER["add_gap_to_driver()"]

    PLOT_TRIGGER --> STRAT["render_strategy_plot()"]
    PLOT_TRIGGER --> SCAT["render_scatterplot()"]
    PLOT_TRIGGER --> LINE["render_lineplot()"]
    PLOT_TRIGGER --> DIST["render_distplot()"]
    PLOT_TRIGGER --> COMP["render_compound_plot()"]

    Y_AXIS --> SCAT
    Y_AXIS --> LINE
    SCAT_SLIDER --> SCAT
    LINE_SLIDER --> LINE
    DRIVERS --> STRAT
    DRIVERS --> SCAT
    DRIVERS --> LINE
    DRIVERS --> DIST
    DRIVERS --> COMP
    COMPOUNDS --> COMP

    ANALYSIS_BTN["Analysis Button"] --> ML_ANALYSIS["run_analysis()"]
```

---

## ML Subsystem

```mermaid
flowchart LR
    subgraph FEATURES["Feature Extraction"]
        RAW_DF["Transformed Laps<br/>DataFrame"]
        EXTRACT["extract_driver_features()<br/>▶ Avg/Max LapTime<br/>▶ Std LapTime<br/>▶ Compound Splits<br/>▶ Position Changes<br/>▶ Gap Stats"]
        MATRIX["Feature Matrix<br/>(normalized)"]
    end

    subgraph MODELS["ML Models (scikit-learn)"]
        KM["KMeans<br/>DrivingStyleClusterer<br/>→ Aggressive / Consistent<br/>Strategic / Qualifier"]
        IF["IsolationForest<br/>PerformanceAnomalyDetector<br/>→ Detect unusual laps<br/>& position changes"]
        GB["GradientBoosting<br/>DriverRankingModel<br/>→ Performance score<br/>& driver rank"]
    end

    subgraph UI["Dashboard Integration"]
        CTRL["Analysis Tab Controls<br/>▶ Num Clusters<br/>▶ Anomaly Sensitivity<br/>▶ Ranking Options"]
        RESULT["Results Display<br/>▶ Cluster Table<br/>▶ Anomaly Highlights<br/>▶ Ranking Cards"]
    end

    RAW_DF --> EXTRACT
    EXTRACT --> MATRIX

    MATRIX --> KM
    MATRIX --> IF
    MATRIX --> GB

    CTRL --> KM
    CTRL --> IF
    CTRL --> GB

    KM --> RESULT
    IF --> RESULT
    GB --> RESULT

    style FEATURES fill:#1a1a2e,color:#eee,stroke:#533483
    style MODELS fill:#16213e,color:#eee,stroke:#0f3460
    style UI fill:#0f3460,color:#eee,stroke:#e94560
```

---

## Key Architectural Decisions

### Two-Layer Design
`f1_visualization/` is a pure data/science package with **zero Dash dependency**. The ML pipeline, caching, and data transforms can be used independently in notebooks or CLI scripts.

### Module-Level Singleton
`DF_DICT` (a `dict[int, dict[str, pd.DataFrame]]`) is populated at import time by scanning all transformed CSVs. All callbacks read from this shared in-memory dictionary, avoiding redundant file I/O.

### Sequencing Via Hidden Store
The `laps-data-sequencer` pattern (a hidden `html.Span` whose children update after laps load) ensures plot callbacks only fire after data is fully ready, preventing race conditions.

### Two Plotting Backends
- **`dashboard/graphs.py`** — Plotly figures for the interactive web dashboard
- **`f1_visualization/plots/`** — Matplotlib figures for programmatic/offline analysis

### Pydantic-Driven Configuration
All settings use `AppSettings` / `CacheSettings` with environment variable support (`F1_` prefix). Paths resolve via a `pyproject.toml` sentinel search that works in both source trees and Docker deployments.

### Preprocessing Pipeline
Data is fetched from FastF1, transformed (compound mapping, delta calculations, fuel correction), and written to CSVs by `preprocess.py`. The dashboard reads these pre-computed CSVs for fast startup.

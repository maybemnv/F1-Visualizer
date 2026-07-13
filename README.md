# F1 Visualizer

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE.txt)

An interactive dashboard and analysis toolkit for Formula 1 race data visualization and machine learning-based performance analysis. Built with Dash, Plotly, and scikit-learn.

---

## Overview

F1 Visualizer provides comprehensive tools for analyzing Formula 1 race data from the 2018 season onwards. The platform combines real-time visualization capabilities with machine learning models to deliver insights into driver performance, race strategies, and competitive dynamics.

### Key Features

- **Interactive Dashboard**: Web-based interface for exploring race data with real-time filtering and visualization
- **Strategy Analysis**: Pit stop timing, tyre degradation curves, and stint comparisons
- **Driver Performance**: Lap time distributions, position changes, and pace comparisons
- **ML-Powered Analytics**: Driving style clustering, anomaly detection, and performance ranking
- **Data Pipeline**: Automated preprocessing with validation and caching

---

## Installation

### Requirements

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended) or pip

### Quick Start

```bash
# Clone the repository
git clone https://github.com/maybemnv/F1-Visualizer.git
cd F1-Visualizer

# Create virtual environment and install dependencies
uv sync

# Run the dashboard
uv run python app.py
```

The dashboard will be available at `http://localhost:8050`.

---

## Dashboard Usage

### Loading Session Data

1. Select a season from the dropdown menu
2. Choose an event (Grand Prix)
3. Select session type (Race or Sprint)
4. Click "Load Session" to fetch data

### Available Visualizations

| Tab          | Description                                                          |
| ------------ | -------------------------------------------------------------------- |
| Strategy     | Pit stop strategies as horizontal bar charts with tyre compounds     |
| Scatterplot  | Individual lap times by driver with compound and tyre age indicators |
| Lineplot     | Position or gap progression throughout the race                      |
| Distribution | Lap time distributions as violin or box plots                        |
| Compound     | Tyre degradation analysis across different compounds                 |
| Analysis     | ML-powered clustering, anomaly detection, and rankings               |

### ML Analysis Features

The Analysis tab provides three machine learning capabilities:

- **Driving Style Clusters**: K-Means clustering identifies driving patterns (Aggressive, Consistent, Strategic, Qualifier)
- **Performance Anomalies**: Isolation Forest detects unusual lap times and position changes
- **Driver Rankings**: Gradient Boosting model ranks drivers based on performance metrics---

## Project Structure

```
F1-Visualizer/
├── app.py                    # Application entry point
├── config.py                 # Pydantic-backed configuration
├── pyproject.toml            # Project metadata & tool config
├── AGENTS.md                 # Guidelines for AI-assisted development
├── Docs/SCHEMA.md            # CSV column definitions
├── Assets/                   # Static assets (CSS, images)
├── Automation/               # Deployment and data-refresh scripts
├── Comments/                 # Design notes and documentation
├── Data/                     # Race and sprint session data
├── Docs/                     # Visual examples and references
├── src/                      # Source packages
│   ├── dashboard/
│   │   ├── layout.py         # UI layout composition
│   │   ├── graphs.py         # Plotly graph generators
│   │   ├── constants.py      # Plot dimensions & magic numbers
│   │   ├── utils.py          # UI helper utilities
│   │   ├── async_loader.py   # Async data loading
│   │   ├── callbacks/        # Dash callback handlers
│   │   └── components/       # Reusable UI components
│   └── f1_visualization/
│       ├── preprocess.py     # Data transformation pipeline
│       ├── data_loader.py    # CSV loading & dtype correction
│       ├── visualization.py  # Re-exports for backward compat
│       ├── annotations.py    # Shared type aliases (Session, Figure, Axes)
│       ├── consts.py         # Seasons, sprint rounds, compound maps
│       ├── exceptions.py     # Domain-specific exception classes
│       ├── logging_config.py # Centralized logging configuration
│       ├── plots/            # Matplotlib plotting functions
│       ├── ml/               # Machine learning models
│       ├── cache/            # Multi-level caching (memory + disk)
│       ├── schemas/          # Pydantic validation models
│       ├── session/          # Session info helpers
│       └── helpers/          # Gap calculation, SC detection, etc.
├── tests/                    # Unit and integration tests
│   ├── dashboard/            # Dashboard package tests
│   └── f1_visualization/     # Core package tests
├── Dockerfile                # Container configuration
└── docker-compose.yml        # Multi-container orchestration
```

---

## Data Pipeline

### Source

All data is sourced from the [FastF1](https://github.com/theOehrly/Fast-F1) package, which provides access to official F1 timing data.

### Availability

- Grand Prix races: 2018 season onwards
- Sprint races: 2021 season onwards
- Excludes test sessions and practice data

### Schema

Refer to `Docs/SCHEMA.md` for detailed column definitions in the processed data files.

---

## Configuration

Settings are managed via [Pydantic Settings](https://docs.pydantic.dev/latest/usage/pydantic_settings/)
with the `F1_` prefix. A `.env` file is supported.

| Variable                    | Default          | Description                          |
| --------------------------- | ---------------- | ------------------------------------ |
| `F1_HOST`                   | 127.0.0.1        | Server bind address                  |
| `F1_PORT`                   | 8050             | Server port                          |
| `F1_DEBUG`                  | false            | Debug mode                           |
| `F1_LOG_LEVEL`              | INFO             | Logging verbosity                    |
| `F1_LOG_TO_FILE`            | true             | Enable file logging                  |
| `F1_LOG_MAX_BYTES`          | 10_000_000       | Max log file size                    |
| `F1_LOG_BACKUP_COUNT`       | 5                | Number of log backups                |
| `F1_DATA_DIR`               | ./Data           | Data directory path                  |
| `F1_CACHE_DIR`              | ./.cache         | Cache directory path                 |
| `F1_CACHE_ENABLED`          | true             | Enable data caching                  |
| `F1_MEMORY_CACHE_SIZE`      | 256              | LRU cache size (entries)             |
| `F1_DISK_CACHE_TTL_HOURS`   | 24               | Disk cache TTL                       |
| `F1_MIN_LAPS_FOR_ANALYSIS`  | 5                | Minimum laps for driver analysis     |
| `F1_UPPER_BOUND_DEFAULT`    | 107.0            | Default lap time percentile cap      |

---

## License

This project is licensed under the Apache License 2.0. See [LICENSE.txt](LICENSE.txt) for details.

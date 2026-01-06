# F1 Visualizer - Project Context

## Project Overview

F1 Visualizer is an interactive dashboard and analysis toolkit for Formula 1 race data visualization and machine learning-based performance analysis. Built with Dash, Plotly, and scikit-learn, it provides comprehensive tools for analyzing Formula 1 race data from the 2018 season onwards.

The platform combines real-time visualization capabilities with machine learning models to deliver insights into driver performance, race strategies, and competitive dynamics.

### Key Features

- **Interactive Dashboard**: Web-based interface for exploring race data with real-time filtering and visualization
- **Strategy Analysis**: Pit stop timing, tyre degradation curves, and stint comparisons
- **Driver Performance**: Lap time distributions, position changes, and pace comparisons
- **ML-Powered Analytics**: Driving style clustering, anomaly detection, and performance ranking
- **Data Pipeline**: Automated preprocessing with validation and caching

## Architecture

### Main Components

- `app.py`: Application entry point that initializes the Dash application
- `config.py`: Configuration management using Pydantic settings
- `dashboard/`: Contains UI components, callbacks, and layout
  - `layout.py`: UI layout composition
  - `callbacks/`: Dash callback handlers (analysis, data, drivers, plots, session, sliders)
  - `components/`: Reusable UI components
  - `graphs.py`: Plotly graph generators
- `f1_visualization/`: Core data processing and ML functionality
  - `preprocess.py`: Data transformation pipeline
  - `plots/`: Matplotlib plotting functions
  - `ml/`: Machine learning models
  - `cache/`: Multi-level caching system
  - `schemas/`: Pydantic data validation
- `Data/`: Race and sprint session data storage
- `tests/`: Unit and integration tests

## Data Pipeline

### Source

All data is sourced from the [FastF1](https://github.com/theOehrly/Fast-F1) package, which provides access to official F1 timing data.

### Availability

- Grand Prix races: 2018 season onwards
- Sprint races: 2021 season onwards
- Excludes test sessions and practice data

### Data Processing

The data pipeline includes:
1. Loading raw data from FastF1 API
2. Transforming data with additional calculated columns
3. Validation and caching for performance
4. Storage in CSV format

## Configuration

The application uses Pydantic-based settings with environment variable support:

### Environment Variables (prefix `F1_`)

| Variable | Default | Description |
|----------|---------|-------------|
| `F1_HOST` | 127.0.0.1 | Server bind address |
| `F1_PORT` | 8050 | Server port |
| `F1_LOG_LEVEL` | INFO | Logging verbosity |
| `F1_CACHE_ENABLED` | true | Enable data caching |
| `F1_DATA_DIR` | ./Data | Data directory path |

### Additional Settings

- `F1_CACHE_DISK_TTL_HOURS`: Disk cache TTL in hours (default: 24)
- `F1_MEMORY_CACHE_SIZE`: LRU cache size (default: 256)
- `F1_MIN_LAPS_FOR_ANALYSIS`: Minimum laps for driver analysis (default: 5)
- `F1_UPPER_BOUND_DEFAULT`: Default upper bound percentage (default: 107.0)

## Dependencies

Key dependencies include:
- `fastf1 >= 3.6.0`: F1 data access
- `pandas >= 2.0.0`: Data manipulation
- `dash >= 3.0.0`: Web framework
- `plotly >= 5.0.0`: Visualization
- `scikit-learn >= 1.3.0`: Machine learning
- `pydantic >= 2.0.0`: Configuration validation

## Building and Running

### Local Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
python app.py
```

The dashboard will be available at `http://localhost:8050`.

### Using uv (recommended)

```bash
# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Run the dashboard
uv run app.py
```

### Docker

Build and run with Docker:

```bash
# Build and run
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d
```

## Dashboard Usage

### Loading Session Data

1. Select a season from the dropdown menu
2. Choose an event (Grand Prix)
3. Select session type (Race or Sprint)
4. Click "Load Session" to fetch data

### Available Visualizations

| Tab | Description |
|-----|-------------|
| Strategy | Pit stop strategies as horizontal bar charts with tyre compounds |
| Scatterplot | Individual lap times by driver with compound and tyre age indicators |
| Lineplot | Position or gap progression throughout the race |
| Distribution | Lap time distributions as violin or box plots |
| Compound | Tyre degradation analysis across different compounds |
| Analysis | ML-powered clustering, anomaly detection, and rankings |

### ML Analysis Features

The Analysis tab provides three machine learning capabilities:

- **Driving Style Clusters**: K-Means clustering identifies driving patterns (Aggressive, Consistent, Strategic, Qualifier)
- **Performance Anomalies**: Isolation Forest detects unusual lap times and position changes
- **Driver Rankings**: Gradient Boosting model ranks drivers based on performance metrics

## Testing

The project includes a comprehensive test suite using pytest:

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=f1_visualization

# Run specific test file
pytest tests/test_graphs.py
```

## Development Conventions

- Code follows Ruff linting standards
- Type hints are used throughout the codebase
- Pydantic is used for data validation and configuration
- FastF1 is the primary source for F1 data
- Dash is used for the web interface
- Plotly for interactive visualizations
- Scikit-learn for machine learning models

## Data Schema

The project uses two main CSV file types:

### `all_laps_*.csv`
- Contains all columns provided by Fastf1.laps
- Includes RoundNumber and EventName columns

### `transformed_laps_*.csv`
- Contains processed data with additional calculated columns
- Includes validity flags, time deltas, and fuel-adjusted times
- See SCHEMA.md for detailed column definitions

## Containerization

The project includes both Dockerfile and docker-compose.yml for containerized deployment:

- Multi-stage Docker build for optimized image size
- Named volumes for data persistence
- Health checks for container monitoring
- Resource limits to prevent excessive usage
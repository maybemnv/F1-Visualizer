# F1 Visualizer - Complete Documentation

An interactive Formula 1 strategy analysis and visualization dashboard featuring race data from 2018 onwards.

**Author**: Manav ([@maybemnv](https://github.com/maybemnv))  
**Repository**: [github.com/maybemnv/F1-Visualizer](https://github.com/maybemnv/F1-Visualizer)

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation Guide](#installation-guide)
3. [Running Locally](#running-locally)
4. [Deployment Guide](#deployment-guide)
5. [Project Rating & Analysis](#project-rating--analysis)
6. [Architecture Overview](#architecture-overview)
7. [Tech Stack](#tech-stack)

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/maybemnv/F1-Visualizer.git
cd F1-Visualizer

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Unix/Mac)
source .venv/bin/activate

# Install dependencies
pip install -e .

# Run the dashboard
python app.py
```

Then open **http://localhost:8000** in your browser.

---

## Installation Guide

### Prerequisites

- **Python**: 3.10 or higher
- **pip**: Latest version recommended
- **Git**: For cloning the repository

### Step-by-Step Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/maybemnv/F1-Visualizer.git
cd F1-Visualizer
```

#### 2. Create Virtual Environment

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Install Dependencies

```bash
# Install the package in editable mode (recommended for development)
pip install -e .

# Or install from requirements.txt
pip install -r requirements.txt
```

#### 4. Install Pre-commit Hooks (Optional, for development)

```bash
pre-commit install
```

### Dependencies Overview

| Package                     | Purpose                    |
| --------------------------- | -------------------------- |
| `fastf1`                    | F1 telemetry data API      |
| `pandas`                    | Data manipulation          |
| `dash`                      | Web application framework  |
| `dash-bootstrap-components` | UI components              |
| `plotly`                    | Interactive visualizations |
| `matplotlib` / `seaborn`    | Static visualizations      |
| `gunicorn`                  | Production server          |

---

## Running Locally

### Development Mode

```bash
# Run with auto-reload for development
python app.py
```

The dashboard will be available at **http://localhost:8000**

### Debug Mode

Edit `app.py` and change the last line:

```python
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)  # Add debug=True
```

### Generate README Visualizations

```bash
# Generate latest race visuals
python readme_machine.py

# Generate for specific race (season, round)
python readme_machine.py 2024 5

# Generate for sprint race
python readme_machine.py 2024 5 --sprint-race

# Update README with new graphics
python readme_machine.py --update-readme
```

---

## Deployment Guide

### Option 1: Deploy to Render (Recommended)

1. **Create a `render.yaml`:**

```yaml
services:
  - type: web
    name: f1-visualizer
    env: python
    plan: free
    buildCommand: pip install -e .
    startCommand: gunicorn app:server -b 0.0.0.0:$PORT
```

2. **Push to GitHub** and connect your repo to Render

3. **Set environment variables** if needed

### Option 2: Deploy to Heroku

1. **Create a `Procfile`:**

```
web: gunicorn app:server -b 0.0.0.0:$PORT
```

2. **Create `runtime.txt`:**

```
python-3.11.0
```

3. **Deploy:**

```bash
heroku create f1-visualizer
git push heroku main
```

### Option 3: Deploy to AWS EC2

1. **Launch an EC2 instance** (Ubuntu recommended)

2. **Clone and setup:**

```bash
git clone https://github.com/maybemnv/F1-Visualizer.git
cd F1-Visualizer
python3 -m venv env
source env/bin/activate
pip install -e .
```

3. **Run with Gunicorn:**

```bash
gunicorn app:server -b 0.0.0.0:8000 --daemon
```

4. **Use automation scripts:**

```bash
# Start server
./Automation/start-server.sh

# Refresh data
./Automation/data-refresh.sh
```

### Option 4: Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e .

EXPOSE 8000
CMD ["gunicorn", "app:server", "-b", "0.0.0.0:8000"]
```

Build and run:

```bash
docker build -t f1-visualizer .
docker run -p 8000:8000 f1-visualizer
```

### Option 5: Railway.app

1. Connect your GitHub repository
2. Railway auto-detects Python and deploys
3. Set the start command: `gunicorn app:server -b 0.0.0.0:$PORT`

---

## Project Rating & Analysis

### Overall Rating: ⭐⭐⭐⭐⭐ (8.5/10)

This is a **production-ready, well-architected** F1 data visualization project with professional code quality.

---

### Detailed Breakdown

| Category            | Rating | Notes                                                                    |
| ------------------- | ------ | ------------------------------------------------------------------------ |
| **Code Quality**    | 9/10   | Excellent use of type hints, docstrings, comprehensive linting with Ruff |
| **Architecture**    | 8.5/10 | Clean separation of concerns (data, visualization, dashboard)            |
| **Documentation**   | 8/10   | Good README, SCHEMA.md for data columns, inline comments                 |
| **Testing**         | 6/10   | Could benefit from unit tests and integration tests                      |
| **UI/UX**           | 8/10   | Clean Bootstrap theme, intuitive controls, responsive                    |
| **Data Pipeline**   | 9/10   | Robust preprocessing with computed metrics and error handling            |
| **Automation**      | 9/10   | Excellent CI/CD scripts, SNS notifications, Reddit automation            |
| **Maintainability** | 8.5/10 | Modular design, configuration via TOML files                             |

---

### Strengths 💪

1. **Professional Code Quality**

   - Comprehensive Ruff linting configuration
   - Type hints throughout the codebase
   - Pre-commit hooks for consistency
   - Clean docstrings and documentation

2. **Robust Data Pipeline**

   - Automated data refresh from FastF1 API
   - Computed metrics (fuel-adjusted times, deltas, gap calculations)
   - Well-documented data schema

3. **Feature-Rich Dashboard**

   - Multiple visualization types (strategy, scatter, line, distribution, compounds)
   - Interactive filtering and driver selection
   - Safety Car/VSC period detection

4. **Production-Ready Automation**

   - Server health monitoring scripts
   - AWS SNS notifications for errors
   - Automated Reddit posting

5. **Great Data Engineering**
   - Efficient caching with dcc.Store
   - Proper handling of pandas Timedelta serialization
   - Computed columns for insights

---

### Areas for Improvement 🔧

1. **Add Unit Tests**

   - Test data processing functions
   - Test callback logic

2. **Add CI/CD Pipeline**

   - GitHub Actions for automated testing
   - Automated deployment on merge

3. **Performance Optimization**

   - Consider Redis for caching larger datasets
   - Add loading states to improve perceived performance

4. **Enhanced Features**
   - Add user authentication for personalized views
   - Export functionality for visualizations
   - Mobile-responsive improvements

---

### Use Cases

- **F1 Fans**: Analyze race strategies and driver performance
- **Data Enthusiasts**: Explore historical F1 data
- **Portfolio Project**: Demonstrates full-stack data visualization skills
- **Educational**: Learn Dash/Plotly best practices

---

## Architecture Overview

```
F1-Visualizer/
├── app.py                    # Main Dash application
├── readme_machine.py         # README visualization generator
├── reddit_machine.py         # Reddit automation
│
├── f1_visualization/         # Core package
│   ├── consts.py            # Constants and config
│   ├── preprocess.py        # Data pipeline
│   └── visualization.py     # Plotting functions
│
├── dashboard/                # Dashboard modules
│   ├── graphs.py            # Plotly graphs
│   └── layout.py            # UI components
│
├── Data/                     # CSV data storage
├── Automation/               # Server scripts
└── .docs/                    # Documentation
```

---

## Tech Stack

| Layer             | Technology                                        |
| ----------------- | ------------------------------------------------- |
| **Frontend**      | Dash, Plotly, Bootstrap                           |
| **Backend**       | Python, Dash callbacks                            |
| **Data**          | FastF1 API, Pandas, NumPy                         |
| **Visualization** | Plotly (interactive), Matplotlib/Seaborn (static) |
| **Deployment**    | Gunicorn, AWS EC2                                 |
| **Code Quality**  | Ruff, pre-commit, type hints                      |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Install pre-commit hooks: `pre-commit install`
4. Make your changes and commit
5. Push and create a Pull Request

---

## License

Apache 2.0 - See [LICENSE.txt](../LICENSE.txt)

---

_Built with ❤️ by Manav_

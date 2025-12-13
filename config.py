"""Application configuration with environment variable support."""

import os
from pathlib import Path

# Base paths
ROOT_DIR = Path(__file__).absolute().parent
DATA_DIR = Path(os.getenv("F1_DATA_DIR", str(ROOT_DIR / "Data")))
CACHE_DIR = Path(os.getenv("F1_CACHE_DIR", str(DATA_DIR / "cache")))

# Server configuration
HOST = os.getenv("F1_HOST", "0.0.0.0")
PORT = int(os.getenv("F1_PORT", "8000"))

# Debug mode
DEBUG = os.getenv("F1_DEBUG", "false").lower() == "true"

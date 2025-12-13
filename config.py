"""Application configuration - backward compatible with Pydantic settings."""

# Re-export from new Pydantic-based settings
from f1_visualization.schemas.settings import settings

# Backward-compatible exports
ROOT_DIR = settings.data_dir.parent
DATA_DIR = settings.data_dir
CACHE_DIR = settings.cache_dir
HOST = settings.host
PORT = settings.port
DEBUG = settings.debug

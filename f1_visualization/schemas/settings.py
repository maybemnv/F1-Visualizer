"""Pydantic settings for application configuration."""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_prefix="F1_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Paths
    data_dir: Path = Field(
        default=Path(__file__).parents[2] / "Data",
        description="Directory containing F1 data files",
    )
    cache_dir: Path = Field(
        default=Path(__file__).parents[2] / ".cache",
        description="Directory for cache files",
    )
    log_dir: Path = Field(
        default=Path(__file__).parents[2] / "logs",
        description="Directory for log files",
    )

    # Server
    host: str = Field(default="127.0.0.1", description="Server host")
    port: int = Field(default=8050, ge=1, le=65535, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")

    # Caching
    cache_enabled: bool = Field(default=True, description="Enable caching")
    memory_cache_size: int = Field(default=256, ge=16, description="LRU cache size")
    disk_cache_ttl_hours: int = Field(default=24, ge=1, description="Disk cache TTL in hours")

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", description="Logging level"
    )
    log_to_file: bool = Field(default=True, description="Enable file logging")
    log_max_bytes: int = Field(default=10_000_000, description="Max log file size")
    log_backup_count: int = Field(default=5, ge=1, description="Number of log backups")

    # Data processing
    min_laps_for_analysis: int = Field(
        default=5, ge=1, description="Minimum laps for driver analysis"
    )
    upper_bound_default: float = Field(
        default=107.0, description="Default upper bound percentage"
    )


class CacheSettings(BaseSettings):
    """Cache-specific settings."""

    model_config = SettingsConfigDict(env_prefix="F1_CACHE_", extra="ignore")

    enabled: bool = Field(default=True)
    memory_size: int = Field(default=256)
    disk_ttl_hours: int = Field(default=24)
    disk_format: Literal["pickle", "parquet"] = Field(default="pickle")


# Global settings instance
settings = AppSettings()
cache_settings = CacheSettings()

"""Centralized logging configuration for F1 Visualizer."""

import logging
import logging.handlers
import sys
from pathlib import Path

from f1_visualization.schemas.settings import settings


def setup_logging(
    level: str | None = None,
    log_to_file: bool | None = None,
    log_dir: Path | None = None,
) -> None:
    """
    Configure application-wide logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_to_file: Whether to log to file
        log_dir: Directory for log files
    """
    level = level or settings.log_level
    log_to_file = log_to_file if log_to_file is not None else settings.log_to_file
    log_dir = log_dir or settings.log_dir

    # Create log directory
    if log_to_file:
        log_dir.mkdir(parents=True, exist_ok=True)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))
    console_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler (if enabled)
    if log_to_file:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_dir / "f1_visualizer.log",
            maxBytes=settings.log_max_bytes,
            backupCount=settings.log_backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(getattr(logging, level))
        file_formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Configure third-party loggers to be less verbose
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("fastf1").setLevel(logging.INFO)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)

    logging.info("Logging configured: level=%s, file=%s", level, log_to_file)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class LogContext:
    """Context manager for adding extra context to log messages."""

    def __init__(self, logger: logging.Logger, **context: str | int | float):
        """
        Initialize log context.

        Args:
            logger: Logger instance
            **context: Key-value pairs to add to log messages
        """
        self.logger = logger
        self.context = context

    def __enter__(self) -> "LogContext":
        """Enter the context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:  # noqa: ANN001
        """Exit the context, logging any exception."""
        if exc_type is not None:
            self.logger.exception(
                "Error in context %s: %s",
                self.context,
                exc_val,
            )
        return False

    def info(self, msg: str, *args: object) -> None:
        """Log info with context."""
        self.logger.info(f"[{self.context}] {msg}", *args)

    def debug(self, msg: str, *args: object) -> None:
        """Log debug with context."""
        self.logger.debug(f"[{self.context}] {msg}", *args)

    def warning(self, msg: str, *args: object) -> None:
        """Log warning with context."""
        self.logger.warning(f"[{self.context}] {msg}", *args)

    def error(self, msg: str, *args: object) -> None:
        """Log error with context."""
        self.logger.error(f"[{self.context}] {msg}", *args)


# Initialize logging on import if not already configured
if not logging.getLogger().handlers:
    setup_logging()

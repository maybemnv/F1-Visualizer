"""Custom exception classes for F1 Visualizer."""


class F1VisualizerError(Exception):
    """Base exception for all F1 Visualizer errors."""

    def __init__(self, message: str, details: dict | None = None):
        """
        Initialize exception.

        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class DataNotFoundError(F1VisualizerError):
    """Raised when requested data is not available."""

    def __init__(
        self,
        message: str = "Requested data not found",
        season: int | None = None,
        event: str | None = None,
        session: str | None = None,
    ):
        """Initialize with optional context about what data was requested."""
        details = {}
        if season:
            details["season"] = season
        if event:
            details["event"] = event
        if session:
            details["session"] = session

        super().__init__(message, details)


class ValidationError(F1VisualizerError):
    """Raised when data validation fails."""

    def __init__(
        self,
        message: str = "Data validation failed",
        field: str | None = None,
        value: str | None = None,
        expected: str | None = None,
    ):
        """Initialize with validation failure context."""
        details = {}
        if field:
            details["field"] = field
        if value:
            details["value"] = value
        if expected:
            details["expected"] = expected

        super().__init__(message, details)


class CacheError(F1VisualizerError):
    """Raised when cache operations fail."""

    def __init__(
        self,
        message: str = "Cache operation failed",
        operation: str | None = None,
        key: str | None = None,
    ):
        """Initialize with cache operation context."""
        details = {}
        if operation:
            details["operation"] = operation
        if key:
            details["key"] = key

        super().__init__(message, details)


class SessionLoadError(F1VisualizerError):
    """Raised when session loading fails."""

    def __init__(
        self,
        message: str = "Failed to load session",
        season: int | None = None,
        event: str | None = None,
        session: str | None = None,
        cause: Exception | None = None,
    ):
        """Initialize with session context."""
        details = {"season": season, "event": event, "session": session}
        if cause:
            details["cause"] = str(cause)

        super().__init__(message, {k: v for k, v in details.items() if v is not None})
        self.__cause__ = cause


class ConfigurationError(F1VisualizerError):
    """Raised when configuration is invalid."""

    def __init__(
        self,
        message: str = "Configuration error",
        setting: str | None = None,
        value: str | None = None,
    ):
        """Initialize with configuration context."""
        details = {}
        if setting:
            details["setting"] = setting
        if value:
            details["value"] = value

        super().__init__(message, details)


class DataProcessingError(F1VisualizerError):
    """Raised when data processing/transformation fails."""

    def __init__(
        self,
        message: str = "Data processing failed",
        step: str | None = None,
        row_count: int | None = None,
    ):
        """Initialize with processing context."""
        details = {}
        if step:
            details["step"] = step
        if row_count is not None:
            details["row_count"] = row_count

        super().__init__(message, details)

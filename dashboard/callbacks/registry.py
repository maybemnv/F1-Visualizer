"""Register dashboard callbacks by importing callback modules."""

from dash import Dash

# Import callback modules so their decorators register with Dash.
from dashboard.callbacks import analysis, data, drivers, plots, session, sliders  # noqa: F401


def register_callbacks(app: Dash) -> None:
    """Register all callbacks with the Dash application."""
    _ = app

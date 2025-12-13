"""Callbacks package for the F1 Visualizer dashboard.

This module provides a centralized way to register all callbacks with the Dash app.
"""

from dash import Dash

# Import all callback modules to register them
from dashboard.callbacks import analysis, data, drivers, plots, session, sliders


def register_callbacks(app: Dash) -> None:
    """
    Register all callbacks with the Dash application.

    This function is called once during app initialization. The callbacks
    are automatically registered when their modules are imported, so this
    function mainly serves as documentation and ensures all modules are loaded.

    Args:
        app: The Dash application instance.
    """
    # Callbacks are registered via decorators when modules are imported
    # This function ensures all modules are loaded and provides a clean API
    _ = app  # App instance available if needed for future extensions

    # Explicitly reference modules to prevent unused import warnings
    _ = session
    _ = drivers
    _ = data
    _ = plots
    _ = sliders
    _ = analysis


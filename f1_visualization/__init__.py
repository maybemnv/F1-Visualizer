"""F1 Visualization package for loading, transforming, and visualizing F1 race data."""

# Core imports for backward compatibility
from f1_visualization.data_loader import DF_DICT, load_laps
from f1_visualization.helpers import (
    add_gap,
    find_sc_laps,
    remove_low_data_drivers,
    teammate_comp_order,
)
from f1_visualization.session import get_drivers, get_session_info, infer_ergast_data

__all__ = [
    # Data loading
    "load_laps",
    "DF_DICT",
    # Session
    "get_session_info",
    "get_drivers",
    "infer_ergast_data",
    # Helpers
    "add_gap",
    "find_sc_laps",
    "remove_low_data_drivers",
    "teammate_comp_order",
]

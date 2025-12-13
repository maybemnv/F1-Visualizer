"""Plotting functions and other visualization helpers.

This module maintains backward compatibility by re-exporting functions
from the new modular structure.
"""

# Re-export everything from the modular structure for backward compatibility
from f1_visualization.data_loader import DF_DICT, load_laps
from f1_visualization.helpers import (
    add_gap,
    find_sc_laps,
    remove_low_data_drivers,
    teammate_comp_order,
)
from f1_visualization.plots import (
    compounds_distplot,
    compounds_lineplot,
    convert_compound_name,
    deduplicate_legend_labels,
    driver_stats_distplot,
    driver_stats_lineplot,
    driver_stats_scatterplot,
    find_legend_order,
    get_plot_args,
    shade_sc_periods,
    strategy_barplot,
)
from f1_visualization.plots.config import get_plot_args as _plot_args
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
    # Plots config
    "get_plot_args",
    "_plot_args",
    "find_legend_order",
    "shade_sc_periods",
    "deduplicate_legend_labels",
    "convert_compound_name",
    # Driver stats plots
    "driver_stats_scatterplot",
    "driver_stats_lineplot",
    "driver_stats_distplot",
    # Strategy plots
    "strategy_barplot",
    "compounds_lineplot",
    "compounds_distplot",
]

"""Plotting functions package for F1 visualization."""

from f1_visualization.plots.config import (
    convert_compound_name,
    deduplicate_legend_labels,
    find_legend_order,
    get_plot_args,
    shade_sc_periods,
)
from f1_visualization.plots.driver_stats import (
    driver_stats_distplot,
    driver_stats_lineplot,
    driver_stats_scatterplot,
)
from f1_visualization.plots.strategy import (
    compounds_distplot,
    compounds_lineplot,
    strategy_barplot,
)

__all__ = [
    # Config
    "get_plot_args",
    "find_legend_order",
    "shade_sc_periods",
    "deduplicate_legend_labels",
    "convert_compound_name",
    # Driver stats
    "driver_stats_scatterplot",
    "driver_stats_lineplot",
    "driver_stats_distplot",
    # Strategy
    "strategy_barplot",
    "compounds_lineplot",
    "compounds_distplot",
]

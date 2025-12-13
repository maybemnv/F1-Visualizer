"""Tab components package."""

from dashboard.components.tabs.analysis_tab import analysis_tab
from dashboard.components.tabs.common import lap_numbers_slider, upper_bound_slider
from dashboard.components.tabs.compound_tab import compound_plot_tab
from dashboard.components.tabs.distplot_tab import distplot_tab
from dashboard.components.tabs.legends_tab import legends_tab
from dashboard.components.tabs.lineplot_tab import line_y_options, lineplot_tab
from dashboard.components.tabs.scatterplot_tab import scatter_y_options, scatterplot_tab
from dashboard.components.tabs.strategy_tab import strategy_tab

__all__ = [
    "upper_bound_slider",
    "lap_numbers_slider",
    "strategy_tab",
    "scatterplot_tab",
    "scatter_y_options",
    "lineplot_tab",
    "line_y_options",
    "distplot_tab",
    "compound_plot_tab",
    "legends_tab",
    "analysis_tab",
]


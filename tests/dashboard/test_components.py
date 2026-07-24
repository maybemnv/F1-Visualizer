"""Tests for dashboard components."""

from dashboard.components.tabs.common import responsive_graph


def test_responsive_graph_sets_dash_responsive_options():
    """Responsive graph helper should size figures to their container."""
    graph = responsive_graph("race-plot")

    assert graph.id == "race-plot"
    assert graph.config == {"responsive": True}
    assert graph.responsive is True
    assert graph.style["width"] == "100%"

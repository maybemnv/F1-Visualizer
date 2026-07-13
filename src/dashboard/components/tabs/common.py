"""Common tab utilities and slider factories."""

from dash import dcc

from dashboard.constants import DEFAULT_UPPER_BOUND, UPPER_BOUND_MAX, UPPER_BOUND_MIN


def upper_bound_slider(slider_id: str, **kwargs) -> dcc.Slider:  # noqa: ANN003
    """Generate generic slider for setting upper bound."""
    return dcc.Slider(
        min=UPPER_BOUND_MIN,
        max=UPPER_BOUND_MAX,
        marks={i: str(i) for i in range(100, 116, 5)} | {150: "Show All"},
        value=DEFAULT_UPPER_BOUND,
        tooltip={"placement": "top"},
        id=slider_id,
        **kwargs,
    )


def lap_numbers_slider(slider_id: str, **kwargs) -> dcc.RangeSlider:  # noqa: ANN003
    """Generate generic range slider for setting lap numbers."""
    return dcc.RangeSlider(
        min=1,
        step=1,
        allowCross=False,
        tooltip={"placement": "bottom"},
        id=slider_id,
        **kwargs,
    )

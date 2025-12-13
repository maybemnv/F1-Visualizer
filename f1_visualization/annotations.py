"""Shared type annotations."""

from typing import NamedTuple, TypeAlias

import fastf1
from matplotlib.axes import Axes as MplAxes
from matplotlib.figure import Figure as MplFigure

Session: TypeAlias = fastf1.core.Session
Figure: TypeAlias = MplFigure
Axes: TypeAlias = MplAxes


class PlotArgs(NamedTuple):
    """Data class for plot styling configuration."""

    hue: str
    palette: dict[str, str]
    markers: dict[str, str]
    labels: list[str]

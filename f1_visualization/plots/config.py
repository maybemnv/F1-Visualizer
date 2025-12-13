"""Plotting configuration and utility functions."""

from collections.abc import Iterable

import numpy as np
from matplotlib import pyplot as plt

from f1_visualization.annotations import Axes, PlotArgs
from f1_visualization.consts import COMPOUND_SELECTION, VISUAL_CONFIG


def find_legend_order(labels: Iterable[str]) -> list[int]:
    """
    Provide the index of a list of compounds sorted from soft to hard.

    Args:
        labels: A list of string representing the tyre compounds.

    Returns:
        A list of ints corresponding to the original index of the
        compound names if they were in sorted order.
    """
    old_indices = list(range(len(labels)))
    sorted_labels = []

    if any(name in labels for name in ("HYPERSOFT", "ULTRASOFT", "SUPERSOFT", "SUPERHARD")):
        sorted_labels = VISUAL_CONFIG["absolute"]["labels"]["18"]
    elif any(label.startswith("C") for label in labels):
        sorted_labels = VISUAL_CONFIG["absolute"]["labels"]["19_22"]
    else:
        sorted_labels = VISUAL_CONFIG["relative"]["labels"]

    pos = [sorted_labels.index(label) for label in labels]
    return [old_index for _, old_index in sorted(zip(pos, old_indices, strict=True))]


def get_plot_args(season: int, absolute_compound: bool) -> PlotArgs:
    """
    Get plotting arguments based on the season and compound type.

    Args:
        season: Championship season
        absolute_compound: If true, use absolute compound names (C1, C2...)
                          Else, use relative compound names (SOFT, MEDIUM, HARD)
    """
    if absolute_compound:
        if season == 2018:  # noqa: PLR2004
            return PlotArgs(
                "CompoundName",
                VISUAL_CONFIG["absolute"]["palette"]["18"],
                VISUAL_CONFIG["absolute"]["markers"]["18"],
                VISUAL_CONFIG["absolute"]["labels"]["18"],
            )
        if season < 2023:  # noqa: PLR2004
            return PlotArgs(
                "CompoundName",
                VISUAL_CONFIG["absolute"]["palette"]["19_22"],
                VISUAL_CONFIG["absolute"]["markers"]["19_22"],
                VISUAL_CONFIG["absolute"]["labels"]["19_22"],
            )
        if season < 2025:  # noqa: PLR2004
            return PlotArgs(
                "CompoundName",
                VISUAL_CONFIG["absolute"]["palette"]["23_24"],
                VISUAL_CONFIG["absolute"]["markers"]["23_24"],
                VISUAL_CONFIG["absolute"]["labels"]["23_24"],
            )
        return PlotArgs(
            "CompoundName",
            VISUAL_CONFIG["absolute"]["palette"]["25_"],
            VISUAL_CONFIG["absolute"]["markers"]["25_"],
            VISUAL_CONFIG["absolute"]["labels"]["25_"],
        )

    return PlotArgs(
        "Compound",
        VISUAL_CONFIG["relative"]["palette"],
        VISUAL_CONFIG["relative"]["markers"],
        VISUAL_CONFIG["relative"]["labels"],
    )


def shade_sc_periods(sc_laps: np.ndarray, vsc_laps: np.ndarray) -> None:
    """
    Shade SC and VSC periods on a matplotlib plot.

    Args:
        sc_laps: Sorted array of integers indicating laps under safety car
        vsc_laps: sorted array of integers indicating laps under virtual safety car
    """
    sc_laps = np.append(sc_laps, [-1])
    vsc_laps = np.append(vsc_laps, [-1])

    def plot_periods(laps: np.ndarray, label: str, hatch: str | None = None) -> None:
        start = 0
        end = 1

        while end < len(laps):
            if laps[end] == laps[end - 1] + 1:
                end += 1
            else:
                plt.axvspan(
                    xmin=laps[start] - 1,
                    xmax=laps[end - 1],
                    alpha=0.5,
                    color="orange",
                    label=label if start == 0 else "_",
                    hatch=hatch,
                )
                start = end
                end += 1

    plot_periods(sc_laps, "SC")
    plot_periods(vsc_laps, "VSC", "xx")


def deduplicate_legend_labels(ax: Axes, **kwargs) -> None:  # noqa: ANN003
    """
    Add legend to the current plot after deduplicating labels.

    Useful when labelled elements are added one-by-one, such as when showing SC periods.
    """
    handles, labels = ax.get_legend_handles_labels()
    if labels:
        deduplicate_labels_handles = dict(zip(labels, handles, strict=True))
        plt.legend(
            handles=deduplicate_labels_handles.values(),
            labels=deduplicate_labels_handles.keys(),
            **kwargs,
        )


def convert_compound_name(
    season: int, round_number: int, compounds: Iterable[str]
) -> tuple[str]:
    """Convert relative compound names to absolute compound names."""
    compound_to_index = {"SOFT": 2, "MEDIUM": 1, "HARD": 0}
    if season == 2018:  # noqa: PLR2004
        compound_to_index = {"SOFT": 0, "MEDIUM": 1, "HARD": 2}

    return_vals = [
        COMPOUND_SELECTION[str(season)][str(round_number)][compound_to_index[compound]]
        for compound in compounds
    ]

    return tuple(return_vals)

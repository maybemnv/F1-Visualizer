"""Driver statistics visualization functions using matplotlib."""

import logging
from collections.abc import Iterable
from math import ceil
from typing import Literal

import fastf1.plotting as p
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib import rcParams

from f1_visualization.annotations import Figure
from f1_visualization.consts import VISUAL_CONFIG
from f1_visualization.data_loader import DF_DICT
from f1_visualization.helpers import find_sc_laps, remove_low_data_drivers, teammate_comp_order
from f1_visualization.plots.config import (
    deduplicate_legend_labels,
    get_plot_args,
    shade_sc_periods,
)
from f1_visualization.session import get_session_info

logging.basicConfig(level=logging.INFO, format="%(filename)s\t%(levelname)s\t%(message)s")
logger = logging.getLogger(__name__)


def driver_stats_scatterplot(
    season: int,
    event: int | str,
    session_type: str = "R",
    drivers: Iterable[str | int] | str | int | None = None,
    y: str = "LapTime",
    upper_bound: int | float = 10,
    absolute_compound: bool = False,
    teammate_comp: bool = False,
    lap_numbers: list[int] | None = None,
) -> Figure:
    """
    Visualize driver data during a race as a scatterplot.

    Args:
        season: Championship season
        event: Round number or name of the event.
        session_type: Follow Fastf1 session identifier convention.
        drivers: See `get_drivers` for all accepted formats.
        y: Name of the column to be used as the y-axis.
        upper_bound: The upper bound on included laps as a percentage of the fastest lap.
        absolute_compound: If true, group tyres by absolute compound names.
        teammate_comp: Toggles teammate comparison mode.
        lap_numbers: A list of consecutive lap numbers representing a segment.
    """
    plt.style.use("dark_background")
    fontdict = {
        "fontsize": rcParams["axes.titlesize"],
        "fontweight": rcParams["axes.titleweight"],
        "color": rcParams["axes.titlecolor"],
        "verticalalignment": "baseline",
        "horizontalalignment": "center",
    }

    if not isinstance(drivers, (int, str)) and drivers is not None:
        drivers = tuple(drivers)

    round_number, event_name, drivers, session = get_session_info(
        season, event, session_type, drivers, teammate_comp
    )
    included_laps = DF_DICT[season][session_type]
    included_laps = included_laps[
        (included_laps["RoundNumber"] == round_number) & (included_laps["Driver"].isin(drivers))
    ]

    if teammate_comp:
        drivers = teammate_comp_order(included_laps, drivers, y)

    if lap_numbers is not None:
        assert sorted(lap_numbers) == list(range(lap_numbers[0], lap_numbers[-1] + 1))
        included_laps = included_laps[included_laps["LapNumber"].isin(lap_numbers)]

    max_width = 4 if teammate_comp else 5
    num_row = ceil(len(drivers) / max_width)
    num_col = min(max_width, len(drivers))
    fig, axs = plt.subplots(
        nrows=num_row,
        ncols=num_col,
        sharey=True,
        sharex=True,
        figsize=(5 * num_col, 5 * num_row),
    )

    args = get_plot_args(season, absolute_compound)

    if len(drivers) == 1:
        axs = np.array([axs])

    if y in {"PctFromLapRep", "DeltaToLapRep"}:
        included_laps = included_laps[included_laps["PctFromLapRep"] > -5]  # noqa: PLR2004

    for index, driver in enumerate(drivers):
        row, col = divmod(index, max_width)
        ax = axs[row][col] if num_row > 1 else axs[col]

        driver_laps = included_laps[included_laps["Driver"] == driver]
        pit_in_laps = driver_laps[driver_laps["PitInTime"].notna()]["LapNumber"].to_numpy()
        driver_laps = driver_laps[driver_laps["PctFromFastest"] < upper_bound]

        if driver_laps.shape[0] < 5:  # noqa: PLR2004
            logger.warning("%s HAS LESS THAN 5 LAPS ON RECORD FOR THIS EVENT", driver)

        sns.scatterplot(
            data=driver_laps,
            x="LapNumber",
            y=y,
            ax=ax,
            hue=args.hue,
            palette=args.palette,
            hue_order=args.labels,
            style="FreshTyre",
            style_order=["True", "False", "Unknown"],
            markers=VISUAL_CONFIG["fresh"]["markers"],
            legend="auto" if index == num_col - 1 else False,
        )
        ax.vlines(
            ymin=plt.yticks()[0][1],
            ymax=plt.yticks()[0][-2],
            x=pit_in_laps,
            label="Pitstop",
            linestyle="dashed",
        )

        driver_color = p.get_driver_color(driver, session)
        fontdict["color"] = driver_color
        ax.set_title(label=driver, fontdict=fontdict, fontsize=12)
        ax.grid(color=driver_color, which="both", axis="both")
        sns.despine(left=True, bottom=True)

    fig.suptitle(t=f"{season} {event_name}", fontsize=20)
    axs.flatten()[num_col - 1].legend(loc="best", fontsize=8, framealpha=0.5)

    return fig


def driver_stats_lineplot(
    season: int,
    event: int | str,
    session_type: str = "R",
    drivers: Iterable[str | int] | str | int | None = None,
    y: str = "Position",
    upper_bound: int | float | None = None,
    grid: Literal["both", "x", "y"] | None = None,
    lap_numbers: list[int] | None = None,
) -> Figure:
    """Visualize driver data during a race as a lineplot."""
    plt.style.use("dark_background")

    if not isinstance(drivers, (int, str)) and drivers is not None:
        drivers = tuple(drivers)

    round_number, event_name, drivers, session = get_session_info(
        season, event, session_type, drivers
    )
    starting_grid = dict(
        zip(session.results["Abbreviation"], session.results["GridPosition"], strict=True)
    )
    included_laps = DF_DICT[season][session_type]
    included_laps = included_laps[
        (included_laps["RoundNumber"] == round_number) & (included_laps["Driver"].isin(drivers))
    ]

    if lap_numbers is not None:
        assert sorted(lap_numbers) == list(range(lap_numbers[0], lap_numbers[-1] + 1))
        included_laps = included_laps[included_laps["LapNumber"].isin(lap_numbers)]

    sc_laps, vsc_laps = find_sc_laps(included_laps)

    if upper_bound is None:
        upper_bound = 100 if y == "Position" or y.startswith("GapTo") else 10

    included_laps = included_laps[
        (included_laps["RoundNumber"] == round_number)
        & (included_laps["Driver"].isin(drivers))
        & (included_laps["PctFromFastest"] < upper_bound)
    ]

    num_laps = included_laps["LapNumber"].nunique()
    fig, ax = plt.subplots(figsize=(ceil(num_laps * 0.25), 8))

    if y == "Position":
        plt.yticks(range(2, 21, 2))

    if y == "Position" or y.startswith("GapTo"):
        ax.invert_yaxis()

    for driver in drivers:
        driver_laps = included_laps[included_laps["Driver"] == driver]

        if driver_laps[y].count() == 0:
            logger.warning("%s has no data entry for %s", driver, y)
            continue

        driver_style = p.get_driver_style(
            identifier=driver,
            session=session,
            style=[
                {"color": "auto", "linestyle": "solid"},
                {"color": "auto", "linestyle": (0, (5, 5))},
            ],
        )

        if y == "Position" and pd.notna(starting_grid[driver]):
            sns.lineplot(
                x=pd.concat([pd.Series([0]), driver_laps["LapNumber"]]),
                y=pd.concat([pd.Series([starting_grid[driver]]), driver_laps[y]]),
                ax=ax,
                errorbar=None,
                **driver_style,
            )
        else:
            sns.lineplot(driver_laps, x="LapNumber", y=y, ax=ax, errorbar=None, **driver_style)
        
        last_lap = driver_laps["LapNumber"].max()
        last_pos = driver_laps[y][driver_laps["LapNumber"] == last_lap].iloc[0]

        annotation_x_margin = driver_laps.shape[0] / 100
        ax.annotate(
            xy=(last_lap + annotation_x_margin, last_pos + 0.25),
            text=driver,
            color=p.get_driver_color(driver, session),
            fontsize=12,
        )
        sns.despine(left=True, bottom=True)

    shade_sc_periods(sc_laps, vsc_laps)
    deduplicate_legend_labels(ax, loc="lower right", fontsize=10)

    if grid in {"both", "x", "y"}:
        plt.grid(visible=True, which="major", axis=grid)
    else:
        plt.grid(visible=False)

    if y == "Position":
        ax.set_xlabel("LapNumber")
        ax.set_ylabel("Position")

    fig.suptitle(t=f"{season} {event_name}", fontsize=20)
    return fig


def driver_stats_distplot(
    season: int,
    event: int | str,
    session_type: str = "R",
    drivers: Iterable[str | int] | str | int | None = None,
    y: str = "LapTime",
    upper_bound: float | int = 10,
    swarm: bool = True,
    violin: bool = True,
    absolute_compound: bool = False,
    teammate_comp: bool = False,
) -> Figure:
    """Visualize race data distribution as a violinplot or boxplot + optional swarmplot."""
    plt.style.use("dark_background")

    if not isinstance(drivers, (int, str)) and drivers is not None:
        drivers = tuple(drivers)

    round_number, event_name, drivers, session = get_session_info(
        season, event, session_type, drivers, teammate_comp
    )

    included_laps = DF_DICT[season][session_type]
    included_laps = included_laps[
        (included_laps["RoundNumber"] == round_number)
        & (included_laps["Driver"].isin(drivers))
        & (included_laps["PctFromFastest"] < upper_bound)
    ]

    if teammate_comp:
        drivers = teammate_comp_order(included_laps, drivers, y)
    drivers = remove_low_data_drivers(included_laps, drivers, 6)

    fig, ax = plt.subplots(figsize=(len(drivers) * 1.5, 10))
    args = get_plot_args(season, absolute_compound)

    driver_colors = [p.get_driver_color(driver, session) for driver in drivers]

    if violin:
        sns.violinplot(
            data=included_laps,
            x="Driver",
            y=y,
            inner=None,
            scale="area",
            palette=driver_colors,
            order=drivers,
        )
    else:
        sns.boxplot(
            data=included_laps,
            x="Driver",
            y=y,
            palette=driver_colors,
            order=drivers,
            whiskerprops={"color": "white"},
            boxprops={"edgecolor": "white"},
            medianprops={"color": "white"},
            capprops={"color": "white"},
            showfliers=False,
        )

    if swarm:
        from f1_visualization.plots.config import find_legend_order
        
        sns.swarmplot(
            data=included_laps,
            x="Driver",
            y=y,
            hue=args.hue,
            palette=args.palette,
            order=drivers,
            linewidth=0,
            size=5,
        )

        handles, labels = ax.get_legend_handles_labels()
        order = find_legend_order(labels)
        ax.legend(
            handles=[handles[idx] for idx in order],
            labels=[labels[idx] for idx in order],
            loc="best",
            title=args.hue,
            frameon=True,
            fontsize=10,
            framealpha=0.5,
        )

    ax.grid(visible=False)
    fig.suptitle(t=f"{season} {event_name}", fontsize=20)

    return fig

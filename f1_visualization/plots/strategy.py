"""Strategy and compound visualization functions using matplotlib."""

import logging
from collections.abc import Iterable
from math import ceil

import fastf1 as f
import seaborn as sns
from matplotlib import pyplot as plt

from f1_visualization.annotations import Figure
from f1_visualization.consts import VISUAL_CONFIG
from f1_visualization.data_loader import DF_DICT
from f1_visualization.helpers import find_sc_laps
from f1_visualization.plots.config import (
    convert_compound_name,
    deduplicate_legend_labels,
    find_legend_order,
    get_plot_args,
    shade_sc_periods,
)
from f1_visualization.session import get_session_info

logging.basicConfig(level=logging.INFO, format="%(filename)s\t%(levelname)s\t%(message)s")
logger = logging.getLogger(__name__)


def strategy_barplot(
    season: int,
    event: int | str,
    session_type: str = "R",
    drivers: Iterable[str] | int | None = None,
    absolute_compound: bool = False,
) -> Figure:
    """
    Visualize tyre strategies as a horizontal barplot.

    Args:
        season: Championship season
        event: Round number or name of the event.
        session_type: Follow Fastf1 session identifier convention.
        drivers: See `get_drivers` for all accepted formats.
        absolute_compound: If true, group tyres by absolute compound names.
    """
    if not isinstance(drivers, int) and drivers is not None:
        drivers = tuple(drivers)

    round_number, event_name, drivers, _session = get_session_info(
        season, event, session_type, drivers
    )
    included_laps = DF_DICT[season][session_type]
    included_laps = included_laps[
        (included_laps["RoundNumber"] == round_number) & (included_laps["Driver"].isin(drivers))
    ]

    fig, ax = plt.subplots(figsize=(5, len(drivers) // 3 + 1))
    plt.style.use("dark_background")

    driver_stints = (
        included_laps[["Driver", "Stint", "Compound", "CompoundName", "FreshTyre", "LapNumber"]]
        .groupby(["Driver", "Stint", "Compound", "CompoundName", "FreshTyre"])
        .count()
        .reset_index()
    )
    driver_stints = driver_stints.rename(columns={"LapNumber": "StintLength"})
    driver_stints = driver_stints.sort_values(by=["Stint"])

    args = get_plot_args(season, absolute_compound)

    for driver in drivers:
        stints = driver_stints.loc[driver_stints["Driver"] == driver]

        previous_stint_end = 0
        for _, stint in stints.iterrows():
            plt.barh(
                [driver],
                stint["StintLength"],
                left=previous_stint_end,
                color=args.palette[stint[args.hue]],
                edgecolor="black",
                fill=True,
                hatch=VISUAL_CONFIG["fresh"]["hatch"][stint["FreshTyre"]],
                label="Fresh" if stint["FreshTyre"] == "True" else "Used",
            )

            previous_stint_end += stint["StintLength"]

    shade_sc_periods(*find_sc_laps(included_laps))
    deduplicate_legend_labels(ax, loc="lower right", fontsize=10)

    plt.title(f"{season} {event_name}", fontsize=16)
    plt.xlabel("Lap Number")
    plt.grid(False)

    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    return fig


def _process_input(
    seasons: int | Iterable[int],
    events: int | str | Iterable[str | int],
    session_types: str | Iterable[str],
    y: str,
    compounds: Iterable[str],
    x: str,
    upper_bound: int | float,
    absolute_compound: bool,
) -> tuple[list[f.events.Event], list]:
    """Sanitize input parameters to compound plots."""
    compounds = [compound.upper() for compound in compounds]

    for compound in compounds:
        assert compound in {"SOFT", "MEDIUM", "HARD"}, (
            f"requested compound {compound} is not valid"
        )

    if x not in {"LapNumber", "TyreLife"}:
        logger.warning("Using %s as the x-axis is not recommended.", x)

    if not absolute_compound and len(events) > 1:
        logger.warning("Different events may use different compounds under the same name!")

    if isinstance(seasons, (int, str)):
        seasons = [seasons]
    if isinstance(events, (int, str)):
        events = [events]
    if isinstance(session_types, str):
        session_types = [session_types]

    assert len(seasons) == len(events) == len(session_types)

    event_objects = [f.get_event(seasons[i], events[i]) for i in range(len(seasons))]
    included_laps_list = []

    for season, event, session_type in zip(seasons, event_objects, session_types, strict=True):
        df_all = DF_DICT[season][session_type]
        df_laps = df_all[
            (df_all["RoundNumber"] == event["RoundNumber"])
            & (df_all["IsValid"])
            & (df_all["Compound"].isin(compounds))
            & (df_all["PctFromFastest"] < upper_bound)
        ]

        if y in {"PctFromLapRep", "DeltaToLapRep"}:
            df_laps = df_laps[df_laps["PctFromLapRep"] > -5]  # noqa: PLR2004

        included_laps_list.append(df_laps)

    return event_objects, included_laps_list


def compounds_lineplot(
    seasons: int | Iterable[int],
    events: int | str | Iterable[int | str],
    session_types: str | Iterable[str] | None = None,
    y: str = "LapTime",
    compounds: Iterable[str] = ["SOFT", "MEDIUM", "HARD"],
    x: str = "TyreLife",
    upper_bound: int | float = 10,
    absolute_compound: bool = True,
) -> Figure:
    """Visualize compound performances as a lineplot."""
    plt.style.use("dark_background")

    if isinstance(seasons, int):
        seasons = [seasons]

    event_objects, included_laps_list = _process_input(
        seasons, events, session_types, y, compounds, x, upper_bound, absolute_compound
    )

    fig, axs = plt.subplots(
        nrows=len(event_objects),
        sharex=True,
        ncols=1,
        figsize=(5, 5 * len(event_objects)),
    )

    if len(event_objects) == 1:
        axs = [axs]

    compounds_copy = compounds.copy()

    for idx, event in enumerate(event_objects):
        ax = axs[idx]
        args = get_plot_args(seasons[idx], absolute_compound)
        included_laps = included_laps_list[idx]
        medians = included_laps.groupby([args.hue, x])[y].median(numeric_only=True)

        round_number = event["RoundNumber"]
        event_name = event["EventName"]

        if absolute_compound:
            compounds_copy = convert_compound_name(seasons[idx], round_number, compounds)

        for compound in compounds_copy:
            if compound in medians.index:
                sns.lineplot(
                    x=medians.loc[compound].index,
                    y=medians.loc[compound].values,
                    ax=ax,
                    color=args.palette[compound],
                    marker=args.markers[compound],
                    markersize=4,
                    label=compound,
                )
            else:
                logger.warning(
                    "%s is not plotted for %s %s because there is not enough data",
                    compounds[idx],
                    seasons[idx],
                    event_name,
                )

        ax.set_ylabel(y, fontsize=12)

        handles, labels = ax.get_legend_handles_labels()
        order = find_legend_order(labels)
        ax.legend(
            handles=[handles[i] for i in order],
            labels=[labels[i] for i in order],
            loc="best",
            title=args.hue,
            frameon=True,
            fontsize=10,
            framealpha=0.5,
        )

        ax.set_title(label=f"{seasons[idx]} {event_name}", fontsize=12)
        ax.grid(which="both", axis="y")
        sns.despine(left=True, bottom=True)

    compounds = [compounds[i] for i in find_legend_order(compounds)]
    fig.suptitle(t=" VS ".join(compounds), fontsize=14)

    return fig


def compounds_distplot(
    seasons: int | Iterable[int],
    events: int | str | Iterable[int | str],
    session_types: str | Iterable[str] | None = None,
    y: str = "LapTime",
    compounds: Iterable[str] = ["SOFT", "MEDIUM", "HARD"],
    violin_plot: bool = False,
    x: str = "TyreLife",
    upper_bound: int | float = 10,
    absolute_compound: bool = True,
) -> Figure:
    """Visualize compound performance as a boxplot or violinplot."""
    plt.style.use("dark_background")

    if isinstance(seasons, int):
        seasons = [seasons]

    event_objects, included_laps_list = _process_input(
        seasons, events, session_types, y, compounds, x, upper_bound, absolute_compound
    )

    x_ticks = max(laps[x].nunique() for laps in included_laps_list)
    fig, axs = plt.subplots(
        nrows=len(event_objects),
        sharex=True,
        ncols=1,
        figsize=(ceil(x_ticks * 0.75), 5 * len(event_objects)),
    )

    if len(event_objects) == 1:
        axs = [axs]

    compounds_copy = compounds.copy()

    for idx, event in enumerate(event_objects):
        ax = axs[idx]
        args = get_plot_args(seasons[idx], absolute_compound)
        included_laps = included_laps_list[idx]

        plotted_compounds = included_laps[args.hue].unique()
        event_name = event["EventName"]
        round_number = event["RoundNumber"]

        if absolute_compound:
            compounds_copy = convert_compound_name(seasons[idx], round_number, compounds)

        for compound in compounds_copy:
            if compound not in plotted_compounds:
                logger.warning(
                    "%s is not plotted for %s %s because there is not enough data",
                    compounds[idx],
                    seasons[idx],
                    event_name,
                )

        if violin_plot:
            sns.violinplot(
                data=included_laps, x=x, y=y, ax=ax, hue=args.hue, palette=args.palette
            )
        else:
            sns.boxplot(data=included_laps, x=x, y=y, ax=ax, hue=args.hue, palette=args.palette)

        ax.set_ylabel(y, fontsize=12)
        xticks = ax.get_xticks()
        xticks = [tick + 1 for tick in xticks if tick % 5 == 0]
        ax.set_xticks(xticks)
        ax.grid(which="both", axis="y")

        handles, labels = ax.get_legend_handles_labels()
        order = find_legend_order(labels)
        ax.legend(
            handles=[handles[i] for i in order],
            labels=[labels[i] for i in order],
            loc="best",
            title=args.hue,
            frameon=True,
            fontsize=12,
            framealpha=0.5,
        )

        ax.set_title(label=f"{seasons[idx]} {event_name}", fontsize=12)
        sns.despine(left=True, bottom=True)

    compounds = [compounds[i] for i in find_legend_order(compounds)]
    fig.suptitle(t=" VS ".join(compounds), fontsize="16")

    return fig

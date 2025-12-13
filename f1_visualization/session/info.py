"""Session info retrieval and driver management utilities."""

import logging
from collections.abc import Iterable
from functools import lru_cache

import fastf1 as f
import pandas as pd

from f1_visualization.annotations import Session

logging.basicConfig(level=logging.INFO, format="%(filename)s\t%(levelname)s\t%(message)s")
logger = logging.getLogger(__name__)


def get_drivers(
    session: Session,
    drivers: Iterable[str | int] | str | int | None = None,
    by: str = "Position",
) -> list[str]:
    """
    Find driver three-letter abbreviations.

    Assumes:
        session.results is sorted by finishing position

    Args:
        session: The race session object, relevant for determining finishing order.
        drivers: The following argument formats are accepted:
            - A single integer retrieve the highest ordered drivers
            - A string representing either the driver's three letter abbreviation
              or driver number.
            - A list of integers and/or strings representing either the driver's
              three letter abbreviation or driver number.
            - None returns all drivers who appear in the session
        by: The key by which the drivers are sorted.

    Returns:
        The drivers' three-letter abbreviations, in the order requested.
    """
    result = session.results.sort_values(by=by, kind="stable")
    if drivers is None:
        return list(result["Abbreviation"].unique())
    if isinstance(drivers, int):
        drivers = result["Abbreviation"].unique()[:drivers]
        return list(drivers)
    if isinstance(drivers, str):
        drivers = [drivers]

    ret = []
    for driver in drivers:
        if isinstance(driver, (int, float)):
            ret.append(session.get_driver(str(int(driver)))["Abbreviation"])
        else:
            ret.append(session.get_driver(driver)["Abbreviation"])

    return ret


def infer_ergast_data(session: Session) -> Session:
    """When Ergast API is not updated yet, some session results data need to be inferred."""
    session.load(laps=True, telemetry=False, weather=False)

    final_laps = session.laps.drop_duplicates(subset="DriverNumber", keep="last")
    final_order = final_laps.sort_values(
        by=["LapNumber", "Time"], ascending=[False, True], ignore_index=True
    )

    final_order["Position"] = final_order.index + 1
    final_order = final_order.set_index("DriverNumber")
    session.results.loc[:, ["Position"]] = final_order["Position"]

    return session


@lru_cache(maxsize=256)
def get_session_info(
    season: int,
    event: int | str,
    session_type: str,
    drivers: tuple[str | int] | str | int | None = None,
    teammate_comp: bool = False,
) -> tuple[int, str, tuple[str], Session]:
    """
    Retrieve session information based on season, event number/name, and session identifier.

    Args:
        season: Championship season
        event: Round number or event name.
        session_type: Currently support R for the race and S for sprint race
        drivers: See `get_drivers` for all accepted formats.
        teammate_comp: If True, the drivers are returned next to their teammates.

    Returns:
        A tuple containing the round number, event name, and the drivers in the specified order.
    """
    session = f.get_session(season, event, session_type)
    session.load(laps=False, telemetry=False, weather=False)

    if session.results["Position"].isna().all():
        logger.warning(
            "Session results not available. Starting and finishing positions are inferred."
        )
        session = infer_ergast_data(session)

    round_number = session.event["RoundNumber"]
    event_name = f"{session.event['EventName']} - {session.name}"

    if teammate_comp:
        drivers = get_drivers(session, drivers, by="TeamName")
    else:
        drivers = get_drivers(session, drivers)

    return round_number, event_name, tuple(drivers), session

"""Feature extraction for driver performance analysis."""

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class DriverFeatures:
    """Extracted features for a driver in a session."""

    driver: str
    season: int
    round_number: int
    
    # Pace metrics
    median_lap_time: float
    lap_time_std: float  # Consistency
    fastest_lap: float
    slowest_lap: float
    
    # Position metrics
    start_position: int
    finish_position: int
    positions_gained: int
    avg_position: float
    
    # Tyre metrics
    num_stints: int
    avg_stint_length: float
    total_laps: int
    
    # Performance ratios
    pct_from_fastest: float
    consistency_score: float  # Lower is better


def extract_driver_features(
    df_laps: pd.DataFrame,
    season: int,
    round_number: int,
    driver: str,
) -> DriverFeatures | None:
    """
    Extract performance features for a single driver in a session.

    Args:
        df_laps: Lap data DataFrame
        season: Championship season
        round_number: Round number
        driver: Driver abbreviation

    Returns:
        DriverFeatures or None if insufficient data
    """
    driver_laps = df_laps[
        (df_laps["Driver"] == driver)
        & (df_laps["RoundNumber"] == round_number)
        & (df_laps["IsAccurate"])  # Only accurate laps
    ].copy()

    if len(driver_laps) < 5:  # noqa: PLR2004
        logger.warning("Insufficient laps for %s in round %d", driver, round_number)
        return None

    # Pace metrics
    lap_times = driver_laps["LapTime"].dropna()
    if len(lap_times) == 0:
        return None

    median_lap = float(lap_times.median())
    lap_std = float(lap_times.std())
    fastest = float(lap_times.min())
    slowest = float(lap_times.max())

    # Position metrics
    positions = driver_laps["Position"].dropna()
    start_pos = int(driver_laps.iloc[0]["Position"]) if len(positions) > 0 else 20
    finish_pos = int(driver_laps.iloc[-1]["Position"]) if len(positions) > 0 else 20
    avg_pos = float(positions.mean()) if len(positions) > 0 else 20.0

    # Tyre metrics
    stints = driver_laps["Stint"].nunique()
    avg_stint = len(driver_laps) / stints if stints > 0 else 0

    # Performance ratios
    fastest_overall = df_laps[
        (df_laps["RoundNumber"] == round_number) & (df_laps["IsAccurate"])
    ]["LapTime"].min()
    
    pct_from_fastest = ((median_lap - fastest_overall) / fastest_overall * 100) if fastest_overall > 0 else 0

    # Consistency score (coefficient of variation)
    consistency = (lap_std / median_lap * 100) if median_lap > 0 else 100

    return DriverFeatures(
        driver=driver,
        season=season,
        round_number=round_number,
        median_lap_time=median_lap,
        lap_time_std=lap_std,
        fastest_lap=fastest,
        slowest_lap=slowest,
        start_position=start_pos,
        finish_position=finish_pos,
        positions_gained=start_pos - finish_pos,
        avg_position=avg_pos,
        num_stints=stints,
        avg_stint_length=avg_stint,
        total_laps=len(driver_laps),
        pct_from_fastest=pct_from_fastest,
        consistency_score=consistency,
    )


def extract_session_features(
    df_laps: pd.DataFrame,
    season: int,
    round_number: int,
) -> pd.DataFrame:
    """
    Extract features for all drivers in a session.

    Args:
        df_laps: Lap data DataFrame
        season: Championship season
        round_number: Round number

    Returns:
        DataFrame with driver features
    """
    session_laps = df_laps[df_laps["RoundNumber"] == round_number]
    drivers = session_laps["Driver"].unique()

    features_list = []
    for driver in drivers:
        features = extract_driver_features(df_laps, season, round_number, driver)
        if features:
            features_list.append(vars(features))

    if not features_list:
        return pd.DataFrame()

    return pd.DataFrame(features_list)


def extract_season_features(
    df_laps: pd.DataFrame,
    season: int,
) -> pd.DataFrame:
    """
    Extract features for all drivers across an entire season.

    Args:
        df_laps: Lap data DataFrame
        season: Championship season

    Returns:
        DataFrame with aggregated driver features per round
    """
    season_laps = df_laps[df_laps["RoundNumber"].notna()]
    rounds = sorted(season_laps["RoundNumber"].unique())

    all_features = []
    for round_num in rounds:
        round_features = extract_session_features(df_laps, season, int(round_num))
        if not round_features.empty:
            all_features.append(round_features)

    if not all_features:
        return pd.DataFrame()

    return pd.concat(all_features, ignore_index=True)


def get_feature_matrix(features_df: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
    """
    Convert features DataFrame to normalized feature matrix for ML.

    Args:
        features_df: DataFrame with driver features

    Returns:
        Tuple of (feature matrix, feature names)
    """
    feature_cols = [
        "median_lap_time",
        "lap_time_std",
        "positions_gained",
        "avg_position",
        "avg_stint_length",
        "pct_from_fastest",
        "consistency_score",
    ]

    # Filter to available columns
    available_cols = [c for c in feature_cols if c in features_df.columns]

    if not available_cols:
        return np.array([]), []

    X = features_df[available_cols].values

    # Normalize features (z-score)
    X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)

    return X, available_cols

"""ML-based driver ranking system."""

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler

from f1_visualization.ml.features import extract_season_features

logger = logging.getLogger(__name__)


@dataclass
class DriverRanking:
    """Ranking result for a driver."""

    driver: str
    rank: int
    score: float  # Higher = better
    avg_position: float
    consistency: float
    races_completed: int
    points_estimate: float


class DriverRankingModel:
    """Gradient Boosting based driver ranking model."""

    def __init__(self, random_state: int = 42):
        """
        Initialize ranking model.

        Args:
            random_state: Random seed
        """
        self.random_state = random_state
        self._model: GradientBoostingRegressor | None = None
        self._scaler = StandardScaler()
        self._feature_cols: list[str] = []

    def fit(self, df_laps: pd.DataFrame, season: int) -> "DriverRankingModel":
        """
        Fit ranking model on season data.

        Uses finishing positions as target to learn what features
        predict better performance.
        """
        features_df = extract_season_features(df_laps, season)

        if features_df.empty:
            logger.warning("No features extracted for season %d", season)
            return self

        self._feature_cols = [
            "median_lap_time",
            "lap_time_std",
            "positions_gained",
            "pct_from_fastest",
            "consistency_score",
            "avg_stint_length",
        ]

        available_cols = [c for c in self._feature_cols if c in features_df.columns]
        if not available_cols:
            return self

        X = features_df[available_cols].values
        # Target: inverse of average position (higher = better)
        y = 21 - features_df["avg_position"].values

        # Handle NaN
        valid_mask = ~np.isnan(X).any(axis=1) & ~np.isnan(y)
        X = X[valid_mask]
        y = y[valid_mask]

        if len(X) < 10:  # noqa: PLR2004
            logger.warning("Not enough samples for ranking model")
            return self

        X = self._scaler.fit_transform(X)

        self._model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=4,
            random_state=self.random_state,
        )
        self._model.fit(X, y)

        self._feature_cols = available_cols
        logger.info("Ranking model fitted on %d samples", len(X))
        return self

    def rank_drivers(self, df_laps: pd.DataFrame, season: int) -> list[DriverRanking]:
        """
        Rank drivers based on their performance.

        Args:
            df_laps: Lap data DataFrame
            season: Championship season

        Returns:
            List of DriverRanking sorted by score (best first)
        """
        features_df = extract_season_features(df_laps, season)

        if features_df.empty:
            return []

        # Aggregate features per driver
        driver_stats = features_df.groupby("driver").agg({
            "median_lap_time": "mean",
            "lap_time_std": "mean",
            "positions_gained": "sum",
            "avg_position": "mean",
            "pct_from_fastest": "mean",
            "consistency_score": "mean",
            "avg_stint_length": "mean",
            "total_laps": "sum",
            "round_number": "count",  # Number of races
        }).reset_index()

        driver_stats = driver_stats.rename(columns={"round_number": "races_completed"})

        if self._model is None:
            # Fallback: rank by average position
            driver_stats["score"] = 21 - driver_stats["avg_position"]
        else:
            available_cols = [c for c in self._feature_cols if c in driver_stats.columns]
            if available_cols:
                X = driver_stats[available_cols].fillna(0).values
                X = self._scaler.transform(X)
                driver_stats["score"] = self._model.predict(X)
            else:
                driver_stats["score"] = 21 - driver_stats["avg_position"]

        # Sort by score descending
        driver_stats = driver_stats.sort_values("score", ascending=False).reset_index(drop=True)

        results = []
        for rank, (_, row) in enumerate(driver_stats.iterrows(), 1):
            # Estimate points (rough approximation)
            points_per_race = max(0, 26 - row["avg_position"]) * 2
            points_estimate = points_per_race * row.get("races_completed", 1)

            results.append(
                DriverRanking(
                    driver=row["driver"],
                    rank=rank,
                    score=float(row["score"]),
                    avg_position=float(row["avg_position"]),
                    consistency=float(row.get("consistency_score", 0)),
                    races_completed=int(row.get("races_completed", 0)),
                    points_estimate=float(points_estimate),
                )
            )

        return results


def rank_drivers(
    df_laps: pd.DataFrame,
    season: int,
) -> list[DriverRanking]:
    """
    Convenience function to rank drivers.

    Args:
        df_laps: Lap data DataFrame
        season: Championship season

    Returns:
        List of DriverRanking sorted by score
    """
    model = DriverRankingModel()
    model.fit(df_laps, season)
    return model.rank_drivers(df_laps, season)

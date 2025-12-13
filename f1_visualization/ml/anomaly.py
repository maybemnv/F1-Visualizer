"""Anomaly detection for identifying unusual driver performance."""

import logging
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of detected anomalies."""

    UNUSUALLY_FAST = "Unusually Fast"
    UNUSUALLY_SLOW = "Unusually Slow"
    UNEXPECTED_POSITION_GAIN = "Unexpected Position Gain"
    UNEXPECTED_POSITION_LOSS = "Unexpected Position Loss"
    ABNORMAL_STINT = "Abnormal Stint Performance"
    NORMAL = "Normal"


@dataclass
class AnomalyResult:
    """Result of anomaly detection for a lap or stint."""

    driver: str
    lap_number: int
    anomaly_type: AnomalyType
    anomaly_score: float  # Higher = more anomalous
    details: dict


class PerformanceAnomalyDetector:
    """Isolation Forest based anomaly detector for race performance."""

    def __init__(
        self,
        contamination: float = 0.1,
        random_state: int = 42,
    ):
        """
        Initialize anomaly detector.

        Args:
            contamination: Expected proportion of anomalies
            random_state: Random seed
        """
        self.contamination = contamination
        self.random_state = random_state
        self._model: IsolationForest | None = None

    def fit(self, df_laps: pd.DataFrame) -> "PerformanceAnomalyDetector":
        """
        Fit anomaly detector on lap data.

        Args:
            df_laps: Lap data DataFrame

        Returns:
            Self for chaining
        """
        features = self._extract_lap_features(df_laps)

        if len(features) < 10:  # noqa: PLR2004
            logger.warning("Not enough samples for anomaly detection")
            return self

        self._model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=100,
        )
        self._model.fit(features)

        logger.info("Anomaly detector fitted on %d samples", len(features))
        return self

    def _extract_lap_features(self, df_laps: pd.DataFrame) -> np.ndarray:
        """Extract features for anomaly detection."""
        feature_cols = []

        # Lap time relative to session median
        if "LapTime" in df_laps.columns:
            median_time = df_laps["LapTime"].median()
            df_laps = df_laps.copy()
            df_laps["LapTimeDelta"] = df_laps["LapTime"] - median_time
            feature_cols.append("LapTimeDelta")

        # Position change from previous lap
        if "Position" in df_laps.columns:
            df_laps["PositionChange"] = df_laps.groupby("Driver")["Position"].diff().fillna(0)
            feature_cols.append("PositionChange")

        # Tyre age effect
        if "TyreLife" in df_laps.columns:
            feature_cols.append("TyreLife")

        if not feature_cols:
            return np.array([])

        return df_laps[feature_cols].dropna().values

    def detect(self, df_laps: pd.DataFrame) -> list[AnomalyResult]:
        """
        Detect anomalies in lap data.

        Args:
            df_laps: Lap data DataFrame

        Returns:
            List of AnomalyResult for detected anomalies
        """
        if self._model is None:
            logger.warning("Model not fitted")
            return []

        df = df_laps.copy()
        
        # Extract features
        median_time = df["LapTime"].median() if "LapTime" in df.columns else 0
        if "LapTime" in df.columns:
            df["LapTimeDelta"] = df["LapTime"] - median_time
        if "Position" in df.columns:
            df["PositionChange"] = df.groupby("Driver")["Position"].diff().fillna(0)

        feature_cols = []
        if "LapTimeDelta" in df.columns:
            feature_cols.append("LapTimeDelta")
        if "PositionChange" in df.columns:
            feature_cols.append("PositionChange")
        if "TyreLife" in df.columns:
            feature_cols.append("TyreLife")

        if not feature_cols:
            return []

        valid_mask = df[feature_cols].notna().all(axis=1)
        features = df.loc[valid_mask, feature_cols].values

        if len(features) == 0:
            return []

        # Predict anomalies (-1 = anomaly, 1 = normal)
        predictions = self._model.predict(features)
        scores = -self._model.score_samples(features)  # Higher = more anomalous

        results = []
        valid_indices = df.index[valid_mask].tolist()

        for i, (pred, score) in enumerate(zip(predictions, scores, strict=True)):
            if pred == -1:  # Anomaly
                idx = valid_indices[i]
                row = df.loc[idx]

                anomaly_type = self._classify_anomaly(row, median_time)

                results.append(
                    AnomalyResult(
                        driver=row.get("Driver", "Unknown"),
                        lap_number=int(row.get("LapNumber", 0)),
                        anomaly_type=anomaly_type,
                        anomaly_score=float(score),
                        details={
                            "lap_time": row.get("LapTime"),
                            "position": row.get("Position"),
                            "compound": row.get("Compound"),
                            "tyre_life": row.get("TyreLife"),
                        },
                    )
                )

        # Sort by anomaly score (most anomalous first)
        results.sort(key=lambda x: x.anomaly_score, reverse=True)
        return results

    def _classify_anomaly(self, row: pd.Series, median_time: float) -> AnomalyType:
        """Classify the type of anomaly."""
        lap_time = row.get("LapTime", median_time)
        position_change = row.get("PositionChange", 0)

        if lap_time < median_time * 0.97:  # noqa: PLR2004
            return AnomalyType.UNUSUALLY_FAST
        if lap_time > median_time * 1.05:  # noqa: PLR2004
            return AnomalyType.UNUSUALLY_SLOW
        if position_change < -3:  # noqa: PLR2004
            return AnomalyType.UNEXPECTED_POSITION_GAIN
        if position_change > 3:  # noqa: PLR2004
            return AnomalyType.UNEXPECTED_POSITION_LOSS

        return AnomalyType.ABNORMAL_STINT


def detect_anomalies(
    df_laps: pd.DataFrame,
    contamination: float = 0.1,
) -> list[AnomalyResult]:
    """
    Convenience function to detect anomalies in lap data.

    Args:
        df_laps: Lap data DataFrame
        contamination: Expected proportion of anomalies

    Returns:
        List of detected anomalies
    """
    detector = PerformanceAnomalyDetector(contamination=contamination)
    detector.fit(df_laps)
    return detector.detect(df_laps)

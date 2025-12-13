"""Clustering models for identifying driving styles."""

import logging
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from f1_visualization.ml.features import get_feature_matrix

logger = logging.getLogger(__name__)


class DrivingStyle(Enum):
    """Identified driving style categories."""

    AGGRESSIVE = "Aggressive"
    CONSISTENT = "Consistent"
    STRATEGIC = "Strategic"
    QUALIFIER = "Qualifier"
    UNKNOWN = "Unknown"


@dataclass
class ClusterResult:
    """Result of clustering analysis."""

    driver: str
    cluster_id: int
    driving_style: DrivingStyle
    cluster_center_distance: float
    features: dict


class DrivingStyleClusterer:
    """K-Means based driving style clusterer."""

    def __init__(self, n_clusters: int = 4, random_state: int = 42):
        """
        Initialize clusterer.

        Args:
            n_clusters: Number of clusters (driving styles)
            random_state: Random seed for reproducibility
        """
        self.n_clusters = n_clusters
        self.random_state = random_state
        self._model: KMeans | None = None
        self._scaler = StandardScaler()
        self._feature_names: list[str] = []
        self._cluster_labels: dict[int, DrivingStyle] = {}

    def fit(self, features_df: pd.DataFrame) -> "DrivingStyleClusterer":
        """
        Fit clustering model on driver features.

        Args:
            features_df: DataFrame with driver features

        Returns:
            Self for chaining
        """
        X, feature_names = get_feature_matrix(features_df)
        
        if len(X) < self.n_clusters:
            logger.warning("Not enough samples for %d clusters", self.n_clusters)
            return self

        self._feature_names = feature_names

        # Fit model
        self._model = KMeans(
            n_clusters=self.n_clusters,
            random_state=self.random_state,
            n_init=10,
        )
        self._model.fit(X)

        # Label clusters based on centroid characteristics
        self._label_clusters(X, features_df)

        logger.info("Clusterer fitted with %d clusters", self.n_clusters)
        return self

    def _label_clusters(self, X: np.ndarray, features_df: pd.DataFrame) -> None:
        """Assign driving style labels to clusters based on characteristics."""
        if self._model is None:
            return

        centroids = self._model.cluster_centers_

        # Find feature indices
        consistency_idx = self._feature_names.index("consistency_score") if "consistency_score" in self._feature_names else -1
        positions_idx = self._feature_names.index("positions_gained") if "positions_gained" in self._feature_names else -1
        pace_idx = self._feature_names.index("pct_from_fastest") if "pct_from_fastest" in self._feature_names else -1

        style_scores = []
        for i, centroid in enumerate(centroids):
            scores = {
                "aggressive": 0.0,
                "consistent": 0.0,
                "strategic": 0.0,
                "qualifier": 0.0,
            }

            # High positions gained + low consistency = Aggressive
            if positions_idx >= 0:
                scores["aggressive"] += centroid[positions_idx]
            if consistency_idx >= 0:
                scores["aggressive"] -= centroid[consistency_idx] * 0.5

            # Low consistency score (less variation) = Consistent
            if consistency_idx >= 0:
                scores["consistent"] -= centroid[consistency_idx]

            # Strategic: good stint management (inferred from avg position)
            if positions_idx >= 0:
                scores["strategic"] += centroid[positions_idx] * 0.5

            # Qualifier: fast pace but loses positions
            if pace_idx >= 0:
                scores["qualifier"] -= centroid[pace_idx]
            if positions_idx >= 0:
                scores["qualifier"] -= centroid[positions_idx] * 0.3

            style_scores.append((i, scores))

        # Assign styles greedily
        assigned_styles = set()
        styles = [DrivingStyle.AGGRESSIVE, DrivingStyle.CONSISTENT, DrivingStyle.STRATEGIC, DrivingStyle.QUALIFIER]

        for style in styles:
            style_key = style.value.lower()
            best_cluster = -1
            best_score = float("-inf")

            for cluster_id, scores in style_scores:
                if cluster_id not in self._cluster_labels and scores[style_key] > best_score:
                    best_score = scores[style_key]
                    best_cluster = cluster_id

            if best_cluster >= 0:
                self._cluster_labels[best_cluster] = style
                assigned_styles.add(best_cluster)

        # Assign Unknown to any remaining
        for i in range(self.n_clusters):
            if i not in self._cluster_labels:
                self._cluster_labels[i] = DrivingStyle.UNKNOWN

    def predict(self, features_df: pd.DataFrame) -> list[ClusterResult]:
        """
        Predict driving styles for drivers.

        Args:
            features_df: DataFrame with driver features

        Returns:
            List of ClusterResult for each driver
        """
        if self._model is None:
            logger.warning("Model not fitted, returning empty results")
            return []

        X, _ = get_feature_matrix(features_df)
        
        if len(X) == 0:
            return []

        cluster_ids = self._model.predict(X)
        distances = self._model.transform(X)

        results = []
        for i, (_, row) in enumerate(features_df.iterrows()):
            cluster_id = int(cluster_ids[i])
            results.append(
                ClusterResult(
                    driver=row["driver"],
                    cluster_id=cluster_id,
                    driving_style=self._cluster_labels.get(cluster_id, DrivingStyle.UNKNOWN),
                    cluster_center_distance=float(distances[i, cluster_id]),
                    features={
                        "consistency": row.get("consistency_score", 0),
                        "positions_gained": row.get("positions_gained", 0),
                        "pace": row.get("pct_from_fastest", 0),
                    },
                )
            )

        return results

    def get_cluster_summary(self) -> dict[int, dict]:
        """Get summary of each cluster."""
        if self._model is None:
            return {}

        summary = {}
        for i in range(self.n_clusters):
            centroid = self._model.cluster_centers_[i]
            summary[i] = {
                "style": self._cluster_labels.get(i, DrivingStyle.UNKNOWN).value,
                "centroid": dict(zip(self._feature_names, centroid.tolist(), strict=False)),
            }
        return summary


def cluster_drivers(
    features_df: pd.DataFrame,
    n_clusters: int = 4,
) -> tuple[list[ClusterResult], dict]:
    """
    Convenience function to cluster drivers by driving style.

    Args:
        features_df: DataFrame with driver features
        n_clusters: Number of clusters

    Returns:
        Tuple of (cluster results, cluster summary)
    """
    clusterer = DrivingStyleClusterer(n_clusters=n_clusters)
    clusterer.fit(features_df)
    results = clusterer.predict(features_df)
    summary = clusterer.get_cluster_summary()
    return results, summary

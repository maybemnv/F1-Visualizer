"""Machine Learning package for driver performance analysis."""

from f1_visualization.ml.anomaly import (
    AnomalyResult,
    AnomalyType,
    PerformanceAnomalyDetector,
    detect_anomalies,
)
from f1_visualization.ml.clustering import (
    ClusterResult,
    DrivingStyle,
    DrivingStyleClusterer,
    cluster_drivers,
)
from f1_visualization.ml.features import (
    DriverFeatures,
    extract_driver_features,
    extract_season_features,
    extract_session_features,
    get_feature_matrix,
)
from f1_visualization.ml.ranking import (
    DriverRanking,
    DriverRankingModel,
    rank_drivers,
)

__all__ = [
    # Features
    "DriverFeatures",
    "extract_driver_features",
    "extract_session_features",
    "extract_season_features",
    "get_feature_matrix",
    # Clustering
    "DrivingStyle",
    "ClusterResult",
    "DrivingStyleClusterer",
    "cluster_drivers",
    # Anomaly
    "AnomalyType",
    "AnomalyResult",
    "PerformanceAnomalyDetector",
    "detect_anomalies",
    # Ranking
    "DriverRanking",
    "DriverRankingModel",
    "rank_drivers",
]

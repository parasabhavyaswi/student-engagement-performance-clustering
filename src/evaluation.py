"""
EduPulse - Evaluation Module
Project ID: SIH26036
Provides Euclidean distance calculations in standardized space, distance-based indicators,
feature deviation analysis, and formal evaluation metric utilities.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.preprocess import scale_instance

logger = logging.getLogger(__name__)


def compute_centroid_distances(
    scaled_vector: np.ndarray,
    kmeans_model: KMeans
) -> Dict[int, float]:
    """
    Calculates the exact Euclidean distance from a standardized student instance
    to each of the K cluster centroids in 4D standardized space:
    d(k) = sqrt( sum_{j=1}^4 (z_j - centroid_{kj})^2 )
    """
    centroids = kmeans_model.cluster_centers_  # shape (K, 4)
    # scaled_vector shape (1, 4)
    diffs = centroids - scaled_vector
    dists = np.linalg.norm(diffs, axis=1)
    return {int(k): round(float(dists[k]), 4) for k in range(len(dists))}


def compute_distance_based_similarity(
    distances: Dict[int, float],
    epsilon: float = 1e-5
) -> Dict[int, float]:
    """
    Computes a distance-based proximity/similarity score for each cluster.
    IMPORTANT: This is a purely geometric distance-based indicator, NOT a calibrated
    probability distribution or Bayesian posterior.
    Formula: inv_dist_k / sum(inv_dist) where inv_dist = 1.0 / (d(k) + epsilon)
    """
    inv_dists = {k: 1.0 / (d + epsilon) for k, d in distances.items()}
    total_inv = sum(inv_dists.values())
    return {k: round((v / total_inv) * 100, 2) for k, v in inv_dists.items()}


def predict_student_cluster(
    total_clicks: float,
    active_days: float,
    weighted_score: float,
    mean_submission_delay: float,
    kmeans_model: KMeans,
    scaler: StandardScaler,
    cluster_metadata: Dict[int, Any]
) -> Dict[str, Any]:
    """
    Predicts the cluster for given student parameters, computes all 4 centroid distances,
    nearest centroid, and feature contributions.
    """
    # 1. Standardize
    scaled_vec = scale_instance(total_clicks, active_days, weighted_score, mean_submission_delay, scaler)

    # 2. Centroid Distances
    distances = compute_centroid_distances(scaled_vec, kmeans_model)

    # 3. Nearest centroid
    predicted_cluster = min(distances.keys(), key=lambda k: distances[k])
    cluster_meta = cluster_metadata.get(predicted_cluster, {})

    # 4. Proximity Indicator
    similarities = compute_distance_based_similarity(distances)

    # 5. Feature Contribution / Difference from Centroid
    centroid_scaled = kmeans_model.cluster_centers_[predicted_cluster]
    feature_names = ["total_clicks (log1p)", "active_days", "weighted_score", "mean_submission_delay"]
    contributions = []

    for idx, fname in enumerate(feature_names):
        z_val = float(scaled_vec[0, idx])
        c_val = float(centroid_scaled[idx])
        diff = z_val - c_val
        contributions.append({
            "feature": fname,
            "student_scaled": round(z_val, 3),
            "centroid_scaled": round(c_val, 3),
            "deviation_from_centroid": round(diff, 3),
            "direction": "Above Centroid" if diff > 0 else "Below Centroid" if diff < 0 else "Matches Centroid"
        })

    return {
        "predicted_cluster": predicted_cluster,
        "cluster_name": cluster_meta.get("name", f"Cluster {predicted_cluster}"),
        "badge_color": cluster_meta.get("badge_color", "#1E88E5"),
        "risk_level": cluster_meta.get("risk_level", "Medium"),
        "description": cluster_meta.get("description", ""),
        "scaled_vector": scaled_vec[0].tolist(),
        "distances": distances,
        "nearest_distance": distances[predicted_cluster],
        "similarities": similarities,
        "feature_contributions": contributions
    }


def explain_nmi() -> str:
    """
    Returns the formal academic explanation of Normalized Mutual Information (NMI).
    """
    return (
        "Normalized Mutual Information (NMI) quantifies the shared information between "
        "the unsupervised cluster assignments and external course outcomes (final_result: "
        "Distinction, Pass, Fail, Withdrawn). NMI values range from 0 (completely independent) "
        "to 1 (perfect agreement). Crucially, NMI is NOT classification accuracy; K-Means is "
        "an unsupervised learning algorithm optimizing intra-cluster spatial variance in 4D "
        "engagement space without access to final academic grades during training."
    )


if __name__ == "__main__":
    from src.clustering import load_kmeans_model, load_cluster_metadata
    from src.preprocess import load_scaler

    km = load_kmeans_model()
    sc = load_scaler()
    meta = load_cluster_metadata()

    pred = predict_student_cluster(2500, 110, 80, -2, km, sc, meta)
    print("Test Prediction:")
    print("Predicted Cluster:", pred["predicted_cluster"], f"({pred['cluster_name']})")
    print("Distances:", pred["distances"])
    print("Nearest Distance:", pred["nearest_distance"])
    print("Similarities (%):", pred["similarities"])
    print("Contributions:\n", pd.DataFrame(pred["feature_contributions"]))

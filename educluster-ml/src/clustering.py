"""
Clustering Module (Objective 2)
-------------------------------
K-Means Segmentation, Optimal-k Sweep, Cluster Mapping & PCA Projections
Project: EduCluster ML (Project ID: SIH26036)

This module executes:
1. Optimal-k sweep (k in [2, 8]) computing Inertia, Silhouette, Davies-Bouldin, and Calinski-Harabasz.
2. Final K-Means clustering (k=4) sorted by descending weighted_avg_score for deterministic cluster labeling:
   - Cluster 0: High-Achieving Self-Directed (#10B981)
   - Cluster 1: Steady & Consistent Learners (#3B82F6)
   - Cluster 2: Crammers / Selective Engagers (#F59E0B)
   - Cluster 3: Disengaged / At-Risk (#EF4444)
3. 2D PCA dimensionality reduction (PC1, PC2) with explained variance ratios.
4. Normalized centroid profile compilation for Radar and Bar visualizations.
"""

import os
from typing import Dict, Any, Tuple, List, Optional

# Suppress loky CPU warning on Windows
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score
)

# Standardized Cluster Metadata & Approved Pedagogic Archetypes
CLUSTER_METADATA: Dict[int, Dict[str, Any]] = {
    0: {
        "name": "High-Achieving Self-Directed",
        "short_name": "High-Achievers",
        "color": "#10B981",       # Emerald
        "badge_bg": "rgba(16, 185, 129, 0.15)",
        "badge_border": "#10B981",
        "description": "Exemplary performance, extensive learning resource utilization, consistent study habits, and early assessment submissions.",
        "icon": "🌟"
    },
    1: {
        "name": "Steady & Consistent Learners",
        "short_name": "Steady Learners",
        "color": "#3B82F6",       # Electric Blue
        "badge_bg": "rgba(59, 130, 246, 0.15)",
        "badge_border": "#3B82F6",
        "description": "Consistent weekly participation, reliable submission discipline, solid passing scores, and systematic pace through course materials.",
        "icon": "📘"
    },
    2: {
        "name": "Crammers / Selective Engagers",
        "short_name": "Deadline Crammers",
        "color": "#F59E0B",       # Golden Amber
        "badge_bg": "rgba(245, 158, 11, 0.15)",
        "badge_border": "#F59E0B",
        "description": "Sporadic attendance with steep spikes in activity 48-72 hours before deadlines, variable passing scores, and high inter-day irregularity.",
        "icon": "⚡"
    },
    3: {
        "name": "Disengaged / At-Risk",
        "short_name": "At-Risk",
        "color": "#EF4444",       # Crimson Red
        "badge_bg": "rgba(239, 68, 68, 0.15)",
        "badge_border": "#EF4444",
        "description": "Low platform clicks, minimal active days, missing or late assessments, failing trajectory, and high probability of course withdrawal.",
        "icon": "⚠️"
    }
}


def run_k_sweep(
    X_scaled: np.ndarray,
    k_range: range = range(2, 9),
    sample_size_sil: int = 4000,
    random_state: int = 42
) -> pd.DataFrame:
    """
    Run k-sweep evaluation across k in [2, 8].

    Computes:
    - Inertia (Elbow method: sum of squared distances to closest centroid)
    - Silhouette Score (mean intra-cluster distance vs nearest-cluster distance)
    - Davies-Bouldin Index (ratio of within-cluster distances to between-cluster distances; lower is better)
    - Calinski-Harabasz Score (Variance Ratio Criterion; higher is better)
    """
    records = []

    for k in k_range:
        km = KMeans(n_clusters=k, init="k-means++", n_init=10, random_state=random_state)
        labels = km.fit_predict(X_scaled)

        # Silhouette computation
        sil = silhouette_score(
            X_scaled,
            labels,
            sample_size=min(sample_size_sil, len(X_scaled)),
            random_state=random_state
        )
        db = davies_bouldin_score(X_scaled, labels)
        ch = calinski_harabasz_score(X_scaled, labels)

        records.append({
            "k": k,
            "inertia": float(km.inertia_),
            "silhouette": float(sil),
            "davies_bouldin": float(db),
            "calinski_harabasz": float(ch)
        })

    return pd.DataFrame(records)


def train_kmeans(
    X_scaled: np.ndarray,
    df_raw: pd.DataFrame,
    n_clusters: int = 4,
    random_state: int = 42
) -> Tuple[KMeans, np.ndarray, Dict[str, Any]]:
    """
    Train production K-Means model (k=4, k-means++, n_init=20).

    Automatically sorts and remaps cluster IDs by descending weighted_avg_score
    so cluster identities are strictly deterministic and reproducible:
    - Cluster 0: High-Achieving Self-Directed (highest avg score)
    - Cluster 1: Steady & Consistent Learners (second highest avg score)
    - Cluster 2: Crammers / Selective Engagers (third highest avg score)
    - Cluster 3: Disengaged / At-Risk (lowest avg score)
    """
    km = KMeans(
        n_clusters=n_clusters,
        init="k-means++",
        n_init=20,
        random_state=random_state
    )
    raw_labels = km.fit_predict(X_scaled)

    # Calculate cluster average score to sort clusters deterministically
    score_col = "weighted_avg_score"
    cluster_mean_scores = []
    for k in range(n_clusters):
        cluster_mask = (raw_labels == k)
        if score_col in df_raw.columns:
            m_score = df_raw.loc[cluster_mask, score_col].mean()
        else:
            # Fallback to feature index 12
            m_score = X_scaled[cluster_mask, 12].mean()
        cluster_mean_scores.append(m_score)

    # Sort descending: rank 0 = highest score -> Cluster 0
    sort_order = np.argsort(cluster_mean_scores)[::-1]
    mapping = {old_id: new_id for new_id, old_id in enumerate(sort_order)}

    # Apply mapping to student cluster labels
    mapped_labels = np.array([mapping[l] for l in raw_labels], dtype=int)

    # Reorder cluster centers in the fitted KMeans model so future predict() calls match
    km.cluster_centers_ = km.cluster_centers_[sort_order]
    km.labels_ = mapped_labels

    cluster_info = {
        "cluster_names": {k: v["name"] for k, v in CLUSTER_METADATA.items()},
        "cluster_colors": {k: v["color"] for k, v in CLUSTER_METADATA.items()},
        "cluster_metadata": CLUSTER_METADATA,
        "cluster_counts": pd.Series(mapped_labels).value_counts().sort_index().to_dict(),
        "cluster_proportions": (pd.Series(mapped_labels).value_counts(normalize=True).sort_index() * 100).to_dict()
    }

    return km, mapped_labels, cluster_info


def compute_pca_projection(
    X_scaled: np.ndarray,
    n_components: int = 2,
    random_state: int = 42
) -> Tuple[np.ndarray, PCA, Dict[str, float]]:
    """
    Project standardized 16-feature space onto 2 principal components.

    Returns:
        pca_coords: Array of shape (N, 2) containing PC1 and PC2.
        pca_model: Fitted PCA object.
        variance_info: Dict of explained variance ratios per component.
    """
    pca = PCA(n_components=n_components, random_state=random_state)
    coords = pca.fit_transform(X_scaled)

    variance_info = {
        "pc1_var": float(pca.explained_variance_ratio_[0]),
        "pc2_var": float(pca.explained_variance_ratio_[1]),
        "total_var": float(np.sum(pca.explained_variance_ratio_))
    }

    return coords, pca, variance_info


def get_centroid_profiles(
    df_raw: pd.DataFrame,
    cluster_labels: np.ndarray,
    feature_names: List[str]
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Compute raw centroid means and normalized (0 to 1) profiles for Radar charts.

    Returns:
        df_centroids_raw: Real-scale feature means per cluster.
        df_centroids_norm: Min-max scaled (0 to 1) feature profile for radar chart.
    """
    df_temp = df_raw[feature_names].copy()
    df_temp["cluster"] = cluster_labels

    # Raw centroid means
    df_centroids_raw = df_temp.groupby("cluster").mean().reset_index()

    # Normalized radar dimensions (0 to 1 scale across cohorts)
    # Define 6 intuitive pedagogic radar axes
    radar_axes = {
        "Platform Engagement": "total_clicks",
        "Active Days": "active_days",
        "Assessment Score": "weighted_avg_score",
        "Completion Rate": "assessment_completion_rate",
        "Attendance Regularity": "activity_regularity_std",  # inverted so higher = more regular
        "Early Proactivity": "pre_course_clicks"
    }

    norm_dict = {"cluster": [0, 1, 2, 3]}
    for axis_name, col in radar_axes.items():
        col_min = df_raw[col].min()
        col_max = df_raw[col].max()
        val_range = max(col_max - col_min, 1e-6)

        raw_vals = df_centroids_raw[col].values
        if axis_name == "Attendance Regularity":
            # Invert regularity std so low std (high regularity) scores closer to 1.0
            norm_vals = 1.0 - (raw_vals - col_min) / val_range
        else:
            norm_vals = (raw_vals - col_min) / val_range

        norm_dict[axis_name] = np.clip(norm_vals, 0.05, 0.98).tolist()

    df_centroids_norm = pd.DataFrame(norm_dict)

    return df_centroids_raw, df_centroids_norm


if __name__ == "__main__":
    from preprocess import load_and_preprocess_data

    df, X_std, scaler, fnames, y = load_and_preprocess_data()
    sweep_df = run_k_sweep(X_std)
    print("=" * 60)
    print("Optimal-k Sweep Results (k=2..8):")
    print(sweep_df.round(4))

    km, labels, info = train_kmeans(X_std, df, n_clusters=4)
    print("\nDeterministic Cluster Counts:")
    for cid, cnt in info["cluster_counts"].items():
        print(f"Cluster {cid} ({info['cluster_names'][cid]}): {cnt} students ({info['cluster_proportions'][cid]:.1f}%)")

    coords, pca, var = compute_pca_projection(X_std)
    print(f"\nPCA Projection complete: PC1={var['pc1_var']*100:.1f}%, PC2={var['pc2_var']*100:.1f}%, Total={var['total_var']*100:.1f}%")
    print("=" * 60)


"""
Validation Module (Objective 3)
-------------------------------
Extrinsic & Intrinsic Cluster Validation Engine
Project: EduPulse (Project ID: SIH26036)

This module computes:
1. Normalized Mutual Information (NMI) against teacher-observed final_result.
2. Adjusted Rand Index (ARI) against teacher-observed final_result.
3. Pearson's Chi-Square Test of Independence (chi2, dof, p-value, expected).
4. Cramér's V effect size metric.
5. Cross-tabulated Contingency Matrix with raw counts, row percentages (recall),
   and column percentages (precision).
"""

import os
from typing import Dict, Any, Tuple

# Suppress loky CPU warning on Windows
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from sklearn.metrics import (
    normalized_mutual_info_score,
    adjusted_rand_score,
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score
)

# Standard result order for clinical & pedagogic coherence
ORDERED_RESULTS = ["Distinction", "Pass", "Fail", "Withdrawn"]
ORDERED_CLUSTERS = [0, 1, 2, 3]


def compute_extrinsic_validation(
    y_true: pd.Series,
    cluster_labels: np.ndarray,
    cluster_names: Dict[int, str]
) -> Dict[str, Any]:
    """
    Validate cluster partitions against teacher-observed ground truth proxy (final_result).

    Metrics:
    - NMI (Normalized Mutual Information)
    - ARI (Adjusted Rand Index)
    - Pearson's Chi-Square (chi2, p-value, degrees of freedom)
    - Cramér's V (Effect size for contingency association)
    - Contingency Matrices (Raw counts, Row %, Column %)
    """
    N = len(y_true)

    # 1. Normalized Mutual Information (arithmetic average method)
    nmi = float(normalized_mutual_info_score(y_true, cluster_labels, average_method="arithmetic"))

    # 2. Adjusted Rand Index
    ari = float(adjusted_rand_score(y_true, cluster_labels))

    # 3. Contingency Matrix (Raw Counts)
    df_ct = pd.crosstab(
        index=y_true,
        columns=cluster_labels,
        rownames=["Teacher Observed (final_result)"],
        colnames=["Cluster ID"]
    )

    # Ensure all ordered rows and columns exist
    df_ct = df_ct.reindex(index=ORDERED_RESULTS, columns=ORDERED_CLUSTERS, fill_value=0)

    # 4. Pearson's Chi-Square Test of Independence
    chi2, p_value, dof, expected = chi2_contingency(df_ct.values)

    # 5. Cramér's V Effect Size: sqrt(chi2 / (N * (min(r, k) - 1)))
    r, k = df_ct.shape
    min_dim_minus_1 = max(min(r, k) - 1, 1)
    cramers_v = float(np.sqrt(chi2 / (N * min_dim_minus_1)))

    # 6. Row percentages (% of each final_result assigned to each cluster)
    row_sums = df_ct.sum(axis=1).replace(0, 1)
    df_ct_row_pct = (df_ct.div(row_sums, axis=0) * 100).round(2)

    # 7. Column percentages (% of each cluster belonging to each final_result)
    col_sums = df_ct.sum(axis=0).replace(0, 1)
    df_ct_col_pct = (df_ct.div(col_sums, axis=1) * 100).round(2)

    # Friendly labeled columns
    renamed_columns = [f"Cluster {c}: {cluster_names.get(c, str(c))}" for c in ORDERED_CLUSTERS]
    df_ct_labeled = df_ct.copy()
    df_ct_labeled.columns = renamed_columns

    df_ct_row_pct_labeled = df_ct_row_pct.copy()
    df_ct_row_pct_labeled.columns = renamed_columns

    df_ct_col_pct_labeled = df_ct_col_pct.copy()
    df_ct_col_pct_labeled.columns = renamed_columns

    return {
        "nmi": nmi,
        "ari": ari,
        "chi2": float(chi2),
        "p_value": float(p_value),
        "dof": int(dof),
        "cramers_v": cramers_v,
        "expected_frequencies": expected,
        "contingency_raw": df_ct,
        "contingency_labeled": df_ct_labeled,
        "contingency_row_pct": df_ct_row_pct_labeled,
        "contingency_col_pct": df_ct_col_pct_labeled,
        "sample_size": N
    }


def compute_intrinsic_validation(
    X_scaled: np.ndarray,
    cluster_labels: np.ndarray,
    sample_size: int = 5000,
    random_state: int = 42
) -> Dict[str, float]:
    """
    Compute intrinsic clustering quality metrics:
    - Silhouette Score (cohesion vs separation)
    - Davies-Bouldin Index (lower indicates superior partition)
    - Calinski-Harabasz Score (higher indicates tighter, better-separated clusters)
    """
    sil = float(silhouette_score(
        X_scaled,
        cluster_labels,
        sample_size=min(sample_size, len(X_scaled)),
        random_state=random_state
    ))
    db = float(davies_bouldin_score(X_scaled, cluster_labels))
    ch = float(calinski_harabasz_score(X_scaled, cluster_labels))

    return {
        "silhouette": sil,
        "davies_bouldin": db,
        "calinski_harabasz": ch
    }


if __name__ == "__main__":
    from preprocess import load_and_preprocess_data
    from clustering import train_kmeans

    df, X_std, scaler, fnames, y = load_and_preprocess_data()
    km, labels, info = train_kmeans(X_std, df, n_clusters=4)

    ext = compute_extrinsic_validation(y, labels, info["cluster_names"])
    intr = compute_intrinsic_validation(X_std, labels)

    print("=" * 60)
    print("EXTRINSIC VALIDATION RESULTS:")
    print(f"Normalized Mutual Information (NMI): {ext['nmi']:.4f}")
    print(f"Adjusted Rand Index (ARI):           {ext['ari']:.4f}")
    print(f"Pearson's Chi-Square (χ²):           {ext['chi2']:.2f} (dof={ext['dof']}, p={ext['p_value']:.4e})")
    print(f"Cramér's V:                          {ext['cramers_v']:.4f}")
    print("\nContingency Matrix (Raw Counts):\n", ext["contingency_raw"])
    print("\nContingency Matrix (Row % - Recall):\n", ext["contingency_row_pct"])
    print("\nINTRINSIC VALIDATION RESULTS:")
    print(f"Silhouette Score:                    {intr['silhouette']:.4f}")
    print(f"Davies-Bouldin Index:                {intr['davies_bouldin']:.4f}")
    print(f"Calinski-Harabasz Score:             {intr['calinski_harabasz']:.2f}")
    print("=" * 60)


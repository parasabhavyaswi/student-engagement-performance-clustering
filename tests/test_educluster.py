"""
EduCluster ML - Complete Pytest Verification Suite
Candidate: Parasa Bhavyaswi (Reg No: 12502256)
Supervisor: Dr. Bhupinder Singh
Affiliation: School of Computer Science & Engineering, Lovely Professional University

Verifies:
1. Feature compilation (16 features, N = 14,003, log1p scaling, StandardScaler)
2. Zero label leakage (final_result strictly isolated)
3. K-Means clustering (k=4, deterministic descending score ordering, cluster shares & medians)
4. 2D PCA projection (82.0% cumulative variance: PC1 = 74.9%, PC2 = 7.1%)
5. Extrinsic statistical validation (Chi2 = 12,136.24, Cramer's V = 0.5375, NMI = 0.3100, ARI = 0.2778)
6. 4-Week Personalized Learning Path recommendation engine
7. Submission deliverables integrity (IEEE_Final_Project_Report.docx & EduCluster_ML_Presentation.pptx)
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.preprocess import (
    load_and_preprocess_oulad,
    FEATURE_COLUMNS,
    LOG1P_COLUMNS,
    FEATURE_DOMAINS
)
from src.clustering import (
    fit_kmeans_pipeline,
    compute_pca_projection,
    evaluate_k_sweep,
    get_cluster_profiles,
    get_centroid_radar_data,
    CLUSTER_PERSONAS
)
from src.validation import (
    compute_validation_metrics,
    get_contingency_matrix
)
from src.recommender import (
    predict_and_recommend,
    CLUSTER_ROADMAPS
)


@pytest.fixture(scope="session")
def pipeline_data():
    X_scaled, df_raw, y_result, scaler = load_and_preprocess_oulad()
    km, labels, df_clustered = fit_kmeans_pipeline(X_scaled, df_raw)
    pca, X_pca, exp_var = compute_pca_projection(X_scaled)
    val_metrics = compute_validation_metrics(df_clustered)
    return {
        "X_scaled": X_scaled,
        "df_raw": df_raw,
        "y_result": y_result,
        "scaler": scaler,
        "km": km,
        "labels": labels,
        "df_clustered": df_clustered,
        "pca": pca,
        "X_pca": X_pca,
        "exp_var": exp_var,
        "val_metrics": val_metrics
    }


def test_cohort_shape_and_features(pipeline_data):
    """Verifies exactly N = 14,003 records and 16 features."""
    X_scaled = pipeline_data["X_scaled"]
    df_raw = pipeline_data["df_raw"]
    assert X_scaled.shape[0] == 14003, f"Expected 14003 rows, got {X_scaled.shape[0]}"
    assert X_scaled.shape[1] == 16, f"Expected 16 features, got {X_scaled.shape[1]}"
    assert len(df_raw) == 14003
    for col in FEATURE_COLUMNS:
        assert col in df_raw.columns, f"Feature column '{col}' missing from raw DataFrame"


def test_zero_target_leakage(pipeline_data):
    """Verifies final_result is not present in feature set X."""
    assert "final_result" not in FEATURE_COLUMNS
    assert len(pipeline_data["y_result"]) == 14003
    assert set(pipeline_data["y_result"].unique()) == {"Distinction", "Pass", "Fail", "Withdrawn"}


def test_standard_scaler_properties(pipeline_data):
    """Verifies StandardScaler produces zero mean and unit variance."""
    X_scaled = pipeline_data["X_scaled"]
    means = np.mean(X_scaled, axis=0)
    stds = np.std(X_scaled, axis=0)
    assert np.allclose(means, 0.0, atol=1e-2), f"Means not close to 0: {means}"
    assert np.allclose(stds, 1.0, atol=1e-2), f"Stds not close to 1: {stds}"


def test_kmeans_deterministic_ordering(pipeline_data):
    """Verifies clusters are deterministically ordered by descending weighted_avg_score."""
    df_c = pipeline_data["df_clustered"]
    means = df_c.groupby("cluster")["weighted_avg_score"].mean()
    assert means[0] > means[1] > means[2] > means[3], f"Clusters not ordered descending: {means}"


def test_cluster_profiles_and_counts(pipeline_data):
    """Verifies the four clusters and their expected sample sizes and medians."""
    df_c = pipeline_data["df_clustered"]
    profiles = get_cluster_profiles(df_c)
    assert len(profiles) == 4

    # C0: High-Achievers
    c0 = df_c[df_c["cluster"] == 0]
    assert 3000 <= len(c0) <= 3250
    assert c0["weighted_avg_score"].median() >= 85.0
    assert c0["avg_submission_delay"].median() < 0.0  # Early

    # C1: Steady Learners
    c1 = df_c[df_c["cluster"] == 1]
    assert 5100 <= len(c1) <= 5400
    assert 68.0 <= c1["weighted_avg_score"].median() <= 75.0

    # C2: Crammers
    c2 = df_c[df_c["cluster"] == 2]
    assert 3050 <= len(c2) <= 3300
    assert 48.0 <= c2["weighted_avg_score"].median() <= 56.0
    assert c2["avg_submission_delay"].median() > 0.0  # Late

    # C3: Disengaged
    c3 = df_c[df_c["cluster"] == 3]
    assert 2350 <= len(c3) <= 2550
    assert c3["weighted_avg_score"].median() < 30.0


def test_pca_variance_explained(pipeline_data):
    """Verifies 2D PCA explains 82.0% variance (PC1 = 74.9%, PC2 = 7.1%)."""
    exp_var = pipeline_data["exp_var"]
    assert len(exp_var) == 2
    assert exp_var[0] == 0.749
    assert exp_var[1] == 0.071
    assert round(sum(exp_var), 3) == 0.820


def test_extrinsic_statistical_validation(pipeline_data):
    """Verifies Chi2 = 12,136.24, Cramer's V = 0.5375, NMI = 0.3100, ARI = 0.2778."""
    val = pipeline_data["val_metrics"]
    assert val["chi2"] == 12136.24
    assert val["cramers_v"] == 0.5375
    assert val["nmi"] == 0.3100
    assert val["ari"] == 0.2778
    assert val["dof"] == 9
    assert val["p_value"] < 0.0001


def test_contingency_matrix_dimensions():
    """Verifies 4x4 contingency matrix cross-tabulation."""
    ct = get_contingency_matrix()
    assert ct.shape == (4, 4)
    assert list(ct.columns) == ["Distinction", "Pass", "Fail", "Withdrawn"]
    assert ct.values.sum() == 14003


def test_recommender_prediction_and_roadmaps(pipeline_data):
    """Verifies recommender returns confidence, nearest_distance, roadmap, and action_plan."""
    km = pipeline_data["km"]
    scaler = pipeline_data["scaler"]
    df_raw = pipeline_data["df_raw"]

    res = predict_and_recommend(
        total_clicks=2800,
        active_days=88,
        weighted_avg_score=88.5,
        avg_submission_delay=-4.5,
        kmeans_model=km,
        scaler=scaler,
        reference_df=df_raw
    )
    assert res["cluster_id"] == 0
    assert "High-Achieving" in res["persona"]
    assert 0.0 <= res["confidence"] <= 100.0
    assert "roadmap" in res and len(res["roadmap"]) == 4
    assert "action_plan" in res and len(res["action_plan"]) == 4

    for w_idx, week in enumerate(res["roadmap"], 1):
        assert week["week"] == w_idx
        assert "title" in week
        assert "action" in week
        assert "commitment" in week


def test_deliverables_files_exist():
    """Verifies that IEEE report and executive presentation exist on disk and are non-empty."""
    docx_file = (
        PROJECT_ROOT / "IEEE_Conference_Template__2_.docx"
        if (PROJECT_ROOT / "IEEE_Conference_Template__2_.docx").exists()
        else (PROJECT_ROOT / "IEEE_Final_Project_Report.docx")
    )
    pptx_file = PROJECT_ROOT / "EduCluster_ML_Presentation.pptx"

    if not docx_file.exists() or not pptx_file.exists():
        from generate_deliverables import main as gen_main
        gen_main()

    assert docx_file.exists(), "IEEE Research manuscript does not exist!"
    assert docx_file.stat().st_size > 500000, "IEEE Research manuscript is smaller than expected!"

    assert pptx_file.exists(), "EduCluster_ML_Presentation.pptx does not exist!"
    assert pptx_file.stat().st_size > 40000, "EduCluster_ML_Presentation.pptx is smaller than expected!"

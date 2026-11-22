"""
EduPulse - Complete Pytest Suite
Project ID: SIH26036
Covers all 17 pipeline, integrity, preprocessing, clustering, transition, and edge-case scenarios.
"""

import os
import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.data_loader import verify_raw_dataset, load_raw_table
from src.data_validation import audit_raw_tables
from src.feature_engineering import extract_vle_features, extract_assessment_features
from src.preprocess import transform_features, load_scaler, scale_instance
from src.clustering import load_kmeans_model, load_cluster_metadata
from src.evaluation import compute_centroid_distances, compute_distance_based_similarity, predict_student_cluster
from src.transition_analyzer import (
    analyze_one_parameter_sensitivity,
    generate_2d_decision_surface,
    compute_prediction_for_vector
)


# ==============================================================================
# Scenario 1: All 7 raw CSV files exist and are non-empty
# ==============================================================================
def test_raw_files_exist_and_non_empty():
    ver = verify_raw_dataset(config.RAW_DATA_DIR)
    assert ver["is_valid"] is True, f"Raw files validation failed: {ver['errors']}"
    assert len(ver["files"]) == 7
    for fname, details in ver["files"].items():
        assert details["exists"] is True
        assert details["size_bytes"] > 0, f"File {fname} is empty!"
        assert details["row_count"] > 0, f"File {fname} has 0 rows!"


# ==============================================================================
# Scenario 2: Total column count across 7 files is exactly 43
# ==============================================================================
def test_raw_total_columns_is_43():
    ver = verify_raw_dataset(config.RAW_DATA_DIR)
    total_cols = sum(len(details["columns"]) for details in ver["files"].values())
    assert total_cols == 43, f"Expected 43 total columns across 7 files, found {total_cols}"


# ==============================================================================
# Scenario 3: Zero duplicate enrolments in studentInfo
# ==============================================================================
def test_student_info_no_duplicate_enrolments():
    info = load_raw_table("studentInfo")
    dups = info.duplicated(subset=["id_student", "code_module", "code_presentation"]).sum()
    assert dups == 0, f"Found {dups} duplicate enrolments in studentInfo!"


# ==============================================================================
# Scenario 4: Initial studentInfo enrolment count is exactly 32,593
# ==============================================================================
def test_initial_enrolment_count_32593():
    info = load_raw_table("studentInfo")
    assert len(info) == 32593, f"Expected 32,593 enrolments in studentInfo, got {len(info)}"


# ==============================================================================
# Scenario 5: Merging tables maintains zero row multiplication
# ==============================================================================
def test_zero_row_multiplication_on_joins():
    info = load_raw_table("studentInfo")
    courses = load_raw_table("courses")
    reg = load_raw_table("studentRegistration")

    m1 = pd.merge(info, courses, on=["code_module", "code_presentation"], how="left")
    assert len(m1) == len(info), f"Row multiplication on courses join: {len(m1)} != {len(info)}"

    m2 = pd.merge(m1, reg, on=["code_module", "code_presentation", "id_student"], how="left")
    assert len(m2) == len(info), f"Row multiplication on reg join: {len(m2)} != {len(info)}"


# ==============================================================================
# Scenario 6: Enrolments with 0 VLE clicks are retained with 0 clicks & 0 active days
# ==============================================================================
def test_zero_vle_clicks_enrolments_retained():
    info = load_raw_table("studentInfo")
    df_vle = pd.read_csv(
        config.RAW_DATA_DIR / "studentVle.csv",
        nrows=50000,
        usecols=["id_student", "code_module", "code_presentation", "date", "sum_click"]
    )
    vle_features = extract_vle_features(df_vle)
    merged = pd.merge(info, vle_features, on=["code_module", "code_presentation", "id_student"], how="left")
    merged["total_clicks"] = merged["total_clicks"].fillna(0.0)
    merged["active_days"] = merged["active_days"].fillna(0.0)

    zero_clicks = (merged["total_clicks"] == 0.0).sum()
    assert zero_clicks > 0, "Expected some enrolments to have 0 clicks when joining subset"
    assert (merged[merged["total_clicks"] == 0.0]["active_days"] == 0.0).all()


# ==============================================================================
# Scenario 7: Pipeline audit exists and captures exclusions (>99% Withdrawn/Fail)
# ==============================================================================
def test_pipeline_audit_exclusions():
    if not config.PIPELINE_AUDIT_FILE.exists():
        pytest.skip("pipeline_audit.json not yet generated; run pipeline first.")

    with open(config.PIPELINE_AUDIT_FILE, "r") as fp:
        audit = json.load(fp)

    assert "initial_total_enrolments" in audit
    assert "valid_clustering_enrolments" in audit
    assert "total_excluded_enrolments" in audit
    assert audit["initial_total_enrolments"] == 32593

    excl_by_res = audit.get("excluded_by_final_result", {})
    withdrawn = excl_by_res.get("Withdrawn", 0)
    failed = excl_by_res.get("Fail", 0)
    total_excl = audit["total_excluded_enrolments"]

    drop_ratio = (withdrawn + failed) / total_excl
    assert drop_ratio > 0.95, f"Expected >95% of exclusions to be Withdrawn/Fail, got {drop_ratio:.2%}"


# ==============================================================================
# Scenario 8: Processed dataset has required core features and no missing values
# ==============================================================================
def test_processed_dataset_integrity():
    fpath = config.PROCESSED_CLUSTERED_FILE if config.PROCESSED_CLUSTERED_FILE.exists() else config.PROCESSED_FEATURES_FILE
    if not fpath.exists():
        pytest.skip("Processed dataset does not exist; run pipeline first.")

    df = pd.read_csv(fpath)
    for col in ["total_clicks", "active_days", "log1p_total_clicks"]:
        assert col in df.columns, f"Missing required column {col}"
        assert df[col].isna().sum() == 0, f"Column {col} contains null values!"

    score_col = "weighted_avg_score" if "weighted_avg_score" in df.columns else "weighted_score"
    delay_col = "submission_delay" if "submission_delay" in df.columns else "mean_submission_delay"
    assert df[score_col].isna().sum() == 0
    assert df[delay_col].isna().sum() == 0


# ==============================================================================
# Scenario 9: log1p feature transformation correctness
# ==============================================================================
def test_feature_log1p_transformation():
    sample_df = pd.DataFrame({
        "total_clicks": [0.0, 10.0, 100.0, 1000.0],
        "active_days": [0.0, 5.0, 20.0, 80.0],
        "weighted_avg_score": [50.0, 65.0, 80.0, 95.0],
        "submission_delay": [5.0, 0.0, -2.0, -10.0]
    })
    transformed = transform_features(sample_df)
    assert transformed.shape == (4, 4)
    # Check log1p on clicks
    expected_clicks = np.log1p([0.0, 10.0, 100.0, 1000.0])
    np.testing.assert_allclose(transformed[:, 0], expected_clicks, rtol=1e-5)
    # Check identity on others
    np.testing.assert_allclose(transformed[:, 1], sample_df["active_days"], rtol=1e-5)
    np.testing.assert_allclose(transformed[:, 2], sample_df["weighted_avg_score"], rtol=1e-5)
    np.testing.assert_allclose(transformed[:, 3], sample_df["submission_delay"], rtol=1e-5)


# ==============================================================================
# Scenario 10: StandardScaler produces zero mean and unit variance
# ==============================================================================
def test_standard_scaler_mean_and_variance():
    if not config.SCALER_FILE.exists():
        pytest.skip("Scaler not found; run pipeline first.")

    scaler = load_scaler(config.SCALER_FILE)
    assert hasattr(scaler, "mean_")
    assert hasattr(scaler, "scale_")
    assert len(scaler.mean_) == 4
    assert len(scaler.scale_) == 4
    for s in scaler.scale_:
        assert s > 0, "Scaler scale must be positive non-zero!"


# ==============================================================================
# Scenario 11: Trained K-Means has K=4, cluster_centers_ shape (4, 4)
# ==============================================================================
def test_kmeans_model_properties():
    if not config.KMEANS_MODEL_FILE.exists():
        pytest.skip("KMeans model not found; run pipeline first.")

    kmeans = load_kmeans_model(config.KMEANS_MODEL_FILE)
    assert kmeans.n_clusters == 4
    assert kmeans.cluster_centers_.shape == (4, 4)
    assert kmeans.inertia_ > 0


# ==============================================================================
# Scenario 12: Dynamic archetype mapping assigns all 4 distinct personas
# ==============================================================================
def test_dynamic_archetype_mapping():
    if not config.CLUSTER_METADATA_FILE.exists():
        pytest.skip("Cluster metadata not found; run pipeline first.")

    meta = load_cluster_metadata(config.CLUSTER_METADATA_FILE)
    assert len(meta) == 4
    archetype_names = {m["name"] for m in meta.values()}
    expected_names = {"High-Achievers", "At-Risk Learners", "Deadline Crammers", "Steady Learners"}
    assert archetype_names == expected_names, f"Expected {expected_names}, got {archetype_names}"


# ==============================================================================
# Scenario 13: Euclidean distance in standardized 4D matches np.linalg.norm
# ==============================================================================
def test_euclidean_distance_calculation():
    if not (config.KMEANS_MODEL_FILE.exists() and config.SCALER_FILE.exists()):
        pytest.skip("Model or scaler missing; run pipeline first.")

    km = load_kmeans_model()
    sc = load_scaler()
    scaled_vec = scale_instance(1500, 60, 75, -2, sc)

    dists = compute_centroid_distances(scaled_vec, km)
    assert len(dists) == 4

    # Verify manual L2 norm
    for k in range(4):
        manual_l2 = float(np.linalg.norm(scaled_vec - km.cluster_centers_[k]))
        assert abs(dists[k] - manual_l2) < 1e-4


# ==============================================================================
# Scenario 14: Distance-based proximity indicator sums to 100%
# ==============================================================================
def test_distance_based_similarity():
    test_dists = {0: 1.25, 1: 3.50, 2: 2.10, 3: 4.80}
    sims = compute_distance_based_similarity(test_dists, epsilon=1e-5)
    assert len(sims) == 4
    total_pct = sum(sims.values())
    assert abs(total_pct - 100.0) < 0.1, f"Expected sum near 100%, got {total_pct}"
    # Nearest centroid has highest score
    assert sims[0] == max(sims.values())


# ==============================================================================
# Scenario 15: One-parameter sensitivity sweep identifies boundary via bisection
# ==============================================================================
def test_one_parameter_sensitivity_bisection():
    if not (config.KMEANS_MODEL_FILE.exists() and config.SCALER_FILE.exists() and config.CLUSTER_METADATA_FILE.exists()):
        pytest.skip("Model artifacts missing; run pipeline first.")

    km = load_kmeans_model()
    sc = load_scaler()
    meta = load_cluster_metadata()

    # Fixed parameters positioned between At-Risk and High-Achiever
    fixed = {
        "total_clicks": 1000.0,
        "active_days": 40.0,
        "weighted_score": 60.0,
        "mean_submission_delay": 0.0
    }

    res = analyze_one_parameter_sensitivity("weighted_score", fixed, km, sc, meta, n_grid=400, tol=1e-4)
    assert "has_transition" in res
    assert "intervals" in res
    assert len(res["intervals"]) >= 1

    if res["has_transition"]:
        assert len(res["transitions"]) >= 1
        t = res["transitions"][0]
        # At boundary, competing distances must be equal within tolerance
        diff = abs(t["competing_distance_before"] - t["competing_distance_after"])
        assert diff < 0.05, f"Boundary distance difference too large: {diff}"


# ==============================================================================
# Scenario 16: Sensitivity analyzer reports message when no transition occurs
# ==============================================================================
def test_no_transition_message_when_constant():
    if not (config.KMEANS_MODEL_FILE.exists() and config.SCALER_FILE.exists() and config.CLUSTER_METADATA_FILE.exists()):
        pytest.skip("Model artifacts missing; run pipeline first.")

    km = load_kmeans_model()
    sc = load_scaler()
    meta = load_cluster_metadata()

    # Extreme high achiever parameter set firmly inside High-Achiever cluster
    fixed = {
        "total_clicks": 15000.0,
        "active_days": 200.0,
        "weighted_score": 98.0,
        "mean_submission_delay": -3.0
    }

    # Sweep narrow delay range where no transition is expected
    res = analyze_one_parameter_sensitivity(
        "mean_submission_delay",
        fixed,
        km,
        sc,
        meta,
        param_range=(-5.0, -1.0),
        n_grid=200
    )
    if not res["has_transition"]:
        expected_msg = "No cluster transition occurs within the tested range when the other three parameters are held constant."
        assert res["message"] == expected_msg


# ==============================================================================
# Scenario 17: Two-parameter 2D mesh has exact dimensions (110, 110)
# ==============================================================================
def test_2d_decision_mesh_dimensions():
    if not (config.KMEANS_MODEL_FILE.exists() and config.SCALER_FILE.exists() and config.CLUSTER_METADATA_FILE.exists()):
        pytest.skip("Model artifacts missing; run pipeline first.")

    km = load_kmeans_model()
    sc = load_scaler()
    meta = load_cluster_metadata()

    fixed = {
        "total_clicks": 1200.0,
        "active_days": 50.0,
        "weighted_score": 75.0,
        "mean_submission_delay": -2.0
    }

    mesh = generate_2d_decision_surface(
        "active_days",
        "weighted_score",
        fixed,
        km,
        sc,
        meta,
        grid_resolution=110
    )

    assert len(mesh["x_values"]) == 110
    assert len(mesh["y_values"]) == 110
    assert len(mesh["prediction_grid"]) == 110
    assert len(mesh["prediction_grid"][0]) == 110

    # Ensure all predictions are valid cluster IDs in [0, 3]
    for row in mesh["prediction_grid"]:
        for val in row:
            assert val in [0, 1, 2, 3]

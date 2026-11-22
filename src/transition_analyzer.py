"""
EduPulse - Cluster Transition Analyzer Module
Project ID: SIH26036
Core Analytical Engine for 1D Sensitivity Sweeps (1,200 grid points), Numerical Bisection Boundary Refinement (45 iterations),
2D Conditional Decision Boundary Meshes (110x110), and Cluster Transition Explanations.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Suppress Windows loky core count warning
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent if "__file__" in locals() else Path.cwd()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.preprocess import scale_instance

logger = logging.getLogger(__name__)


def compute_prediction_for_vector(
    params: Dict[str, float],
    kmeans_model: KMeans,
    scaler: StandardScaler
) -> Tuple[int, np.ndarray, np.ndarray]:
    """
    Transforms, scales, and predicts cluster for a given parameter set.
    Returns: (predicted_cluster, scaled_vector, distances_to_all_centroids)
    """
    clicks = params.get("total_clicks", 0.0)
    days = params.get("active_days", 0.0)
    score = params.get("weighted_avg_score", params.get("weighted_score", 0.0))
    delay = params.get("submission_delay", params.get("mean_submission_delay", 0.0))

    scaled_vec = scale_instance(
        total_clicks=clicks,
        active_days=days,
        weighted_score=score,
        mean_submission_delay=delay,
        scaler=scaler
    )
    centroids = kmeans_model.cluster_centers_
    dists = np.linalg.norm(centroids - scaled_vec, axis=1)
    predicted_cluster = int(np.argmin(dists))
    return predicted_cluster, scaled_vec[0], dists


def refine_boundary_bisection(
    param_name: str,
    fixed_params: Dict[str, float],
    low_val: float,
    high_val: float,
    c_low: int,
    c_high: int,
    kmeans_model: KMeans,
    scaler: StandardScaler,
    tol: float = 1e-5,
    max_iter: int = 45
) -> Tuple[float, float, float, Dict[str, Any]]:
    """
    Uses numerical bisection root-finding (45 iterations, tol <= 1e-5) to locate the exact
    parameter transition boundary where distance to c_low equals distance to c_high in standardized 4D space.
    """
    low = low_val
    high = high_val

    for _ in range(max_iter):
        if (high - low) <= tol:
            break
        mid = (low + high) / 2.0
        test_params = dict(fixed_params)
        test_params[param_name] = mid
        c_mid, _, _ = compute_prediction_for_vector(test_params, kmeans_model, scaler)

        if c_mid == c_low:
            low = mid
        else:
            high = mid

    transition_point = (low + high) / 2.0

    # Verification on both sides
    delta = max(tol * 2, 1e-4)
    p_left = dict(fixed_params)
    p_left[param_name] = max(low_val, transition_point - delta)
    c_ver_left, _, dists_left = compute_prediction_for_vector(p_left, kmeans_model, scaler)

    p_right = dict(fixed_params)
    p_right[param_name] = min(high_val, transition_point + delta)
    c_ver_right, _, dists_right = compute_prediction_for_vector(p_right, kmeans_model, scaler)

    # Distances at the exact boundary
    p_exact = dict(fixed_params)
    p_exact[param_name] = transition_point
    _, _, dists_at_boundary = compute_prediction_for_vector(p_exact, kmeans_model, scaler)

    dist_diff = abs(dists_at_boundary[c_low] - dists_at_boundary[c_high])

    verification_info = {
        "verified_left_cluster": c_ver_left,
        "verified_right_cluster": c_ver_right,
        "boundary_tolerance": tol,
        "distance_difference_at_boundary": round(float(dist_diff), 6),
        "competing_distance_low": round(float(dists_at_boundary[c_low]), 4),
        "competing_distance_high": round(float(dists_at_boundary[c_high]), 4)
    }

    return transition_point, dists_at_boundary[c_low], dists_at_boundary[c_high], verification_info


def analyze_one_parameter_sensitivity(
    param_name: str,
    fixed_params: Dict[str, float],
    kmeans_model: KMeans,
    scaler: StandardScaler,
    cluster_metadata: Dict[int, Any],
    param_range: Optional[Tuple[float, float]] = None,
    n_grid: int = 1200,
    tol: float = 1e-5
) -> Dict[str, Any]:
    """
    Sweeps one parameter across its valid range (1,200 grid points) while holding the other three parameters fixed.
    Dynamically identifies all transition points and intervals using numerical bisection (45 iterations).
    """
    # Normalize parameter name
    canonical_param = param_name
    if param_name in ["weighted_avg_score", "weighted_score"]:
        canonical_param = "weighted_score"
    elif param_name in ["submission_delay", "mean_submission_delay"]:
        canonical_param = "mean_submission_delay"

    if param_range is None:
        p_min, p_max, _, _ = config.FEATURE_RANGES[canonical_param]
    else:
        p_min, p_max = param_range

    grid_vals = np.linspace(p_min, p_max, n_grid)
    grid_clusters = []
    grid_dists = []

    for v in grid_vals:
        curr = dict(fixed_params)
        curr[param_name] = v
        c, _, d = compute_prediction_for_vector(curr, kmeans_model, scaler)
        grid_clusters.append(c)
        grid_dists.append(d)

    grid_clusters = np.array(grid_clusters)
    grid_dists = np.array(grid_dists)

    # Current student prediction
    current_cluster, current_scaled, current_dists = compute_prediction_for_vector(
        fixed_params, kmeans_model, scaler
    )

    # Detect all transitions along the grid
    transitions = []
    change_indices = np.where(grid_clusters[:-1] != grid_clusters[1:])[0]

    for idx in change_indices:
        low_val = grid_vals[idx]
        high_val = grid_vals[idx + 1]
        c_low = int(grid_clusters[idx])
        c_high = int(grid_clusters[idx + 1])

        t_point, d_low, d_high, verif = refine_boundary_bisection(
            param_name=param_name,
            fixed_params=fixed_params,
            low_val=low_val,
            high_val=high_val,
            c_low=c_low,
            c_high=c_high,
            kmeans_model=kmeans_model,
            scaler=scaler,
            tol=tol,
            max_iter=45
        )

        transitions.append({
            "parameter": param_name,
            "transition_value": round(float(t_point), 4),
            "cluster_before": c_low,
            "cluster_before_name": cluster_metadata.get(c_low, {}).get("name", f"Cluster {c_low}"),
            "cluster_after": c_high,
            "cluster_after_name": cluster_metadata.get(c_high, {}).get("name", f"Cluster {c_high}"),
            "competing_distance_before": round(float(d_low), 4),
            "competing_distance_after": round(float(d_high), 4),
            "verification": verif
        })

    # Construct complete parameter intervals
    intervals = []
    if len(transitions) == 0:
        sole_cluster = int(grid_clusters[0])
        intervals.append({
            "range_min": p_min,
            "range_max": p_max,
            "range_str": f"[{p_min:g}, {p_max:g}]",
            "predicted_cluster": sole_cluster,
            "cluster_name": cluster_metadata.get(sole_cluster, {}).get("name", f"Cluster {sole_cluster}"),
            "badge_color": cluster_metadata.get(sole_cluster, {}).get("badge_color", "#1E88E5"),
            "contains_current_value": True
        })
        has_transition = False
        message = "No cluster transition occurs within the tested range when the other three parameters are held constant."
    else:
        has_transition = True
        curr_val = fixed_params[param_name]
        message = f"Found {len(transitions)} cluster transition boundary point(s) along {param_name}."

        # First interval
        first_t = transitions[0]["transition_value"]
        c_first = transitions[0]["cluster_before"]
        intervals.append({
            "range_min": p_min,
            "range_max": first_t,
            "range_str": f"[{p_min:g}, {first_t:.2f})",
            "predicted_cluster": c_first,
            "cluster_name": cluster_metadata.get(c_first, {}).get("name", f"Cluster {c_first}"),
            "badge_color": cluster_metadata.get(c_first, {}).get("badge_color", "#1E88E5"),
            "contains_current_value": (p_min <= curr_val < first_t)
        })

        # Middle intervals
        for i in range(len(transitions) - 1):
            t_curr = transitions[i]["transition_value"]
            t_next = transitions[i + 1]["transition_value"]
            c_mid = transitions[i]["cluster_after"]
            intervals.append({
                "range_min": t_curr,
                "range_max": t_next,
                "range_str": f"[{t_curr:.2f}, {t_next:.2f})",
                "predicted_cluster": c_mid,
                "cluster_name": cluster_metadata.get(c_mid, {}).get("name", f"Cluster {c_mid}"),
                "badge_color": cluster_metadata.get(c_mid, {}).get("badge_color", "#1E88E5"),
                "contains_current_value": (t_curr <= curr_val < t_next)
            })

        # Final interval
        last_t = transitions[-1]["transition_value"]
        c_last = transitions[-1]["cluster_after"]
        intervals.append({
            "range_min": last_t,
            "range_max": p_max,
            "range_str": f"[{last_t:.2f}, {p_max:g}]",
            "predicted_cluster": c_last,
            "cluster_name": cluster_metadata.get(c_last, {}).get("name", f"Cluster {c_last}"),
            "badge_color": cluster_metadata.get(c_last, {}).get("badge_color", "#1E88E5"),
            "contains_current_value": (last_t <= curr_val <= p_max)
        })

    return {
        "parameter": param_name,
        "current_value": fixed_params[param_name],
        "current_cluster": current_cluster,
        "current_cluster_name": cluster_metadata.get(current_cluster, {}).get("name", f"Cluster {current_cluster}"),
        "fixed_params": fixed_params,
        "has_transition": has_transition,
        "message": message,
        "transitions": transitions,
        "intervals": intervals,
        "grid_values": grid_vals.tolist(),
        "grid_clusters": grid_clusters.tolist(),
        "grid_distances": grid_dists.tolist(),
        "tolerance": tol
    }


def generate_2d_decision_surface(
    param_x: str,
    param_y: str,
    fixed_params: Dict[str, float],
    kmeans_model: KMeans,
    scaler: StandardScaler,
    cluster_metadata: Dict[int, Any],
    grid_resolution: int = 110
) -> Dict[str, Any]:
    """
    Computes a 2D conditional decision region grid (110x110) holding the remaining two parameters fixed.
    Evaluates Euclidean distance to centroids across all grid coordinates in standardized space.
    """
    # Normalize parameter names
    px_canon = "weighted_score" if param_x in ["weighted_avg_score", "weighted_score"] else ("mean_submission_delay" if param_x in ["submission_delay", "mean_submission_delay"] else param_x)
    py_canon = "weighted_score" if param_y in ["weighted_avg_score", "weighted_score"] else ("mean_submission_delay" if param_y in ["submission_delay", "mean_submission_delay"] else param_y)

    x_min, x_max, _, _ = config.FEATURE_RANGES[px_canon]
    y_min, y_max, _, _ = config.FEATURE_RANGES[py_canon]

    x_line = np.linspace(x_min, x_max, grid_resolution)
    y_line = np.linspace(y_min, y_max, grid_resolution)
    X_mesh, Y_mesh = np.meshgrid(x_line, y_line)

    n_points = grid_resolution * grid_resolution

    clicks = fixed_params.get("total_clicks", 1200.0)
    days = fixed_params.get("active_days", 50.0)
    score = fixed_params.get("weighted_avg_score", fixed_params.get("weighted_score", 75.0))
    delay = fixed_params.get("submission_delay", fixed_params.get("mean_submission_delay", -2.0))

    grid_data = {
        "total_clicks": np.full(n_points, clicks, dtype=np.float64),
        "active_days": np.full(n_points, days, dtype=np.float64),
        "weighted_score": np.full(n_points, score, dtype=np.float64),
        "mean_submission_delay": np.full(n_points, delay, dtype=np.float64)
    }

    grid_data[px_canon] = X_mesh.ravel()
    grid_data[py_canon] = Y_mesh.ravel()

    # Log-transform clicks
    t_clicks = np.log1p(grid_data["total_clicks"])
    feat_matrix = np.column_stack([
        t_clicks,
        grid_data["active_days"],
        grid_data["weighted_score"],
        grid_data["mean_submission_delay"]
    ])

    # Standardize
    scaled_matrix = scaler.transform(feat_matrix)

    # Compute cluster predictions
    centroids = kmeans_model.cluster_centers_  # (4, 4)
    diff = scaled_matrix[:, np.newaxis, :] - centroids[np.newaxis, :, :]
    dists_sq = np.sum(diff ** 2, axis=2)
    pred_grid = np.argmin(dists_sq, axis=1).reshape((grid_resolution, grid_resolution))

    # Current student coordinate
    student_x = fixed_params[param_x]
    student_y = fixed_params[param_y]
    curr_pred, _, _ = compute_prediction_for_vector(fixed_params, kmeans_model, scaler)

    return {
        "param_x": param_x,
        "param_y": param_y,
        "x_values": x_line.tolist(),
        "y_values": y_line.tolist(),
        "prediction_grid": pred_grid.tolist(),
        "student_x": student_x,
        "student_y": student_y,
        "student_cluster": curr_pred,
        "student_cluster_name": cluster_metadata.get(curr_pred, {}).get("name", f"Cluster {curr_pred}"),
        "fixed_params": {k: v for k, v in fixed_params.items() if k not in [param_x, param_y]},
        "grid_resolution": grid_resolution
    }


def generate_transition_explanation(
    current_result: Dict[str, Any],
    sensitivity_result: Dict[str, Any]
) -> str:
    """
    Constructs an evidence-based explanation of cluster transitions, distance equality,
    and feature contributions along the decision boundary.
    """
    param = sensitivity_result["parameter"]
    curr_val = sensitivity_result["current_value"]
    curr_name = sensitivity_result["current_cluster_name"]

    if not sensitivity_result["has_transition"]:
        return (
            f"Holding the other three parameters constant, varying **{param}** across its entire "
            f"range does not shift the student out of **{curr_name}**. The current values place this learner "
            f"firmly inside the Voronoi cell of this cluster in standardized 4D space."
        )

    transitions = sensitivity_result["transitions"]
    closest_t = min(transitions, key=lambda t: abs(t["transition_value"] - curr_val))
    t_val = closest_t["transition_value"]
    delta = t_val - curr_val

    direction = "increasing" if delta > 0 else "decreasing"
    abs_delta = abs(delta)

    target_name = closest_t["cluster_after_name"] if delta > 0 else closest_t["cluster_before_name"]

    return (
        f"**Transition Boundary Detected:** By {direction} **{param}** by **{abs_delta:.2f}** "
        f"(from {curr_val:.2f} to {t_val:.2f}), the student will transition from **{curr_name}** "
        f"to **{target_name}**. At the exact transition boundary ($x = {t_val:.4f}$), the standardized "
        f"Euclidean distance to Centroid {closest_t['cluster_before']} ({closest_t['competing_distance_before']:.4f}) "
        f"equals the distance to Centroid {closest_t['cluster_after']} ({closest_t['competing_distance_after']:.4f})."
    )

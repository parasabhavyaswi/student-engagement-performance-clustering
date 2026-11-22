"""
EduPulse - Visualization Module (Navy & Alabaster Telemetry Deck)
Project ID: SIH26036
Provides rich, high-contrast Plotly figures in a Navy & Alabaster Command-Center theme:
- plot_k_selection_curves: Silhouette & Davies-Bouldin vs K with K=4 reference line
- plot_cluster_donut: Hollow donut chart (hole=0.58) of cohort distributions
- plot_engagement_vs_performance: Scatter of active_days vs weighted_avg_score
- plot_student_vs_centroid_radar: Polar radar of standardized Z-scores
- plot_one_dim_transition: Step-line chart with exact bisection boundaries
- plot_two_dim_decision_regions: 2D Voronoi decision-region heatmap with star marker
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent if "__file__" in locals() else Path.cwd()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

# High-contrast palette for archetypes
ARCHETYPE_COLORS = {
    "High-Achievers": "#2563EB",     # Electric Blue
    "At-Risk Learners": "#DC2626",   # Crimson Red
    "Deadline Crammers": "#D97706",  # Amber Orange
    "Steady Learners": "#059669"     # Emerald Green
}

# Color palette mapped by cluster ID
CLUSTER_COLORS = {
    0: "#059669",  # Steady Learners
    1: "#D97706",  # Deadline Crammers
    2: "#DC2626",  # At-Risk Learners
    3: "#2563EB"   # High-Achievers
}

PLOT_TEMPLATE = "plotly_white"


# ==============================================================================
# 1. K-Selection Curves
# ==============================================================================
def plot_k_selection_curves(k_eval_table: Union[List[Dict[str, Any]], pd.DataFrame]) -> go.Figure:
    """
    Line+marker plot across K=2..8 comparing Silhouette Score (higher is better)
    and Davies-Bouldin Index (lower is better) with a vertical dotted reference line at K=4.
    """
    if isinstance(k_eval_table, pd.DataFrame):
        ks = k_eval_table["k"].tolist()
        sil = k_eval_table["silhouette"].tolist()
        db = k_eval_table["davies_bouldin"].tolist()
    else:
        ks = [m["k"] for m in k_eval_table]
        sil = [m["silhouette"] for m in k_eval_table]
        db = [m["davies_bouldin"] for m in k_eval_table]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "Silhouette Score (Cluster Separation ↑)",
            "Davies-Bouldin Index (Cluster Compactness ↓)"
        ),
        horizontal_spacing=0.12
    )

    # 1. Silhouette
    fig.add_trace(
        go.Scatter(
            x=ks, y=sil, mode="lines+markers",
            line=dict(color="#0284C7", width=3),
            marker=dict(size=8, color="#0F172A", line=dict(width=1.5, color="#38BDF8")),
            name="Silhouette Score"
        ),
        row=1, col=1
    )

    # 2. Davies-Bouldin
    fig.add_trace(
        go.Scatter(
            x=ks, y=db, mode="lines+markers",
            line=dict(color="#D97706", width=3),
            marker=dict(size=8, color="#0F172A", line=dict(width=1.5, color="#FBBF24")),
            name="Davies-Bouldin"
        ),
        row=1, col=2
    )

    # Vertical reference line at K=4 across both subplots
    for col_idx in [1, 2]:
        fig.add_vline(
            x=4,
            line_width=2.2,
            line_dash="dot",
            line_color="#E11D48",
            annotation_text="Selected K=4",
            annotation_position="top left",
            annotation_font=dict(size=11, color="#E11D48", family="Arial"),
            row=1, col=col_idx
        )

    fig.update_layout(
        template=PLOT_TEMPLATE,
        height=380,
        showlegend=False,
        title=dict(
            text="<b>K-Means Hyperparameter Selection (K = 2 to 8)</b><br><sup>Red dotted line highlights K=4 selected for pedagogical interpretability</sup>",
            x=0.01,
            font=dict(color="#0F172A", size=15)
        ),
        margin=dict(l=35, r=35, t=75, b=35)
    )
    for col_idx in [1, 2]:
        fig.update_xaxes(title_text="Number of Clusters (K)", tickmode="linear", tick0=2, dtick=1, row=1, col=col_idx)

    return fig


# ==============================================================================
# 2. Cluster Donut Chart
# ==============================================================================
def plot_cluster_donut(cluster_profiles: Union[Dict[int, Any], List[Dict[str, Any]], pd.DataFrame]) -> go.Figure:
    """
    Hollow donut chart (hole=0.58) showing enrolment distribution and percentages
    across the four archetypes.
    """
    if isinstance(cluster_profiles, dict):
        items = list(cluster_profiles.values())
    elif isinstance(cluster_profiles, pd.DataFrame):
        items = cluster_profiles.to_dict(orient="records")
    else:
        items = cluster_profiles

    names = [m.get("name", f"Cluster {m.get('archetype_id', i)}") for i, m in enumerate(items)]
    counts = [m.get("count", 0) for m in items]
    percentages = [m.get("percentage", 0.0) for m in items]

    colors = [
        ARCHETYPE_COLORS.get(name, CLUSTER_COLORS.get(i, "#64748B"))
        for i, name in enumerate(names)
    ]

    hover_texts = [
        f"<b>{name}</b><br>Enrolments: {c:,}<br>Share: {pct}%<br>Mean Clicks: {m.get('mean_clicks', 0):.1f}<br>Mean Score: {m.get('mean_score', 0):.1f}%"
        for name, c, pct, m in zip(names, counts, percentages, items)
    ]

    total_count = sum(counts)

    fig = go.Figure(
        data=[
            go.Pie(
                labels=names,
                values=counts,
                hole=0.58,
                marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2.5)),
                hovertext=hover_texts,
                hoverinfo="text",
                textinfo="label+percent",
                textposition="outside",
                textfont=dict(size=12, color="#0F172A", family="Arial")
            )
        ]
    )

    # Center annotation
    fig.add_annotation(
        text=f"<b>{total_count:,}</b><br><span style='font-size:11px;color:#64748B;'>Enrolments</span>",
        x=0.5, y=0.5,
        font=dict(size=18, color="#0F172A"),
        showarrow=False
    )

    fig.update_layout(
        template=PLOT_TEMPLATE,
        height=380,
        showlegend=False,
        title=dict(
            text="<b>Cohort Distribution by Archetype (K=4)</b>",
            x=0.01,
            font=dict(color="#0F172A", size=15)
        ),
        margin=dict(l=30, r=30, t=55, b=30)
    )
    return fig


# ==============================================================================
# 3. Engagement vs Performance Scatter
# ==============================================================================
def plot_engagement_vs_performance(
    valid_df: pd.DataFrame,
    sample_size: int = 4000
) -> go.Figure:
    """
    Scatter plot of active_days vs. weighted_avg_score colored by cluster_name.
    """
    sample_df = valid_df.sample(min(sample_size, len(valid_df)), random_state=42) if len(valid_df) > sample_size else valid_df

    score_col = "weighted_avg_score" if "weighted_avg_score" in sample_df.columns else "weighted_score"
    delay_col = "submission_delay" if "submission_delay" in sample_df.columns else "mean_submission_delay"

    fig = px.scatter(
        sample_df,
        x="active_days",
        y=score_col,
        color="cluster_name",
        color_discrete_map=ARCHETYPE_COLORS,
        hover_data={
            "id_student": True,
            "total_clicks": ":.0f",
            delay_col: ":.1f",
            "final_result": True,
            "cluster_name": True
        },
        labels={
            "active_days": "Active Learning Days (Regularity)",
            score_col: "Weighted Assessment Score (%)",
            "cluster_name": "Archetype"
        },
        opacity=0.68,
        template=PLOT_TEMPLATE
    )

    fig.update_traces(marker=dict(size=6, line=dict(width=0.4, color="#FFFFFF")))
    fig.update_layout(
        height=480,
        title=dict(
            text=f"<b>Student Engagement Regularity vs. Assessment Mastery</b><br><sup>Visualizing {len(sample_df):,} enrolments colored by learned archetype</sup>",
            x=0.01,
            font=dict(color="#0F172A", size=15)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title_text=""
        ),
        margin=dict(l=40, r=40, t=75, b=40)
    )
    return fig


# ==============================================================================
# 4. Standardized Z-Score Radar Chart
# ==============================================================================
def plot_student_vs_centroid_radar(
    feature_comparison: Union[List[Dict[str, Any]], Dict[str, Any], np.ndarray],
    cluster_name: str = "Assigned Archetype",
    centroid_scaled: Optional[np.ndarray] = None
) -> go.Figure:
    """
    Polar radar chart (go.Scatterpolar) comparing the student's standardized 4D Z-score vector
    against their predicted cluster centroid's Z-score vector.
    """
    categories = [
        "Platform Clicks<br>(log1p Z)",
        "Active Days<br>(Regularity Z)",
        "Weighted Score<br>(Mastery Z)",
        "Submission Delay<br>(Pacing Z)"
    ]

    # Extract student and centroid Z values
    if isinstance(feature_comparison, list):
        # List of dicts from predict_student_cluster
        student_z = [item["student_scaled"] for item in feature_comparison]
        centroid_z = [item["centroid_scaled"] for item in feature_comparison]
    elif isinstance(feature_comparison, dict):
        student_z = feature_comparison.get("student_scaled", [0, 0, 0, 0])
        centroid_z = feature_comparison.get("centroid_scaled", [0, 0, 0, 0])
    elif isinstance(feature_comparison, (np.ndarray, list)) and centroid_scaled is not None:
        student_z = list(feature_comparison)
        centroid_z = list(centroid_scaled)
    else:
        student_z = [0.0, 0.0, 0.0, 0.0]
        centroid_z = [0.0, 0.0, 0.0, 0.0]

    # Close the radar loop
    r_student = list(student_z) + [student_z[0]]
    r_centroid = list(centroid_z) + [centroid_z[0]]
    theta = categories + [categories[0]]

    fig = go.Figure()

    # Centroid reference polygon
    fig.add_trace(
        go.Scatterpolar(
            r=r_centroid,
            theta=theta,
            fill="toself",
            name=f"{cluster_name} Centroid",
            line=dict(color="#64748B", dash="dash", width=2.2),
            fillcolor="rgba(100, 116, 139, 0.12)"
        )
    )

    # Student polygon
    fig.add_trace(
        go.Scatterpolar(
            r=r_student,
            theta=theta,
            fill="toself",
            name="Current Student Z-Score",
            line=dict(color="#0284C7", width=2.8),
            fillcolor="rgba(2, 132, 199, 0.28)",
            marker=dict(size=6, color="#0F172A")
        )
    )

    # Calculate radial bounds
    all_vals = list(student_z) + list(centroid_z)
    max_val = max(max(map(abs, all_vals)), 2.5) + 0.5

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[-max_val, max_val],
                tickfont=dict(size=10, color="#64748B"),
                gridcolor="#E2E8F0"
            ),
            angularaxis=dict(
                gridcolor="#CBD5E1",
                tickfont=dict(size=11, color="#0F172A", family="Arial")
            ),
            bgcolor="#F8FAFC"
        ),
        template=PLOT_TEMPLATE,
        height=420,
        title=dict(
            text=f"<b>Standardized 4D Z-Score Profile vs. {cluster_name}</b><br><sup>Values in standard deviations (Z = 0 represents the cohort mean)</sup>",
            x=0.01,
            font=dict(color="#0F172A", size=14)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.18,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=30, r=30, t=65, b=45)
    )

    return fig


# ==============================================================================
# 5. One-Dimensional Step Transition Plot
# ==============================================================================
def plot_one_dim_transition(
    analysis: Dict[str, Any],
    archetype_map: Optional[Dict[int, Any]] = None
) -> go.Figure:
    """
    Step-line chart (shape="hv") sweeping the chosen parameter across its valid range
    with vertical dashed markers for exact bisection transition boundaries and a dotted
    marker for the student's current value.
    """
    grid_vals = np.array(analysis["grid_values"])
    grid_clusters = np.array(analysis["grid_clusters"])
    param_name = analysis["parameter"]
    curr_val = analysis["current_value"]

    # Map cluster IDs to names if archetype_map available
    cluster_names = {}
    if archetype_map:
        for cid, m in archetype_map.items():
            cluster_names[int(cid)] = m.get("name", f"Cluster {cid}")
    else:
        cluster_names = {0: "Cluster 0", 1: "Cluster 1", 2: "Cluster 2", 3: "Cluster 3"}

    y_labels = [cluster_names.get(c, f"Cluster {c}") for c in grid_clusters]

    fig = go.Figure()

    # Step-line trace
    fig.add_trace(
        go.Scatter(
            x=grid_vals,
            y=y_labels,
            mode="lines",
            line=dict(shape="hv", color="#0F172A", width=3.2),
            name="Archetype Assignment",
            hoverinfo="x+y"
        )
    )

    # Vertical dashed markers for exact bisection transition boundaries
    for t in analysis.get("transitions", []):
        t_val = t["transition_value"]
        b_name = t.get("cluster_before_name", f"C{t['cluster_before']}")
        a_name = t.get("cluster_after_name", f"C{t['cluster_after']}")
        fig.add_vline(
            x=t_val,
            line_width=2.0,
            line_dash="dash",
            line_color="#E11D48",
            annotation_text=f"Boundary: {t_val:.2f}",
            annotation_position="top left",
            annotation_font=dict(size=10, color="#E11D48", family="Arial")
        )

    # Dotted marker for current student value
    fig.add_vline(
        x=curr_val,
        line_width=2.5,
        line_dash="dot",
        line_color="#0284C7",
        annotation_text=f"Current Student: {curr_val:.2f}",
        annotation_position="bottom right",
        annotation_font=dict(size=11, color="#0284C7", family="Arial")
    )

    param_label = config.FEATURE_LABELS.get(param_name, param_name.replace("_", " ").title())
    param_unit = config.FEATURE_UNITS.get(param_name, "")
    unit_str = f" ({param_unit})" if param_unit else ""

    fig.update_layout(
        template=PLOT_TEMPLATE,
        height=400,
        title=dict(
            text=f"<b>1D Parameter Sensitivity Sweep: {param_label}</b><br><sup>Step function shows discrete archetype shifts as {param_label} varies with other parameters held constant</sup>",
            x=0.01,
            font=dict(color="#0F172A", size=14)
        ),
        xaxis_title=f"{param_label}{unit_str}",
        yaxis_title="Assigned Archetype",
        showlegend=False,
        margin=dict(l=40, r=40, t=75, b=40)
    )

    return fig


# ==============================================================================
# 6. Two-Dimensional Voronoi Decision Regions
# ==============================================================================
def plot_two_dim_decision_regions(
    grid_data: Dict[str, Any],
    current_values: Optional[Union[Dict[str, float], Tuple[float, float]]] = None,
    archetype_map: Optional[Dict[int, Any]] = None
) -> go.Figure:
    """
    2D discrete Voronoi decision-region heatmap with custom hover labels,
    archetype legend entries, and a star marker (symbol="star") at the student's current coordinates.
    """
    x_vals = np.array(grid_data.get("x_values", grid_data.get("x_line", [])))
    y_vals = np.array(grid_data.get("y_values", grid_data.get("y_line", [])))
    Z = np.array(grid_data.get("prediction_grid", grid_data.get("Z_mesh", [])))

    param_x = grid_data.get("param_x", "active_days")
    param_y = grid_data.get("param_y", "weighted_score")

    # Current student coordinates
    if isinstance(current_values, dict):
        stud_x = current_values.get(param_x, grid_data.get("student_x", 0.0))
        stud_y = current_values.get(param_y, grid_data.get("student_y", 0.0))
    elif isinstance(current_values, (tuple, list)):
        stud_x, stud_y = current_values[0], current_values[1]
    else:
        stud_x = grid_data.get("student_x", 0.0)
        stud_y = grid_data.get("student_y", 0.0)

    # Discrete colormap matching archetype IDs
    # 0: Steady Green, 1: Crammer Orange, 2: At-Risk Red, 3: High-Achiever Blue
    discrete_colorscale = [
        [0.00, "#A7F3D0"],  # 0 Steady Learners (Light emerald)
        [0.25, "#A7F3D0"],
        [0.25, "#FDE68A"],  # 1 Deadline Crammers (Light amber)
        [0.50, "#FDE68A"],
        [0.50, "#FECACA"],  # 2 At-Risk Learners (Light crimson)
        [0.75, "#FECACA"],
        [0.75, "#BFDBFE"],  # 3 High-Achievers (Light blue)
        [1.00, "#BFDBFE"]
    ]

    fig = go.Figure()

    # Decision region heatmap
    fig.add_trace(
        go.Heatmap(
            x=x_vals,
            y=y_vals,
            z=Z,
            colorscale=discrete_colorscale,
            zmin=0,
            zmax=3,
            showscale=False,
            hoverinfo="none"
        )
    )

    # Decision boundaries via contour lines
    fig.add_trace(
        go.Contour(
            x=x_vals,
            y=y_vals,
            z=Z,
            showscale=False,
            contours=dict(start=0.5, end=2.5, size=1.0, coloring="none"),
            line=dict(color="#1E293B", width=2.0)
        )
    )

    # Add invisible scatter points for legend items
    legend_names = {
        0: "Steady Learners Region",
        1: "Deadline Crammers Region",
        2: "At-Risk Learners Region",
        3: "High-Achievers Region"
    }
    if archetype_map:
        for cid, m in archetype_map.items():
            legend_names[int(cid)] = f"{m.get('name', f'Cluster {cid}')} Region"

    legend_colors = {
        0: "#059669",
        1: "#D97706",
        2: "#DC2626",
        3: "#2563EB"
    }

    for cid in sorted(legend_names.keys()):
        fig.add_trace(
            go.Scatter(
                x=[None], y=[None],
                mode="markers",
                marker=dict(size=12, color=legend_colors.get(cid, "#64748B"), symbol="square"),
                name=legend_names[cid]
            )
        )

    # Prominent star marker at student's current coordinates
    fig.add_trace(
        go.Scatter(
            x=[stud_x],
            y=[stud_y],
            mode="markers+text",
            marker=dict(
                size=18,
                color="#F59E0B",
                symbol="star",
                line=dict(width=2.5, color="#0F172A")
            ),
            text=["<b>Student Location</b>"],
            textposition="top center",
            name="Current Student",
            hovertext=f"Current Coordinates:<br>{param_x}: {stud_x:.1f}<br>{param_y}: {stud_y:.1f}",
            hoverinfo="text"
        )
    )

    x_label = config.FEATURE_LABELS.get(param_x, param_x.replace("_", " ").title())
    y_label = config.FEATURE_LABELS.get(param_y, param_y.replace("_", " ").title())

    fig.update_layout(
        template=PLOT_TEMPLATE,
        height=520,
        title=dict(
            text=f"<b>2D Conditional Decision Regions ({x_label} vs. {y_label})</b><br><sup>Gold star indicates current student position in sliced Voronoi space</sup>",
            x=0.01,
            font=dict(color="#0F172A", size=14)
        ),
        xaxis_title=x_label,
        yaxis_title=y_label,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.22,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=40, r=40, t=75, b=60)
    )

    return fig


# ==============================================================================
# Backward Compatibility Aliases & Legacy Plot Functions
# ==============================================================================
def plot_k_evaluation_metrics(metrics: List[Dict[str, Any]]) -> go.Figure:
    """Legacy 4-panel evaluation metrics."""
    return plot_k_selection_curves(metrics)

def plot_cluster_scatter(df: pd.DataFrame, x_col: str = "active_days", y_col: str = "weighted_score", sample_size: int = 4000) -> go.Figure:
    """Legacy cluster scatter plot."""
    return plot_engagement_vs_performance(df, sample_size=sample_size)

def plot_1d_sensitivity_curve(sensitivity_res: Dict[str, Any]) -> go.Figure:
    """Legacy 1D sensitivity curves."""
    return plot_one_dim_transition(sensitivity_res)

def plot_2d_decision_surface(surface_res: Dict[str, Any], cluster_metadata: Optional[Dict[int, Any]] = None) -> go.Figure:
    """Legacy 2D decision surface."""
    return plot_two_dim_decision_regions(surface_res, archetype_map=cluster_metadata)

def plot_radar_profile(scaled_vector: np.ndarray, predicted_cluster: int, kmeans_model: Any, cluster_metadata: Dict[int, Any]) -> go.Figure:
    """Legacy radar profile."""
    centroid = kmeans_model.cluster_centers_[predicted_cluster]
    c_name = cluster_metadata.get(predicted_cluster, {}).get("name", f"Cluster {predicted_cluster}")
    return plot_student_vs_centroid_radar(scaled_vector, cluster_name=c_name, centroid_scaled=centroid)

def plot_centroid_distances_bar(distances: Dict[int, float], similarities: Dict[int, float], cluster_metadata: Dict[int, Any]) -> go.Figure:
    """Horizontal bar charts comparing Euclidean distance and proximity."""
    cluster_ids = sorted(list(distances.keys()))
    names = [cluster_metadata.get(c, {}).get("name", f"Cluster {c}") for c in cluster_ids]
    d_vals = [distances[c] for c in cluster_ids]
    s_vals = [similarities[c] for c in cluster_ids]
    colors = [CLUSTER_COLORS.get(c, "#2563EB") for c in cluster_ids]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "Euclidean Distance to Centroid (Lower = Closer)",
            "Distance-Based Proximity Indicator (%)"
        ),
        horizontal_spacing=0.15
    )
    fig.add_trace(
        go.Bar(
            y=names, x=d_vals, orientation="h",
            marker=dict(color=colors),
            text=[f"{v:.3f}" for v in d_vals], textposition="auto", name="Distance"
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(
            y=names, x=s_vals, orientation="h",
            marker=dict(color=colors),
            text=[f"{v:.1f}%" for v in s_vals], textposition="auto", name="Proximity"
        ),
        row=1, col=2
    )
    fig.update_layout(
        template=PLOT_TEMPLATE, height=320, showlegend=False,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    fig.update_xaxes(title_text="Distance in Standardized 4D Space", row=1, col=1)
    fig.update_xaxes(title_text="Relative Proximity (%)", row=1, col=2)
    return fig

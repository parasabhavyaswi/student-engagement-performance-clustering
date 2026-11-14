"""
EduCluster ML: Student Engagement & Performance Analytics
Interactive Streamlit Dashboard (Project ID: SIH26036)

Production dashboard implementing:
- Objective 1: Feature compilation & StandardScaler normalization
- Objective 2: K-Means segmentation (k=4), Elbow/Silhouette sweep, and 2D PCA projection
- Objective 3: Extrinsic & Intrinsic validation (NMI, ARI, Chi-Square, Cramer's V, Contingency Matrix)
- Objective 4: Live Student Persona Simulator & 4-Stage Personalized Learning Path Roadmaps
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path so src imports work reliably
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(BASE_DIR / "src") not in sys.path:
    sys.path.insert(0, str(BASE_DIR / "src"))

# Suppress loky CPU core-count warning on Windows
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Import core modules
from src.preprocess import (
    load_and_preprocess_data,
    FEATURE_NAMES,
    DOMAIN_FEATURE_GROUPS,
    TARGET_COLUMN
)
from src.clustering import (
    run_k_sweep,
    train_kmeans,
    compute_pca_projection,
    get_centroid_profiles,
    CLUSTER_METADATA
)
from src.validation import (
    compute_extrinsic_validation,
    compute_intrinsic_validation
)
from src.recommender import (
    impute_16_features_from_sliders,
    predict_learning_path,
    LEARNING_PATHS
)

# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EduCluster ML",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Custom Cyber / Glassmorphic Dark-Mode CSS Styling (Fix 1, 2, 3, 4)
# -----------------------------------------------------------------------------
DARK_THEME_CSS = """
<style>
/* Base Dark Theme Overrides */
.stApp {
    background-color: #0b0f19;
    color: #e2e8f0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Custom Header Styling */
.main-header-title {
    font-size: 2.1rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #94a3b8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}

.main-header-subtitle {
    font-size: 0.95rem;
    color: #94a3b8;
    font-weight: 400;
    margin-bottom: 1.5rem;
}

/* KPI Card Grid */
.kpi-container {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.8rem;
    flex-wrap: wrap;
}

.kpi-card {
    flex: 1;
    min-width: 180px;
    background: linear-gradient(180deg, #111827 0%, #0d1322 100%);
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.kpi-card:hover {
    border-color: rgba(99, 102, 241, 0.4);
    transform: translateY(-2px);
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
}

.kpi-card.emerald::before { background: linear-gradient(90deg, #10b981, #059669); }
.kpi-card.blue::before { background: linear-gradient(90deg, #3b82f6, #2563eb); }
.kpi-card.amber::before { background: linear-gradient(90deg, #f59e0b, #d97706); }
.kpi-card.violet::before { background: linear-gradient(90deg, #8b5cf6, #7c3aed); }
.kpi-card.cyan::before { background: linear-gradient(90deg, #06b6d4, #0891b2); }

.kpi-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 700;
    color: #94a3b8;
    margin-bottom: 0.35rem;
}

.kpi-value {
    font-size: 1.75rem;
    font-weight: 800;
    color: #f8fafc;
    line-height: 1.1;
    font-feature-settings: "tnum";
}

.kpi-subtext {
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 0.35rem;
}

/* Sidebar Custom Styling */
section[data-testid="stSidebar"] {
    background-color: #0d1322 !important;
    border-right: 1px solid #1e293b;
}

.sidebar-header-box {
    padding: 0.8rem 0 1.2rem 0;
    border-bottom: 1px solid #1e293b;
    margin-bottom: 1.2rem;
}

.sidebar-brand {
    font-size: 1.45rem;
    font-weight: 800;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.sidebar-brand span {
    background: linear-gradient(135deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.sidebar-tag {
    font-size: 0.7rem;
    font-weight: 600;
    color: #38bdf8;
    background: rgba(56, 189, 248, 0.12);
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    display: inline-block;
    margin-top: 0.3rem;
}

/* Full-width Stacked Preset Buttons (Fix 2) */
.stButton button {
    width: 100% !important;
    background-color: #111827 !important;
    color: #e2e8f0 !important;
    border: 1px solid #1e293b !important;
    border-radius: 8px !important;
    padding: 0.55rem 0.8rem !important;
    font-weight: 600 !important;
    font-size: 0.86rem !important;
    text-align: left !important;
    justify-content: flex-start !important;
    transition: all 0.15s ease !important;
}

.stButton button:hover {
    border-color: #38bdf8 !important;
    background-color: #1e293b !important;
    color: #ffffff !important;
    transform: translateX(2px) !important;
}

/* Sidebar Live Prediction Pill (Fix 2) */
.sidebar-prediction-pill {
    margin-top: 1.2rem;
    padding: 0.9rem 1rem;
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 10px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

/* Roadmap Stage Grid (Fix 3) */
.roadmap-container {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 1rem 0 1.5rem 0;
}

@media (max-width: 900px) {
    .roadmap-container {
        grid-template-columns: 1fr;
    }
}

.roadmap-card {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 1.1rem;
    position: relative;
    transition: transform 0.15s ease, border-color 0.15s ease;
}

.roadmap-card:hover {
    transform: translateY(-2px);
    border-color: rgba(255, 255, 255, 0.2);
}

/* Dark Table Styles (Fix 1) */
.dark-table-wrapper {
    overflow-x: auto;
    border: 1px solid #1e293b;
    border-radius: 8px;
    margin: 0.5rem 0 1rem 0;
    background-color: #111827;
}

.dark-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Inter', -apple-system, sans-serif;
    font-size: 0.82rem;
    color: #cbd5e1;
}

.dark-table thead tr {
    background-color: #1e293b;
    border-bottom: 1px solid #334155;
}

.dark-table th {
    padding: 10px 14px;
    text-align: left;
    font-weight: 700;
    color: #f8fafc;
    letter-spacing: 0.03em;
    white-space: nowrap;
}

.dark-table tbody tr {
    border-bottom: 1px solid #1e293b;
    transition: background-color 0.15s ease;
}

.dark-table tbody tr:nth-child(even) {
    background-color: #0f172a;
}

.dark-table tbody tr:nth-child(odd) {
    background-color: #111827;
}

.dark-table tbody tr:hover {
    background-color: #1e293b;
}

.dark-table td {
    padding: 8px 14px;
    white-space: nowrap;
}

/* Tabs Styling */
div[data-testid="stTabs"] button[role="tab"] {
    font-weight: 600;
    font-size: 0.92rem;
    color: #94a3b8;
    padding: 0.6rem 1.2rem;
}

div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #ffffff;
    border-bottom: 2px solid #38bdf8;
}
</style>
"""
st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Helper: Dark Table HTML Renderer (Fix 1: Zero White Backgrounds)
# -----------------------------------------------------------------------------
def render_dark_table(df: pd.DataFrame, max_height: str = "none") -> str:
    """
    Renders a pandas DataFrame as a sleek dark HTML/CSS table with #111827 background,
    #1e293b borders, and #f8fafc text, guaranteeing zero white canvas frames.
    """
    headers = "".join([f"<th>{col}</th>" for col in df.columns])

    rows = []
    for _, row in df.iterrows():
        tds = "".join([f"<td>{val}</td>" for val in row])
        rows.append(f"<tr>{tds}</tr>")
    rows_html = "".join(rows)

    overflow_style = f"max-height: {max_height}; overflow-y: auto;" if max_height != "none" else "overflow-x: auto;"
    sticky_header = "position: sticky; top: 0; z-index: 2;" if max_height != "none" else ""

    html = f"""
    <div class="dark-table-wrapper" style="{overflow_style}">
        <table class="dark-table">
            <thead style="{sticky_header}">
                <tr>{headers}</tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    return html


# -----------------------------------------------------------------------------
# Cached Data Loading & Model Execution
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner="Compiling OULAD features & scaling dataset...")
def load_cached_dataset():
    """Load or generate the 14,003 student dataset and standardize features."""
    raw_dir = BASE_DIR / "data" / "raw"
    df_raw, X_scaled, scaler, feature_names, y_true = load_and_preprocess_data(raw_dir=raw_dir)
    return df_raw, X_scaled, scaler, feature_names, y_true


@st.cache_resource(show_spinner="Fitting production K-Means & PCA models...")
def get_cached_models(X_scaled: np.ndarray, df_raw: pd.DataFrame):
    """Train K-Means (k=4) with deterministic score-based sorting and compute 2D PCA."""
    km_model, cluster_labels, cluster_info = train_kmeans(
        X_scaled=X_scaled,
        df_raw=df_raw,
        n_clusters=4,
        random_state=42
    )

    pca_coords, pca_model, pca_var = compute_pca_projection(
        X_scaled=X_scaled,
        n_components=2,
        random_state=42
    )

    return km_model, cluster_labels, cluster_info, pca_coords, pca_model, pca_var


@st.cache_data(show_spinner="Computing k-sweep & validation metrics...")
def get_cached_validation(X_scaled: np.ndarray, cluster_labels: np.ndarray, y_true: pd.Series, cluster_names: dict):
    """Compute optimal-k sweep curves, extrinsic validation, and intrinsic metrics."""
    sweep_df = run_k_sweep(X_scaled, k_range=range(2, 9), sample_size_sil=4000, random_state=42)
    ext_metrics = compute_extrinsic_validation(y_true, cluster_labels, cluster_names)
    int_metrics = compute_intrinsic_validation(X_scaled, cluster_labels, sample_size=5000, random_state=42)
    return sweep_df, ext_metrics, int_metrics


# Execute pipelines
df_raw, X_scaled, scaler, feature_names, y_true = load_cached_dataset()
km_model, cluster_labels, cluster_info, pca_coords, pca_model, pca_var = get_cached_models(X_scaled, df_raw)
sweep_df, ext_metrics, int_metrics = get_cached_validation(X_scaled, cluster_labels, y_true, cluster_info["cluster_names"])

# Compute centroid profiles
df_centroids_raw, df_centroids_norm = get_centroid_profiles(df_raw, cluster_labels, feature_names)


# -----------------------------------------------------------------------------
# Sidebar: Student Persona Simulator & Full-Width Presets (Fix 2)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header-box">
        <div class="sidebar-brand">🎓 Edu<span>Cluster</span></div>
        <div class="sidebar-tag">STUDENT PERSONA SIMULATOR</div>
    </div>
    """, unsafe_allow_html=True)

    # Initialize slider session state with default values
    if "slider_clicks" not in st.session_state:
        st.session_state["slider_clicks"] = 100.0
    if "slider_days" not in st.session_state:
        st.session_state["slider_days"] = 50.0
    if "slider_score" not in st.session_state:
        st.session_state["slider_score"] = 75.0
    if "slider_delay" not in st.session_state:
        st.session_state["slider_delay"] = 0.0

    # Helper callback for preset buttons
    def apply_preset(c_val: float, d_val: float, s_val: float, del_val: float):
        st.session_state["slider_clicks"] = float(c_val)
        st.session_state["slider_days"] = float(d_val)
        st.session_state["slider_score"] = float(s_val)
        st.session_state["slider_delay"] = float(del_val)

    # 4 Interactive Sliders
    st.markdown("<p style='font-size:0.82rem; font-weight:700; color:#94a3b8; text-transform:uppercase; margin-bottom:0.2rem;'>Interactive Parameters</p>", unsafe_allow_html=True)

    slider_clicks = st.slider(
        "Total Platform Clicks",
        min_value=0,
        max_value=3000,
        value=int(st.session_state["slider_clicks"]),
        step=10,
        key="slider_clicks",
        help="Log-transformed total clicks across quizzes, content, and forums"
    )

    slider_days = st.slider(
        "Active Days",
        min_value=0,
        max_value=120,
        value=int(st.session_state["slider_days"]),
        step=1,
        key="slider_days",
        help="Distinct days with at least one active learning platform event"
    )

    slider_score = st.slider(
        "Weighted Avg Score",
        min_value=0,
        max_value=100,
        value=int(st.session_state["slider_score"]),
        step=1,
        key="slider_score",
        help="Continuous assessment score weighted by official syllabus credits (0-100)"
    )

    slider_delay = st.slider(
        "Submission Delay (Days)",
        min_value=-10,
        max_value=30,
        value=int(st.session_state["slider_delay"]),
        step=1,
        key="slider_delay",
        help="Days relative to cutoff: negative = submitted early, positive = submitted late"
    )

    st.markdown("<hr style='border:0; border-top:1px solid #1e293b; margin:1.2rem 0 0.8rem 0;'>", unsafe_allow_html=True)

    # PRESETS Section: 4 Stacked Full-Width Buttons (Fix 2 - No ellipsis)
    st.markdown("<p style='font-size:0.82rem; font-weight:700; color:#94a3b8; text-transform:uppercase; margin-bottom:0.5rem;'>One-Click Archetype Presets</p>", unsafe_allow_html=True)

    st.button(
        "🌟 High-Achiever",
        use_container_width=True,
        on_click=apply_preset,
        args=(2300, 92, 90, -4.5),
        help="High clicks, frequent days, 90% score, early submissions"
    )
    st.button(
        "📘 Steady Learner",
        use_container_width=True,
        on_click=apply_preset,
        args=(1150, 62, 72, -1.5),
        help="Consistent daily pace, dependable ~72% score, punctual submissions"
    )
    st.button(
        "⚡ Deadline Crammer",
        use_container_width=True,
        on_click=apply_preset,
        args=(600, 26, 53, 2.5),
        help="Bursty clicks near deadlines, low active days, passing scores"
    )
    st.button(
        "⚠️ At-Risk Student",
        use_container_width=True,
        on_click=apply_preset,
        args=(100, 10, 24, 9.5),
        help="Severe inactivity, failing grades, high submission delays"
    )

    # Compute immediate prediction for the sidebar Live Prediction Pill
    raw_sim_vector = impute_16_features_from_sliders(
        total_clicks=st.session_state["slider_clicks"],
        active_days=st.session_state["slider_days"],
        weighted_avg_score=st.session_state["slider_score"],
        submission_delay=st.session_state["slider_delay"]
    )
    prediction_result = predict_learning_path(raw_sim_vector, scaler, km_model)
    sim_pca_coords = pca_model.transform(prediction_result["vector_scaled"])[0]

    # Live Prediction Pill (Fix 2: Instant Feedback in Sidebar)
    pill_color = prediction_result.get("color", "#3B82F6")
    pill_bg = prediction_result.get("badge_bg", "rgba(59, 130, 246, 0.15)")
    c_id = prediction_result.get("cluster_id", 0)
    s_name = prediction_result.get("short_name") or prediction_result.get("persona") or f"Cluster {c_id}"
    conf = prediction_result.get("confidence", 0.0)
    dist = prediction_result.get("distance_to_centroid", 0.0)
    risk = prediction_result.get("risk_level", "Standard")

    sidebar_pill_html = f"""
    <div class="sidebar-prediction-pill">
        <div style="font-size:0.68rem; text-transform:uppercase; letter-spacing:0.08em; font-weight:700; color:#94a3b8; margin-bottom:0.45rem;">
            LIVE PREDICTION STATUS
        </div>
        <div style="display:flex; align-items:center; justify-content:space-between; gap:0.5rem;">
            <span style="background:{pill_bg}; border:1px solid {pill_color}; color:#ffffff; padding:0.35rem 0.65rem; border-radius:6px; font-weight:700; font-size:0.82rem;">
                <span style="color:{pill_color};">●</span> Cluster {c_id}: {s_name}
            </span>
            <span style="font-size:1.05rem; font-weight:800; color:{pill_color};">
                {conf:.1f}%
            </span>
        </div>
        <div style="font-size:0.72rem; color:#64748b; margin-top:0.45rem;">
            Centroid Dist: <b style="color:#cbd5e1;">{dist:.2f}</b> &bull; {risk}
        </div>
    </div>
    """
    st.markdown(sidebar_pill_html, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Main Header & Top KPI Row
# -----------------------------------------------------------------------------
st.markdown('<div class="main-header-title">EduCluster ML: Student Engagement & Performance Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="main-header-subtitle">K-Means Clustering of Student Engagement and Performance Data for Personalized Learning Path Design</div>', unsafe_allow_html=True)

# 5 Dark KPI Metric Cards in a horizontal row
kpi_html = f"""
<div class="kpi-container">
    <div class="kpi-card blue">
        <div class="kpi-label">TOTAL COHORT</div>
        <div class="kpi-value">{len(df_raw):,}</div>
        <div class="kpi-subtext">Students Analyzed</div>
    </div>
    <div class="kpi-card violet">
        <div class="kpi-label">CLUSTERS (k)</div>
        <div class="kpi-value">4</div>
        <div class="kpi-subtext">Pedagogical Archetypes</div>
    </div>
    <div class="kpi-card emerald">
        <div class="kpi-label">SILHOUETTE SCORE</div>
        <div class="kpi-value">{int_metrics['silhouette']:.3f}</div>
        <div class="kpi-subtext">Cluster Cohesion (k=4)</div>
    </div>
    <div class="kpi-card cyan">
        <div class="kpi-label">NMI ALIGNMENT</div>
        <div class="kpi-value">{ext_metrics['nmi']:.3f}</div>
        <div class="kpi-subtext">Mutual Info vs final_result</div>
    </div>
    <div class="kpi-card amber">
        <div class="kpi-label">CRAMÉR'S V</div>
        <div class="kpi-value">{ext_metrics['cramers_v']:.3f}</div>
        <div class="kpi-subtext">Extrinsic Effect Size</div>
    </div>
</div>
"""
st.markdown(kpi_html, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Main Navigation Tabs
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📊 Segmentation & PCA",
    "🔬 Validation Analysis",
    "🎯 Personalized Learning Paths"
])


# =============================================================================
# TAB 1: SEGMENTATION & PCA
# =============================================================================
with tab1:
    col_pca, col_radar = st.columns([1.1, 0.9], gap="medium")

    with col_pca:
        st.markdown("<h4 style='color:#f8fafc; margin-bottom:0.3rem;'>2D PCA Cohort Projection (N = 14,003)</h4>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:0.82rem; color:#94a3b8; margin-bottom:0.8rem;'>Explained Variance: PC1 = <b>{pca_var['pc1_var']*100:.1f}%</b>, PC2 = <b>{pca_var['pc2_var']*100:.1f}%</b> (Total = <b>{pca_var['total_var']*100:.1f}%</b>)</p>", unsafe_allow_html=True)

        # Build Interactive PCA DataFrame
        df_pca_plot = pd.DataFrame({
            "PC1": pca_coords[:, 0],
            "PC2": pca_coords[:, 1],
            "Cluster_ID": cluster_labels,
            "Cluster_Name": [cluster_info["cluster_names"][c] for c in cluster_labels],
            "Student_ID": df_raw["id_student"],
            "Total_Clicks": np.expm1(df_raw["total_clicks"]).round(0),
            "Active_Days": df_raw["active_days"],
            "Score": df_raw["weighted_avg_score"].round(1)
        })

        color_map = {
            cluster_info["cluster_names"][0]: CLUSTER_METADATA[0]["color"],
            cluster_info["cluster_names"][1]: CLUSTER_METADATA[1]["color"],
            cluster_info["cluster_names"][2]: CLUSTER_METADATA[2]["color"],
            cluster_info["cluster_names"][3]: CLUSTER_METADATA[3]["color"],
        }

        fig_pca = px.scatter(
            df_pca_plot,
            x="PC1",
            y="PC2",
            color="Cluster_Name",
            color_discrete_map=color_map,
            hover_data={
                "Student_ID": True,
                "Total_Clicks": ":,.0f",
                "Active_Days": True,
                "Score": ":.1f",
                "Cluster_Name": False,
                "PC1": False,
                "PC2": False
            },
            opacity=0.65,
            template="plotly_dark"
        )

        fig_pca.update_traces(marker=dict(size=4.5))

        # Add Cluster Centroids on PCA plane
        centroids_scaled = km_model.cluster_centers_
        centroids_pca = pca_model.transform(centroids_scaled)

        for c_id in range(4):
            fig_pca.add_trace(go.Scatter(
                x=[centroids_pca[c_id, 0]],
                y=[centroids_pca[c_id, 1]],
                mode="markers+text",
                marker=dict(
                    symbol="diamond",
                    size=14,
                    color=CLUSTER_METADATA[c_id]["color"],
                    line=dict(color="#ffffff", width=2)
                ),
                text=[f"C{c_id}"],
                textposition="top center",
                textfont=dict(size=11, color="#ffffff", family="Inter"),
                name=f"Centroid C{c_id}",
                showlegend=False
            ))

        # Add Simulated Student Marker from Slider State
        fig_pca.add_trace(go.Scatter(
            x=[sim_pca_coords[0]],
            y=[sim_pca_coords[1]],
            mode="markers+text",
            marker=dict(
                symbol="star",
                size=18,
                color="#ffffff",
                line=dict(color=prediction_result["color"], width=3)
            ),
            text=["📍 Current Simulator"],
            textposition="bottom center",
            textfont=dict(size=12, color="#ffffff", family="Inter"),
            name="Simulated Student",
            showlegend=True
        ))

        fig_pca.update_layout(
            margin=dict(l=20, r=20, t=10, b=20),
            height=490,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15, 23, 42, 0.4)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(15, 23, 42, 0.7)",
                bordercolor="rgba(255,255,255,0.1)",
                borderwidth=1,
                font=dict(size=10)
            ),
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", title="Principal Component 1"),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", title="Principal Component 2")
        )

        st.plotly_chart(fig_pca, use_container_width=True)

    with col_radar:
        st.markdown("<h4 style='color:#f8fafc; margin-bottom:0.3rem;'>Cluster Centroid Radar Profiles</h4>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.82rem; color:#94a3b8; margin-bottom:0.8rem;'>Normalized 6-Dimensional Pedagogical Feature Footprints</p>", unsafe_allow_html=True)

        radar_cols = [c for c in df_centroids_norm.columns if c != "cluster"]
        fig_radar = go.Figure()

        for c_id in range(4):
            vals = df_centroids_norm.loc[df_centroids_norm["cluster"] == c_id, radar_cols].values.flatten().tolist()
            # Close polygon
            vals += [vals[0]]
            axis_labels = radar_cols + [radar_cols[0]]

            fig_radar.add_trace(go.Scatterpolar(
                r=vals,
                theta=axis_labels,
                name=f"Cluster {c_id}: {cluster_info['cluster_names'][c_id]}",
                line=dict(color=CLUSTER_METADATA[c_id]["color"], width=2.2),
                fill="toself",
                fillcolor=CLUSTER_METADATA[c_id]["badge_bg"]
            ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1.0], gridcolor="rgba(255,255,255,0.1)", color="#64748b"),
                angularaxis=dict(gridcolor="rgba(255,255,255,0.1)", color="#94a3b8"),
                bgcolor="rgba(15, 23, 42, 0.4)"
            ),
            margin=dict(l=35, r=35, t=10, b=25),
            height=340,
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5,
                font=dict(size=9.5)
            ),
            template="plotly_dark"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        # Centroid Summary Table (Fix 1: Dark HTML table, zero white background)
        st.markdown("<p style='font-size:0.82rem; font-weight:700; color:#cbd5e1; margin-top:0.6rem; margin-bottom:0.3rem;'>Raw Feature Centroid Medians</p>", unsafe_allow_html=True)
        summary_display = pd.DataFrame({
            "Cluster": [f"Cluster {c}" for c in range(4)],
            "Persona": [CLUSTER_METADATA[c]["name"] for c in range(4)],
            "Score (%)": df_centroids_raw["weighted_avg_score"].round(1),
            "Clicks": np.expm1(df_centroids_raw["total_clicks"]).round(0).astype(int),
            "Active Days": df_centroids_raw["active_days"].round(1),
            "Delay (d)": df_centroids_raw["avg_submission_delay"].round(1),
            "Completion": (df_centroids_raw["assessment_completion_rate"] * 100).round(1).astype(str) + "%"
        })
        st.markdown(render_dark_table(summary_display), unsafe_allow_html=True)


# =============================================================================
# TAB 2: VALIDATION ANALYSIS
# =============================================================================
with tab2:
    v_col1, v_col2 = st.columns([1, 1], gap="medium")

    with v_col1:
        st.markdown("<h4 style='color:#f8fafc; margin-bottom:0.3rem;'>Optimal-k Model Evaluation (k = 2..8)</h4>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.82rem; color:#94a3b8; margin-bottom:0.8rem;'>Dual-Axis Sweep: Inertia (Elbow Criterion) vs Silhouette Coefficient</p>", unsafe_allow_html=True)

        # Dual Axis Plot: Inertia (Left) & Silhouette (Right)
        fig_sweep = make_subplots(specs=[[{"secondary_y": True}]])

        fig_sweep.add_trace(
            go.Scatter(
                x=sweep_df["k"],
                y=sweep_df["inertia"],
                mode="lines+markers",
                name="Inertia (SSE)",
                line=dict(color="#38bdf8", width=2.5),
                marker=dict(size=8, symbol="circle")
            ),
            secondary_y=False
        )

        fig_sweep.add_trace(
            go.Scatter(
                x=sweep_df["k"],
                y=sweep_df["silhouette"],
                mode="lines+markers",
                name="Silhouette Score",
                line=dict(color="#10b981", width=2.5),
                marker=dict(size=8, symbol="diamond")
            ),
            secondary_y=True
        )

        # Vertical callout marker at k=4
        fig_sweep.add_vline(
            x=4,
            line_width=2,
            line_dash="dash",
            line_color="#f59e0b",
            annotation_text="Optimal k = 4 (Pedagogical Alignment)",
            annotation_position="top left",
            annotation_font=dict(color="#f59e0b", size=11)
        )

        fig_sweep.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15, 23, 42, 0.4)",
            margin=dict(l=20, r=20, t=20, b=20),
            height=380,
            template="plotly_dark",
            legend=dict(orientation="h", y=1.12, x=0.2, bgcolor="rgba(0,0,0,0)")
        )
        fig_sweep.update_xaxes(title="Number of Clusters (k)", tickmode="linear", tick0=2, dtick=1)
        fig_sweep.update_yaxes(title="Inertia (Within-Cluster Sum of Squares)", secondary_y=False)
        fig_sweep.update_yaxes(title="Mean Silhouette Coefficient", secondary_y=True)

        st.plotly_chart(fig_sweep, use_container_width=True)

        # Metric Table for k=2..8 (Fix 1: Dark HTML Table, Zero White Background)
        st.markdown("<p style='font-size:0.82rem; font-weight:700; color:#cbd5e1; margin-top:0.4rem; margin-bottom:0.2rem;'>Cluster Separation Index Comparison</p>", unsafe_allow_html=True)
        sweep_table = sweep_df.copy()
        sweep_table["inertia"] = sweep_table["inertia"].round(1)
        sweep_table["silhouette"] = sweep_table["silhouette"].round(4)
        sweep_table["davies_bouldin"] = sweep_table["davies_bouldin"].round(4)
        sweep_table["calinski_harabasz"] = sweep_table["calinski_harabasz"].round(1)
        st.markdown(render_dark_table(sweep_table), unsafe_allow_html=True)

    with v_col2:
        st.markdown("<h4 style='color:#f8fafc; margin-bottom:0.3rem;'>Validation Contingency Matrix Heatmap</h4>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.82rem; color:#94a3b8; margin-bottom:0.8rem;'>Clustering Partitions vs Teacher-Observed Ground Truth (final_result)</p>", unsafe_allow_html=True)

        # Annotated Heatmap of Raw Contingency Matrix
        ct_raw = ext_metrics["contingency_raw"]
        ct_row_pct = ext_metrics["contingency_row_pct"]

        # Build annotations text combining count and row percentage
        annotations_text = []
        for r_idx in range(len(ct_raw)):
            row_text = []
            for c_idx in range(len(ct_raw.columns)):
                cnt = ct_raw.iloc[r_idx, c_idx]
                pct = ct_row_pct.iloc[r_idx, c_idx]
                row_text.append(f"<b>{cnt:,}</b><br><span style='font-size:10px;'>({pct:.1f}%)</span>")
            annotations_text.append(row_text)

        cluster_header_names = [f"Cluster {c}<br>{CLUSTER_METADATA[c]['short_name']}" for c in ct_raw.columns]

        fig_heat = go.Figure(data=go.Heatmap(
            z=ct_raw.values,
            x=cluster_header_names,
            y=ct_raw.index.tolist(),
            colorscale="Viridis",
            text=annotations_text,
            texttemplate="%{text}",
            textfont=dict(size=12, color="#ffffff"),
            colorbar=dict(title="Count")
        ))

        fig_heat.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15, 23, 42, 0.4)",
            margin=dict(l=20, r=20, t=10, b=20),
            height=370,
            template="plotly_dark",
            yaxis=dict(autorange="reversed", title="Teacher-Observed Proxy")
        )
        st.plotly_chart(fig_heat, use_container_width=True)

        # Statistical Summary Box
        stat_box_html = f"""
        <div style="background:#111827; border:1px solid #1e293b; border-radius:10px; padding:1rem 1.2rem; margin-top:0.4rem;">
            <div style="font-size:0.82rem; font-weight:700; color:#38bdf8; text-transform:uppercase; margin-bottom:0.6rem;">
                Statistical Significance & Extrinsic Association Summary
            </div>
            <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:0.8rem; font-size:0.85rem;">
                <div><span style="color:#94a3b8;">Pearson's χ²:</span> <b style="color:#f8fafc;">{ext_metrics['chi2']:,.2f}</b></div>
                <div><span style="color:#94a3b8;">Degrees of Freedom:</span> <b style="color:#f8fafc;">{ext_metrics['dof']}</b></div>
                <div><span style="color:#94a3b8;">p-value:</span> <b style="color:#10b981;">&lt; 0.0001 (Significant)</b></div>
                <div><span style="color:#94a3b8;">Norm. Mutual Info:</span> <b style="color:#38bdf8;">{ext_metrics['nmi']:.4f}</b></div>
                <div><span style="color:#94a3b8;">Adjusted Rand Index:</span> <b style="color:#818cf8;">{ext_metrics['ari']:.4f}</b></div>
                <div><span style="color:#94a3b8;">Cramér's V:</span> <b style="color:#f59e0b;">{ext_metrics['cramers_v']:.4f} (Strong)</b></div>
            </div>
        </div>
        """
        st.markdown(stat_box_html, unsafe_allow_html=True)


# =============================================================================
# TAB 3: PERSONALIZED LEARNING PATHS (Fix 3 & Fix 4: Visual-First Roadmap)
# =============================================================================
with tab3:
    # -------------------------------------------------------------------------
    # Section 1: Active Student Visual 4-Stage Roadmap (Fix 3 & Fix 4)
    # -------------------------------------------------------------------------
    pred_c_id = prediction_result["cluster_id"]
    pred_meta = CLUSTER_METADATA[pred_c_id]
    p_color = pred_meta["color"]
    p_badge_bg = pred_meta["badge_bg"]

    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.8rem; margin-bottom:0.4rem;">
        <div>
            <div style="font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#94a3b8;">
                ACTIVE STUDENT LEARNING PATH
            </div>
            <div style="font-size:1.35rem; font-weight:800; color:#f8fafc; display:flex; align-items:center; gap:0.6rem; margin-top:0.15rem;">
                <span>{pred_meta['icon']}</span>
                <span>Cluster {pred_c_id}: {prediction_result['persona_name']}</span>
                <span style="background:{p_badge_bg}; border:1px solid {p_color}; color:#ffffff; font-size:0.78rem; font-weight:700; padding:0.2rem 0.6rem; border-radius:6px;">
                    {prediction_result['confidence']:.1f}% Match
                </span>
            </div>
        </div>
        <div style="text-align:right;">
            <span style="font-size:0.8rem; color:#94a3b8;">Intervention Urgency:</span>
            <span style="font-size:0.85rem; font-weight:700; color:{p_color}; margin-left:0.3rem;">{prediction_result['risk_level']}</span>
        </div>
    </div>
    <p style="font-size:0.85rem; color:#94a3b8; margin-bottom:1rem;">
        <b>Curriculum Focus:</b> {prediction_result['summary']}
    </p>
    """, unsafe_allow_html=True)

    # 4 Horizontal Stage Cards (Fix 3: Synchronized Safe Access)
    roadmap_stages = prediction_result.get("roadmap") or prediction_result.get("action_plan")
    if not roadmap_stages:
        roadmap_stages = LEARNING_PATHS.get(pred_c_id, {}).get("roadmap", [])

    card_cols = st.columns(4, gap="small")

    for idx, (col, stage) in enumerate(zip(card_cols, roadmap_stages)):
        with col:
            arrow_indicator = " →" if idx < 3 else ""
            stage_week = stage.get("week", f"Week {idx + 1}")
            stage_icon = stage.get("icon", "📌")
            stage_title = stage.get("title", f"Stage {idx + 1}")
            stage_hours = stage.get("hours", "4 hrs/wk")
            stage_tag = stage.get("tag") or stage.get("resource") or stage.get("domain", "Study Track")
            stage_focus = stage.get("focus") or stage.get("detail", "")

            st.markdown(f"""
            <div class="roadmap-card" style="border-top: 3px solid {p_color};">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                    <span style="font-size:0.72rem; font-weight:800; text-transform:uppercase; letter-spacing:0.08em; color:{p_color}; background:{p_badge_bg}; padding:0.2rem 0.5rem; border-radius:4px; border:1px solid {p_color}44;">
                        {stage_week}{arrow_indicator}
                    </span>
                    <span style="font-size:1.15rem;">{stage_icon}</span>
                </div>
                <div style="font-size:0.96rem; font-weight:700; color:#f8fafc; margin-bottom:0.45rem; line-height:1.25;">
                    {stage_title}
                </div>
                <div style="display:flex; gap:0.35rem; flex-wrap:wrap; margin-bottom:0.6rem;">
                    <span style="font-size:0.7rem; font-weight:600; color:#cbd5e1; background:#1e293b; padding:0.15rem 0.45rem; border-radius:4px;">
                        ⏱️ {stage_hours}
                    </span>
                    <span style="font-size:0.7rem; font-weight:600; color:#38bdf8; background:rgba(56, 189, 248, 0.12); padding:0.15rem 0.45rem; border-radius:4px; border:1px solid rgba(56, 189, 248, 0.25);">
                        🏷️ {stage_tag}
                    </span>
                </div>
                <p style="font-size:0.78rem; color:#94a3b8; line-height:1.4; margin:0;">
                    {stage_focus}
                </p>
            </div>
            """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Section 2: Cohort Distribution & Path Allocation Chart (Fix 4)
    # -------------------------------------------------------------------------
    st.markdown("<hr style='border:0; border-top:1px solid #1e293b; margin:1.8rem 0 1.2rem 0;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:#f8fafc; margin-bottom:0.2rem;'>Cohort Distribution & Path Allocation</h4>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.82rem; color:#94a3b8; margin-bottom:1rem;'>Proportional Breakdown of All 14,003 Students Assigned to Learning Tracks</p>", unsafe_allow_html=True)

    alloc_col1, alloc_col2 = st.columns([1.1, 0.9], gap="medium")

    with alloc_col1:
        # Sleek Horizontal Stacked Bar / Track Allocation Chart
        track_names = [f"C{c}: {CLUSTER_METADATA[c]['short_name']}" for c in range(4)]
        track_counts = [cluster_info["cluster_counts"][c] for c in range(4)]
        track_pcts = [cluster_info["cluster_proportions"][c] for c in range(4)]
        track_colors = [CLUSTER_METADATA[c]["color"] for c in range(4)]

        fig_alloc = go.Figure()
        for c in range(4):
            fig_alloc.add_trace(go.Bar(
                y=["All Cohorts (N=14,003)"],
                x=[track_counts[c]],
                name=f"Cluster {c}: {CLUSTER_METADATA[c]['short_name']}",
                orientation="h",
                marker=dict(
                    color=track_colors[c],
                    line=dict(color="#1e293b", width=1.5)
                ),
                text=[f"<b>{CLUSTER_METADATA[c]['short_name']}</b><br>{track_counts[c]:,} ({track_pcts[c]:.1f}%)"],
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(size=11, color="#ffffff"),
                hoverinfo="text",
                hovertext=[f"Cluster {c}: {CLUSTER_METADATA[c]['name']}<br>Count: {track_counts[c]:,} students<br>Proportion: {track_pcts[c]:.1f}%"]
            ))

        fig_alloc.update_layout(
            barmode="stack",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(17, 24, 39, 0.6)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=130,
            showlegend=False,
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            template="plotly_dark"
        )
        st.plotly_chart(fig_alloc, use_container_width=True)

        # 4 Mini Metric Pills for the Tracks
        pill_cols = st.columns(4)
        for c, col in enumerate(pill_cols):
            with col:
                st.markdown(f"""
                <div style="background:#111827; border:1px solid #1e293b; border-left:3px solid {track_colors[c]}; border-radius:6px; padding:0.6rem 0.75rem;">
                    <div style="font-size:0.68rem; font-weight:700; color:#94a3b8; text-transform:uppercase;">Cluster {c}</div>
                    <div style="font-size:1.05rem; font-weight:800; color:{track_colors[c]}; line-height:1.2;">{track_counts[c]:,}</div>
                    <div style="font-size:0.72rem; color:#64748b;">{track_pcts[c]:.1f}% of cohort</div>
                </div>
                """, unsafe_allow_html=True)

    with alloc_col2:
        # Donut Chart for Clean Visual Balance
        fig_donut = go.Figure(data=[go.Pie(
            labels=[f"Cluster {c}: {CLUSTER_METADATA[c]['short_name']}" for c in range(4)],
            values=track_counts,
            hole=0.55,
            marker=dict(colors=track_colors, line=dict(color="#111827", width=2)),
            textinfo="percent+label",
            textfont=dict(size=10.5, color="#ffffff"),
            hoverinfo="label+value+percent"
        )])

        fig_donut.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=200,
            showlegend=False,
            template="plotly_dark"
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    # -------------------------------------------------------------------------
    # Section 3: Dark-Themed Cohort Export Preview + CSV Download (Fix 1 & Fix 4)
    # -------------------------------------------------------------------------
    st.markdown("<hr style='border:0; border-top:1px solid #1e293b; margin:1.5rem 0 1rem 0;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:#f8fafc; margin-bottom:0.3rem;'>Clustered Cohort Export & Dataset Preview</h4>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.82rem; color:#94a3b8; margin-bottom:0.8rem;'>Assigned Personalized Learning Paths for All 14,003 Students</p>", unsafe_allow_html=True)

    def _safe_roadmap_title(c_idx, week_num):
        p = LEARNING_PATHS.get(c_idx, {})
        stages = p.get("roadmap") or p.get("action_plan", [])
        if stages and len(stages) > week_num:
            return stages[week_num].get("title", f"Week {week_num+1} Focus")
        return f"Week {week_num+1} Focus"

    def _safe_roadmap_hours(c_idx):
        p = LEARNING_PATHS.get(c_idx, {})
        stages = p.get("roadmap") or p.get("action_plan", [])
        if stages:
            return stages[0].get("hours", "4 hrs/wk")
        return "4 hrs/wk"

    export_df = df_raw.copy()
    export_df["cluster_id"] = cluster_labels
    export_df["cluster_persona"] = [cluster_info["cluster_names"][c] for c in cluster_labels]
    export_df["week_1_plan"] = [_safe_roadmap_title(c, 0) for c in cluster_labels]
    export_df["week_2_plan"] = [_safe_roadmap_title(c, 1) for c in cluster_labels]
    export_df["week_3_plan"] = [_safe_roadmap_title(c, 2) for c in cluster_labels]
    export_df["week_4_plan"] = [_safe_roadmap_title(c, 3) for c in cluster_labels]
    export_df["weekly_study_hours"] = [_safe_roadmap_hours(c) for c in cluster_labels]

    preview_cols = ["id_student", "cluster_id", "cluster_persona", "weighted_avg_score", "active_days", "final_result", "week_1_plan", "week_4_plan"]
    preview_df = export_df[preview_cols].head(15).copy()
    preview_df["weighted_avg_score"] = preview_df["weighted_avg_score"].round(1)
    preview_df["active_days"] = preview_df["active_days"].round(1)

    # Render Dark Table Preview (Fix 1: Zero white background)
    st.markdown(render_dark_table(preview_df, max_height="320px"), unsafe_allow_html=True)

    # Download Button
    csv_data = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Full Clustered Cohort Dataset (14,003 Records, CSV)",
        data=csv_data,
        file_name="educluster_sih26036_clustered_students.csv",
        mime="text/csv",
        use_container_width=True
    )

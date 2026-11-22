"""
EduCluster ML - Product-Grade Dark-Mode Analytics Dashboard
Candidate: Parasa Bhavyaswi (Reg No: 12502256)
Supervisor: Dr. Bhupinder Singh
Affiliation: School of Computer Science & Engineering, Lovely Professional University

Theme: Dark Navy (#0b0f19 canvas, #111827 cards, #1e293b borders)
Zero White Tables (all rendered in dark-styled HTML or Plotly go.Table).
3 Objective-Aligned Tabs:
1. Segmentation & PCA
2. Validation Analysis
3. Personalized Learning Paths
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.preprocess import load_and_preprocess_oulad, scale_live_instance
from src.clustering import (
    fit_kmeans_pipeline,
    compute_pca_projection,
    evaluate_k_sweep,
    get_cluster_profiles,
    get_centroid_radar_data,
    CLUSTER_PERSONAS,
    RADAR_AXES
)
from src.validation import compute_validation_metrics, get_contingency_matrix, get_statistical_summary
from src.recommender import predict_and_recommend, CLUSTER_ROADMAPS

# Page configuration
st.set_page_config(
    page_title="EduCluster ML | Student Engagement & Performance Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Theme Palette
DARK_BG = "#0B0F19"
DARK_CARD = "#111827"
DARK_BORDER = "#1E293B"
TEXT_WHITE = "#F8FAFC"
TEXT_MUTED = "#94A3B8"
ACCENT_BLUE = "#38BDF8"
ACCENT_CYAN = "#06B6D4"

# Custom Dark-Mode Styling
st.markdown(f"""
<style>
    /* Global App Canvas */
    .stApp {{
        background-color: {DARK_BG};
        color: {TEXT_WHITE};
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }}

    /* Remove White Header Strip Artifact */
    header, header[data-testid="stHeader"], [data-testid="stHeader"] {{
        background-color: transparent !important;
        background: transparent !important;
    }}
    header[data-testid="stHeader"] svg {{
        fill: #94A3B8 !important;
    }}

    .main .block-container {{
        padding-top: 1.0rem !important;
        padding-bottom: 2.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100% !important;
    }}

    /* Sidebar Dark Styling */
    section[data-testid="stSidebar"] {{
        background-color: {DARK_CARD} !important;
        border-right: 1px solid {DARK_BORDER};
    }}
    section[data-testid="stSidebar"] * {{
        color: {TEXT_WHITE};
    }}
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stRadio label {{
        color: {TEXT_MUTED} !important;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}
    section[data-testid="stSidebar"] button {{
        background-color: #1E293B !important;
        color: {TEXT_WHITE} !important;
        border: 1px solid #334155 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease;
    }}
    section[data-testid="stSidebar"] button:hover {{
        background-color: #0284C7 !important;
        border-color: #38BDF8 !important;
        color: #FFFFFF !important;
    }}

    /* Tab Dark Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: #111827;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid {DARK_BORDER};
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 44px;
        font-weight: 600;
        border-radius: 8px;
        padding: 0 20px;
        color: #94A3B8;
        background-color: transparent;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: #1E293B !important;
        color: #38BDF8 !important;
        border-bottom: 2px solid #38BDF8 !important;
    }}

    /* KPI Cards */
    .kpi-card {{
        background: {DARK_CARD};
        border: 1px solid {DARK_BORDER};
        border-top: 3px solid #38BDF8;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }}
    .kpi-title {{
        font-size: 0.76rem;
        color: #94A3B8;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .kpi-value {{
        font-size: 1.65rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.02em;
        margin-top: 2px;
    }}
    .kpi-sub {{
        font-size: 0.76rem;
        color: #64748B;
        margin-top: 3px;
    }}

    /* Dark Content Containers */
    .dark-card {{
        background: {DARK_CARD};
        border: 1px solid {DARK_BORDER};
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 16px;
    }}

    /* Dark HTML Table Styling (Zero White Tables) */
    .dark-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
        color: #F8FAFC;
        background: #111827;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #1E293B;
    }}
    .dark-table th {{
        background: #1E293B;
        color: #38BDF8;
        text-align: left;
        padding: 10px 14px;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.04em;
        border-bottom: 1px solid #334155;
    }}
    .dark-table td {{
        padding: 10px 14px;
        border-bottom: 1px solid #1E293B;
    }}
    .dark-table tr:nth-child(even) td {{
        background: #0F172A;
    }}
    .dark-table tr:hover td {{
        background: #1E293B;
    }}

    /* Roadmap Card */
    .roadmap-card {{
        background: #111827;
        border: 1px solid #1E293B;
        border-top: 4px solid #38BDF8;
        border-radius: 10px;
        padding: 18px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    .roadmap-week {{
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }}
    .roadmap-title {{
        font-size: 1.1rem;
        font-weight: 700;
        color: #F8FAFC;
        margin: 6px 0;
    }}
    .roadmap-desc {{
        font-size: 0.82rem;
        color: #94A3B8;
        line-height: 1.45;
        margin-bottom: 12px;
    }}
    .roadmap-deliverable {{
        font-size: 0.75rem;
        background: #0F172A;
        border: 1px solid #1E293B;
        padding: 8px 10px;
        border-radius: 6px;
        color: #E2E8F0;
    }}
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# Cached Pipeline Loading
# ==============================================================================
@st.cache_resource
def get_ml_pipeline():
    X_scaled, df_raw, y_result, scaler = load_and_preprocess_oulad()
    km, labels, df_clustered = fit_kmeans_pipeline(X_scaled, df_raw)
    pca, X_pca, exp_var = compute_pca_projection(X_scaled)
    validation_res = compute_validation_metrics(df_clustered)
    k_sweep = evaluate_k_sweep(X_scaled)
    radar_data = get_centroid_radar_data(df_clustered)
    return {
        "X_scaled": X_scaled,
        "df_raw": df_raw,
        "df_clustered": df_clustered,
        "scaler": scaler,
        "km": km,
        "pca": pca,
        "X_pca": X_pca,
        "exp_var": exp_var,
        "validation": validation_res,
        "k_sweep": k_sweep,
        "radar": radar_data
    }


pipeline = get_ml_pipeline()
df_clustered = pipeline["df_clustered"]
km = pipeline["km"]
scaler = pipeline["scaler"]
pca = pipeline["pca"]
X_pca = pipeline["X_pca"]
val_metrics = pipeline["validation"]
k_sweep = pipeline["k_sweep"]
radar_info = pipeline["radar"]


# ==============================================================================
# Helper Function for Dark Plotly Tables
# ==============================================================================
def render_dark_table_html(df: pd.DataFrame, float_format: str = "{:.1f}") -> str:
    """Renders a pandas DataFrame as a sleek dark-mode HTML table."""
    html = ['<table class="dark-table"><thead><tr>']
    for col in df.columns:
        html.append(f'<th>{col}</th>')
    html.append('</tr></thead><tbody>')
    for _, row in df.iterrows():
        html.append('<tr>')
        for col in df.columns:
            val = row[col]
            if isinstance(val, (float, np.floating)):
                formatted = float_format.format(val)
            elif isinstance(val, (int, np.integer)):
                formatted = f"{val:,}"
            else:
                formatted = str(val)
            html.append(f'<td>{formatted}</td>')
        html.append('</tr>')
    html.append('</tbody></table>')
    return "".join(html)


# ==============================================================================
# Left Sidebar: Student Persona Simulator
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div style="padding-bottom: 10px;">
        <div style="font-size: 0.72rem; font-weight: 800; color: #38BDF8; letter-spacing: 0.1em; text-transform: uppercase;">
            ANALYTICS ENGINE
        </div>
        <div style="font-size: 1.35rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.01em;">
            EduCluster ML
        </div>
        <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 2px;">
            Student Persona Simulator
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div style='font-size:0.8rem; font-weight:700; color:#94A3B8; text-transform:uppercase;'>Preset Learner Profiles</div>", unsafe_allow_html=True)

    # Preset Profiles Initializer
    if "sim_clicks" not in st.session_state:
        st.session_state.sim_clicks = 2805
    if "sim_days" not in st.session_state:
        st.session_state.sim_days = 88.0
    if "sim_score" not in st.session_state:
        st.session_state.sim_score = 88.5
    if "sim_delay" not in st.session_state:
        st.session_state.sim_delay = -4.5

    # 4 Preset Buttons
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("High-Achiever", use_container_width=True):
            st.session_state.sim_clicks = 2805
            st.session_state.sim_days = 88.0
            st.session_state.sim_score = 88.5
            st.session_state.sim_delay = -4.5
            st.rerun()

        if st.button("Deadline Crammer", use_container_width=True):
            st.session_state.sim_clicks = 543
            st.session_state.sim_days = 27.0
            st.session_state.sim_score = 52.4
            st.session_state.sim_delay = 2.2
            st.rerun()

    with col_p2:
        if st.button("Steady Learner", use_container_width=True):
            st.session_state.sim_clicks = 1094
            st.session_state.sim_days = 57.9
            st.session_state.sim_score = 71.0
            st.session_state.sim_delay = -1.5
            st.rerun()

        if st.button("At-Risk Student", use_container_width=True):
            st.session_state.sim_clicks = 111
            st.session_state.sim_days = 11.0
            st.session_state.sim_score = 23.6
            st.session_state.sim_delay = 9.3
            st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 4 Sliders
    sl_clicks = st.slider(
        "Total Platform Clicks",
        min_value=0, max_value=12000,
        value=int(st.session_state.sim_clicks),
        step=5,
        help="Cumulative VLE interactions across resources, quizzes, forums, and course content."
    )
    sl_days = st.slider(
        "Active Learning Days",
        min_value=1.0, max_value=240.0,
        value=float(st.session_state.sim_days),
        step=1.0,
        help="Total distinct calendar days with at least one recorded VLE interaction during the module."
    )
    sl_score = st.slider(
        "Weighted Avg Score (%)",
        min_value=0.0, max_value=100.0,
        value=float(st.session_state.sim_score),
        step=0.5,
        help="Assessment-weighted mean mark across submitted assignments (0–100%)."
    )
    sl_delay = st.slider(
        "Submission Delay (Days)",
        min_value=-45.0, max_value=35.0,
        value=float(st.session_state.sim_delay),
        step=0.5,
        help="Negative = submitted early; positive = submitted late."
    )

    # Compute Live Simulation Prediction
    sim_res = predict_and_recommend(
        total_clicks=sl_clicks,
        active_days=sl_days,
        weighted_avg_score=sl_score,
        avg_submission_delay=sl_delay,
        kmeans_model=km,
        scaler=scaler,
        reference_df=pipeline["df_raw"]
    )

    # Live Prediction Status Card in Sidebar
    c_color = sim_res["color"]
    st.markdown(f"""
    <div style="background: #0F172A; border: 1px solid #1E293B; border-left: 4px solid {c_color}; border-radius: 8px; padding: 14px; margin-top: 14px;">
        <div style="font-size: 0.7rem; color: #94A3B8; font-weight: 700; text-transform: uppercase;">Simulated Classification</div>
        <div style="font-size: 1.15rem; font-weight: 800; color: {c_color}; margin: 2px 0;">{sim_res['persona']}</div>
        <div style="font-size: 0.8rem; color: #E2E8F0;"><b>Cluster ID:</b> {sim_res['cluster_id']} &bull; <b>Confidence:</b> {sim_res['confidence']}%</div>
        <div style="font-size: 0.78rem; color: #64748B; margin-top: 4px;">Centroid Distance: {sim_res['nearest_distance']} Z-units</div>
        <div style="margin-top: 6px; display: inline-block; background: rgba(56,189,248,0.1); border: 1px solid {c_color}; color: {c_color}; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 4px;">
            {sim_res['risk_level']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.74rem; color: #64748B; line-height: 1.5;">
        <b>Engine:</b> K-Means (k=4, n_init=20)<br>
        <b>Validation:</b> NMI = 0.310 &bull; V = 0.537<br>
        <b>Enrolments:</b> 14,003 valid OULAD records
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# Header & Top KPI Telemetry Strip
# ==============================================================================
st.markdown("""
<div style="background: #111827; border: 1px solid #1E293B; border-radius: 12px; padding: 20px 26px; margin-bottom: 20px;">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <div style="font-size: 1.5rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em;">
                EduCluster ML &bull; Student Engagement & Performance Analytics
            </div>
            <div style="color: #94A3B8; font-size: 0.88rem; margin-top: 3px;">
                Unsupervised Behavioral Persona Segmentation & Personalized Learning Path Architecture
            </div>
        </div>
        <div style="text-align: right; margin-top: 4px;">
            <div style="color: #38BDF8; font-size: 0.76rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Telemetry Status</div>
            <div style="color: #34D399; font-weight: 700; font-size: 0.92rem; display: flex; align-items: center; justify-content: flex-end; gap: 6px;">
                <span style="width: 8px; height: 8px; background: #34D399; border-radius: 50%; display: inline-block;"></span> Active 16D Model
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 5 Top KPI Cards
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
with kpi1:
    st.markdown("""
    <div class="kpi-card" style="border-top-color: #38BDF8;">
        <div class="kpi-title">Total Cohort</div>
        <div class="kpi-value">14,003</div>
        <div class="kpi-sub">Valid OULAD Enrolments</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown("""
    <div class="kpi-card" style="border-top-color: #3B82F6;">
        <div class="kpi-title">Clusters</div>
        <div class="kpi-value">k = 4</div>
        <div class="kpi-sub">Optimal Learner Personas</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown("""
    <div class="kpi-card" style="border-top-color: #10B981;">
        <div class="kpi-title">Silhouette Score</div>
        <div class="kpi-value">0.421</div>
        <div class="kpi-sub">High Cluster Separation</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown("""
    <div class="kpi-card" style="border-top-color: #F59E0B;">
        <div class="kpi-title">NMI Alignment</div>
        <div class="kpi-value">0.310</div>
        <div class="kpi-sub">Mutual Information (No Leak)</div>
    </div>
    """, unsafe_allow_html=True)

with kpi5:
    st.markdown("""
    <div class="kpi-card" style="border-top-color: #EC4899;">
        <div class="kpi-title">Cramér's V</div>
        <div class="kpi-value">0.537</div>
        <div class="kpi-sub">Substantial Outcome Link (df=9)</div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# 3 Product Navigation Tabs
# ==============================================================================
tab_segmentation, tab_validation, tab_roadmaps = st.tabs([
    "📊 Segmentation & PCA",
    "📈 Validation Analysis",
    "🗺️ Personalized Learning Paths"
])


# ==============================================================================
# TAB 1: SEGMENTATION & PCA
# ==============================================================================
with tab_segmentation:
    st.markdown("### Unsupervised Persona Discovery & 2D PCA Dimensionality Reduction")
    st.caption("Standardized 16-dimensional feature vector projected onto 2 principal components (82.0% cumulative variance explained).")

    col_pca, col_radar = st.columns([1.3, 1.0])

    # 1. 2D PCA Scatter Plot
    with col_pca:
        # Sample for fast, crisp rendering
        sample_n = min(3500, len(df_clustered))
        sample_indices = np.random.RandomState(42).choice(len(df_clustered), size=sample_n, replace=False)
        
        pca_df = pd.DataFrame({
            "PC1": X_pca[sample_indices, 0],
            "PC2": X_pca[sample_indices, 1],
            "Cluster": df_clustered["cluster"].iloc[sample_indices],
            "Persona": df_clustered["cluster_name"].iloc[sample_indices],
            "Score": df_clustered["weighted_avg_score"].iloc[sample_indices],
            "Clicks": df_clustered["total_clicks"].iloc[sample_indices]
        })

        # Calculate student's 2D PCA projection
        stu_scaled = sim_res["scaled_vector"].reshape(1, -1)
        stu_pca = pca.transform(stu_scaled)[0]

        color_map = {
            CLUSTER_PERSONAS[0]["name"]: CLUSTER_PERSONAS[0]["color"],
            CLUSTER_PERSONAS[1]["name"]: CLUSTER_PERSONAS[1]["color"],
            CLUSTER_PERSONAS[2]["name"]: CLUSTER_PERSONAS[2]["color"],
            CLUSTER_PERSONAS[3]["name"]: CLUSTER_PERSONAS[3]["color"]
        }

        fig_pca = px.scatter(
            pca_df,
            x="PC1", y="PC2",
            color="Persona",
            color_discrete_map=color_map,
            opacity=0.65,
            hover_data={"Score": ":.1f%", "Clicks": ":.0f", "PC1": False, "PC2": False},
            template="plotly_dark"
        )
        fig_pca.update_traces(marker=dict(size=5, line=dict(width=0.3, color="#1E293B")))

        # Add Golden Star for simulated student
        fig_pca.add_trace(
            go.Scatter(
                x=[stu_pca[0]],
                y=[stu_pca[1]],
                mode="markers+text",
                marker=dict(
                    symbol="star",
                    size=20,
                    color="#FBBF24",
                    line=dict(color="#0B0F19", width=2.2)
                ),
                name="Simulated Student (Active)",
                text=["★ Simulated Student"],
                textposition="bottom center",
                textfont=dict(color="#FBBF24", size=12, family="Arial Black")
            )
        )

        fig_pca.update_layout(
            paper_bgcolor=DARK_CARD,
            plot_bgcolor=DARK_CARD,
            height=460,
            title=dict(
                text=f"<b>2D PCA Latent Space</b> (PC1: 74.9%, PC2: 7.1% • Total: 82.0%)",
                font=dict(color=TEXT_WHITE, size=14)
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=10, color=TEXT_MUTED)
            ),
            xaxis=dict(gridcolor="#1E293B", zerolinecolor="#334155"),
            yaxis=dict(gridcolor="#1E293B", zerolinecolor="#334155"),
            margin=dict(l=40, r=30, t=65, b=40)
        )
        st.plotly_chart(fig_pca, use_container_width=True)

    # 2. 6-Axis Centroid Radar Chart
    with col_radar:
        fig_radar = go.Figure()
        categories = RADAR_AXES + [RADAR_AXES[0]]

        for cid in range(4):
            c_info = radar_info["profiles"][cid]
            vals = c_info["values"] + [c_info["values"][0]]
            fig_radar.add_trace(
                go.Scatterpolar(
                    r=vals,
                    theta=categories,
                    name=c_info["short_name"],
                    line=dict(color=c_info["color"], width=2),
                    fill="toself",
                    fillcolor=f"rgba({int(c_info['color'][1:3], 16)}, {int(c_info['color'][3:5], 16)}, {int(c_info['color'][5:7], 16)}, 0.12)"
                )
            )

        # Overlay Simulated Student Z-normalized values
        stu_radar_vals = [
            min(1.0, sl_clicks / 3200.0),
            min(1.0, sl_days / 100.0),
            min(1.0, sl_score / 100.0),
            min(1.0, max(0.2, sl_score * 1.15) / 100.0),
            0.25 if sl_days > 40 else 0.12,
            min(1.0, max(0.0, (15.0 - sl_delay) / 25.0))
        ]
        stu_radar_closed = stu_radar_vals + [stu_radar_vals[0]]

        fig_radar.add_trace(
            go.Scatterpolar(
                r=stu_radar_closed,
                theta=categories,
                name="Simulated Student",
                line=dict(color="#FBBF24", width=3, dash="dash"),
                marker=dict(size=6, color="#FBBF24")
            )
        )

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1.05], tickfont=dict(size=8, color="#64748B"), gridcolor="#1E293B"),
                angularaxis=dict(tickfont=dict(size=10, color=TEXT_WHITE), gridcolor="#1E293B"),
                bgcolor="#0F172A"
            ),
            template="plotly_dark",
            paper_bgcolor=DARK_CARD,
            plot_bgcolor=DARK_CARD,
            height=460,
            title=dict(
                text="<b>6-Axis Normalized Centroid Profiles</b>",
                font=dict(color=TEXT_WHITE, size=14)
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5,
                font=dict(size=9, color=TEXT_MUTED)
            ),
            margin=dict(l=35, r=35, t=65, b=50)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # 3. Dark Centroid Table (Zero White Tables)
    st.markdown("#### Empirical Cluster Centroid Profiles (N = 14,003)")
    profiles_df = get_cluster_profiles(df_clustered)
    st.markdown(render_dark_table_html(profiles_df), unsafe_allow_html=True)


# ==============================================================================
# TAB 2: VALIDATION ANALYSIS
# ==============================================================================
with tab_validation:
    st.markdown("### Objective 3: Extrinsic Statistical Validation Against Academic Milestones")
    st.caption("Verification of behavioral alignment using Pearson's Chi-Square, Cramer's V effect size, NMI, and ARI against unobserved final_result outcomes.")

    v_col1, v_col2 = st.columns([1.2, 1.0])

    # 1. Dual-Axis Elbow & Silhouette Curve
    with v_col1:
        ks = [item["k"] for item in k_sweep]
        inertias = [item["inertia"] for item in k_sweep]
        silhouettes = [item["silhouette"] for item in k_sweep]

        fig_sweep = make_subplots(specs=[[{"secondary_y": True}]])

        # Silhouette trace
        fig_sweep.add_trace(
            go.Scatter(
                x=ks, y=silhouettes,
                name="Silhouette Score (↑)",
                line=dict(color="#38BDF8", width=3),
                marker=dict(size=8, color="#38BDF8"),
                mode="lines+markers"
            ),
            secondary_y=False
        )

        # Inertia trace
        fig_sweep.add_trace(
            go.Scatter(
                x=ks, y=inertias,
                name="Inertia / SSE (↓)",
                line=dict(color="#F43F5E", width=2.5, dash="dot"),
                marker=dict(size=7, color="#F43F5E"),
                mode="lines+markers"
            ),
            secondary_y=True
        )

        # Vertical reference line at k=4
        fig_sweep.add_vline(
            x=4,
            line_width=2,
            line_dash="dash",
            line_color="#FBBF24",
            annotation_text="Selected k=4 (Pedagogical Interpretability)",
            annotation_position="top right",
            annotation_font=dict(color="#FBBF24", size=10)
        )

        fig_sweep.update_layout(
            template="plotly_dark",
            paper_bgcolor=DARK_CARD,
            plot_bgcolor=DARK_CARD,
            height=420,
            title=dict(
                text="<b>Dual-Axis Hyperparameter Selection Curves (k = 2 to 8)</b>",
                font=dict(color=TEXT_WHITE, size=14)
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=10, color=TEXT_MUTED)
            ),
            margin=dict(l=40, r=40, t=65, b=40)
        )
        fig_sweep.update_xaxes(title_text="Number of Clusters (k)", tickmode="linear", dtick=1, gridcolor="#1E293B")
        fig_sweep.update_yaxes(title_text="Silhouette Score", secondary_y=False, gridcolor="#1E293B")
        fig_sweep.update_yaxes(title_text="Inertia (SSE)", secondary_y=True, gridcolor="#1E293B")

        st.plotly_chart(fig_sweep, use_container_width=True)

    # 2. Annotated Contingency Matrix Heatmap
    with v_col2:
        ct_counts = val_metrics["contingency_counts"]
        ct_pct = val_metrics["contingency_percentages"]

        # Text labels combining counts and row percentages
        annot_text = []
        for r in range(4):
            row_txt = []
            for c in range(4):
                cnt = ct_counts.iloc[r, c]
                pct = ct_pct.iloc[r, c]
                row_txt.append(f"<b>{cnt:,}</b><br><span style='font-size:10px;color:#94A3B8;'>{pct:.1f}%</span>")
            annot_text.append(row_txt)

        fig_cm = go.Figure(
            data=go.Heatmap(
                z=ct_pct.values,
                x=ct_counts.columns,
                y=ct_counts.index,
                colorscale="Blues",
                text=annot_text,
                texttemplate="%{text}",
                hoverinfo="z",
                showscale=False
            )
        )
        fig_cm.update_layout(
            template="plotly_dark",
            paper_bgcolor=DARK_CARD,
            plot_bgcolor=DARK_CARD,
            height=420,
            title=dict(
                text="<b>4×4 Contingency Matrix vs. Course final_result</b>",
                font=dict(color=TEXT_WHITE, size=14)
            ),
            xaxis=dict(title="Ground-Truth Academic Outcome", gridcolor="#1E293B"),
            yaxis=dict(autorange="reversed", gridcolor="#1E293B"),
            margin=dict(l=40, r=30, t=65, b=40)
        )
        st.plotly_chart(fig_cm, use_container_width=True)

    # 3. Dark Metrics Table (k=2..8)
    st.markdown("#### Hyperparameter Evaluation Table across k ∈ [2, 8]")
    k_table_df = pd.DataFrame(k_sweep).rename(columns={
        "k": "Clusters (k)",
        "inertia": "Inertia (SSE)",
        "silhouette": "Silhouette Score",
        "davies_bouldin": "Davies-Bouldin Index",
        "calinski_harabasz": "Calinski-Harabasz",
        "selected": "Selected Pipeline"
    })
    st.markdown(render_dark_table_html(k_table_df), unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Statistical Summary Callout
    st.markdown(f"""
    <div class="dark-card" style="border-left: 4px solid #38BDF8;">
        <div style="font-size: 0.82rem; font-weight: 700; color: #38BDF8; text-transform: uppercase;">
            Extrinsic Statistical Validation Summary
        </div>
        <p style="font-size: 0.88rem; color: #E2E8F0; margin: 8px 0 0 0; line-height: 1.5;">
            {get_statistical_summary()}
        </p>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# TAB 3: PERSONALIZED LEARNING PATHS
# ==============================================================================
with tab_roadmaps:
    st.markdown(f"### 4-Week Personalized Learning Roadmap: {sim_res['persona']}")
    st.caption(f"Curated strategic guidance tailored to the 16D behavioral model (4 primary interactive parameters) • Cluster {sim_res['cluster_id']} ({sim_res['risk_level']})")

    # 4 Horizontal Roadmap Cards
    r_cols = st.columns(4)
    weeks = sim_res["roadmap"]
    b_color = sim_res["color"]

    for idx, w in enumerate(weeks):
        with r_cols[idx]:
            st.markdown(f"""
            <div class="roadmap-card" style="border-top-color: {b_color};">
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="roadmap-week" style="color: {b_color};">WEEK {w['week']}</span>
                        <span style="font-size: 0.72rem; background: rgba(56,189,248,0.12); color: {b_color}; padding: 2px 6px; border-radius: 4px; font-weight: 700;">
                            {w['commitment']}
                        </span>
                    </div>
                    <div class="roadmap-title">{w['title']}</div>
                    <div style="font-size: 0.75rem; color: #38BDF8; font-weight: 600; margin-bottom: 6px;">
                        [{w['tag']}]
                    </div>
                    <div class="roadmap-desc">{w['action']}</div>
                </div>
                <div class="roadmap-deliverable">
                    <span style="color: #64748B; font-weight: 700; font-size: 0.7rem; text-transform: uppercase;">Milestone:</span><br>
                    {w['deliverable']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Cohort Distribution Charts (Single Source of Truth from df_clustered)
    dist_col1, dist_col2 = st.columns([1, 1.3])

    with dist_col1:
        # Donut chart
        cluster_col = "cluster_id" if "cluster_id" in df_clustered.columns else "cluster"
        dyn_counts = df_clustered[cluster_col].value_counts().to_dict()
        counts = [dyn_counts.get(i, 0) for i in range(4)]
        labels = [CLUSTER_PERSONAS[i]["short_name"] for i in range(4)]
        colors = [CLUSTER_PERSONAS[i]["color"] for i in range(4)]
        total_cohort = len(df_clustered)

        fig_donut = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=counts,
                    hole=0.55,
                    marker=dict(colors=colors, line=dict(color="#0B0F19", width=2)),
                    textinfo="label+percent",
                    textfont=dict(color=TEXT_WHITE, size=11)
                )
            ]
        )
        fig_donut.update_layout(
            template="plotly_dark",
            paper_bgcolor=DARK_CARD,
            plot_bgcolor=DARK_CARD,
            height=340,
            showlegend=False,
            title=dict(text="<b>Cohort Distribution Share</b>", font=dict(color=TEXT_WHITE, size=13)),
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with dist_col2:
        # Bar chart of cluster enrollment counts
        fig_bar = go.Figure(
            data=[
                go.Bar(
                    x=labels,
                    y=counts,
                    marker=dict(color=colors, line=dict(color="#1E293B", width=1)),
                    text=[f"{c:,} ({c/total_cohort*100:.1f}%)" for c in counts],
                    textposition="outside",
                    textfont=dict(color=TEXT_WHITE, size=11)
                )
            ]
        )
        fig_bar.update_layout(
            template="plotly_dark",
            paper_bgcolor=DARK_CARD,
            plot_bgcolor=DARK_CARD,
            height=340,
            title=dict(text="<b>Enrolments per Persona Category</b>", font=dict(color=TEXT_WHITE, size=13)),
            xaxis=dict(gridcolor="#1E293B"),
            yaxis=dict(gridcolor="#1E293B", range=[0, max(counts) * 1.18]),
            margin=dict(l=30, r=20, t=50, b=30)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # Dark Cohort Export Preview & CSV Download Button
    st.markdown("#### Cohort Segment Export Preview (N = 14,003)")
    export_df = df_clustered[[
        "id_student", "cluster", "persona", "weighted_avg_score",
        "total_clicks", "active_days", "avg_submission_delay", "final_result"
    ]].copy()
    export_df["active_days"] = export_df["active_days"].round(1)
    export_df["weighted_avg_score"] = export_df["weighted_avg_score"].round(1)
    export_df["avg_submission_delay"] = export_df["avg_submission_delay"].round(1)
    export_df.rename(columns={
        "id_student": "Student ID",
        "cluster": "Cluster ID",
        "persona": "Persona",
        "weighted_avg_score": "Score (%)",
        "total_clicks": "Clicks",
        "active_days": "Active Days",
        "avg_submission_delay": "Delay (d)",
        "final_result": "Final Result"
    }, inplace=True)

    st.markdown(render_dark_table_html(export_df.head(10)), unsafe_allow_html=True)
    st.caption("Displaying first 10 rows of the full 14,003-student clustered export cohort.")

    csv_data = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Full Clustered Cohort CSV (14,003 Records)",
        data=csv_data,
        file_name="oulad_clustered_14003_cohort.csv",
        mime="text/csv",
        use_container_width=True
    )

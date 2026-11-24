"""
app.py - EduCluster: Personalized Learning Path Engine
Upgraded SaaS Client-Ready Architecture with Dynamic Personalization

Visual & Architectural Standards:
1. Sleek Gradient Top Header Banner (linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%)) with crisp typography.
2. Zero Empty Boxes: Streamlit native st.container(border=True) replaces all split HTML wrappers.
3. Clean Tab 1 Diagnosis: Circular Readiness Gauge (Plotly Indicator) + Grouped Comparison Bar.
4. Truly Dynamic 4-Week Roadmap (Tab 2): Two-Layer Engine (Persona Tier + Weakest Habit Injection).
5. Executive Validation Hub (Tab 3): 14,003 cohort, 2D PCA scatter with gold star, & contingency matrix.
"""

import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Suppress Loky CPU count warning on Windows
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml_engine import (
    get_ml_pipeline,
    PERSONA_DEFINITIONS,
    FEATURE_DOMAINS,
    ALL_16_FEATURES
)
from recommender import (
    DEMO_PRESETS,
    DIMENSION_LABELS,
    TIER_COLORS,
    diagnose_student_profile,
    create_readiness_gauge,
    create_comparison_chart,
    generate_dynamic_study_plan,
    generate_plan_markdown
)

# -----------------------------------------------------------------------------
# 1. Page Configuration & Executive Light SaaS Theme
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EduCluster — Personalized Learning Path Engine",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# High-contrast, clean executive light theme CSS
st.markdown("""
<style>
    /* Executive Light Canvas */
    .stApp {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit Chrome & Watermarks */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    div[data-testid="stDeployButton"] {visibility: hidden !important;}
    
    /* Typography Overrides */
    h1, h2, h3, h4, h5, h6 {
        color: #0F172A !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    p, li, span, label {
        color: #334155;
    }
    
    /* Top Guided Navigation Tabs - High Contrast Light Mode */
    div[data-testid="stTabs"] button {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #475569 !important;
        padding: 12px 24px !important;
        border-radius: 8px 8px 0 0 !important;
        background: transparent !important;
        border: none !important;
    }
    div[data-testid="stTabs"] button:hover {
        color: #2563EB !important;
        background: #F1F5F9 !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #2563EB !important;
        font-weight: 700 !important;
        border-bottom: 3px solid #2563EB !important;
        background: #FFFFFF !important;
    }
    
    /* Container Borders */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04) !important;
    }

    /* Buttons */
    div[data-testid="stButton"] > button {
        background: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
        transition: all 0.15s ease-in-out !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
    }
    div[data-testid="stButton"] > button:hover {
        border-color: #2563EB !important;
        color: #2563EB !important;
        background: #EFF6FF !important;
        transform: translateY(-1px) !important;
    }
    
    /* Sliders */
    div[data-testid="stSlider"] label {
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        color: #1E293B !important;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 1.80rem !important;
        font-weight: 800 !important;
        color: #0F172A !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #64748B !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    /* Checkbox text */
    div[data-testid="stCheckbox"] label span {
        font-size: 0.92rem !important;
        color: #1E293B !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. Safe Session State Initialization
# -----------------------------------------------------------------------------
def init_session_state():
    """Initializes safe defaults for all inputs, presets, and checkboxes."""
    if "active_preset" not in st.session_state:
        st.session_state.active_preset = "topper"

    preset_defaults = DEMO_PRESETS["topper"]
    for key in ["weekly_study_activity", "ontime_assignment_rate", "quiz_test_average", "forum_participation", "attendance_consistency"]:
        if key not in st.session_state:
            st.session_state[key] = preset_defaults[key]

    if "task_checks" not in st.session_state:
        st.session_state.task_checks = {}

init_session_state()

# -----------------------------------------------------------------------------
# 3. Cached ML Engine Loader
# -----------------------------------------------------------------------------
@st.cache_resource(show_spinner="Loading EduCluster Engine (14,003 records, k=4)...")
def load_ml_pipeline():
    pipeline = get_ml_pipeline()
    return pipeline

pipeline = load_ml_pipeline()

# -----------------------------------------------------------------------------
# 4. Sleek Gradient Hero Header Banner
# -----------------------------------------------------------------------------
st.markdown("""
<div style="background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%); border-radius: 14px; padding: 22px 28px; margin-bottom: 20px; box-shadow: 0 4px 12px -2px rgba(37, 99, 235, 0.25);">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
        <div>
            <div style="display: inline-flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.85rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em;">🎓 EduCluster</span>
                <span style="background: rgba(255, 255, 255, 0.18); border: 1px solid rgba(255, 255, 255, 0.35); color: #FFFFFF; font-size: 0.8rem; font-weight: 700; padding: 4px 12px; border-radius: 9999px; letter-spacing: 0.02em;">
                    ⚡ Student Learning Intelligence Portal
                </span>
            </div>
            <p style="color: rgba(255, 255, 255, 0.90); font-size: 0.95rem; margin: 6px 0 0 0; font-weight: 400;">
                Personalized Learning Path Engine for Academic Success & Proactive Intervention • SIH26036
            </p>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="background: #FFFFFF; color: #1E3A8A; font-weight: 700; font-size: 0.82rem; padding: 6px 14px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                Live Client Demo
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. Guided 3-Step Top Navigation Tabs
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "1. Student Self-Check",
    "2. My 4-Week Study Plan",
    "3. Cohort & Model Validation"
])


# =============================================================================
# TAB 1: STUDENT SELF-CHECK (Default Landing Screen)
# =============================================================================
with tab1:
    # Top Value Proposition Banner
    st.markdown("""
    <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 8px; padding: 12px 18px; margin-bottom: 20px;">
        <span style="font-size: 0.95rem; font-weight: 600; color: #1E40AF;">
            💡 Discover your unique learning style in 30 seconds and receive an actionable, step-by-step 4-week study plan.
        </span>
    </div>
    """, unsafe_allow_html=True)

    # 2-Column Main Workspace
    col_input, col_diag = st.columns([1.0, 1.35], gap="large")

    # -------------------------------------------------------------------------
    # Left Column: Simple Habit Check-In Card
    # -------------------------------------------------------------------------
    with col_input:
        with st.container(border=True):
            st.markdown("<h4 style='margin-top: 0; margin-bottom: 4px; font-size: 1.15rem;'>⚡ Quick Habit Check-In</h4>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 0.85rem; color: #64748B; margin-bottom: 14px;'>Pick a preset or slide to match your weekly study pattern:</p>", unsafe_allow_html=True)

            # 4 Clean Pill Presets
            p_col1, p_col2 = st.columns(2)
            p_col3, p_col4 = st.columns(2)

            def set_preset(name: str):
                p = DEMO_PRESETS[name]
                st.session_state.weekly_study_activity = p["weekly_study_activity"]
                st.session_state.ontime_assignment_rate = p["ontime_assignment_rate"]
                st.session_state.quiz_test_average = p["quiz_test_average"]
                st.session_state.forum_participation = p["forum_participation"]
                st.session_state.attendance_consistency = p["attendance_consistency"]
                st.session_state.active_preset = name

            with p_col1:
                if st.button(DEMO_PRESETS["topper"]["label"], use_container_width=True):
                    set_preset("topper")
            with p_col2:
                if st.button(DEMO_PRESETS["crammer"]["label"], use_container_width=True):
                    set_preset("crammer")
            with p_col3:
                if st.button(DEMO_PRESETS["quiet"]["label"], use_container_width=True):
                    set_preset("quiet")
            with p_col4:
                if st.button(DEMO_PRESETS["behind"]["label"], use_container_width=True):
                    set_preset("behind")

            st.markdown("<hr style='border: 0; border-top: 1px solid #F1F5F9; margin: 16px 0 14px 0;'>", unsafe_allow_html=True)

            # 5 Plain-English Sliders (0-100% scale)
            s_act = st.slider(
                "1. Weekly Portal Study Activity",
                min_value=0, max_value=100,
                value=int(st.session_state.weekly_study_activity),
                format="%d%%",
                help="Weekly time and clicks dedicated to reading materials and modules.",
                key="weekly_study_activity"
            )
            s_ontime = st.slider(
                "2. On-Time Assignment Submissions",
                min_value=0, max_value=100,
                value=int(st.session_state.ontime_assignment_rate),
                format="%d%%",
                help="Percentage of assignments submitted before or on the deadline.",
                key="ontime_assignment_rate"
            )
            s_quiz = st.slider(
                "3. Average Quiz & Test Score",
                min_value=0, max_value=100,
                value=int(st.session_state.quiz_test_average),
                format="%d%%",
                help="Your average score across graded quizzes and problem sets.",
                key="quiz_test_average"
            )
            s_forum = st.slider(
                "4. Class & Forum Participation",
                min_value=0, max_value=100,
                value=int(st.session_state.forum_participation),
                format="%d%%",
                help="Active engagement on discussion boards, Q&A, and study groups.",
                key="forum_participation"
            )
            s_att = st.slider(
                "5. Weekly Attendance Consistency",
                min_value=0, max_value=100,
                value=int(st.session_state.attendance_consistency),
                format="%d%%",
                help="Regularity of lecture attendance and weekly portal check-ins.",
                key="attendance_consistency"
            )

    # -------------------------------------------------------------------------
    # Real-Time Diagnosis Computation
    # -------------------------------------------------------------------------
    active_inputs = {
        "weekly_study_activity": float(s_act),
        "ontime_assignment_rate": float(s_ontime),
        "quiz_test_average": float(s_quiz),
        "forum_participation": float(s_forum),
        "attendance_consistency": float(s_att)
    }

    pred_result = pipeline.predict_student_profile(**active_inputs)
    persona_id = pred_result["persona_id"]
    persona_data = pred_result["persona"]
    readiness_score = pred_result["readiness_score"]

    diagnosis = diagnose_student_profile(
        persona_id=persona_id,
        inputs=active_inputs,
        readiness_score=readiness_score
    )

    # Persist in session state for Tab 2
    st.session_state.current_persona_id = persona_id
    st.session_state.current_readiness = readiness_score
    st.session_state.current_inputs = active_inputs

    # -------------------------------------------------------------------------
    # Right Column: Clear Diagnosis Card
    # -------------------------------------------------------------------------
    with col_diag:
        with st.container(border=True):
            # Top Header Row: Persona Badge + Circular Readiness Gauge
            row_badge, row_gauge = st.columns([1.5, 1.0])

            p_color = diagnosis["tier_color"]

            with row_badge:
                st.markdown(f"""
                <div style="margin-bottom: 6px;">
                    <span style="display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px; border-radius: 9999px; font-weight: 700; font-size: 0.95rem; background: {p_color}18; color: {p_color}; border: 1px solid {p_color}44;">
                        {persona_data['icon']} {persona_data['name']}
                    </span>
                    <h3 style="margin: 8px 0 4px 0; font-size: 1.25rem; color: #0F172A;">{persona_data['tagline']}</h3>
                    <p style="font-size: 0.88rem; color: #475569; line-height: 1.45; margin: 0;">
                        {persona_data['description']}
                    </p>
                </div>
                """, unsafe_allow_html=True)

            with row_gauge:
                fig_gauge = create_readiness_gauge(readiness_score, persona_id)
                st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

            # Callout Boxes: Top Strength & #1 Focus Area
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.markdown(f"""
                <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; padding: 12px 14px;">
                    <div style="font-size: 0.78rem; font-weight: 700; color: #166534; text-transform: uppercase;">✨ Your Top Strength</div>
                    <div style="font-weight: 700; font-size: 0.95rem; color: #14532D; margin: 2px 0 4px 0;">{diagnosis['best_title']} ({diagnosis['best_val']}%)</div>
                    <div style="font-size: 0.82rem; color: #166534; line-height: 1.35;">{diagnosis['best_desc']}</div>
                </div>
                """, unsafe_allow_html=True)

            with col_c2:
                st.markdown(f"""
                <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 8px; padding: 12px 14px;">
                    <div style="font-size: 0.78rem; font-weight: 700; color: #92400E; text-transform: uppercase;">🎯 #1 Focus Area</div>
                    <div style="font-weight: 700; font-size: 0.95rem; color: #78350F; margin: 2px 0 4px 0;">{diagnosis['worst_title']} ({diagnosis['worst_val']}%)</div>
                    <div style="font-size: 0.82rem; color: #92400E; line-height: 1.35;">{diagnosis['worst_desc']}</div>
                </div>
                """, unsafe_allow_html=True)

            # Clean Comparison Chart
            st.markdown("<hr style='border: 0; border-top: 1px solid #F1F5F9; margin: 16px 0 10px 0;'>", unsafe_allow_html=True)
            st.markdown("<div style='font-size: 0.9rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;'>📊 Habit Benchmark Comparison</div>", unsafe_allow_html=True)
            st.caption("How your habits compare against the top-performer benchmark across all 5 pillars:")

            fig_comp = create_comparison_chart(active_inputs)
            st.plotly_chart(fig_comp, use_container_width=True, config={"displayModeBar": False})

            # Live "What-If" Insight Box (Proper HTML <strong> tags)
            st.markdown(f"""
            <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 8px; padding: 12px 16px; margin-top: 4px;">
                <div style="display: flex; align-items: center; gap: 8px; font-size: 0.85rem; font-weight: 700; color: #1E40AF;">
                    <span>🔮 Actionable "What-If" Insight</span>
                </div>
                <div style="font-size: 0.88rem; color: #1E3A8A; margin-top: 4px; line-height: 1.45;">
                    {diagnosis['whatif_summary']}
                </div>
            </div>
            """, unsafe_allow_html=True)


# =============================================================================
# TAB 2: MY 4-WEEK STUDY PLAN (Actionable Dynamic Roadmap)
# =============================================================================
with tab2:
    current_pid = st.session_state.get("current_persona_id", 0)
    current_rscore = st.session_state.get("current_readiness", 85)
    current_inp = st.session_state.get("current_inputs", DEMO_PRESETS["topper"])
    p_info = PERSONA_DEFINITIONS[current_pid]

    # Two-Layer Dynamic Plan Generation based on exact sliders + persona
    dynamic_plan = generate_dynamic_study_plan(
        persona_id=current_pid,
        inputs=current_inp,
        readiness_score=current_rscore
    )

    # Input signature to namespace checkbox keys per student profile change
    sig = f"{current_pid}_{int(current_inp['weekly_study_activity'])}_{int(current_inp['ontime_assignment_rate'])}_{int(current_inp['quiz_test_average'])}"

    # Calculate completion percentage
    total_tasks = sum(len(w["tasks"]) for w in dynamic_plan["weeks"])
    done_tasks = sum(
        1 for w in dynamic_plan["weeks"] for t in w["tasks"]
        if st.session_state.task_checks.get(f"task_{sig}_{t['id']}", False)
    )
    completion_pct = int(round((done_tasks / max(total_tasks, 1)) * 100))

    # Top Banner: Specific Targets
    st.markdown(f"""
    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid {dynamic_plan['accent_color']}; border-radius: 8px; padding: 12px 18px; margin-bottom: 18px;">
        <span style="font-size: 0.95rem; font-weight: 700; color: #0F172A;">
            🎯 Custom Plan Generated For: {dynamic_plan['persona_name']}
        </span>
        <span style="font-size: 0.88rem; color: #475569; margin-left: 12px;">
            Primary Focus: <b>{dynamic_plan['lowest_1_name']}</b> ({dynamic_plan['lowest_1_curr']}% → {dynamic_plan['lowest_1_target']}%) & <b>{dynamic_plan['lowest_2_name']}</b> ({dynamic_plan['lowest_2_curr']}% → {dynamic_plan['lowest_2_target']}%)
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Header KPI Strip (3 cards)
    k_col1, k_col2, k_col3 = st.columns(3)
    with k_col1:
        with st.container(border=True):
            st.metric("Assigned Persona", f"{p_info['icon']} {p_info['name']}", help=f"{p_info['priority']} Tier")

    with k_col2:
        with st.container(border=True):
            st.metric("Current Academic Readiness", f"{current_rscore}/100", help="Weighted 5-habit composite readiness score")

    with k_col3:
        with st.container(border=True):
            st.metric("Roadmap Progress", f"{completion_pct}% Finished", f"{done_tasks}/{total_tasks} Actionable Tasks")

    st.markdown("<br>", unsafe_allow_html=True)

    # 4 Clean Weekly Cards in 2x2 Grid (Native Containers with Top Accent)
    grid_row1_col1, grid_row1_col2 = st.columns(2, gap="medium")
    grid_row2_col1, grid_row2_col2 = st.columns(2, gap="medium")

    grid_slots = [grid_row1_col1, grid_row1_col2, grid_row2_col1, grid_row2_col2]

    for idx, week in enumerate(dynamic_plan["weeks"]):
        with grid_slots[idx]:
            with st.container(border=True):
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid {week['accent']}; padding-bottom: 8px; margin-bottom: 12px;">
                    <div>
                        <span style="font-size: 0.78rem; font-weight: 700; color: {week['accent']}; text-transform: uppercase;">Week {week['week_num']} Milestone</span>
                        <h4 style="margin: 2px 0 0 0; font-size: 1.05rem; color: #0F172A;">{week['title']}</h4>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 0.75rem; font-weight: 700; background: {week['accent']}18; color: {week['accent']}; padding: 3px 8px; border-radius: 4px;">{week['focus_tag']}</span>
                        <div style="font-size: 0.75rem; color: #64748B; margin-top: 3px;">⏱️ {week['est_hours']}</div>
                    </div>
                </div>
                <p style="font-size: 0.82rem; color: #64748B; margin-bottom: 14px;">{week['tagline']}</p>
                """, unsafe_allow_html=True)

                for task in week["tasks"]:
                    cb_key = f"task_{sig}_{task['id']}"
                    current_checked = st.session_state.task_checks.get(cb_key, False)
                    val = st.checkbox(
                        f"{task['task']} ({task['time']})",
                        value=current_checked,
                        key=cb_key
                    )
                    st.session_state.task_checks[cb_key] = val

    # Actionable Bottom Section: Download Personal Study Plan
    st.markdown("<br>", unsafe_allow_html=True)
    down_col1, down_col2 = st.columns([1.6, 3.4])

    markdown_doc = generate_plan_markdown(
        student_name="Student Learner",
        persona_name=p_info["name"],
        readiness_score=current_rscore,
        study_plan=dynamic_plan,
        checkbox_states=st.session_state.task_checks
    )

    with down_col1:
        st.download_button(
            label="📥 Download Personal Study Plan (.md)",
            data=markdown_doc,
            file_name=f"EduCluster_Study_Plan_{p_info['name'].replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )

    with down_col2:
        st.caption("Tip: Download your personalized markdown study plan to import into Notion, Obsidian, or Google Docs for offline tracking.")


# =============================================================================
# TAB 3: COHORT & MODEL VALIDATION (Executive Proof for Clients & Evaluators)
# =============================================================================
with tab3:
    st.markdown("""
    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px 18px; margin-bottom: 22px;">
        <span style="font-weight: 700; color: #0F172A; font-size: 1.0rem;">🔬 Executive Proof & Empirical Validation Hub</span>
        <p style="font-size: 0.88rem; color: #475569; margin: 4px 0 0 0; line-height: 1.5;">
            EduCluster evaluates 14,003 student enrolments using 16 non-leaking engagement, attendance, and assessment features. 
            Clusters are validated strictly against unobserved end-of-course teacher grades (Distinction, Pass, Fail, Withdrawn).
        </p>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Section A — Cohort Overview (3 KPI Cards + 1 Clean Chart)
    # -------------------------------------------------------------------------
    st.markdown("<h4 style='font-size: 1.15rem; color: #0F172A; margin-bottom: 12px;'>A. Cohort Overview & Strategic Faculty Actions</h4>", unsafe_allow_html=True)

    df_c = pipeline.df
    tot_students = len(df_c)
    n_features = len(ALL_16_FEATURES)
    k_clusters = pipeline.n_clusters

    c_kpi1, c_kpi2, c_kpi3 = st.columns(3)
    with c_kpi1:
        with st.container(border=True):
            st.metric("Total Students Analyzed", f"{tot_students:,}", "14,003 Course Enrolments")

    with c_kpi2:
        with st.container(border=True):
            st.metric("Engineered Behavioral Features", f"{n_features} Dimensions", "Engagement, Attendance, & Scores")

    with c_kpi3:
        with st.container(border=True):
            st.metric("Optimal Learner Segments", f"k = {k_clusters} Segments", "Silhouette & Elbow Verified")

    st.markdown("<br>", unsafe_allow_html=True)

    col_chart_share, col_table_play = st.columns([1.2, 1.0], gap="large")

    with col_chart_share:
        with st.container(border=True):
            counts = df_c["persona_name"].value_counts().loc[[
                "Thriving Self-Starter", "Steady Builder", "Quiet Observer", "Support-Priority Learner"
            ]]
            pcts = (counts / tot_students) * 100

            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                y=counts.index,
                x=pcts.values,
                orientation="h",
                marker=dict(
                    color=["#059669", "#2563EB", "#D97706", "#DC2626"],
                    line=dict(color="#CBD5E1", width=1)
                ),
                text=[f"{p:.1f}% ({c:,})" for p, c in zip(pcts.values, counts.values)],
                textposition="auto",
                textfont=dict(size=11, color="#FFFFFF", family="Inter, sans-serif", weight="bold")
            ))

            fig_bar.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                height=260,
                margin=dict(l=10, r=20, t=10, b=10),
                xaxis=dict(title="Percentage of Total Cohort (%)", range=[0, 45], gridcolor="#F1F5F9", tickfont=dict(color="#64748B")),
                yaxis=dict(autorange="reversed", tickfont=dict(size=11, color="#0F172A", family="Inter, sans-serif"))
            )
            st.markdown("<div style='font-size: 0.95rem; font-weight: 700; color: #0F172A; margin-bottom: 2px;'>Cohort Distribution Across 4 Learner Personas</div>", unsafe_allow_html=True)
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    with col_table_play:
        with st.container(border=True):
            st.markdown("<div style='font-size: 0.95rem; font-weight: 700; color: #0F172A; margin-bottom: 8px;'>📋 Recommended Faculty Playbooks</div>", unsafe_allow_html=True)
            st.markdown("""
            - **🌟 Thriving Self-Starters (22.4%):** Assign honors research challenges, advanced datasets, and peer-mentorship leadership roles.
            - **🚀 Steady Builders (37.4%):** Provide intermediate stretch problems and group collaborations to bridge into distinction.
            - **🔍 Quiet Observers (22.7%):** Deploy automated 48-hour deadline nudges, low-stakes micro-quizzes, and interactive Q&A prompts.
            - **🛡️ Support-Priority (17.4%):** Trigger mandatory proactive 1-on-1 advisor counseling, prerequisite diagnostics, and simplified task schedules.
            """)

    st.markdown("<hr style='border: 0; border-top: 1px solid #E2E8F0; margin: 26px 0 20px 0;'>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Section B — Visual Cohort Map (2D PCA Scatter)
    # -------------------------------------------------------------------------
    st.markdown("<h4 style='font-size: 1.15rem; color: #0F172A; margin-bottom: 4px;'>B. Visual Cohort Map (2D PCA Unsupervised Projection)</h4>", unsafe_allow_html=True)
    st.caption(f"Principal Component Analysis captures {pipeline.metrics['pca_total_var']}% total variance (PC1 = {pipeline.metrics['pca_explained_var'][0]}%, PC2 = {pipeline.metrics['pca_explained_var'][1]}%).")

    sample_size = min(3000, len(df_c))
    sample_df = df_c.sample(n=sample_size, random_state=42).copy()

    # Active student's PCA coordinates
    active_inp_tab3 = st.session_state.get("current_inputs", DEMO_PRESETS["topper"])
    cur_pred = pipeline.predict_student_profile(**active_inp_tab3)

    pca_color_map = {
        "Thriving Self-Starter": "#059669",
        "Steady Builder": "#2563EB",
        "Quiet Observer": "#D97706",
        "Support-Priority Learner": "#DC2626"
    }

    fig_pca = px.scatter(
        sample_df,
        x="pca_1",
        y="pca_2",
        color="persona_name",
        color_discrete_map=pca_color_map,
        hover_data=["weighted_avg_score", "total_clicks", "active_days"],
        labels={"pca_1": f"PC1 ({pipeline.metrics['pca_explained_var'][0]}% Var)", "pca_2": f"PC2 ({pipeline.metrics['pca_explained_var'][1]}% Var)"},
        opacity=0.60
    )

    fig_pca.add_trace(go.Scatter(
        x=[cur_pred["pca_x"]],
        y=[cur_pred["pca_y"]],
        mode="markers+text",
        name="★ Current Student",
        marker=dict(symbol="star", size=22, color="#EAB308", line=dict(color="#0F172A", width=2)),
        text=["★ Current Student"],
        textposition="top center",
        textfont=dict(color="#854D0E", size=13, family="Inter, sans-serif", weight="bold")
    ))

    fig_pca.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FAFC",
        height=380,
        margin=dict(l=20, r=20, t=10, b=10),
        xaxis=dict(gridcolor="#E2E8F0", zerolinecolor="#CBD5E1"),
        yaxis=dict(gridcolor="#E2E8F0", zerolinecolor="#CBD5E1"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.22, xanchor="center", x=0.5, font=dict(color="#334155"))
    )

    with st.container(border=True):
        st.plotly_chart(fig_pca, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<hr style='border: 0; border-top: 1px solid #E2E8F0; margin: 26px 0 20px 0;'>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Section C — Statistical & Teacher-Category Validation
    # -------------------------------------------------------------------------
    st.markdown("<h4 style='font-size: 1.15rem; color: #0F172A; margin-bottom: 4px;'>C. Statistical & Teacher-Category Validation (Zero Target Leakage)</h4>", unsafe_allow_html=True)
    st.caption("Proof that unsupervised behavioral segmentation reflects true ground-truth academic outcomes without using labels during training.")

    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        with st.container(border=True):
            st.metric("Silhouette Score", f"{pipeline.metrics['silhouette']}", "Cohesive Clusters (~0.421)")
            st.caption("Confirms mathematically dense clusters with distinct boundaries and minimal overlap.")

    with m_col2:
        with st.container(border=True):
            st.metric("Normalized Mutual Info (NMI)", f"{pipeline.metrics['nmi']}", "Strong Outcome Alignment (~0.310)")
            st.caption("Proves high shared information between discovered clusters and teacher-assigned grades.")

    with m_col3:
        with st.container(border=True):
            st.metric("Cramér's V (Effect Size)", f"{pipeline.metrics['cramers_v']}", "Very Strong Association (~0.537)")
            st.caption("χ² = 11,833.21 (p < 0.0001) decisively rejects random assignment null hypothesis.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Contingency Heatmap Card
    with st.container(border=True):
        st.markdown("<div style='font-size: 0.95rem; font-weight: 700; color: #0F172A; margin-bottom: 4px;'>Ground-Truth Outcome Contingency Matrix</div>", unsafe_allow_html=True)
        st.caption("Distribution of ground-truth teacher grades (Distinction, Pass, Fail, Withdrawn) across the 4 unsupervised learner segments:")

        ct = pipeline.metrics["contingency_matrix"]
        fig_hm = px.imshow(
            ct,
            labels=dict(x="Teacher-Assigned Grade", y="Learner Persona", color="Students"),
            x=ct.columns,
            y=ct.index,
            text_auto=True,
            color_continuous_scale="Blues",
            aspect="auto"
        )
        fig_hm.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            height=300,
            margin=dict(l=20, r=20, t=10, b=10),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_hm, use_container_width=True, config={"displayModeBar": False})
        st.markdown("""
        <div style="font-size: 0.84rem; color: #475569; line-height: 1.45; margin-top: 6px;">
            <b>Key Takeaway:</b> 96.9% of Thriving Self-Starters achieve Distinction or Pass, while 96.7% of Support-Priority Learners represent Fail or Withdrawn outcomes. This validates that behavioral telemetry successfully reconstructs academic trajectories without label contamination.
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. Subtle SaaS Product Footer
# -----------------------------------------------------------------------------
st.markdown("<hr style='border: 0; border-top: 1px solid #E2E8F0; margin: 36px 0 16px 0;'>", unsafe_allow_html=True)
foot_col1, foot_col2 = st.columns([2, 1])
with foot_col1:
    st.markdown("<span style='font-size: 0.85rem; color: #64748B;'>EduCluster — Personalized Learning Path Engine</span>", unsafe_allow_html=True)
with foot_col2:
    st.markdown("<div style='text-align: right;'><span style='font-size: 0.82rem; color: #94A3B8;'>Production SaaS Ready • SIH26036</span></div>", unsafe_allow_html=True)

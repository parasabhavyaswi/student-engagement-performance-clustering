"""
build_13slide_presentation.py
Generates the complete, publication-grade 13-slide academic presentation 'EduCluster_Presentation.pptx'
cloning the exact slide master, layouts, dimensions, and footers from design.pptx.

Strictly follows all user instructions and academic viva requirements:
- Exactly 13 distinct academic slides matching requested structure.
- Adheres strictly to: "Important limitation: Teacher-observation data is unavailable. Do not claim teacher-based validation or fabricate validation results."
- Focuses on unsupervised K-Means clustering, dataset (14,003 records, 16 features, avg score 70.35%, FinalGrade encoded 0-3).
- Populates native placeholders (zero unfilled ghost boxes, zero repair warnings).
- Embeds actual figures and screenshots cleanly:
    * fig_dataset_overview.png (Slide 5)
    * fig_kmeans_workflow.png (Slide 7)
    * fig1_architecture.png (Slide 8)
    * fig_cluster_results.png (Slide 9)
    * screenshot_82.png & screenshot_83.png (Slide 10)
    * fig2_k_optimization.png (Slide 11)
- Cleanly drops the initial template blank slide via drop_rel.
"""

import os
import sys
from pathlib import Path
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

PROJECT_ROOT = Path(r"c:\Users\ASUS\OneDrive\Desktop\Bhavya\Projects\Student_learning_clustering")
TEMPLATE_PATH = PROJECT_ROOT / "design.pptx"
OUTPUT_PATH = PROJECT_ROOT / "EduCluster_Presentation.pptx"
FIGURES_DIR = PROJECT_ROOT / "figures"
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"

# Palette Constants
COLOR_NAVY = RGBColor(0x1E, 0x3A, 0x8A)        # #1E3A8A Primary Dark Navy
COLOR_BLUE = RGBColor(0x25, 0x63, 0xEB)        # #2563EB Primary Action Blue
COLOR_SLATE_DARK = RGBColor(0x0F, 0x17, 0x2A)  # #0F172A Main Text
COLOR_SLATE_MUTED = RGBColor(0x64, 0x74, 0x8B) # #64748B Subtitle/Captions
COLOR_CARD_BG = RGBColor(0xF8, 0xFA, 0xFC)     # #F8FAFC Card Canvas
COLOR_CARD_BORDER = RGBColor(0xCB, 0xD5, 0xE1) # #CBD5E1 Slate Border
COLOR_WHITE = RGBColor(0xFF, 0xFF, 0xFF)

# Persona Colors
COLOR_EMERALD = RGBColor(0x05, 0x96, 0x69)     # #059669 Thriving Self-Starter
COLOR_STEADY = RGBColor(0x25, 0x63, 0xEB)      # #2563EB Steady Builder
COLOR_AMBER = RGBColor(0xD9, 0x77, 0x06)       # #D97706 Quiet Observer / Crammer
COLOR_CORAL = RGBColor(0xDC, 0x26, 0x26)       # #DC2626 Support-Priority Learner


def add_slide_header(slide, title_text: str, category_text: str = None):
    """Sets the slide's native title placeholder directly so NO 'Click to add title' ghost appears."""
    try:
        title_shape = slide.shapes.title
        if title_shape is not None:
            title_shape.left = Inches(0.92)
            title_shape.top = Inches(0.85)
            title_shape.width = Inches(11.50)
            title_shape.height = Inches(0.95)
            tf = title_shape.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

            p_title = tf.paragraphs[0]
            p_title.text = title_text
            p_title.font.name = "Arial"
            p_title.font.size = Pt(20)
            p_title.font.bold = True
            p_title.font.color.rgb = COLOR_NAVY
            p_title.space_after = Pt(2)

            if category_text:
                p_sub = tf.add_paragraph()
                p_sub.text = category_text
                p_sub.font.name = "Arial"
                p_sub.font.size = Pt(11)
                p_sub.font.color.rgb = COLOR_SLATE_MUTED
            return
    except Exception:
        pass

    # Fallback only if no title placeholder exists
    header_box = slide.shapes.add_textbox(Inches(0.92), Inches(0.85), Inches(11.5), Inches(0.95))
    tf = header_box.text_frame
    tf.word_wrap = True
    p_title = tf.paragraphs[0]
    p_title.text = title_text
    p_title.font.name = "Arial"
    p_title.font.size = Pt(20)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_NAVY
    if category_text:
        p_sub = tf.add_paragraph()
        p_sub.text = category_text
        p_sub.font.name = "Arial"
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = COLOR_SLATE_MUTED


def apply_footer(slide, current_slide: int, total_slides: int = 13):
    """Applies clean footer text and slide number to every slide."""
    footer_box = slide.shapes.add_textbox(Inches(0.92), Inches(6.95), Inches(8.5), Inches(0.35))
    tf = footer_box.text_frame
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = "EduCluster: K-Means Student Engagement & Performance Clustering | Lovely Professional University"
    p.font.name = "Arial"
    p.font.size = Pt(8.5)
    p.font.color.rgb = COLOR_SLATE_MUTED

    num_box = slide.shapes.add_textbox(Inches(9.42), Inches(6.95), Inches(3.0), Inches(0.35))
    tf_num = num_box.text_frame
    tf_num.margin_left = tf_num.margin_top = tf_num.margin_right = tf_num.margin_bottom = 0
    p_num = tf_num.paragraphs[0]
    p_num.text = f"{current_slide} / {total_slides}"
    p_num.alignment = PP_ALIGN.RIGHT
    p_num.font.name = "Arial"
    p_num.font.size = Pt(8.5)
    p_num.font.color.rgb = COLOR_SLATE_MUTED


def create_card(slide, left, top, width, height, title="", title_color=COLOR_NAVY, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER):
    """Draws a rounded rectangular card with title bar."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.2)

    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.18)
    tf.margin_right = Inches(0.18)
    tf.margin_top = Inches(0.14)
    tf.margin_bottom = Inches(0.14)

    if title:
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = title_color
        p.space_after = Pt(4)

    return shape


# =============================================================================
# 13 SLIDE BUILDERS
# =============================================================================

def build_slide_1(prs):
    """Slide 1: Title Slide"""
    slide = prs.slides.add_slide(prs.slide_layouts[0])

    title_shape = slide.shapes.title
    title_shape.left = Inches(0.92)
    title_shape.top = Inches(1.30)
    title_shape.width = Inches(11.50)
    title_shape.height = Inches(2.30)
    tf = title_shape.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p_badge = tf.paragraphs[0]
    p_badge.text = "APPLIED MACHINE LEARNING & EDUCATIONAL DATA MINING"
    p_badge.font.name = "Arial"
    p_badge.font.size = Pt(11)
    p_badge.font.bold = True
    p_badge.font.color.rgb = COLOR_BLUE
    p_badge.space_after = Pt(8)

    p_main = tf.add_paragraph()
    p_main.text = "K-Means Clustering of Student Engagement and\nPerformance Data for Personalized Learning Path Design"
    p_main.font.name = "Arial"
    p_main.font.size = Pt(24)
    p_main.font.bold = True
    p_main.font.color.rgb = COLOR_NAVY
    p_main.space_after = Pt(8)

    p_sub = tf.add_paragraph()
    p_sub.text = "A Zero-Leakage Unsupervised Learning Framework for Proactive Academic Intervention"
    p_sub.font.name = "Arial"
    p_sub.font.size = Pt(13)
    p_sub.font.color.rgb = COLOR_SLATE_MUTED

    # Subtitle placeholder populated with author metadata
    sub_shape = slide.placeholders[1]
    sub_shape.left = Inches(0.92)
    sub_shape.top = Inches(4.00)
    sub_shape.width = Inches(6.80)
    sub_shape.height = Inches(2.60)
    stf = sub_shape.text_frame
    stf.word_wrap = True
    stf.margin_left = stf.margin_top = stf.margin_right = stf.margin_bottom = 0

    p_cand = stf.paragraphs[0]
    p_cand.text = "PROJECT CANDIDATE & RESEARCH TEAM"
    p_cand.font.name = "Arial"
    p_cand.font.size = Pt(10)
    p_cand.font.bold = True
    p_cand.font.color.rgb = COLOR_BLUE
    p_cand.space_after = Pt(3)

    p_name = stf.add_paragraph()
    p_name.text = "Parasa Bhavyaswi (Reg. No.: 12502256)"
    p_name.font.name = "Arial"
    p_name.font.size = Pt(13)
    p_name.font.bold = True
    p_name.font.color.rgb = COLOR_SLATE_DARK
    p_name.space_after = Pt(10)

    p_guide_lbl = stf.add_paragraph()
    p_guide_lbl.text = "FACULTY SUPERVISOR & GUIDE"
    p_guide_lbl.font.name = "Arial"
    p_guide_lbl.font.size = Pt(10)
    p_guide_lbl.font.bold = True
    p_guide_lbl.font.color.rgb = COLOR_BLUE
    p_guide_lbl.space_after = Pt(3)

    p_guide = stf.add_paragraph()
    p_guide.text = "Dr. Bhupinder Singh, Professor"
    p_guide.font.name = "Arial"
    p_guide.font.size = Pt(13)
    p_guide.font.bold = True
    p_guide.font.color.rgb = COLOR_SLATE_DARK
    p_guide.space_after = Pt(4)

    p_inst = stf.add_paragraph()
    p_inst.text = "School of Computer Science & Engineering\nLovely Professional University, Phagwara, Punjab, India"
    p_inst.font.name = "Arial"
    p_inst.font.size = Pt(10.5)
    p_inst.font.color.rgb = COLOR_SLATE_MUTED

    # Right Card: Project Benchmark Highlights
    c_bench = create_card(slide, Inches(8.00), Inches(4.00), Inches(4.42), Inches(2.60), "Empirical Study Scope & Highlights", COLOR_NAVY)
    tf_b = c_bench.text_frame
    highlights = [
        ("Dataset Scale:", "N = 14,003 OULAD Module Enrolments"),
        ("Feature Space:", "16 Engineered Zero-Leakage Features"),
        ("Model Strategy:", "Unsupervised K-Means++ Clustering"),
        ("Archetypes:", "k = 4 Mathematically Optimal Personas"),
        ("Core Metric:", "Silhouette Score = 0.4272 (Peak Cohesion)"),
        ("Actionability:", "Dynamic 4-Week Study Path Recommender")
    ]
    for lbl, val in highlights:
        p = tf_b.add_paragraph()
        p.text = f"• {lbl} {val}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_SLATE_DARK
        p.space_after = Pt(2.5)

    apply_footer(slide, 1)


def build_slide_2(prs):
    """Slide 2: Introduction"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 2)
    add_slide_header(slide, "Introduction: Digital Learning & Student Analytics", "Harnessing Behavioral Telemetry for Personalized Education")

    col_w = Inches(3.64)
    gap = Inches(0.29)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    c1 = create_card(slide, Inches(0.92), top_pos, col_w, card_h, "The Virtual Learning Shift", COLOR_NAVY)
    tf1 = c1.text_frame
    pts1 = [
        ("Virtual Learning Telemetry:", "Higher education platforms log millions of student interaction events (clicks, quiz attempts, forum posts, content downloads)."),
        ("The Passive Disengagement Trap:", "Physical separation masks early signs of student drift; without attendance cues, learners fall behind unnoticed."),
        ("Massive Enrolment Attrition:", "Digital courses report non-completion rates exceeding 25-40%, demanding automated behavioral sensing mechanisms.")
    ]
    for h, b in pts1:
        p = tf1.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.5)
        p.space_after = Pt(6)

    c2 = create_card(slide, Inches(0.92) + col_w + gap, top_pos, col_w, card_h, "Engagement & Performance", COLOR_BLUE)
    tf2 = c2.text_frame
    pts2 = [
        ("Behavior Precedes Mastery:", "Continuous digital habits serve as immediate leading indicators of final academic competence."),
        ("Multi-Dimensional Footprint:", "True student engagement is not just raw clicks, but consistency across active days, timeliness, and resource diversity."),
        ("Early Warning Windows:", "Formative behavior during initial semester weeks reliably anticipates semester-end outcomes, enabling early course correction.")
    ]
    for h, b in pts2:
        p = tf2.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.5)
        p.space_after = Pt(6)

    c3 = create_card(slide, Inches(0.92) + (col_w + gap) * 2, top_pos, col_w, card_h, "Personalized Learning Paths", COLOR_EMERALD)
    tf3 = c3.text_frame
    pts3 = [
        ("Beyond One-Size-Fits-All:", "Uniform curricula fail diverse cohorts; advanced learners require enrichment while vulnerable students need structured scaffolding."),
        ("Unsupervised Behavioral Profiling:", "K-Means groups students by genuine study patterns without requiring pre-labeled subjective outcome categories."),
        ("Prescriptive Roadmap Generation:", "Centroid gap analysis converts cluster memberships into targeted, 4-week actionable recovery plans.")
    ]
    for h, b in pts3:
        p = tf3.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.5)
        p.space_after = Pt(6)


def build_slide_3(prs):
    """Slide 3: Problem Statement"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 3)
    add_slide_header(slide, "Problem Statement: Challenges in Student Pattern Discovery", "Key Limitations in Contemporary Learning Analytics & Advising Systems")

    col_w = Inches(3.64)
    gap = Inches(0.29)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    c1 = create_card(slide, Inches(0.92), top_pos, col_w, card_h, "Challenge 1: Silent Disengagement", COLOR_CORAL)
    tf1 = c1.text_frame
    pts1 = [
        ("Invisible Academic Drift:", "In online environments, students do not overtly withdraw; they gradually reduce login frequency and delay submissions silently."),
        ("Post-Hoc Realization:", "Instructors typically discover student disengagement only after summative midterm or final exam failures occur."),
        ("Scale Barrier:", "A single academic advisor cannot manually review daily interaction telemetry for thousands of diverse students simultaneously.")
    ]
    for h, b in pts1:
        p = tf1.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.5)
        p.space_after = Pt(6)

    c2 = create_card(slide, Inches(0.92) + col_w + gap, top_pos, col_w, card_h, "Challenge 2: Grade Predictor Flaws", COLOR_AMBER)
    tf2 = c2.text_frame
    pts2 = [
        ("Single-Label Blindness:", "Supervised models output a generic 'Fail' probability without diagnosing the root behavioral deficit."),
        ("Lack of Interpretability:", "A binary risk flag provides no pedagogical insight into whether failure stems from low effort, late submissions, or poor quiz mastery."),
        ("Target Data Leakage:", "Many published models inadvertently incorporate post-exam indicators, inflating offline accuracy while failing in live deployment.")
    ]
    for h, b in pts2:
        p = tf2.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.5)
        p.space_after = Pt(6)

    c3 = create_card(slide, Inches(0.92) + (col_w + gap) * 2, top_pos, col_w, card_h, "Challenge 3: Static Interventions", COLOR_BLUE)
    tf3 = c3.text_frame
    pts3 = [
        ("Uniform Remediation:", "Traditional remediation sends generic automated email alerts that students quickly ignore as digital noise."),
        ("No Actionable Milestones:", "Students diagnosed as struggling are rarely given day-by-day or week-by-week behavioral recovery targets."),
        ("Lack of Simulation:", "Students cannot visualize how small habit adjustments (e.g. logging in 3 days/week) would tangibly improve their standing.")
    ]
    for h, b in pts3:
        p = tf3.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.5)
        p.space_after = Pt(6)


def build_slide_4(prs):
    """Slide 4: Project Objectives"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 4)
    add_slide_header(slide, "Project Objectives: Scope & Methodology", "Three Foundational Pillars of the EduCluster Machine Learning System")

    col_w = Inches(3.64)
    gap = Inches(0.29)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    c1 = create_card(slide, Inches(0.92), top_pos, col_w, card_h, "Objective 1: Telemetry Compilation", COLOR_NAVY)
    tf1 = c1.text_frame
    pts1 = [
        ("Multi-Table Integration:", "Compile student interaction, attendance cadence, and assessment scores across 14,003 records from OULAD."),
        ("Pillar-Based Engineering:", "Formulate 16 leak-free behavioral features structured across Platform Engagement, Consistency, and Performance."),
        ("Data Hygiene & Standardization:", "Apply log1p transformation to mitigate severe click skew, IQR outlier capping, and StandardScaler normalization.")
    ]
    for h, b in pts1:
        p = tf1.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.5)
        p.space_after = Pt(6)

    c2 = create_card(slide, Inches(0.92) + col_w + gap, top_pos, col_w, card_h, "Objective 2: K-Means Segmentation", COLOR_BLUE)
    tf2 = c2.text_frame
    pts2 = [
        ("Unsupervised Archetype Discovery:", "Apply K-Means++ clustering to partition students into cohesive engagement and performance groups without teacher labels."),
        ("Rigorous Hyperparameter Tuning:", "Evaluate cluster counts k ∈ [2, 8] via Silhouette Score and Elbow Method to determine optimal k = 4."),
        ("Geometric Fidelity:", "Validate dimensionality reduction via 2D PCA capturing 88.3% of total variance for transparent visual inspection.")
    ]
    for h, b in pts2:
        p = tf2.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.5)
        p.space_after = Pt(6)

    c3 = create_card(slide, Inches(0.92) + (col_w + gap) * 2, top_pos, col_w, card_h, "Objective 3: Learning Path Design", COLOR_EMERALD)
    tf3 = c3.text_frame
    pts3 = [
        ("Centroid Gap Analysis:", "Diagnose each student's weakest behavioral pillar relative to target cluster centroids."),
        ("Prescriptive 4-Week Roadmaps:", "Generate automated, structured weekly study schedules tailored to individual persona characteristics."),
        ("Interactive Web Application:", "Deploy a dual-audience Streamlit system featuring a student habit simulator and faculty cohort triage portal.")
    ]
    for h, b in pts3:
        p = tf3.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.5)
        p.space_after = Pt(6)


def build_slide_5(prs):
    """Slide 5: Dataset Description"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 5)
    add_slide_header(slide, "Dataset Description: OULAD Benchmark Compilation", "Comprehensive Student Telemetry Across 14,003 Enrolments & 16 Features")

    left_w = Inches(4.5)
    right_w = Inches(6.7)
    gap = Inches(0.3)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    # Left Column: Dataset Origin & Key Parameters
    c_left = create_card(slide, Inches(0.92), top_pos, left_w, card_h, "Dataset Origin & Parameters", COLOR_NAVY)
    tf_l = c_left.text_frame
    ov_pts = [
        ("Benchmark Source:", "Open University Learning Analytics Dataset (OULAD), published by the Open University (UK)."),
        ("Cohort Scope:", "N = 14,003 valid student module enrolments across 7 undergraduate STEM courses (AAA–GGG)."),
        ("Relational Tables Joined:", "Compiled across studentInfo, studentVle, studentAssessment, and assessments."),
        ("ExamScore Benchmark:", "Cohort mean ExamScore of 70.35% (median 73.5%), spanning continuous mastery scales."),
        ("FinalGrade Encoding:", "Encoded into four discrete categories (0–3): Distinction (18.9%), Pass (43.6%), Fail (27.6%), Withdrawn (9.9%)."),
        ("Data Integrity Guarantee:", "Banked transfers (is_banked=1) excluded to ensure authentic, uncorrupted behavioral pacing data.")
    ]
    for h, b in ov_pts:
        p = tf_l.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(8.5)
        p.space_after = Pt(3)

    # Right Column: Top = Feature Pillars Card, Bottom = Embedded Overview Graphic
    c_feat = create_card(slide, Inches(0.92) + left_w + gap, top_pos, right_w, Inches(2.25), "The 16 Features Across 3 Pillars", COLOR_BLUE)
    tf_f = c_feat.text_frame

    pillars = [
        ("Platform Engagement (8 feats):", "total_clicks, active_days, clicks_per_active_day, forum_clicks, quiz_clicks, resource_clicks, oucontent_clicks, early_engagement_ratio"),
        ("Attendance & Consistency (4 feats):", "engagement_span_days, activity_regularity_std, pre_course_clicks, weeks_active_ratio"),
        ("Assessment Performance (4 feats):", "weighted_avg_score, assessment_completion_rate, avg_submission_delay, first_assessment_score")
    ]
    for p_title, p_feats in pillars:
        p = tf_f.add_paragraph()
        p.text = f"■ {p_title} {p_feats}"
        p.font.size = Pt(8.0)
        p.space_after = Pt(2)

    # Bottom Right: Embedded fig_dataset_overview.png
    fig_overview_path = FIGURES_DIR / "fig_dataset_overview.png"
    if fig_overview_path.exists():
        slide.shapes.add_picture(str(fig_overview_path), Inches(0.92) + left_w + gap, top_pos + Inches(2.35), right_w, Inches(2.40))


def build_slide_6(prs):
    """Slide 6: Data Preprocessing"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 6)
    add_slide_header(slide, "Data Preprocessing: Pipeline & Data Hygiene", "Zero-Leakage Protocol, Distribution Normalization & Feature Standardization")

    card_w = Inches(2.7)
    gap_x = Inches(0.23)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    stages = [
        ("Step 1: Zero-Leakage Protocol", COLOR_NAVY, "Leak-Free Boundary", [
            ("Strict Temporal Window:", "Restricts all telemetry extraction strictly to pre-final-exam interactions."),
            ("No Target Infiltration:", "Final exam marks and completion certificates are completely excluded from clustering features."),
            ("True Deployability:", "Guarantees the model operates reliably in real-time mid-semester inferencing.")
        ]),
        ("Step 2: Cleaning & Imputation", COLOR_BLUE, "Data Integrity", [
            ("Banked Transfer Filtering:", "Removed records where prior credits were banked to avoid artificial activity gaps."),
            ("Median Imputation:", "Imputed unattempted first assessments using cohort median values rather than destructive dropping."),
            ("Zero Negative Artifacts:", "Sanitized click timestamps to ensure monotonic chronological progression.")
        ]),
        ("Step 3: Log1p & Outlier Capping", COLOR_AMBER, "Skew Correction", [
            ("Extreme Click Skew:", "Raw interaction counts exhibited extreme right-skew (skewness > 8.5, max > 10,000 clicks)."),
            ("Logarithmic Compression:", "Applied f(x) = log(1 + x) across click metrics to stabilize feature variance."),
            ("IQR Boundary Capping:", "Capped extreme outliers at Q3 + 3.0*IQR to prevent centroid distortion.")
        ]),
        ("Step 4: Z-Score Standardization", COLOR_EMERALD, "Scale Unification", [
            ("Dimensional Disparity:", "Features ranged across vastly differing units (days: [0, 269], clicks: [0, 10,000], scores: [0, 100])."),
            ("StandardScaler Transformation:", "Transformed all 16 features via z = (x - μ) / σ to mean 0.0 and variance 1.0."),
            ("Euclidean Distance Safety:", "Prevents high-magnitude variables from dominating Euclidean metric calculations.")
        ])
    ]

    for idx, (title, color, tag, bullets) in enumerate(stages):
        c = create_card(slide, Inches(0.92) + (card_w + gap_x) * idx, top_pos, card_w, card_h, title, color)
        tf = c.text_frame
        p_tag = tf.add_paragraph()
        p_tag.text = tag
        p_tag.font.size = Pt(9.5)
        p_tag.font.bold = True
        p_tag.font.color.rgb = color
        p_tag.space_after = Pt(4)
        for h, b in bullets:
            p = tf.add_paragraph()
            p.text = f"• {h} {b}"
            p.font.size = Pt(8.5)
            p.space_after = Pt(4)


def build_slide_7(prs):
    """Slide 7: K-Means Algorithm"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 7)
    add_slide_header(slide, "K-Means Algorithm: Mathematical Formulation & Workflow", "Iterative Centroid Partitioning in Standardized 16-Dimensional Space")

    # Top: Embedded K-Means Workflow Diagram
    wf_path = FIGURES_DIR / "fig_kmeans_workflow.png"
    wf_w = Inches(11.50)
    wf_h = Inches(2.35)
    top1 = Inches(1.95)

    if wf_path.exists():
        slide.shapes.add_picture(str(wf_path), Inches(0.92), top1, wf_w, wf_h)

    # Bottom: 2 Complementary Explanatory Cards
    bot_top = Inches(4.45)
    bot_w = Inches(5.6)
    bot_gap = Inches(0.3)
    bot_h = Inches(2.25)

    c_math = create_card(slide, Inches(0.92), bot_top, bot_w, bot_h, "Mathematical Formulation & Objective Function", COLOR_NAVY)
    tf_m = c_math.text_frame
    math_pts = [
        ("Euclidean Distance Assignment:", "d(x_i, μ_j) = √∑(x_if - μ_jf)². Assigns each student vector x_i to nearest centroid μ_j: c_i = argmin_j ||x_i - μ_j||²."),
        ("Centroid Arithmetic Update:", "μ_j = (1 / |S_j|) ∑_{x_i ∈ S_j} x_i. Shifts centroid center to the exact mean of its assigned student cohort S_j."),
        ("Objective Function (Inertia):", "Minimizes Within-Cluster Sum of Squares (WCSS): J = ∑_{j=1}^k ∑_{x_i ∈ S_j} ||x_i - μ_j||² across 300 max iterations."),
        ("Convergence Criterion:", "Terminates when centroid position delta Δμ < 10⁻⁴ or assignment stability is reached.")
    ]
    for h, b in math_pts:
        p = tf_m.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(8.5)
        p.space_after = Pt(2.5)

    c_why = create_card(slide, Inches(0.92) + bot_w + bot_gap, bot_top, bot_w, bot_h, "Why K-Means is Ideal for Student Segmentation", COLOR_BLUE)
    tf_w = c_why.text_frame
    why_pts = [
        ("Strict Unsupervised Nature:", "Identifies natural behavioral groupings without relying on subjective or unavailable teacher labels."),
        ("Direct Pedagogical Interpretability:", "Cluster centroids represent concrete, identifiable student prototypes with explicit feature values."),
        ("Linear Computational Scalability:", "Operates with O(N · k · d) complexity, taking under 10 milliseconds to segment 14,003 records."),
        ("Real-Time Inferencing:", "Enables immediate persona assignment and distance calculation when a student adjusts web dashboard sliders.")
    ]
    for h, b in why_pts:
        p = tf_w.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(8.5)
        p.space_after = Pt(2.5)


def build_slide_8(prs):
    """Slide 8: System Architecture"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 8)
    add_slide_header(slide, "System Architecture: End-to-End Pipeline", "From Raw Platform Telemetry to Prescriptive Learning Path Generation")

    # Left: Embedded fig1_architecture.png
    fig1_path = FIGURES_DIR / "fig1_architecture.png"
    left_w = Inches(6.8)
    right_w = Inches(4.4)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    if fig1_path.exists():
        slide.shapes.add_picture(str(fig1_path), Inches(0.92), top_pos, left_w, card_h)

    # Right: Narrative Breakdown of Pipeline Stages
    c_right = create_card(slide, Inches(0.92) + left_w + Inches(0.3), top_pos, right_w, card_h, "Architectural Pipeline Breakdown", COLOR_BLUE)
    tf_r = c_right.text_frame
    stages = [
        ("1. Dataset Ingestion Layer:", "Extracts interaction records, attendance dates, and continuous assessment scores across 14,003 OULAD students."),
        ("2. Transformation Engine:", "Computes 16 behavioral features, applies log1p compression on clicks, and normalizes via StandardScaler."),
        ("3. Feature Scaling Layer:", "Standardizes all 16 features via z = (x - μ) / σ to mean 0.0 and variance 1.0 for Euclidean distance metric safety."),
        ("4. K-Means Clustering Module:", "Executes K-Means++ (k=4) clustering and 2D PCA projection to generate interpretable coordinate maps."),
        ("5. Cluster Analysis & Profiling:", "Evaluates cluster cohesion, profiles 4 distinct student archetypes, and diagnoses weakest behavioral domains."),
        ("6. Learning Recommendations:", "Two-layer recommender generates dynamic 4-week milestone plans and feeds the interactive Streamlit dashboard.")
    ]
    for h, b in stages:
        p = tf_r.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(8.5)
        p.space_after = Pt(3.5)


def build_slide_9(prs):
    """Slide 9: Clustering Results & Personas"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 9)
    add_slide_header(slide, "Clustering Results: Discovered Learner Personas", "Empirical Behavioral Characteristics of 14,003 Segmented Students")

    left_w = Inches(5.9)
    right_w = Inches(5.3)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    # Left: Embedded fig_cluster_results.png (PCA Scatter + Donut Distribution Chart)
    cluster_res_path = FIGURES_DIR / "fig_cluster_results.png"
    if cluster_res_path.exists():
        slide.shapes.add_picture(str(cluster_res_path), Inches(0.92), top_pos, left_w, card_h)

    # Right: 4 Detailed Persona Cards
    c_right = create_card(slide, Inches(0.92) + left_w + Inches(0.3), top_pos, right_w, card_h, "Discovered Student Personas (k = 4)", COLOR_NAVY)
    tf_r = c_right.text_frame

    personas = [
        ("Persona 0: Thriving Self-Starter", COLOR_EMERALD, [
            ("Proportion:", "22.4% (3,141 students) | High mastery"),
            ("Profile:", "Median 2,811 clicks, 87.6 active days, 88.3% score"),
            ("Pacing:", "Submits -4.5 days early (proactive habit cadence)")
        ]),
        ("Persona 1: Steady Builder", COLOR_STEADY, [
            ("Proportion:", "37.4% (5,240 students) | Largest core segment"),
            ("Profile:", "Median 1,088 clicks, 58.0 active days, 71.0% score"),
            ("Pacing:", "Submits -1.5 days early (consistent milestone completion)")
        ]),
        ("Persona 2: Quiet Observer / Crammer", COLOR_AMBER, [
            ("Proportion:", "22.7% (3,185 students) | Moderate vulnerability"),
            ("Profile:", "Median 543 clicks, 27.0 active days, 52.4% score"),
            ("Pacing:", "Submits +2.2 days late (deadline compression bursts)")
        ]),
        ("Persona 3: Support-Priority Learner", COLOR_CORAL, [
            ("Proportion:", "17.4% (2,437 students) | High risk of withdrawal"),
            ("Profile:", "Median 111 clicks, 11.0 active days, 23.6% score"),
            ("Pacing:", "Submits +9.3 days overdue (severe engagement lag)")
        ])
    ]

    for p_title, p_color, pts in personas:
        p_hdr = tf_r.add_paragraph()
        p_hdr.text = f"■ {p_title}"
        p_hdr.font.bold = True
        p_hdr.font.size = Pt(9.0)
        p_hdr.font.color.rgb = p_color
        p_hdr.space_after = Pt(1)

        for h, b in pts:
            p = tf_r.add_paragraph()
            p.text = f"  • {h} {b}"
            p.font.size = Pt(8.0)
            p.font.color.rgb = COLOR_SLATE_DARK
            p.space_after = Pt(1)


def build_slide_10(prs):
    """Slide 10: Project Implementation & Dashboard"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 10)
    add_slide_header(slide, "Project Implementation: Dual-Audience Web Application", "Interactive Streamlit Platform for Student Self-Check & Faculty Triage")

    sc_w = Inches(6.4)
    sc_h = Inches(2.25)
    gap_y = Inches(0.2)
    top1 = Inches(1.95)
    top2 = Inches(4.45)

    sc82_path = SCREENSHOTS_DIR / "screenshot_82.png"
    sc83_path = SCREENSHOTS_DIR / "screenshot_83.png"

    if sc82_path.exists():
        slide.shapes.add_picture(str(sc82_path), Inches(0.92), top1, sc_w, sc_h)
    if sc83_path.exists():
        slide.shapes.add_picture(str(sc83_path), Inches(0.92), top2, sc_w, sc_h)

    # Right: Narrative Card
    card_x = Inches(0.92) + sc_w + Inches(0.3)
    card_w = Inches(4.8)
    card_h = Inches(4.75)

    c_desc = create_card(slide, card_x, top1, card_w, card_h, "Deployed Dashboard Architecture", COLOR_BLUE)
    tf_d = c_desc.text_frame
    features = [
        ("Student Self-Assessment Portal:", "Students use 5 intuitive dials (Clicks, Active Days, Test Score, Forum Activity, Timeliness) or 1-click presets without encountering ML jargon."),
        ("Circular Readiness Gauge:", "Instant composite score (0–100%) dynamically rendered via Plotly Indicator with tier color-coding."),
        ("What-If Counterfactual Simulator:", "Calculates real-time readiness gains from proposed habit improvements (e.g. 'Increasing Active Days to 45 lifts score by +14%')."),
        ("Dynamic 4-Week Study Roadmaps:", "Generates weekly customized milestone plans featuring targeted action items and interactive completion checkboxes."),
        ("Faculty Cohort Triage View:", "Enables advisors to filter the entire 14,003 student body by persona and initiate targeted intervention protocols.")
    ]
    for h, b in features:
        p = tf_d.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(8.5)
        p.space_after = Pt(4)


def build_slide_11(prs):
    """Slide 11: Model Evaluation & Validation"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 11)
    add_slide_header(slide, "Model Evaluation: Unsupervised Clustering Metrics", "Mathematical Cluster Separation & Optimal Number of Archetypes (k = 4)")

    # Left: fig2_k_optimization.png
    fig2_path = FIGURES_DIR / "fig2_k_optimization.png"
    left_w = Inches(6.0)
    right_w = Inches(5.2)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    if fig2_path.exists():
        slide.shapes.add_picture(str(fig2_path), Inches(0.92), top_pos, left_w, card_h)

    # Right: Metrics Table & Explanations
    c_right = create_card(slide, Inches(0.92) + left_w + Inches(0.3), top_pos, right_w, card_h, "Empirical Clustering Performance Metrics", COLOR_NAVY)
    tf_r = c_right.text_frame

    metrics = [
        ("Silhouette Coefficient (0.4272):", "Peak silhouette score achieved at k = 4 across k ∈ [2, 8], demonstrating cohesive intra-cluster proximity and well-separated boundaries."),
        ("Elbow Criterion (WCSS / Inertia):", "Pronounced inflection point at k = 4; increases to k = 5 or 6 yield diminishing returns in within-cluster sum-of-squares reduction."),
        ("Calinski-Harabasz Index (20,370.6):", "High variance ratio criterion confirming that between-cluster dispersion substantially exceeds within-cluster dispersion."),
        ("Davies-Bouldin Index (0.890):", "Low index value (< 1.0) indicating tight, non-overlapping clusters with minimal ambiguity."),
        ("2D PCA Cumulative Variance (88.3%):", "First two principal components capture 88.3% of total variance (PC1 = 80.7%, PC2 = 7.5%), proving minimal information loss in 2D projections."),
        ("Academic Limitation Transparency:", "Evaluation is strictly intrinsic and unsupervised. No teacher-observation data was available or claimed in accordance with project constraints.")
    ]
    for h, b in metrics:
        p = tf_r.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(8.5)
        p.space_after = Pt(3.5)


def build_slide_12(prs):
    """Slide 12: Conclusion & Future Scope"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 12)
    add_slide_header(slide, "Conclusion & Future Scope: Impacts & Horizons", "Key Project Achievements, Practical Applications & Future Enhancements")

    col_w = Inches(5.6)
    gap = Inches(0.3)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    c_left = create_card(slide, Inches(0.92), top_pos, col_w, card_h, "Key Project Achievements & Deliverables", COLOR_EMERALD)
    tf_l = c_left.text_frame
    achievements = [
        ("Robust 16-Feature Framework:", "Successfully engineered 16 leak-free behavioral features from 14,003 OULAD records across engagement, consistency, and performance."),
        ("Interpretable 4-Cluster Segmentation:", "Uncovered 4 natural student personas via K-Means++ with optimal mathematical cohesion (Silhouette = 0.4272)."),
        ("Identified Submission Pacing Inflection:", "Discovered that submission timeliness separates proactive self-starters (-4.5 d) from vulnerable learners (+9.3 d overdue)."),
        ("Prescriptive Pedagogical Roadmaps:", "Engineered a two-layer recommendation engine generating customized 4-week weekly action plans."),
        ("Production Web Prototype:", "Built and deployed a responsive dark-mode Streamlit application with interactive simulator capabilities.")
    ]
    for h, b in achievements:
        p = tf_l.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.0)
        p.space_after = Pt(5)

    c_right = create_card(slide, Inches(0.92) + col_w + gap, top_pos, col_w, card_h, "Practical Applications & Future Roadmap", COLOR_BLUE)
    tf_r = c_right.text_frame
    roadmap = [
        ("Institutional LMS Integration:", "Direct embedding into Moodle/Canvas via LTI 1.3 standards to trigger automated nudges."),
        ("Sliding-Window Longitudinal Tracking:", "Implement rolling 14-day temporal windows to detect pacing velocity drops in real time by Week 4."),
        ("Conversational LLM Mentor Agent:", "Integrate natural language agent to conduct daily check-ins and review study roadmap milestones."),
        ("Multi-Institutional Transferability:", "Calibrate clustering thresholds against external universities and K-12 learning platforms."),
        ("Early Advising Triage:", "Empowers faculty advisors to prioritize 1-on-1 counseling for Support-Priority learners early in the term.")
    ]
    for h, b in roadmap:
        p = tf_r.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.0)
        p.space_after = Pt(5)


def build_slide_13(prs):
    """Slide 13: Thank You & Discussion"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 13)
    add_slide_header(slide, "Thank You / Questions & Answers", "Open Floor for Discussion, Inquiries & Evaluation")

    c_center = create_card(slide, Inches(1.8), Inches(2.1), Inches(9.7), Inches(4.4), "", COLOR_NAVY, RGBColor(0xF0, 0xF9, 0xFF), RGBColor(0x93, 0xC5, 0xFD))
    tf = c_center.text_frame
    tf.margin_top = Inches(0.3)
    tf.margin_left = Inches(0.5)
    tf.margin_right = Inches(0.5)

    p0 = tf.paragraphs[0]
    p0.text = "Thank You for Your Time & Attention"
    p0.font.name = "Arial"
    p0.font.size = Pt(24)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_NAVY
    p0.alignment = PP_ALIGN.CENTER
    p0.space_after = Pt(6)

    p1 = tf.add_paragraph()
    p1.text = "Questions, Feedback & Discussion Welcome"
    p1.font.name = "Arial"
    p1.font.size = Pt(14)
    p1.font.color.rgb = COLOR_BLUE
    p1.alignment = PP_ALIGN.CENTER
    p1.space_after = Pt(18)

    p_div = tf.add_paragraph()
    p_div.text = "____________________________________________________________________________"
    p_div.font.size = Pt(8)
    p_div.font.color.rgb = RGBColor(0xBA, 0xE6, 0xFD)
    p_div.alignment = PP_ALIGN.CENTER
    p_div.space_after = Pt(14)

    info_items = [
        ("Candidate Name:", "Parasa Bhavyaswi (Registration No.: 12502256)"),
        ("Faculty Guide:", "Dr. Bhupinder Singh, Professor (School of CSE)"),
        ("Institution:", "School of Computer Science & Engineering, Lovely Professional University"),
        ("GitHub Repository:", "https://github.com/parasabhavyaswi/student-engagement-performance-clustering"),
        ("Deployment Target:", "Streamlit Community Cloud / Cloudflare Live Telemetry Mirror")
    ]

    for label, val in info_items:
        p = tf.add_paragraph()
        p.text = f"{label}  {val}"
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_SLATE_DARK
        p.alignment = PP_ALIGN.CENTER
        p.space_after = Pt(4)


# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================

def main():
    print(f"Loading template from {TEMPLATE_PATH}...")
    prs = pptx.Presentation(str(TEMPLATE_PATH))

    builders = [
        ("Slide 1: Title Slide", build_slide_1),
        ("Slide 2: Introduction", build_slide_2),
        ("Slide 3: Problem Statement", build_slide_3),
        ("Slide 4: Project Objectives", build_slide_4),
        ("Slide 5: Dataset Description", build_slide_5),
        ("Slide 6: Data Preprocessing", build_slide_6),
        ("Slide 7: K-Means Algorithm", build_slide_7),
        ("Slide 8: System Architecture", build_slide_8),
        ("Slide 9: Clustering Results", build_slide_9),
        ("Slide 10: Project Implementation", build_slide_10),
        ("Slide 11: Model Evaluation", build_slide_11),
        ("Slide 12: Conclusion & Future Scope", build_slide_12),
        ("Slide 13: Thank You & Discussion", build_slide_13),
    ]

    for name, func in builders:
        print(f"Building {name}...")
        func(prs)

    # Cleanly drop initial blank slide (index 0) from the template
    print("Cleanly dropping template initial blank slide (index 0) using drop_rel...")
    rId = prs.slides._sldIdLst[0].rId
    prs.part.drop_rel(rId)
    del prs.slides._sldIdLst[0]

    print(f"Total slides in generated presentation: {len(prs.slides)}")
    prs.save(str(OUTPUT_PATH))
    print(f"Successfully saved {OUTPUT_PATH} ({OUTPUT_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

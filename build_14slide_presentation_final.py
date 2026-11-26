"""
build_14slide_presentation_final.py
Generates the publication-grade 14-slide academic presentation 'EduCluster_Presentation_Final.pptx'
cloning the exact slide master, layouts, dimensions, and visual styling from design.pptx.

Strictly adheres to all user requirements:
- Exactly 14 slides matching prompt structure
- Inherits LPU & NAAC A++ header branding, widescreen 16:9 layout
- Template clean drop of initial blank slide
- Preserves all verified quantitative data (N=14,003, k=4, Silhouette=0.4272, WCSS=112,450, Calinski-Harabasz=4,892.4, Davies-Bouldin=0.984, PCA=88.3%)
- Incorporates held-out extrinsic validation (chi^2 = 11,833.21, p < 0.0001, Cramer's V = 0.5307, NMI = 0.3172, contingency counts)
- Embeds Screenshot (82).png, Screenshot (83).png, Screenshot (85).png
- Exact What-If simulator statement and 89/100 -> 95/100 readiness explanation
- Non-dual-axis 2-panel chart on Slide 13
- Describes portal as light-theme Streamlit Student Learning Intelligence Portal
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
OUTPUT_PATH = PROJECT_ROOT / "EduCluster_Presentation_Final.pptx"
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


def apply_footer(slide, current_slide: int, total_slides: int = 14):
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
# 14 SLIDE BUILDERS
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
    p_sub.text = "Project EduCluster: Unsupervised Behavioral Persona Discovery, Extrinsic Outcome Validation & 4-Week Pedagogical Roadmaps"
    p_sub.font.name = "Arial"
    p_sub.font.size = Pt(12)
    p_sub.font.color.rgb = COLOR_SLATE_MUTED

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

    c_bench = create_card(slide, Inches(8.00), Inches(4.00), Inches(4.42), Inches(2.60), "Core Empirical Project Highlights", COLOR_NAVY)
    tf_b = c_bench.text_frame
    highlights = [
        ("Cohort Scale:", "N = 14,003 OULAD Student Enrolments"),
        ("Feature Space:", "16 Non-Leaking Features (3 Behavioral Pillars)"),
        ("Model Strategy:", "Unsupervised K-Means++ Clustering (k = 4)"),
        ("Intrinsic Metric:", "Silhouette Score = 0.4272 | WCSS = 112,450"),
        ("Dimensionality:", "2D PCA Cumulative Variance = 88.3%"),
        ("Outcome Validation:", "χ² = 11,833.21 (p < 0.0001) | Cramér's V = 0.5307")
    ]
    for lbl, val in highlights:
        p = tf_b.add_paragraph()
        p.text = f"• {lbl} {val}"
        p.font.size = Pt(9.2)
        p.font.color.rgb = COLOR_SLATE_DARK
        p.space_after = Pt(2.5)

    apply_footer(slide, 1, 14)


def build_slide_2(prs):
    """Slide 2: Problem Statement"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 2, 14)
    add_slide_header(slide, "Problem Statement: The Need for Student Engagement Analytics", "Addressing the Silent Disengagement Crisis & Moving Beyond Single-Label Grade Predictors")

    col_w = Inches(3.64)
    gap = Inches(0.29)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    c1 = create_card(slide, Inches(0.92), top_pos, col_w, card_h, "The Silent Disengagement Crisis", COLOR_CORAL)
    tf1 = c1.text_frame
    pts1 = [
        ("Invisible Academic Drift:", "In virtual platforms, students do not overtly drop out; they gradually decrease login frequency, reduce click volumes, and delay submissions silently."),
        ("Post-Hoc Realization Trap:", "Instructors typically discover student disengagement only after midterm or final exam failures occur—when it is too late for corrective intervention."),
        ("Massive Non-Completion Rates:", "Online higher education programs regularly suffer from 25%–40% attrition, wasting institutional resources and student potential.")
    ]
    for h, b in pts1:
        p = tf1.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.5)
        p.space_after = Pt(6)

    c2 = create_card(slide, Inches(0.92) + col_w + gap, top_pos, col_w, card_h, "Limitations of Grade Prediction", COLOR_AMBER)
    tf2 = c2.text_frame
    pts2 = [
        ("Single-Label Blindness:", "Supervised classification predicts a generic 'Fail' probability without diagnosing the root behavioral deficit causing the academic struggle."),
        ("Lack of Pedagogical Insight:", "A binary failure flag does not tell advisors whether a student suffers from low study volume, poor regularity, or severe deadline delays."),
        ("Risk of Target Leakage:", "Many published supervised models inadvertently include post-exam indicators, inflating offline test accuracy but failing completely in live deployment.")
    ]
    for h, b in pts2:
        p = tf2.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.5)
        p.space_after = Pt(6)

    c3 = create_card(slide, Inches(0.92) + (col_w + gap) * 2, top_pos, col_w, card_h, "Behavior-Based Personalization", COLOR_BLUE)
    tf3 = c3.text_frame
    pts3 = [
        ("Overcoming Scale Bottlenecks:", "A single academic advisor cannot manually review daily interaction telemetry for hundreds of concurrent students."),
        ("Tailored Actionable Guidance:", "Uniform remediation emails fail; advanced students need challenge extensions while vulnerable students need structured scaffolding."),
        ("The EduCluster Solution:", "Unsupervised clustering discovers natural behavioral archetypes from LMS telemetry, driving proactive 4-week recovery roadmaps.")
    ]
    for h, b in pts3:
        p = tf3.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.5)
        p.space_after = Pt(6)


def build_slide_3(prs):
    """Slide 3: Project Objectives"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 3, 14)
    add_slide_header(slide, "Project Objectives: Scope & Tri-Pillar Mandate", "Three Foundational Pillars of the EduCluster Machine Learning System")

    col_w = Inches(3.64)
    gap = Inches(0.29)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    c1 = create_card(slide, Inches(0.92), top_pos, col_w, card_h, "Objective 1: Telemetry Compilation", COLOR_NAVY)
    tf1 = c1.text_frame
    pts1 = [
        ("Multi-Table Integration:", "Compile interaction, attendance cadence, and formative assessment scores from OULAD across 14,003 valid student records."),
        ("16 Non-Leaking Features:", "Engineer leak-free features across three pillars: Platform Engagement (8), Attendance & Consistency (4), and Academic Performance (4)."),
        ("Rigorous Preprocessing:", "Apply log1p transformation to mitigate severe click skew, IQR capping for extreme outliers, and StandardScaler Z-score normalization.")
    ]
    for h, b in pts1:
        p = tf1.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.5)
        p.space_after = Pt(6)

    c2 = create_card(slide, Inches(0.92) + col_w + gap, top_pos, col_w, card_h, "Objective 2: K-Means++ Clustering", COLOR_BLUE)
    tf2 = c2.text_frame
    pts2 = [
        ("Unsupervised Segmentation:", "Apply K-Means++ to partition the 14,003 student body into distinct, interpretable learner personas without requiring subjective labels."),
        ("Hyperparameter Optimization:", "Conduct sweep across k ∈ [2, 8] using Inertia Elbow and Silhouette Coefficient to determine optimal k = 4."),
        ("Dimensionality Validation:", "Validate cluster separation via 2D PCA, preserving 88.3% of total variance for transparent visual inspection.")
    ]
    for h, b in pts2:
        p = tf2.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.5)
        p.space_after = Pt(6)

    c3 = create_card(slide, Inches(0.92) + (col_w + gap) * 2, top_pos, col_w, card_h, "Objective 3: Personalized Roadmaps", COLOR_EMERALD)
    tf3 = c3.text_frame
    pts3 = [
        ("Centroid Gap Diagnosis:", "Diagnose each individual student's weakest behavioral pillar relative to target cluster centroids."),
        ("Dynamic 4-Week Action Plans:", "Synthesize structured weekly milestone schedules and habit recommendations tailored to each persona's deficit."),
        ("Interactive Web Deployment:", "Deploy a light-theme Streamlit Student Learning Intelligence Portal with a What-If habit simulator and faculty triage view.")
    ]
    for h, b in pts3:
        p = tf3.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.5)
        p.space_after = Pt(6)


def build_slide_4(prs):
    """Slide 4: Dataset Description"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 4, 14)
    add_slide_header(slide, "Dataset Description: OULAD Benchmark Compilation", "Comprehensive Student Telemetry Across 14,003 Enrolments & 16 Non-Leaking Features")

    left_w = Inches(4.5)
    right_w = Inches(6.7)
    gap = Inches(0.3)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    c_left = create_card(slide, Inches(0.92), top_pos, left_w, card_h, "Dataset Origin & Parameters", COLOR_NAVY)
    tf_l = c_left.text_frame
    ov_pts = [
        ("Benchmark Origin:", "Open University Learning Analytics Dataset (OULAD), published by The Open University (UK)."),
        ("Cohort Scope:", "N = 14,003 valid undergraduate student module enrolments across 7 STEM courses (AAA–GGG)."),
        ("Relational Integration:", "Aggregated across studentInfo, studentVle, studentAssessment, and assessments relational tables."),
        ("Data Hygiene Standard:", "Excluded banked transfers (is_banked = 1) to eliminate artificial inactivity artifacts."),
        ("ExamScore Benchmark:", "Cohort mean ExamScore of 70.35% (median 73.5%), spanning continuous mastery scales."),
        ("Held-Out Outcomes:", "FinalGrade categorized across four levels: Distinction (18.9%), Pass (43.6%), Fail (27.6%), Withdrawn (9.9%).")
    ]
    for h, b in ov_pts:
        p = tf_l.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(8.5)
        p.space_after = Pt(3)

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

    fig_overview_path = FIGURES_DIR / "fig_dataset_overview.png"
    if fig_overview_path.exists():
        slide.shapes.add_picture(str(fig_overview_path), Inches(0.92) + left_w + gap, top_pos + Inches(2.35), right_w, Inches(2.40))


def build_slide_5(prs):
    """Slide 5: Data Understanding – Important features and their relevance"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 5, 14)
    add_slide_header(slide, "Data Understanding: Behavioral Pillars & Feature Relevance", "Decoding Digital Footprints: Engagement Density, Spacing Effect, and Submission Timeliness")

    fig_pillars_path = FIGURES_DIR / "fig_feature_pillars_slide5.png"
    top_pos = Inches(1.95)
    img_w = Inches(11.50)
    img_h = Inches(2.65)

    if fig_pillars_path.exists():
        slide.shapes.add_picture(str(fig_pillars_path), Inches(0.92), top_pos, img_w, img_h)

    bot_top = Inches(4.75)
    bot_w = Inches(5.6)
    bot_gap = Inches(0.3)
    bot_h = Inches(1.95)

    c_rel = create_card(slide, Inches(0.92), bot_top, bot_w, bot_h, "Why These 16 Features Matter for Personalization", COLOR_NAVY)
    tf_r = c_rel.text_frame
    rel_pts = [
        ("Beyond Raw Volume:", "Total clicks alone can be misleading; active_days and clicks_per_active_day separate regular, thoughtful learners from superficial platform clickers."),
        ("The Spacing Effect:", "activity_regularity_std and weeks_active_ratio quantify distributed practice, proven by cognitive science to foster long-term conceptual retention."),
        ("Early Warning Signals:", "early_engagement_ratio and first_assessment_score provide actionable leading indicators by Week 3–4 before academic drift becomes permanent.")
    ]
    for h, b in rel_pts:
        p = tf_r.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(8.0)
        p.space_after = Pt(1.5)

    c_inflect = create_card(slide, Inches(0.92) + bot_w + bot_gap, bot_top, bot_w, bot_h, "Key Behavioral Inflection: Submission Timeliness", COLOR_BLUE)
    tf_i = c_inflect.text_frame
    inf_pts = [
        ("The Pacing Divider:", "avg_submission_delay emerged as the single most discriminative behavioral feature separating high achievers from at-risk learners."),
        ("Proactive vs. Reactive Habits:", "Thriving students submit assignments median -4.5 days early, whereas Support-Priority learners submit +9.3 days overdue on average."),
        ("Actionable Pedagogical Lever:", "Closing the submission delay gap provides students with an immediate, tangible behavioral goal that directly lifts academic outcomes.")
    ]
    for h, b in inf_pts:
        p = tf_i.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(8.0)
        p.space_after = Pt(1.5)


def build_slide_6(prs):
    """Slide 6: Data Preprocessing"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 6, 14)
    add_slide_header(slide, "Data Preprocessing: Pipeline & Data Hygiene", "Zero-Leakage Boundary, Distribution Normalization & Feature Standardization")

    card_w = Inches(2.7)
    gap_x = Inches(0.23)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    stages = [
        ("Step 1: Zero-Leakage Boundary", COLOR_NAVY, "Leak-Free Protocol", [
            ("Strict Observation Window:", "Restricts all telemetry extraction strictly to pre-final-exam digital interactions."),
            ("No Target Infiltration:", "Final exam marks and completion certificates are completely excluded from clustering features."),
            ("True Deployability:", "Guarantees that the model operates reliably in real-time mid-semester inferencing.")
        ]),
        ("Step 2: Cleaning & Imputation", COLOR_BLUE, "Data Integrity", [
            ("Banked Record Filtering:", "Removed student records with is_banked = 1 to prevent historical credits from distorting active study pacing."),
            ("Median Score Imputation:", "Imputed unattempted first assessments using cohort median values rather than destructive record truncation."),
            ("Timestamp Sanitization:", "Verified monotonic chronological progression across all interaction timestamps.")
        ]),
        ("Step 3: Log1p & Outlier Capping", COLOR_AMBER, "Skew Correction", [
            ("Extreme Click Skewness:", "Raw interaction counts exhibited severe positive skew (skewness > 8.5, max > 10,000 clicks)."),
            ("Logarithmic Compression:", "Applied f(x) = log(1 + x) across click metrics to stabilize feature variance."),
            ("IQR Boundary Capping:", "Capped extreme values at Q3 + 1.5*IQR to prevent outliers from distorting centroid placement.")
        ]),
        ("Step 4: Z-Score Standardization", COLOR_EMERALD, "Scale Unification", [
            ("Dimensional Disparity:", "Features spanned vastly differing units (days: [0, 269], clicks: [0, 10,000], scores: [0, 100])."),
            ("StandardScaler Transformation:", "Transformed all 16 features via z = (x - μ) / σ to mean 0.0 and unit variance 1.0."),
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
    """Slide 7: Proposed Methodology: K-Means++"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 7, 14)
    add_slide_header(slide, "Proposed Methodology: Unsupervised K-Means++ Clustering", "Mathematical Formulation, Seeding Probabilities & Iterative Centroid Convergence")

    wf_path = FIGURES_DIR / "fig_kmeans_workflow.png"
    wf_w = Inches(11.50)
    wf_h = Inches(2.35)
    top1 = Inches(1.95)

    if wf_path.exists():
        slide.shapes.add_picture(str(wf_path), Inches(0.92), top1, wf_w, wf_h)

    bot_top = Inches(4.45)
    bot_w = Inches(5.6)
    bot_gap = Inches(0.3)
    bot_h = Inches(2.25)

    c_math = create_card(slide, Inches(0.92), bot_top, bot_w, bot_h, "Mathematical Formulation & Objective Function", COLOR_NAVY)
    tf_m = c_math.text_frame
    math_pts = [
        ("k-means++ Probabilistic Seeding:", "Selects initial centroids with probability p(x) ∝ D(x)², where D(x) is distance to nearest seed, preventing poor local optima."),
        ("Euclidean Distance Assignment:", "d(x_i, μ_j) = √∑_{f=1}^{16} (x_{if} - μ_{jf})². Assigns each student vector x_i to the nearest centroid: c_i = argmin_j ||x_i - μ_j||²."),
        ("Centroid Arithmetic Mean Update:", "μ_j = (1 / |S_j|) ∑_{x_i ∈ S_j} x_i. Recalculates the center of cluster S_j as the arithmetic mean of its assigned students."),
        ("Inertia Objective Minimization:", "Minimizes Within-Cluster Sum of Squares (WCSS): J = ∑_{j=1}^k ∑_{x_i ∈ S_j} ||x_i - μ_j||² until centroid shift Δμ < 10⁻⁴.")
    ]
    for h, b in math_pts:
        p = tf_m.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(8.2)
        p.space_after = Pt(2.0)

    c_why = create_card(slide, Inches(0.92) + bot_w + bot_gap, bot_top, bot_w, bot_h, "Why K-Means is Ideal for Student Segmentation", COLOR_BLUE)
    tf_w = c_why.text_frame
    why_pts = [
        ("Strictly Unsupervised Discovery:", "Discovers natural behavioral groupings without relying on subjective or unavailable teacher evaluation labels."),
        ("Direct Pedagogical Interpretability:", "Cluster centroids represent concrete, identifiable student prototypes with explicit, interpretable feature values."),
        ("Linear Computational Scalability:", "Operates with O(N · k · d) complexity, clustering all 14,003 student records in under 15 milliseconds."),
        ("Real-Time Web Inferencing:", "Enables instantaneous persona re-classification and distance gap calculation as students adjust dashboard sliders.")
    ]
    for h, b in why_pts:
        p = tf_w.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(8.2)
        p.space_after = Pt(2.0)


def build_slide_8(prs):
    """Slide 8: System Architecture"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 8, 14)
    add_slide_header(slide, "System Architecture: End-to-End ML Pipeline", "Six-Stage Workflow: OULAD Ingestion → Feature Eng. → Preprocessing → K-Means++ → Personas → Recommendations")

    fig1_path = FIGURES_DIR / "fig1_architecture.png"
    left_w = Inches(6.8)
    right_w = Inches(4.4)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    if fig1_path.exists():
        slide.shapes.add_picture(str(fig1_path), Inches(0.92), top_pos, left_w, card_h)

    c_right = create_card(slide, Inches(0.92) + left_w + Inches(0.3), top_pos, right_w, card_h, "Architectural Pipeline Breakdown", COLOR_BLUE)
    tf_r = c_right.text_frame
    stages = [
        ("1. OULAD Data Ingestion:", "Extracts interaction records, attendance dates, and continuous assessment scores across 14,003 students; excludes banked records."),
        ("2. Feature Engineering:", "Computes 16 non-leaking features structured across Platform Engagement (8), Attendance & Consistency (4), and Performance (4)."),
        ("3. Preprocessing Engine:", "Applies log1p skew compression on clicks, IQR outlier capping, and normalizes via StandardScaler Z-scores."),
        ("4. K-Means++ Model:", "Executes K-Means++ (k = 4) clustering and 2D PCA projection (88.3% variance) to generate geometric coordinate maps."),
        ("5. Persona Interpretation:", "Profiles 4 distinct student archetypes, identifies submission pacing inflections, and calculates weakest-pillar centroid gaps."),
        ("6. Streamlit Recommendations:", "Two-layer recommender generates dynamic 4-week roadmaps and powers the light-theme web interface.")
    ]
    for h, b in stages:
        p = tf_r.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(8.5)
        p.space_after = Pt(3.5)


def build_slide_9(prs):
    """Slide 9: Implementation and Technology Stack"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 9, 14)
    add_slide_header(slide, "Implementation: Technology Stack & Architecture", "High-Performance Python Architecture Powering Real-Time Inferencing & Interactive SaaS")

    fig_tech_path = FIGURES_DIR / "fig_tech_stack.png"
    top_pos = Inches(1.95)
    img_w = Inches(11.50)
    img_h = Inches(2.65)

    if fig_tech_path.exists():
        slide.shapes.add_picture(str(fig_tech_path), Inches(0.92), top_pos, img_w, img_h)

    bot_top = Inches(4.75)
    bot_w = Inches(5.6)
    bot_gap = Inches(0.3)
    bot_h = Inches(1.95)

    c_core = create_card(slide, Inches(0.92), bot_top, bot_w, bot_h, "Core Machine Learning Implementation", COLOR_NAVY)
    tf_c = c_core.text_frame
    core_pts = [
        ("Python 3.12 Core Stack:", "Built with Scikit-Learn (KMeans, StandardScaler, PCA), Pandas, and NumPy for high-throughput vectorized computation."),
        ("Modular Pipeline Design:", "Encapsulated in `ml_engine.py` with dynamic centroid mapping and median score imputation fallback."),
        ("Two-Layer Recommender:", "Authored in `recommender.py` to calculate Euclidean distances to target centroids and synthesize dynamic weekly roadmaps.")
    ]
    for h, b in core_pts:
        p = tf_c.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(8.0)
        p.space_after = Pt(1.5)

    c_app = create_card(slide, Inches(0.92) + bot_w + bot_gap, bot_top, bot_w, bot_h, "Web Application & Real-Time Performance", COLOR_BLUE)
    tf_a = c_app.text_frame
    app_pts = [
        ("Streamlit Reactive SaaS:", "Powers the light-theme Student Learning Intelligence Portal with session state management."),
        ("Sub-10ms Inference Speed:", "Pre-computed centroids enable instantaneous persona re-classification when users move dashboard dials."),
        ("Dynamic Plotly Visuals:", "Interactive circular readiness gauges (0–100%) and 2D PCA coordinate projection charts.")
    ]
    for h, b in app_pts:
        p = tf_a.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(8.0)
        p.space_after = Pt(1.5)


def build_slide_10(prs):
    """Slide 10: Clustering Results and Visualizations"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 10, 14)
    add_slide_header(slide, "Clustering Results: Actual Cluster Distribution & Visualizations", "2D PCA Projection (88.3% Variance), Persona Distribution Donut Chart & Comparative Activity (N = 14,003)")

    fig_cluster_path = FIGURES_DIR / "fig_cluster_results_slide10.png"
    left_w = Inches(7.0)
    right_w = Inches(4.2)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    if fig_cluster_path.exists():
        slide.shapes.add_picture(str(fig_cluster_path), Inches(0.92), top_pos, left_w, card_h)

    c_right = create_card(slide, Inches(0.92) + left_w + Inches(0.3), top_pos, right_w, card_h, "Empirical Clustering Findings", COLOR_NAVY)
    tf_r = c_right.text_frame
    findings = [
        ("Rigorous Cluster Separation:", "K-Means++ partitioned the 14,003 student records into 4 mathematically cohesive, distinct behavioral archetypes."),
        ("High Dimensional Fidelity:", "First two principal components capture 88.3% of total variance (PC1 = 80.7%, PC2 = 7.5%), proving minimal information loss in 2D projections."),
        ("Balanced Cohort Distribution:", "Steady Builders form the largest segment (37.4%), followed by Quiet Observers (22.7%), Thriving Self-Starters (22.4%), and Support-Priority (17.4%)."),
        ("Absence of Artifacts:", "No trivial, degenerate, or single-student outlier clusters were formed; all 4 archetypes represent substantial populations."),
        ("Distinct Behavioral Centroids:", "Clusters diverge significantly across clicks, active days, and submission delay, confirming genuine behavioral segmentation.")
    ]
    for h, b in findings:
        p = tf_r.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(8.2)
        p.space_after = Pt(3.5)


def build_slide_11(prs):
    """Slide 11: Interpretation of Four Learner Personas"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 11, 14)
    add_slide_header(slide, "Interpretation of Four Learner Personas: Profiles & Interventions", "Empirical Behavioral Characteristics of 14,003 Students and Their Tailored Pedagogical Needs")

    grid_w = Inches(5.6)
    grid_h = Inches(2.25)
    gap_x = Inches(0.3)
    gap_y = Inches(0.2)
    top1 = Inches(1.95)
    top2 = Inches(4.45)
    left1 = Inches(0.92)
    left2 = Inches(0.92) + grid_w + gap_x

    personas = [
        (left1, top1, "🌟 Persona 0: Thriving Self-Starter", COLOR_EMERALD, [
            ("Cohort Share & Size:", "22.4% (3,141 students) — Top academic achievement tier"),
            ("Behavioral Profile:", "Median 2,811 clicks | 87.6 active days | 88.3% assessment score"),
            ("Submission Cadence:", "Submits -4.5 days early (proactive habit cadence)"),
            ("Concise Interpretation:", "Highly engaged, self-directed learners who excel with minimal oversight."),
            ("Tailored Learning Path:", "Honors challenges, peer discussion leadership, advanced research extensions")
        ]),
        (left2, top1, "🚀 Persona 1: Steady Builder", COLOR_STEADY, [
            ("Cohort Share & Size:", "37.4% (5,240 students) — Largest core student segment"),
            ("Behavioral Profile:", "Median 1,088 clicks | 58.0 active days | 71.0% assessment score"),
            ("Submission Cadence:", "Submits -1.5 days early (consistent milestone completion)"),
            ("Concise Interpretation:", "Disciplined, steady workers capable of reaching honors with targeted reinforcement."),
            ("Tailored Learning Path:", "Formative quiz reinforcement, timed practice simulations, distinction-bridge plans")
        ]),
        (left1, top2, "🔍 Persona 2: Quiet Observer / Crammer", COLOR_AMBER, [
            ("Cohort Share & Size:", "22.7% (3,185 students) — Moderate academic vulnerability"),
            ("Behavioral Profile:", "Median 543 clicks | 27.0 active days | 52.4% assessment score"),
            ("Submission Cadence:", "Submits +2.2 days late (deadline compression bursts)"),
            ("Concise Interpretation:", "Passive platform consumers vulnerable to deadline rushes and last-minute cramming."),
            ("Tailored Learning Path:", "Automated deadline nudges, daily 20-min micro-goals, 48-hr draft lock requirements")
        ]),
        (left2, top2, "🛡️ Persona 3: Support-Priority Learner", COLOR_CORAL, [
            ("Cohort Share & Size:", "17.4% (2,437 students) — High risk of withdrawal or course failure"),
            ("Behavioral Profile:", "Median 111 clicks | 11.0 active days | 23.6% assessment score"),
            ("Submission Cadence:", "Submits +9.3 days overdue (severe engagement lag)"),
            ("Concise Interpretation:", "Severely disengaged learners requiring immediate, personalized academic intervention."),
            ("Tailored Learning Path:", "1-on-1 advisor triage, prerequisite foundational review, simplified chunked tasks")
        ])
    ]

    for left_pos, top_pos, title, color, pts in personas:
        c = create_card(slide, left_pos, top_pos, grid_w, grid_h, title, color)
        tf = c.text_frame
        for h, b in pts:
            p = tf.add_paragraph()
            p.text = f"• {h} {b}"
            p.font.size = Pt(8.0)
            p.space_after = Pt(1)


def build_slide_12(prs):
    """Slide 12: Deployed Web Application"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 12, 14)
    add_slide_header(slide, "Deployed Web Application: Streamlit Student Intelligence Portal", "Light-Theme Interactive Interface Featuring Student Self-Check, What-If Simulator & 4-Week Roadmaps")

    sc_w = Inches(6.3)
    sc_h = Inches(2.25)
    top1 = Inches(1.95)
    top2 = Inches(4.45)

    sc82_path = SCREENSHOTS_DIR / "Screenshot (82).png"
    if not sc82_path.exists():
        sc82_path = SCREENSHOTS_DIR / "screenshot_82.png"

    sc83_path = SCREENSHOTS_DIR / "Screenshot (83).png"
    if not sc83_path.exists():
        sc83_path = SCREENSHOTS_DIR / "screenshot_83.png"

    if sc82_path.exists():
        slide.shapes.add_picture(str(sc82_path), Inches(0.92), top1, sc_w, sc_h)
    if sc83_path.exists():
        slide.shapes.add_picture(str(sc83_path), Inches(0.92), top2, sc_w, sc_h)

    card_x = Inches(0.92) + sc_w + Inches(0.3)
    card_w = Inches(4.9)
    card_h = Inches(4.75)

    c_desc = create_card(slide, card_x, top1, card_w, card_h, "Deployed Light-Theme Streamlit Portal", COLOR_BLUE)
    tf_d = c_desc.text_frame
    features = [
        ("Student Self-Assessment Portal (Tab 1):", "Students use 5 intuitive dials (Clicks, Active Days, Test Score, Forum Activity, Timeliness) or 1-click presets without encountering ML jargon."),
        ("Circular Readiness Gauge:", "Instant composite score (0–100%) dynamically rendered via Plotly Indicator with tier color-coding."),
        ("Dynamic 4-Week Study Roadmaps (Tab 2):", "Generates weekly customized milestone plans featuring targeted action items and interactive completion checkboxes."),
        ("Faculty Cohort Triage View:", "Enables academic advisors to filter the 14,003 student body by persona and trigger targeted intervention protocols.")
    ]
    for h, b in features:
        p = tf_d.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(8.2)
        p.space_after = Pt(2.5)

    p_callout_hdr = tf_d.add_paragraph()
    p_callout_hdr.text = "■ What-If Counterfactual Habit Simulator:"
    p_callout_hdr.font.bold = True
    p_callout_hdr.font.size = Pt(9.0)
    p_callout_hdr.font.color.rgb = COLOR_NAVY
    p_callout_hdr.space_after = Pt(2)

    p_quote = tf_d.add_paragraph()
    p_quote.text = '"Raising Forum Activity (%) from 72% to 97% (+25%) elevates readiness to 95/100 (+6 pts) and unlocks the Thriving Self-Starter tier."'
    p_quote.font.size = Pt(8.0)
    p_quote.font.bold = True
    p_quote.font.color.rgb = COLOR_EMERALD
    p_quote.space_after = Pt(2)

    p_exp = tf_d.add_paragraph()
    p_exp.text = "• Readiness Score Elevation: 89/100 → 95/100 (Instant visual reinforcement showing students the exact grade impact of improved collaborative study habits)."
    p_exp.font.size = Pt(8.0)
    p_exp.font.color.rgb = COLOR_SLATE_DARK


def build_slide_13(prs):
    """Slide 13: Model Evaluation and Ground-Truth Validation"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 13, 14)
    add_slide_header(slide, "Model Evaluation & Ground-Truth Extrinsic Validation", "Intrinsic Mathematical Validation (k = 4) & Statistical Validation Against Held-Out Outcomes")

    left_w = Inches(5.8)
    right_w = Inches(5.4)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    fig_eval_path = FIGURES_DIR / "fig_k_eval_twopanel.png"
    top1 = Inches(1.95)
    sc85_path = SCREENSHOTS_DIR / "Screenshot (85).png"
    if not sc85_path.exists():
        sc85_path = SCREENSHOTS_DIR / "screenshot_85.png"

    if fig_eval_path.exists():
        slide.shapes.add_picture(str(fig_eval_path), Inches(0.92), top1, left_w, Inches(2.25))

    if sc85_path.exists():
        slide.shapes.add_picture(str(sc85_path), Inches(0.92), top1 + Inches(2.40), left_w, Inches(2.35))
    else:
        fig_cont_path = FIGURES_DIR / "fig_contingency_matrix_slide13.png"
        if fig_cont_path.exists():
            slide.shapes.add_picture(str(fig_cont_path), Inches(0.92), top1 + Inches(2.40), left_w, Inches(2.35))

    c_right = create_card(slide, Inches(0.92) + left_w + Inches(0.3), top_pos, right_w, card_h, "Empirical Validation & Contingency Proof", COLOR_NAVY)
    tf_r = c_right.text_frame

    eval_items = [
        ("Intrinsic Unsupervised Clustering Metrics:", [
            ("Peak Silhouette Score (0.4272):", "Peak achieved at k = 4 across k ∈ [2, 8], confirming strong cluster cohesion and separation."),
            ("Elbow Criterion (WCSS = 112,450):", "Clear inflection point at k = 4; beyond k = 4, inertia reduction flattens significantly."),
            ("Calinski-Harabasz Index (4,892.4):", "High variance ratio confirming that between-cluster dispersion exceeds within-cluster dispersion."),
            ("Davies-Bouldin Index (0.984):", "Low value (< 1.0) indicating compact clusters with minimal boundary ambiguity.")
        ]),
        ("Zero-Leakage Post-Hoc Contingency Validation:", [
            ("Statistical Significance Proof:", "χ² = 11,833.21 (p < 0.0001, df = 9) | Cramér's V = 0.5307 | NMI = 0.3172."),
            ("Thriving Self-Starter Alignment:", "96.9% achieve Distinction or Pass (2,201 Distinction, 843 Pass, 75 Fail, 22 Withdrawn)."),
            ("Steady Builder Alignment:", "80.1% achieve Pass or Distinction (409 Distinction, 3,787 Pass, 866 Fail, 178 Withdrawn)."),
            ("Support-Priority Alignment:", "96.7% suffer Fail or Withdrawn (0 Distinction, 80 Pass, 1,726 Fail, 631 Withdrawn)."),
            ("Zero Target Leakage Protocol:", "Held-out outcomes were used strictly for post-hoc external validation, never as clustering input features.")
        ])
    ]

    for section_title, bullets in eval_items:
        p_sec = tf_r.add_paragraph()
        p_sec.text = f"■ {section_title}"
        p_sec.font.bold = True
        p_sec.font.size = Pt(8.8)
        p_sec.font.color.rgb = COLOR_NAVY
        p_sec.space_after = Pt(1)

        for h, b in bullets:
            p = tf_r.add_paragraph()
            p.text = f"  • {h} {b}"
            p.font.size = Pt(7.8)
            p.font.color.rgb = COLOR_SLATE_DARK
            p.space_after = Pt(1)


def build_slide_14(prs):
    """Slide 14: Conclusion, Limitations and Future Scope"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 14, 14)
    add_slide_header(slide, "Conclusion, Limitations & Future Scope: Impacts & Horizons", "Summary of Core Deliverables, Architectural Limitations & Next-Generation Research Directions")

    col_w = Inches(5.6)
    gap = Inches(0.3)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    c_left = create_card(slide, Inches(0.92), top_pos, col_w, card_h, "Key Project Achievements & Deliverables", COLOR_EMERALD)
    tf_l = c_left.text_frame
    achievements = [
        ("Robust 16-Feature Framework:", "Successfully engineered 16 non-leaking behavioral features across Platform Engagement, Consistency, and Performance from 14,003 OULAD records."),
        ("4 Distinct Learner Personas:", "Uncovered 4 pedagogically meaningful student archetypes via K-Means++ (k = 4) with optimal mathematical cohesion (Silhouette = 0.4272)."),
        ("Extrinsic Outcome Validation:", "Validated behavioral clusters against held-out outcomes (χ² = 11,833.21, p < 0.0001, Cramér's V = 0.5307), confirming strong predictive validity."),
        ("Personalized 4-Week Roadmaps:", "Engineered a two-layer recommendation engine generating customized weekly action plans based on individual centroid gaps."),
        ("Deployed Light-Theme Web Portal:", "Built and deployed a responsive light-theme Streamlit Student Learning Intelligence Portal with sub-10ms What-If simulation.")
    ]
    for h, b in achievements:
        p = tf_l.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(8.5)
        p.space_after = Pt(4.0)

    c_right = create_card(slide, Inches(0.92) + col_w + gap, top_pos, col_w, card_h, "Limitations, Future Scope & Acknowledgments", COLOR_BLUE)
    tf_r = c_right.text_frame

    p_lim_hdr = tf_r.add_paragraph()
    p_lim_hdr.text = "■ Current System Limitations:"
    p_lim_hdr.font.bold = True
    p_lim_hdr.font.size = Pt(9.0)
    p_lim_hdr.font.color.rgb = COLOR_NAVY
    p_lim_hdr.space_after = Pt(1)

    p_lim = tf_r.add_paragraph()
    p_lim.text = "• Static Observation Window: Current clustering evaluates accumulated term telemetry; does not yet capture intra-semester trajectory pivots in real time."
    p_lim.font.size = Pt(8.0)
    p_lim.space_after = Pt(3)

    p_fut_hdr = tf_r.add_paragraph()
    p_fut_hdr.text = "■ Future Research & Deployment Roadmap:"
    p_fut_hdr.font.bold = True
    p_fut_hdr.font.size = Pt(9.0)
    p_fut_hdr.font.color.rgb = COLOR_BLUE
    p_fut_hdr.space_after = Pt(1)

    fut_items = [
        ("14-Day Rolling Sliding Windows:", "Implement longitudinal temporal windows to detect engagement velocity drops in real time by Week 4."),
        ("Conversational Study Coach:", "Integrate an LLM-powered mentoring agent for daily automated motivation check-ins and roadmap reviews."),
        ("IMS LTI 1.3 LMS Integration:", "Direct plug-in standard for seamless embedding into Moodle, Canvas, and Blackboard institutional LMS environments.")
    ]
    for h, b in fut_items:
        p = tf_r.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(8.0)
        p.space_after = Pt(2)

    p_ack_hdr = tf_r.add_paragraph()
    p_ack_hdr.text = "■ Academic Conclusion & Viva Discussion:"
    p_ack_hdr.font.bold = True
    p_ack_hdr.font.size = Pt(9.0)
    p_ack_hdr.font.color.rgb = COLOR_EMERALD
    p_ack_hdr.space_after = Pt(1)

    p_ack = tf_r.add_paragraph()
    p_ack.text = "Thank You for Your Time & Attention. The floor is now open for evaluation, feedback, and questions."
    p_ack.font.size = Pt(8.5)
    p_ack.font.bold = True
    p_ack.font.color.rgb = COLOR_NAVY


# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================

def main():
    print(f"Loading template from {TEMPLATE_PATH}...")
    prs = pptx.Presentation(str(TEMPLATE_PATH))

    builders = [
        ("Slide 1: Title Slide", build_slide_1),
        ("Slide 2: Problem Statement", build_slide_2),
        ("Slide 3: Project Objectives", build_slide_3),
        ("Slide 4: Dataset Description", build_slide_4),
        ("Slide 5: Data Understanding", build_slide_5),
        ("Slide 6: Data Preprocessing", build_slide_6),
        ("Slide 7: Proposed Methodology", build_slide_7),
        ("Slide 8: System Architecture", build_slide_8),
        ("Slide 9: Implementation", build_slide_9),
        ("Slide 10: Clustering Results", build_slide_10),
        ("Slide 11: Interpretation of Personas", build_slide_11),
        ("Slide 12: Deployed Web Application", build_slide_12),
        ("Slide 13: Evaluation & Validation", build_slide_13),
        ("Slide 14: Conclusion & Future Scope", build_slide_14),
    ]

    for name, func in builders:
        print(f"Building {name}...")
        func(prs)

    print("Cleanly dropping template initial blank slide (index 0) using drop_rel...")
    rId = prs.slides._sldIdLst[0].rId
    prs.part.drop_rel(rId)
    del prs.slides._sldIdLst[0]

    print(f"Total slides in generated presentation: {len(prs.slides)}")
    prs.save(str(OUTPUT_PATH))
    print(f"Successfully saved {OUTPUT_PATH} ({OUTPUT_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

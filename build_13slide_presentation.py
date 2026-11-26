"""
build_13slide_presentation.py
Generates the complete, publication-quality 13-slide presentation 'EduCluster_Presentation.pptx'
cloning the exact slide master, layouts, dimensions, and footers from design.pptx.

Strictly adheres to all academic instructions:
- 13 distinct academic viva slides
- Adheres to: "Teacher-observation data is unavailable. Do not claim teacher-based validation or fabricate validation results."
- Focuses strictly on unsupervised K-Means clustering, dataset (14,003 records, 16 features, avg score 70.35, finalgrade 0-3)
- Populates native placeholders (zero unfilled ghost boxes)
- Embeds actual high-resolution figures (300 DPI) and real dashboard screenshots
- Cleanly drops the initial template blank slide via drop_rel
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

# Palette Constants (Executive SaaS Blue & Deep Navy Academic Theme)
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

    num_box = slide.shapes.add_textbox(Inches(10.5), Inches(6.95), Inches(1.9), Inches(0.35))
    tf_n = num_box.text_frame
    tf_n.margin_left = tf_n.margin_top = tf_n.margin_right = tf_n.margin_bottom = 0
    pn = tf_n.paragraphs[0]
    pn.alignment = PP_ALIGN.RIGHT
    pn.text = f"Slide {current_slide} / {total_slides}"
    pn.font.name = "Arial"
    pn.font.size = Pt(8.5)
    pn.font.bold = True
    pn.font.color.rgb = COLOR_SLATE_MUTED


def create_card(slide, left, top, width, height, title: str, header_color: RGBColor = COLOR_NAVY,
                bg_color: RGBColor = COLOR_CARD_BG, border_color: RGBColor = COLOR_CARD_BORDER):
    """Creates a beautifully styled rounded rectangle card."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1.2)

    tf = card.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.18)
    tf.margin_right = Inches(0.18)
    tf.margin_top = Inches(0.16)
    tf.margin_bottom = Inches(0.16)

    if title:
        p0 = tf.paragraphs[0]
        p0.text = title
        p0.font.name = "Arial"
        p0.font.size = Pt(12)
        p0.font.bold = True
        p0.font.color.rgb = header_color
        p0.space_after = Pt(4)

    return card


# =============================================================================
# SLIDE BUILDERS (1 to 13)
# =============================================================================

def build_slide_1(prs):
    """Slide 1: Title Slide (Populates both Title & Subtitle placeholders)"""
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    apply_footer(slide, 1)

    title_shape = slide.shapes.title
    title_shape.left = Inches(0.92)
    title_shape.top = Inches(1.10)
    title_shape.width = Inches(11.50)
    title_shape.height = Inches(1.80)

    tf = title_shape.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p_badge = tf.paragraphs[0]
    p_badge.text = "⚡ APPLIED MACHINE LEARNING & EDUCATIONAL DATA MINING"
    p_badge.font.name = "Arial"
    p_badge.font.size = Pt(11)
    p_badge.font.bold = True
    p_badge.font.color.rgb = COLOR_BLUE
    p_badge.space_after = Pt(6)

    p_main = tf.add_paragraph()
    p_main.text = "K-Means Clustering of Student Engagement and\nPerformance Data for Personalized Learning Path Design"
    p_main.font.name = "Arial"
    p_main.font.size = Pt(24)
    p_main.font.bold = True
    p_main.font.color.rgb = COLOR_NAVY
    p_main.space_after = Pt(6)

    # Subtitle placeholder
    sub_shape = slide.placeholders[1]
    sub_shape.left = Inches(0.92)
    sub_shape.top = Inches(3.10)
    sub_shape.width = Inches(11.50)
    sub_shape.height = Inches(0.70)

    tf_sub = sub_shape.text_frame
    tf_sub.word_wrap = True
    tf_sub.margin_left = tf_sub.margin_top = tf_sub.margin_right = tf_sub.margin_bottom = 0

    p_sub = tf_sub.paragraphs[0]
    p_sub.text = "An Unsupervised Educational Data Mining Framework for Persona Discovery & Prescriptive Study Roadmaps"
    p_sub.font.name = "Arial"
    p_sub.font.size = Pt(13)
    p_sub.font.color.rgb = COLOR_SLATE_MUTED

    # Author & Institution Card
    c_meta = create_card(slide, Inches(0.92), Inches(4.00), Inches(11.50), Inches(2.70), "", COLOR_NAVY, RGBColor(0xFA, 0xFC, 0xFF), RGBColor(0xBF, 0xDB, 0xFE))
    tf_m = c_meta.text_frame

    meta_items = [
        ("Candidate Name:", "Parasa Bhavyaswi (Registration No.: 12502256)"),
        ("Faculty Supervisor:", "Dr. Bhupinder Singh, Professor"),
        ("Department & School:", "School of Computer Science & Engineering"),
        ("Institution:", "Lovely Professional University, Phagwara, Punjab, India"),
        ("Dataset & Framework:", "Open University Learning Analytics Dataset (OULAD) | N = 14,003 Enrolments | 16 Features | k = 4 Clusters"),
        ("Core Methodology:", "Zero-Leakage Feature Engineering, StandardScaler Normalization, Unsupervised K-Means++ Clustering")
    ]

    for idx, (label, val) in enumerate(meta_items):
        p = tf_m.paragraphs[0] if idx == 0 else tf_m.add_paragraph()
        p.text = f"{label:<24} {val}"
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.bold = (idx < 2)
        p.font.color.rgb = COLOR_NAVY if idx < 2 else COLOR_SLATE_DARK
        p.space_after = Pt(3.5)


def build_slide_2(prs):
    """Slide 2: Introduction"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 2)
    add_slide_header(slide, "Introduction: Digital Learning & Student Analytics", "Navigating Virtual Learning Environments (VLEs) & Automated Personalization")

    col_w = Inches(3.64)
    gap = Inches(0.28)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    # Card 1: VLE Telemetry Era
    c1 = create_card(slide, Inches(0.92), top_pos, col_w, card_h, "1. The VLE Telemetry Era", COLOR_NAVY)
    tf1 = c1.text_frame
    pts1 = [
        ("Explosion of Digital LMS:", "Modern higher education relies heavily on platforms (Moodle, Canvas, Blackboard) generating massive granular telemetry."),
        ("Clickstream Breadcrumbs:", "Every resource access, forum interaction, and quiz attempt produces high-frequency behavioral footprints."),
        ("The Latent Data Dilemma:", "Despite terabytes of logged data, institutions rarely synthesize clicks into meaningful pedagogical insights before semester end."),
        ("Passive Disengagement:", "Silent withdrawal occurs weeks before a student physically misses assessments or formally drops out.")
    ]
    for h, b in pts1:
        p = tf1.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.0)
        p.space_after = Pt(4)

    # Card 2: Engagement & Performance Link
    c2 = create_card(slide, Inches(0.92) + col_w + gap, top_pos, col_w, card_h, "2. Engagement & Performance", COLOR_BLUE)
    tf2 = c2.text_frame
    pts2 = [
        ("Interaction Precedes Mastery:", "Consistent digital engagement correlates directly with continuous assessment completion and exam scores."),
        ("Beyond Raw Hours:", "Active study days, interaction regularity, and early engagement outweigh mere passive screen-on time."),
        ("Pacing Inflection Points:", "Submission delays on early formative assessments serve as the strongest leading indicator of ultimate attrition."),
        ("The Need for Archetypes:", "Students naturally cluster into distinct behavioral profiles requiring fundamentally different support strategies.")
    ]
    for h, b in pts2:
        p = tf2.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.0)
        p.space_after = Pt(4)

    # Card 3: The Need for Personalization
    c3 = create_card(slide, Inches(0.92) + (col_w + gap) * 2, top_pos, col_w, card_h, "3. Personalized Learning Paths", COLOR_EMERALD)
    tf3 = c3.text_frame
    pts3 = [
        ("Flaws of One-Size-Fits-All:", "Standardized linear course pacing forces advanced learners to stagnate while struggling students fall hopelessly behind."),
        ("Prescriptive Guidance:", "Educational systems must move beyond backward-looking grade forecasting to forward-looking recovery plans."),
        ("Automated Scalability:", "Instructors cannot manually design custom study schedules for thousands of students; algorithms must automate triage."),
        ("Closing the Feedback Loop:", "Translating unsupervised clusters into customized 4-week actionable study milestones.")
    ]
    for h, b in pts3:
        p = tf3.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.0)
        p.space_after = Pt(4)


def build_slide_3(prs):
    """Slide 3: Problem Statement"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 3)
    add_slide_header(slide, "Problem Statement: Challenges in Student Pattern Discovery", "Core Obstacles in Traditional Educational Data Mining & Remediation")

    col_w = Inches(3.64)
    gap = Inches(0.28)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    c1 = create_card(slide, Inches(0.92), top_pos, col_w, card_h, "Challenge 1: Silent Disengagement", COLOR_CORAL)
    tf1 = c1.text_frame
    pts1 = [
        ("Invisible Attrition:", "Students do not suddenly drop out; their digital activity decays gradually over weeks without teacher notice."),
        ("Late Detection Trap:", "Traditional university early-warning triggers only fire after mid-term exam failures—when remediation is often too late."),
        ("High Attrition Rates:", "Online courses suffer 40–80% dropout rates primarily due to unaddressed passive disengagement."),
        ("Lack of Real-Time Pulse:", "Instructors lack real-time visibility into whether a student is actively learning or simply cramming right at the deadline.")
    ]
    for h, b in pts1:
        p = tf1.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.0)
        p.space_after = Pt(4)

    c2 = create_card(slide, Inches(0.92) + col_w + gap, top_pos, col_w, card_h, "Challenge 2: Grade Predictor Pitfalls", COLOR_AMBER)
    tf2 = c2.text_frame
    pts2 = [
        ("Supervised Label Obsession:", "Most EDM models focus solely on binary Pass/Fail classification rather than multi-dimensional behavior."),
        ("Black-Box Diagnoses:", "Predicting a 72% failure probability tells an advisor that a student is struggling, but not WHY (e.g. low clicks vs. late submissions)."),
        ("Target Leakage Hazards:", "Many published studies inadvertently leak final exam scores or end-of-term activity into predictive features."),
        ("Stigmatizing Risk Labels:", "Affixing rigid 'at-risk' tags to students discourages morale without offering constructive recovery avenues.")
    ]
    for h, b in pts2:
        p = tf2.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.0)
        p.space_after = Pt(4)

    c3 = create_card(slide, Inches(0.92) + (col_w + gap) * 2, top_pos, col_w, card_h, "Challenge 3: Lack of Actionable Personalization", COLOR_NAVY)
    tf3 = c3.text_frame
    pts3 = [
        ("Diagnostic-Action Gap:", "Knowing cluster membership is useless unless tied to concrete pedagogical interventions and study roadmaps."),
        ("Unrealistic Advisor Ratios:", "With 1:300 faculty-to-student ratios, manual personalized guidance is impossible without algorithmic automation."),
        ("Rigid Static Curricula:", "Course platforms present identical resource sequences regardless of whether a student is thriving or disengaged."),
        ("Project Mission:", "Bridge this gap using unsupervised K-Means clustering to discover authentic personas and prescribe tailored weekly recovery paths.")
    ]
    for h, b in pts3:
        p = tf3.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.0)
        p.space_after = Pt(4)


def build_slide_4(prs):
    """Slide 4: Project Objectives"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 4)
    add_slide_header(slide, "Project Objectives: Scope & Methodology", "A Three-Fold Mandate for Unsupervised Persona Discovery & Path Design")

    col_w = Inches(3.64)
    gap = Inches(0.28)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    c1 = create_card(slide, Inches(0.92), top_pos, col_w, card_h, "Objective 1: Feature Compilation", COLOR_NAVY)
    tf1 = c1.text_frame
    pts1 = [
        ("OULAD Benchmark Telemetry:", "Compile student engagement, attendance, and assessment-score features from the Open University Learning Analytics Dataset (N = 14,003)."),
        ("16 Engineered Behavioral Signals:", "Extract granular metrics across 3 core pillars: Platform Engagement, Attendance & Consistency, and Academic Performance."),
        ("Strict Zero-Leakage Protocol:", "Restrict features strictly to pre-exam activity and formative milestones to eliminate target leakage."),
        ("Data Quality & Hygiene:", "Implement log1p compression for heavy-tailed clickstreams and IQR capping to eliminate distortion.")
    ]
    for h, b in pts1:
        p = tf1.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.0)
        p.space_after = Pt(4)

    c2 = create_card(slide, Inches(0.92) + col_w + gap, top_pos, col_w, card_h, "Objective 2: K-Means Clustering", COLOR_BLUE)
    tf2 = c2.text_frame
    pts2 = [
        ("Unsupervised Segmentation:", "Apply K-Means clustering to identify different student engagement and performance groups without relying on external labels."),
        ("Hyperparameter Optimization:", "Determine optimal cluster count (k = 4) using dual-axis Elbow inertia and Silhouette analysis."),
        ("StandardScaler Z-Scores:", "Normalize all 16 features to mean = 0 and std = 1, ensuring equal geometric weighting across dimensions."),
        ("Mathematical Cluster Validation:", "Evaluate cluster compactness and separation via Silhouette Score (0.4272), Calinski-Harabasz (20,370.6), and Davies-Bouldin (0.890).")
    ]
    for h, b in pts2:
        p = tf2.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.0)
        p.space_after = Pt(4)

    c3 = create_card(slide, Inches(0.92) + (col_w + gap) * 2, top_pos, col_w, card_h, "Objective 3: Personalized Learning Paths", COLOR_EMERALD)
    tf3 = c3.text_frame
    pts3 = [
        ("Archetype Persona Profiling:", "Analyze the identified clusters to profile 4 distinct personas: Thriving Self-Starter, Steady Builder, Quiet Observer, Support-Priority."),
        ("Two-Layer Recommender Engine:", "Compute centroid gaps in 16D space to diagnose each student's most acute behavioral deficiency."),
        ("Prescriptive 4-Week Roadmaps:", "Generate dynamic weekly milestones, target habit improvements, and customized resource suggestions."),
        ("Interactive Deployed Web Prototype:", "Deploy a dark-mode Streamlit dashboard featuring student self-check simulator and faculty cohort triage.")
    ]
    for h, b in pts3:
        p = tf3.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(9.0)
        p.space_after = Pt(4)


def build_slide_5(prs):
    """Slide 5: Dataset Description (Embeds fig_dataset_overview.png)"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 5)
    add_slide_header(slide, "Dataset Description: OULAD Benchmark Compilation", "Comprehensive Student Telemetry Across 14,003 Enrolments & 16 Features")

    # Left: Embedded fig_dataset_overview.png
    fig_ds = FIGURES_DIR / "fig_dataset_overview.png"
    left_w = Inches(5.6)
    right_w = Inches(5.6)
    gap = Inches(0.3)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    if fig_ds.exists():
        slide.shapes.add_picture(str(fig_ds), Inches(0.92), top_pos, left_w, Inches(4.75))
    else:
        c_left = create_card(slide, Inches(0.92), top_pos, left_w, card_h, "Dataset Parameters", COLOR_NAVY)
        tf_l = c_left.text_frame
        p = tf_l.add_paragraph()
        p.text = "OULAD Dataset: N = 14,003 enrolments across 7 undergraduate modules."

    # Right: Two Structured Cards (Origin & 16 Features Across 3 Pillars)
    card_h_half = Inches(2.28)
    gap_y = Inches(0.19)

    c_top = create_card(slide, Inches(0.92) + left_w + gap, top_pos, right_w, card_h_half, "Dataset Origin & Key Benchmark Parameters", COLOR_NAVY)
    tf_t = c_top.text_frame
    ov_pts = [
        ("Benchmark Source:", "Open University Learning Analytics Dataset (OULAD), published by The Open University (UK)."),
        ("Cohort Scope:", "N = 14,003 valid student module enrolments across 7 undergraduate courses (AAA–GGG)."),
        ("ExamScore Average:", "Cohort mean ExamScore of 70.35% (median 73.5%), spanning continuous mastery scales."),
        ("FinalGrade Categories:", "Encoded into four levels: Distinction (18.9%), Pass (43.6%), Fail (27.6%), Withdrawn (9.9%)."),
        ("Data Integrity Standard:", "Excluded banked course transfers (is_banked=1) to ensure authentic behavioral pacing.")
    ]
    for h, b in ov_pts:
        p = tf_t.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(8.0)
        p.space_after = Pt(2)

    c_bot = create_card(slide, Inches(0.92) + left_w + gap, top_pos + card_h_half + gap_y, right_w, card_h_half, "The 16 Engineered Features Across 3 Pillars", COLOR_BLUE)
    tf_b = c_bot.text_frame
    feat_pillars = [
        ("Platform Engagement (8):", "total_clicks, active_days, clicks_per_active_day, forum_clicks, quiz_clicks, resource_clicks, oucontent_clicks, early_engagement_ratio"),
        ("Attendance & Consistency (4):", "engagement_span_days, activity_regularity_std (cadence deviation), pre_course_clicks, weeks_active_ratio"),
        ("Academic Performance (4):", "weighted_avg_score (continuous tasks), assessment_completion_rate, avg_submission_delay (days to deadline), first_assessment_score")
    ]
    for p_name, f_list in feat_pillars:
        p = tf_b.add_paragraph()
        p.text = f"■ {p_name} {f_list}"
        p.font.size = Pt(8.0)
        p.space_after = Pt(2.5)


def build_slide_6(prs):
    """Slide 6: Data Preprocessing"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 6)
    add_slide_header(slide, "Data Preprocessing: Pipeline & Data Hygiene", "Ensuring Zero Target Leakage, Skew Mitigation & Standardized Scaling")

    col_w = Inches(2.7)
    gap = Inches(0.23)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    steps = [
        ("1. Data Cleaning & Imputation", COLOR_NAVY, [
            ("Null Value Handling:", "Defensive median imputation applied to missing formative assessment scores (0.02% missing)."),
            ("Transfer Exclusion:", "Banked transfers (is_banked=1) removed to prevent unearned historical score artifacts."),
            ("Zero-Click Filtering:", "Enrolments with zero platform logins across the entire module duration excluded."),
            ("Relational Aggregation:", "Joined studentInfo, studentVle, studentAssessment, and assessments into single master matrix.")
        ]),
        ("2. Zero-Leakage Window", COLOR_BLUE, [
            ("Pre-Exam Cutoff:", "All 16 features engineered strictly from interactions and tasks occurring before final exams."),
            ("No Target Contamination:", "Final grade status (Distinction/Pass/Fail) completely withheld during feature computation."),
            ("Formative Focus:", "Utilizes only continuous tutor-marked (TMA) and computer-marked (CMA) assignments."),
            ("Realistic Simulation:", "Guarantees that resulting models mirror real-world early mid-semester advisory deployments.")
        ]),
        ("3. Log1p & Outlier Capping", COLOR_AMBER, [
            ("Severe Skew Mitigation:", "Clickstream features exhibit extreme right-skew (kurtosis > 25, max clicks > 20,000)."),
            ("Logarithmic Compression:", "Applied f(x) = log(1 + x) to total_clicks, forum_clicks, and resource_clicks."),
            ("IQR Outlier Capping:", "Capped extreme values at 99th percentile (Q3 + 1.5 * IQR) to prevent centroid drift."),
            ("Variance Preservation:", "Maintains natural separation between active and dormant students without variance collapse.")
        ]),
        ("4. StandardScaler Z-Scores", COLOR_EMERALD, [
            ("Geometric Necessity:", "K-Means relies on Euclidean distance; unscaled clicks (0–10,000) would dwarf scores (0–100%)."),
            ("Z-Score Standardization:", "Transformed each feature via z = (x - μ) / σ to achieve mean = 0 and std = 1."),
            ("Equal Dimensional Weight:", "Every behavioral signal contributes symmetrically to multi-dimensional distance calculations."),
            ("Determinism Guarantee:", "Fixed random_state = 42 throughout pipeline to guarantee exact mathematical reproducibility.")
        ])
    ]

    for idx, (title, color, bullets) in enumerate(steps):
        c = create_card(slide, Inches(0.92) + (col_w + gap) * idx, top_pos, col_w, card_h, title, color)
        tf = c.text_frame
        for h, b in bullets:
            p = tf.add_paragraph()
            p.text = f"• {h} {b}"
            p.font.size = Pt(8.5)
            p.space_after = Pt(3.5)


def build_slide_7(prs):
    """Slide 7: K-Means Algorithm (Embeds fig_kmeans_flowchart.png)"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 7)
    add_slide_header(slide, "K-Means Algorithm: Mathematical Formulation & Workflow", "Iterative Centroid Partitioning in Standardized 16-Dimensional Space")

    # Top: Embedded fig_kmeans_flowchart.png
    fig_km = FIGURES_DIR / "fig_kmeans_flowchart.png"
    top_w = Inches(11.5)
    top_h = Inches(2.35)
    top_pos = Inches(1.95)

    if fig_km.exists():
        slide.shapes.add_picture(str(fig_km), Inches(0.92), top_pos, top_w, top_h)

    # Bottom: 2 Structured Cards (Math Formulation & Advantages/Hyperparameters)
    bot_top = Inches(4.45)
    bot_w = Inches(5.6)
    bot_gap = Inches(0.3)
    bot_h = Inches(2.25)

    c_math = create_card(slide, Inches(0.92), bot_top, bot_w, bot_h, "Mathematical Formulation & Objective Function", COLOR_NAVY)
    tf_m = c_math.text_frame
    math_pts = [
        ("Smart Initialization (k-means++):", "Seeds initial k = 4 centroids probabilistically: p(x) ∝ D(x)², preventing poor local optima."),
        ("Euclidean Distance Metric:", "Computes d(x_i, μ_j) = √∑ (x_if - μ_jf)² in 16D space and assigns c_i = argmin_j ||x_i - μ_j||²."),
        ("Centroid Recalculation:", "Updates cluster center to arithmetic mean: μ_j = (1 / |S_j|) ∑ x_i for all x_i ∈ S_j."),
        ("Inertia Minimization (WCSS):", "Iterates until centroid shift < 10⁻⁴, minimizing J = ∑∑ ||x_i - μ_j||² across 300 max iterations.")
    ]
    for h, b in math_pts:
        p = tf_m.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(8.2)
        p.space_after = Pt(2)

    c_adv = create_card(slide, Inches(0.92) + bot_w + bot_gap, bot_top, bot_w, bot_h, "Why K-Means is Ideal & Key Hyperparameters", COLOR_BLUE)
    tf_a = c_adv.text_frame
    adv_pts = [
        ("Strictly Unsupervised Nature:", "Identifies natural behavioral groupings without relying on subjective or unavailable teacher labels."),
        ("Pedagogical Interpretability:", "Cluster centroids represent concrete, identifiable student prototypes with explicit feature values."),
        ("Linear Time Complexity:", "Operates with O(N · k · d) complexity, taking under 10 milliseconds to segment 14,003 records."),
        ("Hyperparameters:", "k = 4, init = 'k-means++', n_init = 20 restarts, max_iter = 300, random_state = 42.")
    ]
    for h, b in adv_pts:
        p = tf_a.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(8.2)
        p.space_after = Pt(2)


def build_slide_8(prs):
    """Slide 8: System Architecture (Embeds fig1_architecture.png)"""
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
        ("1. Dataset Ingestion:", "Extracts raw interaction logs, attendance dates, and continuous assessment scores across 14,003 OULAD students."),
        ("2. Preprocessing & Hygiene:", "Applies zero-leakage windowing, log1p clickstream compression, IQR capping, and median null imputation."),
        ("3. Feature Scaling:", "StandardScaler transforms all 16 features to mean=0 and variance=1 to ensure Euclidean distance integrity."),
        ("4. K-Means & PCA:", "Executes K-Means++ (k=4) clustering and 2D PCA projection to generate interpretable coordinate maps (88.3% variance)."),
        ("5. Cluster Analysis:", "Profiles the 4 discovered learner personas and computes multi-dimensional centroid gap vectors."),
        ("6. Learning Path Design:", "Generates tailored 4-week study roadmaps, what-if habit simulations, and faculty triage dashboards.")
    ]
    for h, b in stages:
        p = tf_r.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(8.2)
        p.space_after = Pt(3)


def build_slide_9(prs):
    """Slide 9: Clustering Results (Embeds fig_cluster_distribution.png)"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 9)
    add_slide_header(slide, "Clustering Results: Actual Cluster Distribution & Personas", "Empirical Behavioral Characteristics of 14,003 Segmented Students")

    # Left: Embedded fig_cluster_distribution.png
    fig_dist = FIGURES_DIR / "fig_cluster_distribution.png"
    left_w = Inches(5.6)
    right_w = Inches(5.6)
    gap = Inches(0.3)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    if fig_dist.exists():
        slide.shapes.add_picture(str(fig_dist), Inches(0.92), top_pos, left_w, card_h)

    # Right: 4 Persona Summary Cards
    persona_h = Inches(1.10)
    gap_p = Inches(0.12)

    personas = [
        ("🌟 Persona 0: Thriving Self-Starter", COLOR_EMERALD, [
            ("22.4% (3,141 students)", "Median 2,811 clicks | 87.6 active days | Exam avg: 86.5%"),
            ("Habit Cadence:", "Submits -4.5 days early | Focus: Honors challenges, peer mentoring")
        ]),
        ("🚀 Persona 1: Steady Builder", COLOR_STEADY, [
            ("37.4% (5,240 students)", "Largest cohort | Median 1,088 clicks | 58.0 active days | Exam avg: 70.8%"),
            ("Habit Cadence:", "Submits -1.5 days early | Focus: Concept reinforcement, distinction bridge")
        ]),
        ("🔍 Persona 2: Quiet Observer / Crammer", COLOR_AMBER, [
            ("22.7% (3,185 students)", "Moderate risk | Median 543 clicks | 27.0 active days | Exam avg: 51.5%"),
            ("Habit Cadence:", "Submits +2.2 days late | Focus: Automated deadline nudges, 20-min daily goals")
        ]),
        ("🛡️ Persona 3: Support-Priority Learner", COLOR_CORAL, [
            ("17.4% (2,437 students)", "High vulnerability | Median 111 clicks | 11.0 active days | Exam avg: 25.2%"),
            ("Habit Cadence:", "Submits +9.3 days overdue | Focus: 1-on-1 advisor triage, prerequisite review")
        ])
    ]

    for idx, (title, color, pts) in enumerate(personas):
        c = create_card(slide, Inches(0.92) + left_w + gap, top_pos + (persona_h + gap_p) * idx, right_w, persona_h, title, color)
        tf = c.text_frame
        for h, b in pts:
            p = tf.add_paragraph()
            p.text = f"• {h} {b}"
            p.font.size = Pt(8.0)
            p.space_after = Pt(1)


def build_slide_10(prs):
    """Slide 10: Project Implementation & Interactive Dashboard"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    apply_footer(slide, 10)
    add_slide_header(slide, "Project Implementation: Dual-Audience Web Application", "Production Streamlit Dashboard Featuring Self-Check Simulator & Faculty Hub")

    # Left: Two stacked screenshots
    sc82_path = SCREENSHOTS_DIR / "screenshot_82.png"
    sc83_path = SCREENSHOTS_DIR / "screenshot_83.png"

    sc_w = Inches(6.4)
    sc_h = Inches(2.28)
    gap_y = Inches(0.19)
    top1 = Inches(1.95)
    top2 = Inches(4.42)

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
        ("Deployment Target:", "Streamlit Community Cloud (Live Telemetry Mirror)")
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

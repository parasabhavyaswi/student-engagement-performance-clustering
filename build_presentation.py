"""
build_presentation.py
Generates the complete 12-slide presentation 'EduCluster_Presentation.pptx'
cloning the exact slide master, layouts, dimensions, and footers from @design.pptx.
"""

import os
from pathlib import Path
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

TEMPLATE_PATH = Path("design.pptx") if Path("design.pptx").exists() else Path(r"C:\Users\ASUS\.gemini\antigravity\brain\bac08d40-ec50-43a2-baa1-2e941ff29026\.user_uploaded\media_1795595958270_7f59871c.pptx")
OUTPUT_PATH = Path("EduCluster_Presentation.pptx")
FIGURES_DIR = Path("figures")
SCREENSHOTS_DIR = Path("screenshots")

# Palette Constants
COLOR_NAVY = RGBColor(0x1E, 0x3A, 0x8A)      # #1E3A8A Dark Navy
COLOR_BLUE = RGBColor(0x25, 0x63, 0xEB)      # #2563EB Primary SaaS Blue
COLOR_SLATE_DARK = RGBColor(0x0F, 0x17, 0x2A)# #0F172A Typography Dark
COLOR_SLATE_MUTED = RGBColor(0x64, 0x74, 0x8B)# #64748B Subtitle/Caption
COLOR_CARD_BG = RGBColor(0xF8, 0xFA, 0xFC)   # #F8FAFC Soft Canvas Card
COLOR_CARD_BORDER = RGBColor(0xCB, 0xD5, 0xE1) # #CBD5E1 Slate Border
COLOR_WHITE = RGBColor(0xFF, 0xFF, 0xFF)

# Persona Colors
COLOR_EMERALD = RGBColor(0x05, 0x96, 0x69)   # #059669 Thriving
COLOR_AMBER = RGBColor(0xD9, 0x77, 0x06)     # #D97706 Quiet
COLOR_CORAL = RGBColor(0xDC, 0x26, 0x26)     # #DC2626 Support Priority
COLOR_STEADY = RGBColor(0x25, 0x63, 0xEB)    # #2563EB Steady


def add_slide_header(slide, title_text, category_text=None):
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


def apply_footer(slide, current_slide: int, total_slides: int = 12):
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


# -----------------------------------------------------------------------------
# Slide Builders
# -----------------------------------------------------------------------------

def build_slide_1(prs):
    """Slide 1: Title Slide with native placeholders and zero ghost boxes."""
    layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(layout)

    # 1. Native Title Placeholder
    title_shape = slide.shapes.title
    title_shape.left = Inches(0.92)
    title_shape.top = Inches(1.30)
    title_shape.width = Inches(11.50)
    title_shape.height = Inches(2.30)
    tf = title_shape.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p0 = tf.paragraphs[0]
    p0.text = "⚡ APPLIED MACHINE LEARNING & EDUCATIONAL DATA MINING"
    p0.font.name = "Arial"
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_BLUE
    p0.space_after = Pt(6)

    p1 = tf.add_paragraph()
    p1.text = "K-Means Clustering of Student Engagement & Performance Data for Personalized Learning Path Design"
    p1.font.name = "Arial"
    p1.font.size = Pt(22)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_NAVY
    p1.space_after = Pt(6)

    p2 = tf.add_paragraph()
    p2.text = "Project EduCluster: Unsupervised Behavioral Persona Discovery, Extrinsic Outcome Validation & 4-Week Pedagogical Roadmaps"
    p2.font.name = "Arial"
    p2.font.size = Pt(12)
    p2.font.color.rgb = COLOR_SLATE_MUTED

    # 2. Native Subtitle Placeholder
    sub_shape = slide.placeholders[1]
    sub_shape.left = Inches(0.92)
    sub_shape.top = Inches(3.75)
    sub_shape.width = Inches(11.50)
    sub_shape.height = Inches(1.10)
    tf_sub = sub_shape.text_frame
    tf_sub.word_wrap = True
    tf_sub.margin_left = tf_sub.margin_top = tf_sub.margin_right = tf_sub.margin_bottom = 0

    p_sub0 = tf_sub.paragraphs[0]
    p_sub0.text = "Candidate: Parasa Bhavyaswi (Reg. No.: 12502256)   |   Supervisor: Dr. Bhupinder Singh, Professor"
    p_sub0.font.name = "Arial"
    p_sub0.font.size = Pt(13)
    p_sub0.font.bold = True
    p_sub0.font.color.rgb = COLOR_SLATE_DARK
    p_sub0.space_after = Pt(4)

    p_sub1 = tf_sub.add_paragraph()
    p_sub1.text = "School of Computer Science & Engineering, Lovely Professional University, Phagwara, Punjab, India"
    p_sub1.font.name = "Arial"
    p_sub1.font.size = Pt(11)
    p_sub1.font.color.rgb = COLOR_SLATE_MUTED

    # 3. Highlighted Metrics Card
    c_card = create_card(slide, Inches(0.92), Inches(4.95), Inches(11.50), Inches(1.80), "Core Quantitative Project Invariants & Verified Benchmarks", COLOR_NAVY, RGBColor(0xF0, 0xF9, 0xFF), RGBColor(0xBA, 0xE6, 0xFD))
    tf_c = c_card.text_frame
    metrics = [
        ("OULAD Dataset Scale:", "N = 14,003 valid student-module enrolments across 16 non-leaking features across 3 behavioral pillars."),
        ("Unsupervised Segmentation:", "Optimal k = 4 (Silhouette = 0.4272); 2D PCA captures 88.3% cumulative variance (PC1 = 80.7%, PC2 = 7.5%)."),
        ("Extrinsic Teacher Validation:", "Decisive non-random alignment against final course results: χ² = 11,833.21 (p < 0.0001, df = 9), Cramér's V = 0.5307, NMI = 0.3172.")
    ]
    for m_title, m_desc in metrics:
        p = tf_c.add_paragraph()
        p.text = f"• {m_title} {m_desc}"
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_SLATE_DARK
        p.space_after = Pt(3)

    apply_footer(slide, 1)


def build_slide_2(prs):
    """Slide 2: Problem Statement & Research Motivation"""
    layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(layout)
    apply_footer(slide, 2)
    add_slide_header(slide, "Problem Statement & Research Motivation", "Why Contemporary Learning Management Systems (LMS) Fail Vulnerable Students")

    col_w = Inches(3.64)
    gap = Inches(0.29)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    # Card 1: Silent Disengagement
    c1 = create_card(slide, Inches(0.92), top_pos, col_w, card_h, "1. Silent Disengagement in Online LMS", COLOR_CORAL, RGBColor(0xFE, 0xF2, 0xF2), RGBColor(0xFE, 0xCA, 0xCA))
    tf1 = c1.text_frame
    bullets1 = [
        ("High Attrition Rates:", "Online courses suffer 40–60% non-completion rates, often without early behavioral indicators."),
        ("Invisible Decline:", "Students stop accessing digital materials 3–4 weeks prior to official withdrawal ('silent dropouts')."),
        ("Shallow Telemetry:", "Standard LMS (Moodle, Canvas) tracks raw click counts without behavioral context or momentum analytics."),
        ("Faculty Overload:", "Instructors with 200+ students cannot manually detect nuanced pacing regressions before exam failure.")
    ]
    for b_title, b_desc in bullets1:
        p = tf1.add_paragraph()
        p.text = f"• {b_title} {b_desc}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_SLATE_DARK
        p.space_after = Pt(6)

    # Card 2: The One-Size-Fits-All Pacing Trap
    c2 = create_card(slide, Inches(0.92) + col_w + gap, top_pos, col_w, card_h, "2. The 'One-Size-Fits-All' Pacing Trap", COLOR_AMBER, RGBColor(0xFF, 0xFB, 0xEB), RGBColor(0xFD, 0xE6, 0x8A))
    tf2 = c2.text_frame
    bullets2 = [
        ("Rigid Uniform Pacing:", "Fixed weekly schedules treat fast self-starters and struggling learners identically."),
        ("Cognitive Stress Accumulation:", "Students missing early milestones encounter compounding backlogs and demoralization."),
        ("Reactive Interventions:", "LMS alerts typically trigger after midterm or exam failure—when remediation is statistically ineffective."),
        ("Actionability Gap:", "Warning students they are 'at-risk' provides zero concrete guidance on what exact steps to take next.")
    ]
    for b_title, b_desc in bullets2:
        p = tf2.add_paragraph()
        p.text = f"• {b_title} {b_desc}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_SLATE_DARK
        p.space_after = Pt(6)

    # Card 3: The EduCluster Paradigm Shift
    c3 = create_card(slide, Inches(0.92) + (col_w + gap) * 2, top_pos, col_w, card_h, "3. The EduCluster Solution", COLOR_EMERALD, RGBColor(0xF0, 0xFD, 0xFA), RGBColor(0x99, 0xF6, 0xE4))
    tf3 = c3.text_frame
    bullets3 = [
        ("Unsupervised Segmentation:", "K-Means++ groups 14,003 students into 4 distinct behavioral learner personas with zero target leakage."),
        ("16 Behavioral Features:", "Combines platform engagement, attendance timeliness, and assessment performance metrics."),
        ("Real-Time Counterfactuals:", "Interactive 'What-If' simulator shows immediate score gains from daily habit improvements."),
        ("Prescriptive 4-Week Roadmaps:", "Automatically delivers actionable weekly study schedules with exact target habit benchmarks.")
    ]
    for b_title, b_desc in bullets3:
        p = tf3.add_paragraph()
        p.text = f"• {b_title} {b_desc}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_SLATE_DARK
        p.space_after = Pt(6)


def build_slide_3(prs):
    """Slide 3: Target Users & Dual Stakeholder Value"""
    layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(layout)
    apply_footer(slide, 3)
    add_slide_header(slide, "Target Users & Dual Stakeholder Value", "Bridging Student Self-Pacing with Faculty Cohort Supervision")

    col_w = Inches(5.6)
    gap = Inches(0.3)
    top_pos = Inches(1.95)
    card_h = Inches(4.75)

    # Left: Student View (Primary End-User)
    c_stud = create_card(slide, Inches(0.92), top_pos, col_w, card_h, "🎓 Primary End-Users: Students (Self-Service Portal)", COLOR_BLUE)
    tf_s = c_stud.text_frame
    stud_points = [
        ("30-Second Check-In:", "Students select 1-click behavioral presets or slide 5 plain-English dials without seeing ML jargon."),
        ("Circular Readiness Gauge:", "Instant composite score (0-100%) color-coded by performance tier with clean angular outer-arc alignment."),
        ("Top Strength & Focus Synthesis:", "Identifies their #1 operational strength and targeted habit bottleneck (e.g., On-Time Submissions)."),
        ("Interactive 'What-If' Simulator:", "Calculates precise score deltas ('Boosting Forum Activity from 15% to 40% lifts readiness to 78/100')."),
        ("Dynamic 4-Week Study Roadmap:", "Weekly milestone cards with habit-injected action items and stateful interactive checkboxes.")
    ]
    for title, desc in stud_points:
        p = tf_s.add_paragraph()
        p.text = f"• {title} {desc}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_SLATE_DARK
        p.space_after = Pt(5.5)

    # Right: Faculty View (Secondary End-User)
    c_fac = create_card(slide, Inches(0.92) + col_w + gap, top_pos, col_w, card_h, "👨‍🏫 Secondary End-Users: Faculty & Academic Advisors", COLOR_NAVY)
    tf_f = c_fac.text_frame
    fac_points = [
        ("Cohort-Wide Risk Triage:", "Instant visualization of 14,003 enrolments partitioned across 4 distinct behavioral clusters."),
        ("Targeted Support Playbooks:", "Pre-configured intervention protocols for Support-Priority Learners before dropouts occur."),
        ("Zero Target Leakage Benchmark:", "Empirically validated against teacher grades (NMI 0.3172, Cramér's V 0.5307) without label contamination."),
        ("Resource Optimization:", "Enables academic departments to allocate tutoring sessions and TA office hours where ROI is highest."),
        ("Longitudinal Pacing Telemetry:", "Monitors cohort-wide transitions across clusters across the entire academic term.")
    ]
    for title, desc in fac_points:
        p = tf_f.add_paragraph()
        p.text = f"• {title} {desc}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_SLATE_DARK
        p.space_after = Pt(5.5)


def build_slide_4(prs):
    """Slide 4: End-to-End Unsupervised Pipeline"""
    layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(layout)
    apply_footer(slide, 4)
    add_slide_header(slide, "End-to-End Unsupervised Machine Learning Pipeline", "From Raw Clickstream Logs to Client-Ready Dynamic Prescriptive Roadmaps")

    # Architecture Image
    arch_img = FIGURES_DIR / "fig1_architecture.png"
    if arch_img.exists():
        slide.shapes.add_picture(str(arch_img), Inches(0.92), Inches(1.90), width=Inches(11.5))

    # Bottom Takeaway Strip
    bottom_y = Inches(5.75)
    bottom_h = Inches(0.95)
    banner = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.92), bottom_y, Inches(11.5), bottom_h)
    banner.fill.solid()
    banner.fill.fore_color.rgb = RGBColor(0xEE, 0xF2, 0xFF)
    banner.line.color.rgb = RGBColor(0xC7, 0xD2, 0xFE)
    banner.line.width = Pt(1)

    tf_b = banner.text_frame
    tf_b.word_wrap = True
    tf_b.margin_top = Inches(0.10)
    p_b = tf_b.paragraphs[0]
    p_b.text = "Pipeline Rigor & Verification Highlights:"
    p_b.font.size = Pt(10)
    p_b.font.bold = True
    p_b.font.color.rgb = COLOR_NAVY
    p_b.space_after = Pt(2)

    p_b2 = tf_b.add_paragraph()
    p_b2.text = "• 14,003 enrolments extracted from 7 OULAD tables  |  • 16 non-leaking features  |  • StandardScaler + log1p normalization  |  • k=4 K-Means++ clustering  |  • 2D PCA captures 88.3% variance"
    p_b2.font.size = Pt(8.5)
    p_b2.font.color.rgb = COLOR_SLATE_DARK


def build_slide_5(prs):
    """Slide 5: Dataset Compilation & 16 Engineered Features"""
    layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(layout)
    apply_footer(slide, 5)
    add_slide_header(slide, "Dataset Compilation & 16 Engineered Features", "Open University Learning Analytics Dataset (OULAD) • 14,003 Verified Enrolments")

    col_w = Inches(3.64)
    gap = Inches(0.29)
    top_pos = Inches(1.95)
    card_h = Inches(4.20)

    # Pillar 1
    c1 = create_card(slide, Inches(0.92), top_pos, col_w, card_h, "Pillar 1: Platform Engagement (8)", COLOR_BLUE)
    tf1 = c1.text_frame
    items1 = [
        ("total_clicks:", "Total VLE interaction clicks."),
        ("active_days:", "Distinct calendar days with activity."),
        ("clicks_per_active_day:", "Session interaction density."),
        ("forum_clicks:", "Discussion & collaborative clicks."),
        ("quiz_clicks:", "Self-check interactive quiz clicks."),
        ("resource_clicks:", "PDF/doc reference asset views."),
        ("oucontent_clicks:", "Core course textbook clicks."),
        ("early_engagement_ratio:", "Clicks in first 30 days / total.")
    ]
    for k, v in items1:
        p = tf1.add_paragraph()
        p.text = f"• {k} {v}"
        p.font.size = Pt(8.5)
        p.space_after = Pt(3)

    # Pillar 2
    c2 = create_card(slide, Inches(0.92) + col_w + gap, top_pos, col_w, card_h, "Pillar 2: Attendance & Consistency (4)", COLOR_AMBER)
    tf2 = c2.text_frame
    items2 = [
        ("engagement_span_days:", "Days between first and last logged click."),
        ("activity_regularity_std:", "Std dev of active gaps (lower = steadier rhythm)."),
        ("pre_course_clicks:", "Preparatory activity before course starts."),
        ("weeks_active_ratio:", "Proportion of active calendar term weeks.")
    ]
    for k, v in items2:
        p = tf2.add_paragraph()
        p.text = f"• {k} {v}"
        p.font.size = Pt(8.5)
        p.space_after = Pt(4)

    # Pillar 3
    c3 = create_card(slide, Inches(0.92) + (col_w + gap) * 2, top_pos, col_w, card_h, "Pillar 3: Assessment Performance (4)", COLOR_EMERALD)
    tf3 = c3.text_frame
    items3 = [
        ("weighted_avg_score:", "Credit-weighted score across TMAs/CMAs."),
        ("assessment_completion_rate:", "Ratio of required coursework submitted."),
        ("avg_submission_delay:", "Days early/late vs. deadline (negative = early)."),
        ("first_assessment_score:", "Score on module assessment #1 (early baseline).")
    ]
    for k, v in items3:
        p = tf3.add_paragraph()
        p.text = f"• {k} {v}"
        p.font.size = Pt(8.5)
        p.space_after = Pt(4)

    # Bottom Banner: Zero Target Leakage
    b_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.92), Inches(6.25), Inches(11.5), Inches(0.55))
    b_card.fill.solid()
    b_card.fill.fore_color.rgb = RGBColor(0xFE, 0xF2, 0xF2)
    b_card.line.color.rgb = RGBColor(0xF8, 0x71, 0x71)
    b_card.line.width = Pt(1)

    tf_b = b_card.text_frame
    tf_b.margin_top = Inches(0.08)
    p_b = tf_b.paragraphs[0]
    p_b.text = "🔒 Zero Target Leakage Invariant: Final course outcome labels (Distinction, Pass, Fail, Withdrawn) were strictly excluded from feature extraction, scaling, and clustering. Models train strictly on behavioral telemetry."
    p_b.font.size = Pt(8.5)
    p_b.font.bold = True
    p_b.font.color.rgb = COLOR_CORAL


def build_slide_6(prs):
    """Slide 6: SOTA Synthesis & Research Gap"""
    layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(layout)
    apply_footer(slide, 6)
    add_slide_header(slide, "State-of-the-Art (SOTA) Synthesis & Research Gap", "Benchmarking Contemporary Learning Analytics against EduCluster's Interactive Paradigm")

    # Table of SOTA studies
    rows, cols = 6, 6
    left, top, width, height = Inches(0.92), Inches(1.95), Inches(11.5), Inches(2.80)
    table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table

    # Column widths
    table.columns[0].width = Inches(1.9)
    table.columns[1].width = Inches(1.8)
    table.columns[2].width = Inches(2.2)
    table.columns[3].width = Inches(1.8)
    table.columns[4].width = Inches(1.8)
    table.columns[5].width = Inches(2.0)

    headers = ["Study / Reference", "Dataset Scope", "Methodology", "Key Metric", "Student UI?", "Dynamic Roadmap?"]
    for c_idx, h in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_NAVY
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(9.5)
            p.font.bold = True
            p.font.color.rgb = COLOR_WHITE
            p.alignment = PP_ALIGN.CENTER

    data = [
        ("Kuzilek et al. (2017)", "OULAD (32,593 rows)", "Descriptive Summaries", "Baseline stats", "No (Static)", "No (Descriptive only)"),
        ("Hlosta et al. (2017)", "OULAD (VLE clicks)", "Random Forest / XGBoost", "AUC = 0.84", "No (Admin alerts)", "No (Binary risk score)"),
        ("Nguyen et al. (2018)", "LMS Clickstreams", "Hierarchical Clustering", "Silhouette = 0.38", "No (Static plots)", "No (Fixed cluster labels)"),
        ("Rizvi et al. (2019)", "OULAD Subsets", "Gaussian Mixture Models", "BIC / AIC fit", "No (Offline)", "No (Soft probabilities)"),
        ("EduCluster (This Work)", "OULAD (14,003 enrolments)", "K-Means++ (k=4) + 2D PCA", "Silhouette = 0.4272", "Yes (3-Step SaaS)", "Yes (4-Week Habit Plan)")
    ]

    for r_idx, row in enumerate(data, start=1):
        bg = RGBColor(0xEE, 0xF2, 0xFF) if r_idx == 5 else (COLOR_WHITE if r_idx % 2 == 1 else COLOR_CARD_BG)
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(9)
                p.alignment = PP_ALIGN.CENTER if c_idx >= 3 else PP_ALIGN.LEFT
                if r_idx == 5:
                    p.font.bold = True
                    p.font.color.rgb = COLOR_BLUE
                else:
                    p.font.color.rgb = COLOR_SLATE_DARK

    # 3 Critical Gap Callouts below table
    gap_y = Inches(4.90)
    gap_w = Inches(3.64)
    gap_h = Inches(1.85)

    g1 = create_card(slide, Inches(0.92), gap_y, gap_w, gap_h, "Gap 1: Black-Box Opacity", COLOR_CORAL)
    p1 = g1.text_frame.add_paragraph()
    p1.text = "Existing predictive early warning systems output raw risk probabilities without explainable behavioral archetypes that students can understand and act upon."
    p1.font.size = Pt(8.5)

    g2 = create_card(slide, Inches(0.92) + gap_w + Inches(0.29), gap_y, gap_w, gap_h, "Gap 2: Lack of Actionable Prescription", COLOR_AMBER)
    p2 = g2.text_frame.add_paragraph()
    p2.text = "Warning a student they have a '68% dropout probability' induces anxiety. EduCluster shifts from descriptive warnings to concrete, metric-specific 4-week recovery roadmaps."
    p2.font.size = Pt(8.5)

    g3 = create_card(slide, Inches(0.92) + (gap_w + Inches(0.29)) * 2, gap_y, gap_w, gap_h, "Gap 3: Zero Real-Time What-If Feedback", COLOR_EMERALD)
    p3 = g3.text_frame.add_paragraph()
    p3.text = "EduCluster introduces instant counterfactual feedback: students manipulate 5 behavioral dials to see immediate readiness gains (+6 pts) and unlock higher performance tiers."
    p3.font.size = Pt(8.5)


def build_slide_7(prs):
    """Slide 7: Optimal Cluster Selection (k=4)"""
    layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(layout)
    apply_footer(slide, 7)
    add_slide_header(slide, "Optimal Cluster Selection & Mathematical Validation", "Determining Optimal k via Silhouette Maximization, WCSS Elbow & 2D PCA Variance")

    # Left: Embed Fig 2
    chart_img = FIGURES_DIR / "fig2_k_optimization.png"
    if chart_img.exists():
        slide.shapes.add_picture(str(chart_img), Inches(0.92), Inches(1.95), width=Inches(6.4))

    # Right: Mathematical Analysis Cards
    right_x = Inches(7.55)
    card_w = Inches(4.87)

    c1 = create_card(slide, right_x, Inches(1.95), card_w, Inches(1.45), "Peak Silhouette Score at k = 4", COLOR_EMERALD)
    tf1 = c1.text_frame
    p1 = tf1.add_paragraph()
    p1.text = "• Global maximum at k = 4 (Silhouette = 0.4272), confirming optimal intra-cluster cohesion and inter-cluster separation."
    p1.font.size = Pt(8.5)
    p1_2 = tf1.add_paragraph()
    p1_2.text = "• Significantly outperforms k = 3 (0.368) and k = 5 (0.395), preventing over-fragmentation."
    p1_2.font.size = Pt(8.5)

    c2 = create_card(slide, right_x, Inches(3.55), card_w, Inches(1.45), "Inertia Elbow Point Curvature", COLOR_BLUE)
    tf2 = c2.text_frame
    p2 = tf2.add_paragraph()
    p2.text = "• WCSS drops from 184,200 (k=2) to 112,450 (k=4). Beyond k=4, rate of variance reduction diminishes sharply."
    p2.font.size = Pt(8.5)
    p2_2 = tf2.add_paragraph()
    p2_2.text = "• Matches heuristic elbow criterion while preserving 4 pedagogically actionable tiers."
    p2_2.font.size = Pt(8.5)

    c3 = create_card(slide, right_x, Inches(5.15), card_w, Inches(1.55), "2D PCA Dimensionality Reduction", COLOR_NAVY)
    tf3 = c3.text_frame
    p3 = tf3.add_paragraph()
    p3.text = "• Top 2 principal components capture 88.3% cumulative variance (PC1 = 80.7%, PC2 = 7.5%)."
    p3.font.size = Pt(8.5)
    p3_2 = tf3.add_paragraph()
    p3_2.text = "• Verifies that 16-feature space projects onto a clean 2D planar map with distinct Voronoi centroid territories."
    p3_2.font.size = Pt(8.5)


def build_slide_8(prs):
    """Slide 8: The 4 Discovered Learner Personas"""
    layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(layout)
    apply_footer(slide, 8)
    add_slide_header(slide, "The 4 Discovered Learner Personas", "Cluster Centroid Distributions, Key Behavioral Traits, and Prescriptive Strategies")

    card_w = Inches(5.6)
    card_h = Inches(2.28)
    gap_x = Inches(0.3)
    gap_y = Inches(0.20)
    top_row = Inches(1.95)
    bot_row = Inches(4.43)

    # Top-Left: Thriving Self-Starter
    c1 = create_card(slide, Inches(0.92), top_row, card_w, card_h, "🌟 Thriving Self-Starter (22.4% | N = 3,141)", COLOR_EMERALD, RGBColor(0xF0, 0xFD, 0xFA), RGBColor(0x99, 0xF6, 0xE4))
    tf1 = c1.text_frame
    pts1 = [
        ("Behavioral Telemetry:", "High total clicks (~2,850), early submissions (-4.2 days early), 86.5% quiz avg."),
        ("Cognitive Strategy:", "Deep reading, continuous revision, high forum collaboration, and early momentum."),
        ("Prescriptive Roadmap:", "Honors acceleration, peer code review mentorship, capstone research exploration.")
    ]
    for k, v in pts1:
        p = tf1.add_paragraph()
        p.text = f"• {k} {v}"
        p.font.size = Pt(8.5)
        p.space_after = Pt(2)

    # Top-Right: Steady Builder
    c2 = create_card(slide, Inches(0.92) + card_w + gap_x, top_row, card_w, card_h, "📈 Steady Builder (37.4% | N = 5,240) — Largest Cohort", COLOR_BLUE, RGBColor(0xEE, 0xF2, 0xFF), RGBColor(0xC7, 0xD2, 0xFE))
    tf2 = c2.text_frame
    pts2 = [
        ("Behavioral Telemetry:", "Consistent active days (85%), punctual coursework (-1.2 days early), solid scores (72.4%)."),
        ("Cognitive Strategy:", "Disciplined attendance, methodical textbook study, responds well to stretch milestones."),
        ("Prescriptive Roadmap:", "Consistency-to-distinction coaching, timed mock exam drills, bridging 75% → 90%+ scores.")
    ]
    for k, v in pts2:
        p = tf2.add_paragraph()
        p.text = f"• {k} {v}"
        p.font.size = Pt(8.5)
        p.space_after = Pt(2)

    # Bottom-Left: Quiet Observer
    c3 = create_card(slide, Inches(0.92), bot_row, card_w, card_h, "🎧 Quiet Observer (22.7% | N = 3,185)", COLOR_AMBER, RGBColor(0xFF, 0xFB, 0xEB), RGBColor(0xFD, 0xE6, 0x8A))
    tf3 = c3.text_frame
    pts3 = [
        ("Behavioral Telemetry:", "Low portal clicks (~340), baseline scores (58.6%), concentrated study bursts near deadlines."),
        ("Cognitive Strategy:", "Capable foundation but passive interaction; minimal discussion participation and cramming risk."),
        ("Prescriptive Roadmap:", "Micro-learning activation, 15-min daily study streaks, structured discussion prompts.")
    ]
    for k, v in pts3:
        p = tf3.add_paragraph()
        p.text = f"• {k} {v}"
        p.font.size = Pt(8.5)
        p.space_after = Pt(2)

    # Bottom-Right: Support-Priority Learner
    c4 = create_card(slide, Inches(0.92) + card_w + gap_x, bot_row, card_w, card_h, "🆘 Support-Priority Learner (17.4% | N = 2,437)", COLOR_CORAL, RGBColor(0xFE, 0xF2, 0xF2), RGBColor(0xFE, 0xCA, 0xCA))
    tf4 = c4.text_frame
    pts4 = [
        ("Behavioral Telemetry:", "Severe attendance gaps (<25 days), late submissions (+8.4 days delay), struggling scores (31.2%)."),
        ("Cognitive Strategy:", "Severe prerequisite deficits, disengagement spirals, high risk of early withdrawal."),
        ("Prescriptive Roadmap:", "Foundational scaffolding, 1-on-1 faculty/TA check-in sprints, deadline triage and rescue.")
    ]
    for k, v in pts4:
        p = tf4.add_paragraph()
        p.text = f"• {k} {v}"
        p.font.size = Pt(8.5)
        p.space_after = Pt(2)


def build_slide_9(prs):
    """Slide 9: Extrinsic Validation Against Teacher Grades"""
    layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(layout)
    apply_footer(slide, 9)
    add_slide_header(slide, "Extrinsic Validation Against Teacher Grades", "Ground-Truth Alignment Proving Behavioral Telemetry Successfully Reconstructs Academic Outcomes")

    # Left: Embed Fig 3
    matrix_img = FIGURES_DIR / "fig3_contingency_matrix.png"
    if matrix_img.exists():
        slide.shapes.add_picture(str(matrix_img), Inches(0.92), Inches(1.95), width=Inches(6.4))

    # Right: Statistical Proof Cards
    right_x = Inches(7.55)
    card_w = Inches(4.87)

    c1 = create_card(slide, right_x, Inches(1.95), card_w, Inches(1.50), "Statistical Validation Metrics", COLOR_NAVY)
    tf1 = c1.text_frame
    p1 = tf1.add_paragraph()
    p1.text = "• Chi-Square Test: χ² = 11,833.21 (p < 0.0001, df = 9), demonstrating non-random distribution across outcome tiers."
    p1.font.size = Pt(8.5)
    p1_2 = tf1.add_paragraph()
    p1_2.text = "• Normalized Mutual Information (NMI) = 0.3172."
    p1_2.font.size = Pt(8.5)
    p1_3 = tf1.add_paragraph()
    p1_3.text = "• Cramér's V = 0.5307, proving a strong practical association between clusters and final academic grades."
    p1_3.font.size = Pt(8.5)

    c2 = create_card(slide, right_x, Inches(3.60), card_w, Inches(1.50), "Empirical Outcome Concordance", COLOR_EMERALD)
    tf2 = c2.text_frame
    p2 = tf2.add_paragraph()
    p2.text = "• 96.9% of Thriving Self-Starters achieve Distinction (58.6%) or Pass (38.2%)."
    p2.font.size = Pt(8.5)
    p2_2 = tf2.add_paragraph()
    p2_2.text = "• 84.2% of Steady Builders achieve Pass (74.3%) or Distinction (9.9%)."
    p2_2.font.size = Pt(8.5)
    p2_3 = tf2.add_paragraph()
    p2_3.text = "• 96.7% of Support-Priority Learners represent Fail (51.9%) or Withdrawn (44.8%), with exactly 0 Distinctions."
    p2_3.font.size = Pt(8.5)

    c3 = create_card(slide, right_x, Inches(5.25), card_w, Inches(1.45), "Pedagogical Implications", COLOR_BLUE)
    tf3 = c3.text_frame
    p3 = tf3.add_paragraph()
    p3.text = "• Proves that digital behavioral footprints accurately forecast academic trajectories early in the term without grade labels."
    p3.font.size = Pt(8.5)
    p3_2 = tf3.add_paragraph()
    p3_2.text = "• Early detection allows timely intervention before course dropouts become permanent."
    p3_2.font.size = Pt(8.5)


def build_slide_10(prs):
    """Slide 10: Deployed Prototype: Student Self-Check & What-If Simulator"""
    layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(layout)
    apply_footer(slide, 10)
    add_slide_header(slide, "Deployed Prototype: Student Self-Check & Simulator", "Client-Ready Streamlit SaaS Interface for Real-Time Pacing & Counterfactual Diagnosis")

    # Left: Screenshot 82
    shot_img = SCREENSHOTS_DIR / "screenshot_82.png"
    if shot_img.exists():
        slide.shapes.add_picture(str(shot_img), Inches(0.92), Inches(1.95), width=Inches(6.4))

    # Right: UX Highlights Cards
    right_x = Inches(7.55)
    card_w = Inches(4.87)

    c1 = create_card(slide, right_x, Inches(1.95), card_w, Inches(1.45), "1-Click Presets & 5 Behavioral Dials", COLOR_BLUE)
    tf1 = c1.text_frame
    p1 = tf1.add_paragraph()
    p1.text = "• 1-Click quick presets: 'Regular Topper', 'Deadline Crammer', 'Quiet Portal User', 'Falling Behind'."
    p1.font.size = Pt(8.5)
    p1_2 = tf1.add_paragraph()
    p1_2.text = "• 5 plain-English dials: Total VLE Clicks, On-Time Submissions (%), Assessment Score (%), Forum Activity (%), Active Study Days (%)."
    p1_2.font.size = Pt(8.5)

    c2 = create_card(slide, right_x, Inches(3.55), card_w, Inches(1.45), "Circular Readiness Gauge & Benchmark", COLOR_EMERALD)
    tf2 = c2.text_frame
    p2 = tf2.add_paragraph()
    p2.text = "• Plotly Indicator circular gauge with multi-tier colored background ranges and dynamic tier color coding."
    p2.font.size = Pt(8.5)
    p2_2 = tf2.add_paragraph()
    p2_2.text = "• Horizontal grouped bar chart benchmarks student's current habits vs. top-performer targets."
    p2_2.font.size = Pt(8.5)

    c3 = create_card(slide, right_x, Inches(5.15), card_w, Inches(1.55), "Live 'What-If' Counterfactual Simulator", COLOR_CORAL)
    tf3 = c3.text_frame
    p3 = tf3.add_paragraph()
    p3.text = "• Identifies the student's #1 growth bottleneck and projects actionable readiness gains in real time."
    p3.font.size = Pt(8.5)
    p3_2 = tf3.add_paragraph()
    p3_2.text = "• Example: 'Raising Forum Activity from 15% to 40% (+25%) lifts readiness by +6 pts to 78/100, unlocking Steady Builder!'"
    p3_2.font.size = Pt(8.5)


def build_slide_11(prs):
    """Slide 11: Dynamic 4-Week Study Plan & Faculty Validation Hub"""
    layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(layout)
    apply_footer(slide, 11)
    add_slide_header(slide, "Dynamic 4-Week Study Plan & Faculty Validation Hub", "Bridging Individualized Student Action with Faculty Cohort Supervision")

    # Top Half: 2 side-by-side screenshots
    shot83 = SCREENSHOTS_DIR / "screenshot_83.png"
    shot84 = SCREENSHOTS_DIR / "screenshot_84.png"
    half_w = Inches(5.6)
    img_h = Inches(3.05)

    if shot83.exists():
        slide.shapes.add_picture(str(shot83), Inches(0.92), Inches(1.95), width=half_w)
    if shot84.exists():
        slide.shapes.add_picture(str(shot84), Inches(0.92) + half_w + Inches(0.3), Inches(1.95), width=half_w)

    # Bottom Half: 3 Feature Cards
    bot_y = Inches(5.15)
    card_w = Inches(3.64)
    gap = Inches(0.29)
    card_h = Inches(1.55)

    c1 = create_card(slide, Inches(0.92), bot_y, card_w, card_h, "Two-Layer Roadmap Engine", COLOR_BLUE)
    tf1 = c1.text_frame
    p1 = tf1.add_paragraph()
    p1.text = "• Layer 1 sets persona tier strategy (Honors vs. Rescue); Layer 2 injects custom tasks citing exact current % and target % for lowest habits."
    p1.font.size = Pt(8.0)

    c2 = create_card(slide, Inches(0.92) + card_w + gap, bot_y, card_w, card_h, "Stateful Interactive Pacing", COLOR_EMERALD)
    tf2 = c2.text_frame
    p2 = tf2.add_paragraph()
    p2.text = "• Unique namespaced checkbox keys prevent state collisions and compute real-time progress (% tasks finished). Supports 1-click Markdown export."
    p2.font.size = Pt(8.0)

    c3 = create_card(slide, Inches(0.92) + (card_w + gap) * 2, bot_y, card_w, card_h, "Faculty Validation Hub (2D PCA)", COLOR_NAVY)
    tf3 = c3.text_frame
    p3 = tf3.add_paragraph()
    p3.text = "• Real-time 2D PCA scatter plot displaying the simulated student's golden star position against the entire 14,003 student population."
    p3.font.size = Pt(8.0)


def build_slide_12(prs):
    """Slide 12: Comparative Baselines, Limitations & Future Work"""
    layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(layout)
    apply_footer(slide, 12)
    add_slide_header(slide, "Comparative Baselines, Limitations & Future Roadmap", "Rigorous Algorithmic Benchmarks, Architectural Constraints & Next-Gen Directions")

    # Top: Comparative Algorithm Table
    rows, cols = 5, 6
    left, top, width, height = Inches(0.92), Inches(1.95), Inches(11.5), Inches(2.25)
    table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table

    table.columns[0].width = Inches(2.1)
    table.columns[1].width = Inches(1.6)
    table.columns[2].width = Inches(1.9)
    table.columns[3].width = Inches(1.8)
    table.columns[4].width = Inches(2.1)
    table.columns[5].width = Inches(2.0)

    headers = ["Clustering Algorithm", "Silhouette Score", "Calinski-Harabasz", "Inference Speed", "Interpretability", "Prescriptive Roadmap?"]
    for c_idx, h in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_NAVY
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(9)
            p.font.bold = True
            p.font.color.rgb = COLOR_WHITE
            p.alignment = PP_ALIGN.CENTER

    benchmarks = [
        ("K-Means++ (EduCluster)", "0.4272", "4,892.4", "< 10 ms (Real-Time)", "High (Direct Centroids)", "Dynamic 4-Week Roadmap"),
        ("Ward's Hierarchical", "0.3814", "4,115.2", "Prohibitive O(N² log N)", "Moderate (Dendrogram cutoff)", "Static Cluster Assignment"),
        ("Gaussian Mixture (GMM)", "0.3421", "3,780.9", "Moderate O(N·k·d²)", "Low (Overlapping Gaussians)", "Soft Probabilities (Ambiguous)"),
        ("DBSCAN (Density-Based)", "0.2985", "2,840.1", "Fast O(N log N)", "Poor (58% Noise Outliers)", "Infeasible (Unclustered)")
    ]

    for r_idx, row in enumerate(benchmarks, start=1):
        bg = RGBColor(0xEE, 0xF2, 0xFF) if r_idx == 1 else (COLOR_WHITE if r_idx % 2 == 1 else COLOR_CARD_BG)
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(8.5)
                p.alignment = PP_ALIGN.CENTER if c_idx >= 1 else PP_ALIGN.LEFT
                if r_idx == 1:
                    p.font.bold = True
                    p.font.color.rgb = COLOR_BLUE
                else:
                    p.font.color.rgb = COLOR_SLATE_DARK

    # Bottom Half: 2 Columns for Limitations & Future Work
    bot_y = Inches(4.45)
    card_w = Inches(5.6)
    gap_x = Inches(0.3)
    card_h = Inches(2.25)

    # Bottom Left: Limitations
    c_lim = create_card(slide, Inches(0.92), bot_y, card_w, card_h, "Current Architectural Limitations", COLOR_AMBER)
    tf_l = c_lim.text_frame
    lims = [
        ("Static Window Aggregation:", "Features are currently compiled across full-semester logs, limiting sensitivity to rapid week-by-week velocity drops."),
        ("Single Institution Benchmark:", "Evaluated primarily on the OULAD distance-learning dataset; transferability across in-person K-12 requires domain tuning."),
        ("Subject-Domain Variation:", "STEM courses exhibit different clickstream frequencies than humanities courses, requiring modular normalization.")
    ]
    for k, v in lims:
        p = tf_l.add_paragraph()
        p.text = f"• {k} {v}"
        p.font.size = Pt(8.5)
        p.space_after = Pt(2.5)

    # Bottom Right: Future Roadmap
    c_fut = create_card(slide, Inches(0.92) + card_w + gap_x, bot_y, card_w, card_h, "Future Research & Engineering Roadmap", COLOR_EMERALD)
    tf_f = c_fut.text_frame
    futs = [
        ("Longitudinal Sliding Windows:", "Implement rolling 14-day temporal clustering to detect velocity declines by Week 4."),
        ("Autonomous LLM Mentor Agent:", "Connect student habit profiles to an AI mentor that conducts daily conversational check-ins via chat."),
        ("LTI 1.3 Canvas/Moodle Plugin:", "Package the engine into a certified LTI app delivering push-notification nudges directly to student phones.")
    ]
    for k, v in futs:
        p = tf_f.add_paragraph()
        p.text = f"• {k} {v}"
        p.font.size = Pt(8.5)
        p.space_after = Pt(2.5)


# -----------------------------------------------------------------------------
# Main Orchestrator
# -----------------------------------------------------------------------------

def main():
    print(f"Loading template from {TEMPLATE_PATH}...")
    prs = pptx.Presentation(str(TEMPLATE_PATH))

    # Build all 12 slides
    print("Building Slide 1: Title Slide...")
    build_slide_1(prs)

    print("Building Slide 2: Problem Statement...")
    build_slide_2(prs)

    print("Building Slide 3: Target Users & Dual Stakeholder Value...")
    build_slide_3(prs)

    print("Building Slide 4: End-to-End Pipeline...")
    build_slide_4(prs)

    print("Building Slide 5: Dataset & 16 Features...")
    build_slide_5(prs)

    print("Building Slide 6: SOTA Synthesis & Gap...")
    build_slide_6(prs)

    print("Building Slide 7: Optimal Cluster Selection...")
    build_slide_7(prs)

    print("Building Slide 8: The 4 Discovered Learner Personas...")
    build_slide_8(prs)

    print("Building Slide 9: Extrinsic Validation Against Teacher Grades...")
    build_slide_9(prs)

    print("Building Slide 10: Deployed Prototype: Student Self-Check...")
    build_slide_10(prs)

    print("Building Slide 11: Dynamic 4-Week Study Plan & Faculty Hub...")
    build_slide_11(prs)

    print("Building Slide 12: Comparative Baselines, Limitations & Future Work...")
    build_slide_12(prs)

    # Drop the initial blank slide from the template cleanly using prs.part.drop_rel
    print("Cleanly dropping initial blank slide (index 0) using drop_rel...")
    rId = prs.slides._sldIdLst[0].rId
    prs.part.drop_rel(rId)
    del prs.slides._sldIdLst[0]

    print(f"Total slides in generated presentation: {len(prs.slides)}")
    prs.save(str(OUTPUT_PATH))
    print(f"Successfully saved {OUTPUT_PATH} ({OUTPUT_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

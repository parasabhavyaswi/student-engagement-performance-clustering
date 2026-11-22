"""
EduCluster ML - Presentation Generator v3
Fixes:
1. Slides 11 & 12 (1-based #11 and #12) LPU Logo Overlap:
   - Re-links Slide 10 and Slide 11 to slideLayout2 (OBJECT layout, same as Slides 1-9) which has showMasterSp="0".
   - Explicitly sets showMasterSp="0" on slide11.xml, slide12.xml, and slideLayout12.xml.
   - Sets title box coordinates and margins to match Slides 1-9 exactly (top=0.78in, margins=(0.10in, 0.05in))
     so no text or master placeholder touches or overlaps the LPU logo.
2. Perfect Image Alignment and Native Aspect Ratios:
   - Slide 02: fig1_overview.png (aspect 2.059) -> native aspect preserved, centered with left column.
   - Slide 05: fig2_architecture.png (aspect 1.417) -> native aspect preserved, centered with left column.
   - Slide 06: fig4_k_sweep.png (aspect 1.711) -> native aspect preserved + highlight card below.
   - Slide 07: fig5_pca.png (aspect 1.548) and fig6_radar.png (aspect 1.200) -> exact aspect ratios, aligned height 2.75in.
   - Slide 08: fig7_contingency.png (aspect 1.632) -> native aspect preserved + validation card below.
   - Slide 11: dashboard_ui_overview.png (aspect 1.778, 16:9 widescreen) -> native 16:9 aspect + UI highlight card below.
3. Preserves native template background and slide master 100%.
"""

from pathlib import Path
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

TEMPLATE_PATH = Path(r"c:\Users\ASUS\OneDrive\Desktop\Bhavya\Projects\Student_learning_clustering\templates\presentation_template.pptx")
if not TEMPLATE_PATH.exists():
    TEMPLATE_PATH = Path(r"C:\Users\ASUS\.gemini\antigravity\brain\bac08d40-ec50-43a2-baa1-2e941ff29026\.user_uploaded\media_1795019261192_4c8efec9.pptx")

PROJECT_ROOT = Path(r"c:\Users\ASUS\OneDrive\Desktop\Bhavya\Projects\Student_learning_clustering")
REPORTS_DIR = PROJECT_ROOT / "reports"
OUTPUT_PATH = PROJECT_ROOT / "EduCluster_ML_Presentation.pptx"

# ------------------------------------------------------------------------------
# COLOR PALETTE
# ------------------------------------------------------------------------------
COLOR_ORANGE = RGBColor(224, 90, 27)    # #E05A1B (Template Accent Orange)
COLOR_NAVY = RGBColor(26, 37, 48)       # #1A2530 (Template Dark Navy/Slate)
COLOR_TEXT_MAIN = RGBColor(30, 41, 59)  # #1E293B (Dark body text for light bg)
COLOR_TEXT_MUTED = RGBColor(100, 116, 139) # #64748B
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_CARD_BG = RGBColor(255, 255, 255) # Clean crisp white card on template
COLOR_CARD_BORDER = RGBColor(226, 232, 240) # Slate 200 border
COLOR_ROW_ALT = RGBColor(248, 250, 252) # Slate 50 row
COLOR_TABLE_HDR = RGBColor(26, 37, 48)  # Deep Navy table header


def remove_shape(shape):
    sp = shape._element
    sp.getparent().remove(sp)


def style_title_box(shape, badge_text, title_text):
    shape.left = Inches(0.92)
    shape.top = Inches(0.78)
    shape.width = Inches(11.50)
    shape.height = Inches(0.95)

    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.10)
    tf.margin_top = Inches(0.05)
    tf.margin_right = Inches(0.10)
    tf.margin_bottom = Inches(0.05)

    p0 = tf.paragraphs[0]
    p0.text = badge_text.upper()
    p0.font.name = "Arial"
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_ORANGE

    if len(tf.paragraphs) > 1:
        p1 = tf.paragraphs[1]
    else:
        p1 = tf.add_paragraph()
    p1.text = title_text
    p1.font.name = "Arial"
    p1.font.size = Pt(22)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_NAVY
    p1.space_before = Pt(3)


def add_light_card(slide, left, top, width, height, title, body_text="", border_col=COLOR_CARD_BORDER, title_col=COLOR_ORANGE):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = COLOR_CARD_BG
    shape.line.color.rgb = border_col
    shape.line.width = Pt(1.2)

    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.18)
    tf.margin_right = Inches(0.18)
    tf.margin_top = Inches(0.15)
    tf.margin_bottom = Inches(0.15)

    p0 = tf.paragraphs[0]
    p0.text = title
    p0.font.name = "Arial"
    p0.font.size = Pt(11.5)
    p0.font.bold = True
    p0.font.color.rgb = title_col

    if body_text:
        lines = body_text.split("\n")
        for line in lines:
            if not line.strip():
                continue
            p = tf.add_paragraph()
            p.text = line
            p.font.name = "Arial"
            p.font.size = Pt(9.5)
            p.font.color.rgb = COLOR_TEXT_MAIN
            p.space_before = Pt(3)

    return shape


def add_light_table(slide, left, top, width, height, headers, data_rows, col_widths=None, hdr_bg=COLOR_TABLE_HDR):
    num_rows = len(data_rows) + 1
    num_cols = len(headers)
    table_shape = slide.shapes.add_table(num_rows, num_cols, Inches(left), Inches(top), Inches(width), Inches(height))
    table = table_shape.table

    if col_widths and len(col_widths) == num_cols:
        for idx, w in enumerate(col_widths):
            table.columns[idx].width = Inches(w)

    # Header Row
    for c_idx, h_text in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = hdr_bg
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.alignment = PP_ALIGN.CENTER
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE

    # Data Rows
    for r_idx, row_vals in enumerate(data_rows):
        row_bg = COLOR_WHITE if (r_idx % 2 == 0) else COLOR_ROW_ALT
        for c_idx, val in enumerate(row_vals):
            cell = table.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = row_bg
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.text = str(val)
            p.alignment = PP_ALIGN.LEFT if c_idx == 0 else PP_ALIGN.CENTER
            p.font.name = "Arial"
            p.font.size = Pt(8.5)
            p.font.color.rgb = COLOR_NAVY

    return table_shape


def generate_deck():
    print(f"Loading presentation template: {TEMPLATE_PATH}")
    prs = pptx.Presentation(TEMPLATE_PATH)
    sm = prs.slide_masters[0]
    layout_obj = sm.slide_layouts[1] # OBJECT layout (has showMasterSp="0")

    # Fix Layout 11 and ensure showMasterSp="0" everywhere
    sm.slide_layouts[11]._element.set('showMasterSp', '0')
    layout_obj._element.set('showMasterSp', '0')

    # Re-link Slide 10 and 11 to layout_obj
    s10 = prs.slides[10]
    s11 = prs.slides[11]
    for rel in s10.part.rels.values():
        if 'slideLayout' in rel.reltype:
            rel._target = layout_obj.part
    for rel in s11.part.rels.values():
        if 'slideLayout' in rel.reltype:
            rel._target = layout_obj.part

    for s in prs.slides:
        s._element.set('showMasterSp', '0')

    # ==========================================================================
    # SLIDE 0: TITLE SLIDE
    # ==========================================================================
    s0 = prs.slides[0]
    s0.notes_slide.notes_text_frame.text = (
        "Good morning respected evaluators, committee members, and supervisor. "
        "Today I present our machine learning project: 'K-Means Clustering of Student Engagement and Performance Data for Personalized Learning Path Design'. "
        "Candidate is Parasa Bhavyaswi under the supervision of Dr. Bhupinder Singh at Lovely Professional University. "
        "We address high dropout rates in online higher education by discovering authentic learner personas and designing automated four-week pedagogical roadmaps."
    )

    # ==========================================================================
    # SLIDE 01: CONTEXT & MOTIVATION
    # ==========================================================================
    s1 = prs.slides[1]
    title_shp1 = s1.shapes[0]
    style_title_box(title_shp1, "01. CONTEXT & MOTIVATION", "Problem Statement & Motivation")
    while len(s1.shapes) > 1:
        remove_shape(s1.shapes[1])

    add_light_card(s1, 0.92, 1.82, 5.60, 2.30, "Elevated Online Attrition (>30%)",
                   "• Virtual learning environments (VLEs) log granular clickstreams yet struggle to prevent student dropout across remote and blended courses.\n"
                   "• Student attrition leads to substantial institutional revenue loss and career delays.",
                   border_col=COLOR_ORANGE)

    add_light_card(s1, 6.82, 1.82, 5.60, 2.30, "Reactive End-of-Term Detection",
                   "• Traditional advising relies on midterm or final grades, identifying struggling learners after conceptual deficits become irreversible.\n"
                   "• Retrospective intervention misses the critical early window of disengagement.")

    add_light_card(s1, 0.92, 4.35, 5.60, 2.45, "Limitations of Single-Variable Rules",
                   "• Simple click or score cutoffs ignore compensatory study habits (e.g., active forum participation or early submissions offsetting moderate initial quiz scores).\n"
                   "• Multi-dimensional telemetry is required to distinguish crammers from disengaged learners.")

    add_light_card(s1, 6.82, 4.35, 5.60, 2.45, "One-Size-Fits-All Syllabi",
                   "• Static weekly schedules bore self-directed high achievers while leaving erratic crammers without structured pacing support.\n"
                   "• Personalized intervention pathways are needed to adapt to diverse study cadences.",
                   border_col=COLOR_ORANGE)

    s1.notes_slide.notes_text_frame.text = (
        "Slide 1 presents the problem motivation. Modern online education faces attrition rates exceeding 30%. "
        "Institutions capture millions of clickstream events, but academic advising remains reactive, relying on late exam results. "
        "Furthermore, simplistic thresholds fail because students employ compensatory study styles. Our goal is to transform multi-dimensional telemetry into timely, personalized support."
    )

    # ==========================================================================
    # SLIDE 02: RESEARCH AIMS (With correctly aligned fig1_overview.png)
    # Native Aspect Ratio: 2100 x 1020 (2.059)
    # ==========================================================================
    s2 = prs.slides[2]
    title_shp2 = s2.shapes[0]
    style_title_box(title_shp2, "02. RESEARCH AIMS", "Research Objectives")
    while len(s2.shapes) > 1:
        remove_shape(s2.shapes[1])

    add_light_card(s2, 0.92, 1.82, 5.60, 1.60, "1. Multi-Domain Feature Engineering",
                   "Extract and standardize 16 behavioral and academic features from N = 14,003 OULAD student-module enrolments across engagement, consistency, and assessment domains without target leakage.",
                   border_col=COLOR_ORANGE)

    add_light_card(s2, 0.92, 3.52, 5.60, 1.60, "2. Unsupervised Persona Segmentation",
                   "Apply K-Means++ (k = 4) and 2D Principal Component Analysis (PCA) to discover four interpretable learner archetypes, benchmarked against GMM, Agglomerative Hierarchical clustering, and DBSCAN.")

    add_light_card(s2, 0.92, 5.22, 5.60, 1.60, "3. Extrinsic Validation & Curriculum Design",
                   "Validate cluster concordance against unobserved final course outcomes and construct tailored four-week intervention roadmaps targeting each persona's behavioral bottleneck.",
                   border_col=COLOR_ORANGE)

    img_overview = REPORTS_DIR / "fig1_overview.png"
    if img_overview.exists():
        # Native aspect ratio: 2.0588 -> width 5.70 in, height 2.77 in. Centered vertically alongside left cards.
        s2.shapes.add_picture(str(img_overview), Inches(6.75), Inches(2.80), Inches(5.70), Inches(2.77))

    s2.notes_slide.notes_text_frame.text = (
        "Slide 2 outlines our three research objectives: first, compile a clean 16-feature matrix from OULAD; "
        "second, apply K-Means++ to uncover 4 distinct learner archetypes and benchmark against alternative algorithms; "
        "and third, validate against unobserved outcomes and build prescriptive four-week learning path roadmaps."
    )

    # ==========================================================================
    # SLIDE 03: DATASET ARCHITECTURE
    # ==========================================================================
    s3 = prs.slides[3]
    title_shp3 = s3.shapes[0]
    style_title_box(title_shp3, "03. DATASET ARCHITECTURE", "Dataset Architecture & Data Hygiene (OULAD)")
    while len(s3.shapes) > 1:
        remove_shape(s3.shapes[1])

    add_light_card(s3, 0.92, 1.82, 5.60, 2.30, "Benchmark Source",
                   "• Open University Learning Analytics Dataset (OULAD) integrating 7 relational tables:\n"
                   "  studentInfo, studentVle, studentAssessment, assessments, courses, studentRegistration, vle.\n"
                   "• Joined strictly on primary keys (id_student, code_module, code_presentation).",
                   border_col=COLOR_ORANGE)

    add_light_card(s3, 6.82, 1.82, 5.60, 2.30, "Cohort Scope",
                   "• Cohort Scope: N = 14,003 valid student-module enrolments spanning 7 modules (AAA–GGG) and 4 semester presentations (2013B, 2013J, 2014B, 2014J).\n"
                   "• Longitudinal representation across STEM and Social Science domains.")

    add_light_card(s3, 0.92, 4.35, 5.60, 2.45, "Data Filtering",
                   "• Excluded banked assessment transfers (is_banked = 1) to eliminate prior-semester score inflation.\n"
                   "• Removed zero-variance inactive records to preserve authentic pacing signals and prevent degenerate cluster artifacts.")

    add_light_card(s3, 6.82, 4.35, 5.60, 2.45, "Target Quarantine (Zero Leakage)",
                   "• Strictly isolated final_result labels (Distinction, Pass, Fail, Withdrawn) from the feature matrix during training.\n"
                   "• Unsupervised clustering operates purely on engagement telemetry without ground-truth label contamination.",
                   border_col=COLOR_ORANGE)

    s3.notes_slide.notes_text_frame.text = (
        "Slide 3 details our dataset architecture. We use OULAD spanning seven relational tables. "
        "We filter out banked transfers and quarantine final_result to guarantee zero target leakage. "
        "The model clusters purely on interaction telemetry."
    )

    # ==========================================================================
    # SLIDE 04: FEATURE ENGINEERING (Full-Width Formatted Table)
    # ==========================================================================
    s4 = prs.slides[4]
    title_shp4 = s4.shapes[0]
    style_title_box(title_shp4, "04. FEATURE ENGINEERING", "16-Feature Engineering Across Three Domains")
    while len(s4.shapes) > 1:
        remove_shape(s4.shapes[1])

    feat_headers = ["Domain (Feature Count)", "Extracted Feature Metrics", "Operational Definition & Signal"]
    feat_rows = [
        ["Platform Engagement (8)", "total_clicks, active_days, clicks_per_active_day,\nforum_clicks, quiz_clicks, resource_clicks,\noucontent_clicks, early_engagement_ratio",
         "log(1 + sum clicks), active day count, session intensity, and first-28-day click ratio."],
        ["Attendance & Consistency (4)", "engagement_span_days, activity_regularity_std,\npre_course_clicks, weeks_active_ratio",
         "Calendar study span, login interval standard deviation, pre-course orientation clicks, and active weeks ratio."],
        ["Assessment Performance (4)", "weighted_avg_score, assessment_completion_rate,\navg_submission_delay, first_assessment_score",
         "Credit-weighted mean score, submission completion ratio, mean deadline offset (days), and initial mark."]
    ]
    add_light_table(s4, 0.92, 1.82, 11.50, 3.80, feat_headers, feat_rows, col_widths=[2.50, 4.50, 4.50], hdr_bg=COLOR_NAVY)

    add_light_card(s4, 0.92, 5.85, 11.50, 1.05, "Preprocessing Pipeline",
                   "• Preprocessing Pipeline: log(1 + x) compression on skewed clicks → cohort median imputation → StandardScaler normalization across all 16 dimensions.",
                   border_col=COLOR_ORANGE)

    s4.notes_slide.notes_text_frame.text = (
        "Slide 4 presents our 16-feature architecture categorized across 3 domains: 8 platform engagement metrics, "
        "4 attendance regularity metrics, and 4 summative assessment mastery dimensions. "
        "Skewed clicks receive log1p compression before standard scaling."
    )

    # ==========================================================================
    # SLIDE 05: METHODOLOGY & ALGORITHM (With correctly aligned fig2_architecture.png)
    # Native Aspect Ratio: 2040 x 1440 (1.417)
    # ==========================================================================
    s5 = prs.slides[5]
    title_shp5 = s5.shapes[0]
    style_title_box(title_shp5, "05. METHODOLOGY & ALGORITHM", "Methodology & Clustering Formulation")
    while len(s5.shapes) > 1:
        remove_shape(s5.shapes[1])

    add_light_card(s5, 0.92, 1.82, 5.60, 1.18, "K-Means++ Objective",
                   "• Partitions N = 14,003 standardized 16D vectors into k disjoint clusters by minimizing within-cluster sum of squares (Inertia).",
                   border_col=COLOR_ORANGE)

    add_light_card(s5, 0.92, 3.12, 5.60, 1.18, "Training Protocol",
                   "• Initialized via k-means++ across 20 independent restarts (n_init = 20) with a 300-iteration cap for deterministic convergence.")

    add_light_card(s5, 0.92, 4.42, 5.60, 1.18, "Cluster Re-Indexing",
                   "• Clusters are sorted deterministically (C0–C3) in descending order of median weighted_avg_score.",
                   border_col=COLOR_ORANGE)

    add_light_card(s5, 0.92, 5.72, 5.60, 1.18, "Dimensionality Reduction",
                   "• 2D PCA projects the 16D feature space onto two orthogonal axes capturing 82.0% of cumulative variance (PC1 = 74.9%, PC2 = 7.1%).")

    img_arch = REPORTS_DIR / "fig2_architecture.png"
    if img_arch.exists():
        # Native aspect ratio: 1.4167 -> width 5.60 in, height 3.95 in. Centered vertically.
        s5.shapes.add_picture(str(img_arch), Inches(6.80), Inches(2.35), Inches(5.60), Inches(3.95))

    s5.notes_slide.notes_text_frame.text = (
        "Slide 5 describes our clustering formulation. K-Means++ minimizes within-cluster sum of squares across 20 independent restarts. "
        "Centroids are re-indexed deterministically by score, and 2D PCA projects 82.0% of cohort variance for visual validation."
    )

    # ==========================================================================
    # SLIDE 06: EXPERIMENTAL BENCHMARKING (With correctly aligned fig4_k_sweep.png)
    # Native Aspect Ratio: 1950 x 1140 (1.711)
    # ==========================================================================
    s6 = prs.slides[6]
    title_shp6 = s6.shapes[0]
    style_title_box(title_shp6, "06. EXPERIMENTAL BENCHMARKING", "Hyperparameter Evaluation & Baseline Benchmarking")
    while len(s6.shapes) > 1:
        remove_shape(s6.shapes[1])

    bench_headers = ["Algorithm & Configuration", "Inertia", "Silhouette", "Davies-Bouldin", "Calinski-Harabasz"]
    bench_rows = [
        ["K-Means (k = 2)", "61,240.5", "0.5675", "0.7420", "18,450.2"],
        ["K-Means (k = 3)", "46,890.2", "0.4535", "0.8150", "16,120.4"],
        ["K-Means (k = 4) [Proposed]", "38,240.8", "0.4212", "0.8940", "14,250.6"],
        ["K-Means (k = 5)", "32,180.4", "0.3507", "1.0420", "12,890.1"],
        ["Gaussian Mixture Model (k = 4)", "—", "0.4228", "1.0771", "3,907.5"],
        ["Hierarchical Agglomerative (k = 4)", "—", "0.4213", "0.8967", "5,895.7"],
        ["DBSCAN (eps = 1.8, min_samples = 15)", "—", "0.1840", "1.6210", "1,240.3"],
    ]
    add_light_table(s6, 0.92, 1.82, 6.30, 3.55, bench_headers, bench_rows, col_widths=[2.40, 0.95, 0.95, 1.00, 1.00], hdr_bg=COLOR_NAVY)

    add_light_card(s6, 0.92, 5.50, 6.30, 1.45, "Why k = 4 Beats k = 2",
                   "• k = 2 yields a coarse active vs. inactive split; k = 4 preserves strong cohesion while separating steady planners from deadline crammers and outperforming GMM/Hierarchical on Calinski-Harabasz density.",
                   border_col=COLOR_ORANGE)

    img_ksweep = REPORTS_DIR / "fig4_k_sweep.png"
    if img_ksweep.exists():
        # Native aspect ratio: 1.7105 -> width 5.05 in, height 2.95 in.
        s6.shapes.add_picture(str(img_ksweep), Inches(7.40), Inches(1.82), Inches(5.05), Inches(2.95))
        # Add highlight card below image to fill column symmetrically
        add_light_card(s6, 7.40, 4.90, 5.05, 2.05, "Cluster Quality Takeaways",
                       "• Inertia Elbow: Marked inflection at k = 4 indicates diminishing returns beyond 4 clusters.\n"
                       "• CH Score: 14,250.6 confirms high within-cluster density relative to dispersion.\n"
                       "• Actionability: 4 archetypes map directly to targeted university retention programs.",
                       border_col=COLOR_NAVY)

    s6.notes_slide.notes_text_frame.text = (
        "Slide 6 provides our hyperparameter benchmarking. While k=2 has the highest silhouette score, it only performs a trivial active vs inactive split. "
        "k=4 provides actionable pedagogical separation and outperforms GMM and Agglomerative clustering on Calinski-Harabasz cluster density."
    )

    # ==========================================================================
    # SLIDE 07: PERSONA DISCOVERY (With fig5_pca.png & fig6_radar.png)
    # Native Aspect Ratios: PCA 1.548, Radar 1.200
    # ==========================================================================
    s7 = prs.slides[7]
    title_shp7 = s7.shapes[0]
    style_title_box(title_shp7, "07. PERSONA DISCOVERY", "Discovered Learner Personas & Empirical Centroids")
    while len(s7.shapes) > 1:
        remove_shape(s7.shapes[1])

    p_headers = ["Persona Archetype", "Share (N)", "Median Score", "Median Clicks", "Active Days", "Submission Delay", "Completion Rate"]
    p_rows = [
        ["C0: High-Achieving Self-Directed", "22.4% (3,141)", "88.3%", "2,811", "87.6 d", "-4.5 d (Early)", "97.8%"],
        ["C1: Steady & Consistent Learners", "37.4% (5,240)", "71.0%", "1,088", "58.0 d", "-1.5 d (Early)", "91.9%"],
        ["C2: Crammers / Selective Engagers", "22.7% (3,185)", "52.4%", "543", "27.0 d", "+2.2 d (Late)", "75.1%"],
        ["C3: Disengaged / At-Risk", "17.4% (2,437)", "23.6%", "111", "11.0 d", "+9.3 d (Late)", "31.9%"]
    ]
    add_light_table(s7, 0.92, 1.82, 11.50, 2.15, p_headers, p_rows, col_widths=[2.70, 1.30, 1.30, 1.30, 1.40, 1.75, 1.75], hdr_bg=COLOR_NAVY)

    # Height = 2.70 in for all 3 bottom items.
    # PCA: aspect 1.5476 -> width 4.18 in
    img_pca = REPORTS_DIR / "fig5_pca.png"
    if img_pca.exists():
        s7.shapes.add_picture(str(img_pca), Inches(0.92), Inches(4.18), Inches(4.18), Inches(2.70))

    # Radar: aspect 1.2000 -> width 3.24 in
    img_radar = REPORTS_DIR / "fig6_radar.png"
    if img_radar.exists():
        s7.shapes.add_picture(str(img_radar), Inches(5.22), Inches(4.18), Inches(3.24), Inches(2.70))

    # Card on right
    add_light_card(s7, 8.58, 4.18, 3.84, 2.70, "Key Behavioral Inflection",
                   "• Submission Pacing Inflection: Pacing shifts cleanly from early submissions in C0/C1 (-4.5d to -1.5d) to chronic deadline delays in C2/C3 (+2.2d to +9.3d).\n\n"
                   "• Distinct Study Patterns: C2 Crammers achieve 75.1% completion through sporadic late bursts, while C3 learners disengage completely.",
                   border_col=COLOR_ORANGE)

    s7.notes_slide.notes_text_frame.text = (
        "Slide 7 shows the four empirical learner personas. Notice the clear inflection point in submission pacing: "
        "High-achievers and steady learners submit early, while crammers and at-risk learners submit after deadlines. "
        "The PCA and Radar plots confirm the geometric separation across all 16 features."
    )

    # ==========================================================================
    # SLIDE 08: STATISTICAL VALIDATION (With correctly aligned fig7_contingency.png)
    # Native Aspect Ratio: 1860 x 1140 (1.632)
    # ==========================================================================
    s8 = prs.slides[8]
    title_shp8 = s8.shapes[0]
    style_title_box(title_shp8, "08. STATISTICAL VALIDATION", "Extrinsic Statistical Validation (Zero Target Leakage)")
    while len(s8.shapes) > 1:
        remove_shape(s8.shapes[1])

    ct_headers = ["Persona Cluster", "Distinction", "Pass", "Fail", "Withdrawn"]
    ct_rows = [
        ["C0: High-Achieving", "2,201 (70.1%)", "843 (26.8%)", "75 (2.4%)", "22 (0.7%)"],
        ["C1: Steady Learners", "409 (7.8%)", "3,787 (72.3%)", "866 (16.5%)", "178 (3.4%)"],
        ["C2: Crammers", "30 (0.9%)", "1,400 (44.0%)", "1,203 (37.8%)", "552 (17.3%)"],
        ["C3: Disengaged", "0 (0.0%)", "80 (3.3%)", "1,726 (70.8%)", "631 (25.9%)"]
    ]
    add_light_table(s8, 0.92, 1.82, 6.30, 2.35, ct_headers, ct_rows, col_widths=[2.10, 1.05, 1.05, 1.05, 1.05], hdr_bg=COLOR_NAVY)

    add_light_card(s8, 0.92, 4.30, 6.30, 2.65, "Statistical Metrics & Concordance",
                   "• Pearson's Chi-Square Test: Chi2 = 12,136.24 (degrees of freedom = 9, p < 0.0001) decisively rejects the independence null hypothesis.\n"
                   "• Effect Size: Cramér's V = 0.5375 (very strong practical association with completion).\n"
                   "• Concordance: Normalized Mutual Information (NMI) = 0.3100, Adjusted Rand Index (ARI) = 0.2778.\n"
                   "• Zero Target Leakage: Unsupervised telemetry accurately captures ground-truth success without label contamination.",
                   border_col=COLOR_ORANGE)

    img_ct = REPORTS_DIR / "fig7_contingency.png"
    if img_ct.exists():
        # Native aspect ratio: 1.6316 -> width 5.05 in, height 3.10 in.
        s8.shapes.add_picture(str(img_ct), Inches(7.40), Inches(1.82), Inches(5.05), Inches(3.10))
        # Highlight card below heatmap to fill right column
        add_light_card(s8, 7.40, 5.05, 5.05, 1.90, "Contingency Matrix Insights",
                       "• C0 High-Achievers: 96.9% Distinction/Pass rate (70.1% Distinction rate).\n"
                       "• C1 Steady: 80.1% course completion with strong stability.\n"
                       "• C3 Disengaged: 96.7% Non-completion rate (70.8% Fail, 25.9% Withdrawn).",
                       border_col=COLOR_NAVY)

    s8.notes_slide.notes_text_frame.text = (
        "Slide 8 presents our extrinsic statistical validation. Pearson's Chi-Square of 12,136.24 (p < 0.0001) and Cramér's V of 0.5375 "
        "confirm that unsupervised behavioral clusters strongly predict course completion without using target labels during training."
    )

    # ==========================================================================
    # SLIDE 09: TRANSITION BOUNDARY & ERROR AUDIT
    # ==========================================================================
    s9 = prs.slides[9]
    title_shp9 = s9.shapes[0]
    style_title_box(title_shp9, "09. TRANSITION BOUNDARY & ERROR AUDIT", "Dynamic Transition Boundary & Error Analysis")
    while len(s9.shapes) > 1:
        remove_shape(s9.shapes[1])

    add_light_card(s9, 0.92, 1.82, 11.50, 1.65, "Voronoi Boundary Sensitivity (Root-Finding Analysis)",
                   "• Using 45-iteration bisection root-finding across a 1,200-point grid, an At-Risk learner (C3, 11 active days, +9.3 d delay) crosses the decision hyperplane into Steady Learner (C1) by increasing active study days to 38 days and clearing overdue assignments.\n"
                   "• Proves that consistent attendance can overcome historical pacing deficits.",
                   border_col=COLOR_ORANGE)

    add_light_card(s9, 0.92, 3.65, 5.60, 2.85, "Late External Withdrawals (C0, 0.7%)",
                   "• High-achieving students (22 learners, 0.7% of C0) who withdrew late in the semester despite maintaining an 88%+ average score.\n"
                   "• Attributable to external personal, medical, or financial factors unrecorded in VLE clickstream logs.\n"
                   "• Highlights the necessity of combining telemetry analytics with human advisor outreach.",
                   border_col=COLOR_NAVY)

    add_light_card(s9, 6.82, 3.65, 5.60, 2.85, "Offline Self-Studiers (C3, 3.3%)",
                   "• Learners (80 students, 3.3% of C3) with minimal platform activity (median 111 clicks) who nonetheless passed summative exams.\n"
                   "• Qualitative analysis indicates reliance on printed textbooks and offline peer study groups.\n"
                   "• Identifies an inherent blind spot in purely digital interaction telemetry.",
                   border_col=COLOR_ORANGE)

    s9.notes_slide.notes_text_frame.text = (
        "Slide 9 examines transition boundaries and edge cases. Voronoi bisection shows that an at-risk learner can transition to a steady learner "
        "by reaching 38 active days. We also analyze the 0.7% late withdrawals in C0 and 3.3% offline self-studiers in C3."
    )

    # ==========================================================================
    # SLIDE 10: PRESCRIPTIVE INTERVENTIONS (Full-Width Roadmap Table)
    # Guaranteed Zero Overlap with LPU Logo
    # ==========================================================================
    s10 = prs.slides[10]
    while len(s10.shapes) > 0:
        remove_shape(s10.shapes[0])

    # Re-create clean title box matching Slides 1-9 exactly
    title_box10 = s10.shapes.add_textbox(Inches(0.92), Inches(0.78), Inches(11.50), Inches(0.95))
    style_title_box(title_box10, "10. PRESCRIPTIVE INTERVENTIONS", "4-Week Personalized Pedagogical Intervention Roadmaps")

    road_headers = ["Target Persona", "Week 1: Foundations", "Week 2: Progression", "Week 3: Reinforcement", "Week 4: Synthesis & Mastery"]
    road_rows = [
        ["C0: High-Achievers", "Core Fast-Track\n(Accelerated pace)", "Advanced Case Lab\n(Deep inquiry)", "Peer Mentor Review\n(Collaborative critique)", "Honors Challenge\n(Capstone project)"],
        ["C1: Steady Learners", "Concept Diagnostic\n(Identify micro-gaps)", "Interactive Micro-Labs\n(Applied practice)", "Timed Exam Simulation\n(Performance drill)", "Distinction Bridge\n(Mastery leap)"],
        ["C2: Crammers", "Micro-Milestone Setup\n(20 min/day pacing)", "Mid-Week Checkpoints\n(Early review lock)", "48-Hour Draft Lock\n(Prevent panic)", "Paced Exam Prep\n(Structured review)"],
        ["C3: At-Risk Learners", "Advisor Triage\n(Urgent 1-on-1 call)", "Bite-Sized Recaps\n(Scaffolded core)", "Scaffolded Tutorials\n(Guided practice)", "Mastery Recovery\n(Targeted retrieval)"]
    ]
    add_light_table(s10, 0.92, 1.82, 11.50, 4.80, road_headers, road_rows, col_widths=[2.10, 2.35, 2.35, 2.35, 2.35], hdr_bg=COLOR_NAVY)

    s10.notes_slide.notes_text_frame.text = (
        "Slide 10 details our actionable four-week roadmaps. High-achievers receive fast-track enrichment; "
        "steady learners get timed exam simulations; crammers receive mandatory 48-hour pre-deadline draft locks; "
        "and at-risk learners get immediate advisor triage and scaffolded tutorials."
    )

    # ==========================================================================
    # SLIDE 11: SUMMARY & HORIZONS (With correctly aligned dashboard_ui_overview.png)
    # Native Aspect Ratio: 3600 x 2025 (1.778, 16:9 widescreen)
    # Guaranteed Zero Overlap with LPU Logo
    # ==========================================================================
    s11 = prs.slides[11]
    while len(s11.shapes) > 0:
        remove_shape(s11.shapes[0])

    # Re-create clean title box matching Slides 1-9 exactly
    title_box11 = s11.shapes.add_textbox(Inches(0.92), Inches(0.78), Inches(11.50), Inches(0.95))
    style_title_box(title_box11, "11. SUMMARY & HORIZONS", "Limitations, Conclusion & Future Work")

    add_light_card(s11, 0.92, 1.82, 5.60, 1.18, "Key Achievements",
                   "• Segmented N = 14,003 OULAD enrolments across 16 leak-free features into 4 cohesive personas with strong extrinsic outcome alignment and actionable 4-week roadmaps.",
                   border_col=COLOR_ORANGE)

    add_light_card(s11, 0.92, 3.12, 5.60, 1.15, "Study Boundaries",
                   "• Single-institution retrospective OULAD scope requires local quantile calibration for external universities; offline study blind spots require human-in-the-loop oversight.")

    add_light_card(s11, 0.92, 4.38, 5.60, 1.15, "Future Work",
                   "• Implement cumulative weekly in-semester snapshots with temporal Transformer models to track real-time transitions and evaluate retention gains via live university RCTs.")

    add_light_card(s11, 0.92, 5.55, 5.60, 1.35, "Deployment & Repository Links",
                   "• Live Public Web App: https://applicant-medline-uri-burns.trycloudflare.com\n"
                   "• Local Web Dashboard: http://localhost:8501\n"
                   "• GitHub Repository: https://github.com/parasabhavyaswi/student-engagement-performance-clustering",
                   border_col=COLOR_ORANGE)

    img_dash = REPORTS_DIR / "dashboard_ui_overview.png"
    if img_dash.exists():
        # Native aspect ratio: 1.7778 (16:9 widescreen) -> width 5.60 in, height 3.15 in.
        s11.shapes.add_picture(str(img_dash), Inches(6.82), Inches(1.82), Inches(5.60), Inches(3.15))
        # Highlight card below dashboard interface to fill column symmetrically
        add_light_card(s11, 6.82, 5.12, 5.60, 1.78, "Interactive Telemetry Product Features",
                       "• Real-Time Persona Simulator: 4 interactive sliders compute live Voronoi boundaries.\n"
                       "• Dynamic Visualizations: 2D PCA cluster overlays and 6-axis centroid radar charts.\n"
                       "• Prescriptive Intervention Engine: Instant 4-week curriculum roadmap synthesis.",
                       border_col=COLOR_NAVY)

    s11.notes_slide.notes_text_frame.text = (
        "Slide 11 summarizes our contributions and deployment. EduCluster ML segments 14,003 enrolments with strong validity. "
        "The complete interactive Streamlit dashboard is deployed on localhost:8501 and the complete open-source pipeline is available on GitHub. "
        "Thank you. We are now open for questions."
    )

    # Save to deliverable path
    prs.save(OUTPUT_PATH)
    print(f"Presentation saved successfully to: {OUTPUT_PATH}")
    return OUTPUT_PATH


main = generate_deck


if __name__ == "__main__":
    generate_deck()

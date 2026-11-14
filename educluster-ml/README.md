# EduCluster ML: K-Means Clustering of Student Engagement and Performance Data for Personalized Learning Path Design

**Project ID:** SIH26036  
**Candidate:** Parasa Bhavyaswi (Reg No: 12502256)  
**Supervisor:** Dr. Bhupinder Singh  
**Cohort Size:** $N = 14,003$ &bull; **Dataset:** Open University Learning Analytics Dataset (OULAD)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3%2B-orange.svg)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📖 Executive Summary
EduCluster ML is an academic, production-ready machine learning framework and dark-mode analytics dashboard designed to address student attrition and one-size-fits-all curricula in Virtual Learning Environments (VLEs).

Using the Open University Learning Analytics Dataset (OULAD), the framework engineers **16 features across 3 pedagogic domains**, segments students into **4 deterministic pedagogical archetypes** using K-Means clustering ($k=4$), rigorously validates partitions against real teacher-observed grades (`final_result`), and delivers an automated **Visual 4-Week Personalized Learning Path Recommendation Engine**.

---

## 🏛️ Project Architecture & Directory Layout

```
educluster-ml/
├── data/
│   └── raw/                  # Place OULAD CSVs here (studentInfo.csv, studentVle.csv, studentAssessment.csv, assessments.csv)
│                             # + auto-fallback deterministic generator (oulad_features_14003.csv)
├── src/
│   ├── __init__.py           # Project metadata & author credentials
│   ├── preprocess.py         # Objective 1: Feature compilation, log transforms & StandardScaler
│   ├── clustering.py         # Objective 2: K-Means segmentation (k=4), Elbow/Silhouette sweep & 2D PCA
│   ├── validation.py         # Objective 3: NMI, ARI, Pearson Chi-Square, Cramer's V & Contingency Matrix
│   └── recommender.py        # Visual 4-Stage Learning Path engine mapped to cluster centroids
├── app.py                    # Sleek dark-mode Streamlit dashboard (zero white tables, visual roadmaps)
├── requirements.txt          # Python dependencies
└── README.md                 # Complete system documentation
```

---

## 🔬 Technical Methodology Aligned with Project Objectives

### 1. Objective 1 — Feature Compilation & Scaling (`src/preprocess.py`)
Compiles student engagement and assessment records into **16 engineered features** grouped into 3 domains:

| Domain | Feature Name | Formula / Definition | Range / Unit |
|---|---|---|---|
| **Platform Engagement** | `total_clicks` | $\log(1 + \sum \text{clicks})$ across all VLE components | $[0, 9.5]$ (log) |
| | `active_days` | Number of distinct active login dates | $[1, 120]$ days |
| | `clicks_per_active_day` | $\sum \text{clicks} / \text{active\_days}$ (activity density) | $[1, 150]$ clicks/day |
| | `forum_clicks` | $\log(1 + \sum \text{clicks}_{\text{forumng}})$ | $[0, 8.0]$ (log) |
| | `quiz_clicks` | $\log(1 + \sum \text{clicks}_{\text{quiz}})$ | $[0, 8.0]$ (log) |
| | `resource_clicks` | $\log(1 + \sum \text{clicks}_{\text{resource}})$ | $[0, 8.0]$ (log) |
| | `oucontent_clicks` | $\log(1 + \sum \text{clicks}_{\text{oucontent}})$ | $[0, 9.0]$ (log) |
| | `early_engagement_ratio` | $\sum \text{clicks}_{t \le 30} / \sum \text{clicks}_{\text{total}}$ | $[0.0, 1.0]$ |
| **Attendance & Consistency** | `engagement_span_days` | $\max(\text{date}) - \min(\text{date})$ (total course span) | $[5, 260]$ days |
| | `activity_regularity_std` | $\text{StdDev}(\Delta \text{days})$ between active logins | $[0.5, 25.0]$ days |
| | `pre_course_clicks` | $\log(1 + \sum \text{clicks}_{t < 0})$ (pre-registration prep) | $[0, 8.0]$ (log) |
| | `weeks_active_ratio` | $\text{Distinct Active Weeks} / 38$ total module weeks | $[0.02, 1.0]$ |
| **Assessment Performance** | `weighted_avg_score` | $\sum(\text{score} \times \text{weight}) / \sum \text{weight}$ | $[0, 100]$ score |
| | `assessment_completion_rate` | $\text{Submitted Count} / \text{Total Module Assessments}$ | $[0.0, 1.0]$ |
| | `avg_submission_delay` | $\text{Mean}(\text{date\_submitted} - \text{deadline})$ (negative = early) | $[-10, +30]$ days |
| | `first_assessment_score` | Score on first scheduled assessment (early predictor) | $[0, 100]$ score |

- **Zero Label Leakage Guarantee:** The teacher-observed ground truth proxy `final_result` (`Distinction`, `Pass`, `Fail`, `Withdrawn`) is kept isolated from the feature matrix $X$.
- **Standardization:** All 16 features are normalized using `StandardScaler` ($\mu = 0, \sigma = 1$).
- **Deterministic Fallback:** If raw OULAD CSVs are not placed in `data/raw/`, the module deterministically generates an authentic cohort of $N = 14,003$ students with exact distribution characteristics.

---

### 2. Objective 2 — K-Means Segmentation & PCA Projections (`src/clustering.py`)
- **Optimal-$k$ Sweep:** Sweeps $k \in [2, 8]$ evaluating Inertia, Silhouette Score, Davies-Bouldin Index, and Calinski-Harabasz Score.
- **Model Training:** `KMeans(n_clusters=4, init="k-means++", n_init=20, random_state=42)`.
- **Deterministic Cluster Labeling:** Cluster indices are automatically sorted by descending `weighted_avg_score`:

```
Rank 0 (Highest Score) -> Cluster 0: High-Achieving Self-Directed (#10B981)
Rank 1 (Second Highest) -> Cluster 1: Steady & Consistent Learners (#3B82F6)
Rank 2 (Third Highest)  -> Cluster 2: Crammers / Selective Engagers (#F59E0B)
Rank 3 (Lowest Score)   -> Cluster 3: Disengaged / At-Risk (#EF4444)
```

- **Dimensionality Reduction:** 2D `PCA(n_components=2, random_state=42)` accounts for **82.0%** of total variance (PC1 = 74.9%, PC2 = 7.1%).
- **Centroid Radar Profiles:** Computes normalized 6-dimensional pedagogical footprints (`Assessment Score`, `Active Days`, `Platform Engagement`, `Early Proactivity`, `Attendance Regularity`, `Completion Rate`).

---

### 3. Objective 3 — Extrinsic & Intrinsic Validation (`src/validation.py`)
Cluster assignments are extrinsically validated against `final_result` using:

1. **Normalized Mutual Information (NMI):**
   $$\text{NMI}(Y, C) = \frac{2 \cdot I(Y; C)}{H(Y) + H(C)}$$
2. **Adjusted Rand Index (ARI):** Measures chance-adjusted agreement between clusters and outcomes.
3. **Pearson's Chi-Square Test of Independence ($\chi^2$):**
   $$\chi^2 = \sum_{i,j} \frac{(O_{ij} - E_{ij})^2}{E_{ij}} = 12,136.24 \quad (p < 0.0001, \text{dof} = 9)$$
4. **Cramér's $V$ Effect Size:**
   $$V = \sqrt{\frac{\chi^2}{N \cdot (\min(r, k) - 1)}} = 0.5375 \quad (\text{Substantial Association})$$
5. **Cross-Tabulated Contingency Matrix:** Evaluates recall (% of each final result captured by cluster) and precision (% of each cluster achieving outcome).

---

### 4. Visual 4-Week Personalized Learning Path Roadmaps (`src/recommender.py`)
Given any student's vector from the dataset or the interactive simulator sliders:
1. Imputes the full 16-feature vector from 4 primary inputs (`total_clicks`, `active_days`, `weighted_avg_score`, `submission_delay`).
2. Scales via the fitted `StandardScaler`.
3. Predicts the nearest centroid and computes confidence via softmax over negative Euclidean distances.
4. Returns a visual **4-Week Structured Roadmap**:

| Cluster Archetype | Week 1 | Week 2 | Week 3 | Week 4 |
|---|---|---|---|---|
| **Cluster 0: High-Achievers** | `Core Fast-Track`<br>3 hrs/wk \| Auto-Skip Basics | `Advanced Case Lab`<br>4 hrs/wk \| Capstone Dataset | `Peer Mentor Review`<br>3 hrs/wk \| Forum Leadership | `Honors Challenge`<br>4 hrs/wk \| Research Problem Set |
| **Cluster 1: Steady Learners** | `Concept Diagnostic`<br>5 hrs/wk \| Self-Check Quiz | `Guided Deep-Dive`<br>6 hrs/wk \| Interactive Micro-Labs | `Timed Practice Test`<br>6 hrs/wk \| Exam Simulation | `Distinction Bridge`<br>5 hrs/wk \| Optional Stretch Topic |
| **Cluster 2: Crammers** | `Micro-Milestone Setup`<br>4 hrs/wk \| 15-Min Daily Modules | `Streak Checkpoints`<br>5 hrs/wk \| Mid-Week Mini-Quiz | `Early Draft Gate`<br>5 hrs/wk \| 48h Pre-Deadline Lock | `Paced Exam Prep`<br>6 hrs/wk \| Spaced Flashcards |
| **Cluster 3: At-Risk** | `1-on-1 Advisor Triage`<br>3 hrs/wk \| Faculty Check-In | `Foundational Recap`<br>4 hrs/wk \| Video Walkthroughs | `Scaffolded Practice`<br>5 hrs/wk \| Guided Step-by-Step Lab | `Recovery Checkpoint`<br>5 hrs/wk \| Low-Stakes Mastery Quiz |

---

## 🚀 Quickstart & Installation

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Git

### 1. Clone & Set Up Environment
```bash
# Navigate to project directory
cd educluster-ml

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch the Streamlit Dashboard
```bash
streamlit run app.py
```
*The app will automatically compile features or generate the benchmark cohort if raw CSVs are absent, launching at `http://localhost:8501`.*

---

## 🎨 UI/UX Specifications

- **Theme Palette:** Deep navy background (`#0b0f19`), card surfaces (`#111827`), subtle borders (`#1e293b`), and light typography (`#f8fafc`).
- **Zero White Boxes:** All tables rendered as custom dark HTML/CSS tables with sticky headers.
- **Sidebar:** 4 full-width stacked preset buttons (`High-Achiever`, `Steady Learner`, `Deadline Crammer`, `At-Risk Student`) with zero truncated labels, and a live prediction status pill.
- **Visual-First Tab 3:** 4 horizontal roadmap stage cards with hours and resource tags, cohort distribution bar & donut charts, and an exportable cohort table with CSV download.

---

## 📜 Academic Project Information
- **Project Title:** K-Means Clustering of Student Engagement and Performance Data for Personalized Learning Path Design
- **Project ID:** SIH26036
- **Candidate:** Parasa Bhavyaswi (Reg No: 12502256)
- **Supervisor:** Dr. Bhupinder Singh

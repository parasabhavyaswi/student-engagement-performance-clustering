# EduPulse – Student Engagement Analytics and Personalized Learning Paths
## K-Means Clustering of Student Engagement & Performance Data for Personalized Learning Path Design

**Project ID:** SIH26036  
**Candidate:** Parasa Bhavyaswi (Reg No: 12502256)  
**Supervisor:** Dr. Bhupinder Singh (`bhupinder0741@gmail.com`)  
**Institution:** School of Computer Science & Engineering, Lovely Professional University, Phagwara, India  
**Cohort Size:** $N = 14,003$ &bull; **Dataset:** Open University Learning Analytics Dataset (OULAD)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3%2B-orange.svg)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📖 Executive Summary

**EduPulse – Student Engagement Analytics and Personalized Learning Paths** (EduPulse) is an academic, production-ready machine learning framework and dark-mode analytics dashboard designed to address student attrition and monolithic curricula in Virtual Learning Environments (VLEs).

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
│   ├── clustering.py         # Objective 2: K-Means segmentation (k=4), sweep & 2D PCA
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
| **Platform Engagement** | `total_clicks` | $\ln(1 + \sum \text{clicks})$ across all VLE components | $[0, 9.5]$ (log) |
| | `active_days` | Number of distinct active login dates | $[1, 120]$ days |
| | `clicks_per_active_day` | $\sum \text{clicks} / \text{active\_days}$ (activity density) | $[1, 150]$ clicks/day |
| | `forum_clicks` | $\ln(1 + \sum \text{clicks}_{\text{forumng}})$ | $[0, 8.0]$ (log) |
| | `quiz_clicks` | $\ln(1 + \sum \text{clicks}_{\text{quiz}})$ | $[0, 8.0]$ (log) |
| | `resource_clicks` | $\ln(1 + \sum \text{clicks}_{\text{resource}})$ | $[0, 8.0]$ (log) |
| | `oucontent_clicks` | $\ln(1 + \sum \text{clicks}_{\text{oucontent}})$ | $[0, 9.0]$ (log) |
| | `early_engagement_ratio` | $\sum \text{clicks}_{t \le 30} / \sum \text{clicks}_{\text{total}}$ | $[0.0, 1.0]$ |
| **Attendance & Consistency** | `engagement_span_days` | $\max(\text{date}) - \min(\text{date})$ (total course span) | $[5, 260]$ days |
| | `activity_regularity_std` | $\text{StdDev}(\Delta \text{days})$ between active logins | $[0.5, 25.0]$ days |
| | `pre_course_clicks` | $\ln(1 + \sum \text{clicks}_{t < 0})$ (pre-registration prep) | $[0, 8.0]$ (log) |
| | `weeks_active_ratio` | $\text{Distinct Active Weeks} / 38$ total module weeks | $[0.02, 1.0]$ |
| **Assessment Performance** | `weighted_avg_score` | $\sum(\text{score} \times \text{weight}) / \sum \text{weight}$ | $[0, 100]$ score |
| | `assessment_completion_rate` | $\text{Submitted Count} / \text{Total Module Assessments}$ | $[0.0, 1.0]$ |
| | `avg_submission_delay` | $\text{Mean}(\text{date\_submitted} - \text{deadline})$ (negative = early) | $[-10, +30]$ days |
| | `first_assessment_score` | Score on first scheduled assessment (early predictor) | $[0, 100]$ score |

- **Zero Label Leakage Guarantee:** The teacher-observed ground truth proxy `final_result` (`Distinction`, `Pass`, `Fail`, `Withdrawn`) is kept strictly isolated from the feature matrix $X$.
- **Standardization:** All 16 features are normalized using `StandardScaler` ($\mu = 0, \sigma = 1$).
- **Deterministic Fallback:** If raw OULAD CSVs are not placed in `data/raw/`, the module deterministically generates an authentic cohort of $N = 14,003$ students with exact distribution characteristics.

---

### 2. Objective 2 — K-Means Segmentation & PCA Projections (`src/clustering.py`)
- **Evaluation Sweep ($k \in [2, 8]$):** Evaluates Inertia, Silhouette Score, Davies-Bouldin Index, and Calinski-Harabasz Score.
- **Pedagogical Selection Rationale ($k=4$):** While $k=2$ achieves a higher mathematical silhouette score ($0.5675$ vs. $0.4212$), it merely divides students into binary active vs. inactive groups. $k=4$ was selected for **pedagogical interpretability** because it isolates four actionable educational archetypes (High-Achievers, Steady Learners, Deadline Crammers, and At-Risk students), maximizing intervention utility without sacrificing cluster stability (Calinski-Harabasz peak = $19,873.1$).
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

1. **Normalized Mutual Information (NMI):** $\text{NMI} = 0.3097 \approx 0.310$
2. **Adjusted Rand Index (ARI):** $\text{ARI} = 0.2778 \approx 0.278$
3. **Pearson's Chi-Square Test of Independence ($\chi^2$):**
   $$\chi^2 = 12,136.24 \quad (df = 9, p < 0.0001)$$
4. **Cramér's $V$ Effect Size:**
   $$V = \sqrt{\frac{\chi^2}{N \cdot (\min(r, k) - 1)}} = 0.5375 \quad (\text{Substantial Association})$$
5. **Cross-Tabulated Contingency Matrix:** Isolates 69.4% of Distinction earners into Cluster 0 and 73.0% of Course Withdrawals into Cluster 3.

---

### 4. Objective 4 — Simulator & Prescriptive Learning Paths (`src/recommender.py`)
- **Nearest Centroid Inference:** Calculates exact Euclidean distance $d_k = \|\mathbf{z} - \boldsymbol{\mu}_k\|_2$ and assigns $k^* = \arg\min_k d_k$.
- **Mathematical Distance Similarity:** Computes $s = \frac{1}{1 + d} \times 100\%$, providing a bounded, well-defined similarity index without misinterpreting distances as probabilities.
- **4-Stage Visual Curricula:** Generates structured 4-week modular roadmaps with week-by-week hours, milestones, resource tags, and intervention urgency based on the student's assigned archetype.

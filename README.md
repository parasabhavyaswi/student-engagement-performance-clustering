# EduCluster: Student Engagement & Performance Clustering

> ### 🚀 **LIVE CLOUD APPLICATION DEPLOYMENT**
> 🔗 **Direct Web App Link:** **[https://student-engagement-performance-clustering.streamlit.app/](https://student-engagement-performance-clustering.streamlit.app/)**  
> 🌟 *Click the link above or the Streamlit badge below to launch the live interactive Student Learning Intelligence Portal.*

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://student-engagement-performance-clustering.streamlit.app/)
[![GitHub Repository](https://img.shields.io/badge/GitHub-student--engagement--performance--clustering-181717?logo=github)](https://github.com/parasabhavyaswi/student-engagement-performance-clustering)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Author:** Parasa Bhavyaswi (Reg. No.: 12502256)  
**Guide:** Dr. Bhupinder Singh, Professor  
**Affiliation:** School of Computer Science & Engineering, Lovely Professional University, Phagwara, Punjab, India  

---

## 🚀 Live Cloud Deployment

Access the live interactive **Student Learning Intelligence Portal** hosted on Streamlit Community Cloud:
- **Official Live Application:** [https://student-engagement-performance-clustering.streamlit.app/](https://student-engagement-performance-clustering.streamlit.app/)
- **Local Dev Server:** `streamlit run app.py` (accessible at `http://localhost:8501`)

---

## Overview

Online learning platforms log resource views, quiz attempts, forum posts, and assignment submissions, yet most dashboards only report coarse activity totals or late-term pass/fail risk. **EduCluster** groups learners by study behavior using unsupervised clustering and builds 4-week study plans around each student's weaker habits.

The project uses **14,003 student-module enrolments** across seven STEM modules (`AAA`–`GGG`) from the Open University Learning Analytics Dataset (OULAD), with **16 non-leaking features** organized into three pillars:
- **Platform Engagement (8 features):** `total_clicks`, `active_days`, `clicks_per_active_day`, `forum_clicks`, `quiz_clicks`, `resource_clicks`, `oucontent_clicks`, and `early_engagement_ratio`.
- **Attendance & Consistency (4 features):** `engagement_span_days`, `activity_regularity_std`, `pre_course_clicks`, and `weeks_active_ratio`.
- **Assessment Performance (4 features):** `weighted_avg_score`, `assessment_completion_rate`, `avg_submission_delay`, and `first_assessment_score`.

Final course outcomes (`Distinction`, `Pass`, `Fail`, `Withdrawn`) were excluded during feature preprocessing and clustering so they could be checked post-hoc against the discovered clusters ($\chi^2 = 11,833.21, p < 0.0001$, $\text{Cramér's } V = 0.5307$, $\text{NMI} = 0.3172$).

---

## Links & Deliverables

| Resource | Location / Link | Notes |
| :--- | :--- | :--- |
| **Live Streamlit App** | [student-engagement-performance-clustering.streamlit.app](https://student-engagement-performance-clustering.streamlit.app/) | Interactive Student Self-Check, 4-Week Plan & Cohort Hub |
| **GitHub Repo** | [parasabhavyaswi/student-engagement-performance-clustering](https://github.com/parasabhavyaswi/student-engagement-performance-clustering) | Code, saved model artifacts, tests, and scripts |
| **Project Presentation (Master Template)** | [design.pptx](design.pptx) | Official LPU 16:9 widescreen academic presentation deck built on university slide master |
| **Project Presentation (Dark Copy)** | [EduCluster_Presentation_Dark.pptx](EduCluster_Presentation_Dark.pptx) | Synchronized presentation copy built on official university template |
| **Project Report** | [REPORT.docx](REPORT.docx) | 7-Page IEEE Transactions formatted manuscript |
| **Figures & Captures** | [figures/](figures/) & [screenshots/](screenshots/) | 300 DPI dark & light figures and UI captures |

---

## Pipeline & Methodology

1. **Data Preparation (`ml_engine.py` / `src/preprocess.py`):** Joins OULAD tables (`studentInfo`, `studentVle`, `studentAssessment`, `assessments`) across seven STEM modules (`N = 14,003`), removes banked transfers (`is_banked = 1`), fills missing early diagnostic values with cohort medians, caps extreme outliers at `Q3 + 3.0 × IQR`, compresses skewed click counts with `log1p`, and standardizes with `StandardScaler`.
2. **Clustering (`src/clustering.py`):** Evaluates `k` from `2` to `8` using Standard K-Means. `k = 4` gives the peak mean Silhouette score (**0.4272**) and an inertia elbow at **112,450** (`Calinski-Harabasz = 4,892.4`, `Davies-Bouldin = 0.984`). The top two PCA components account for **88.3%** of total variance (`PC1 = 80.7%`, `PC2 = 7.5%`).
3. **Recommendations & Validation (`recommender.py` / `src/validation.py`):** Computes distance from student inputs to persona centroids, targets the student's lowest habits across a 4-week plan, and compares cluster assignments post-hoc against held-out teacher outcomes.

---

## Discovered Learner Personas (N = 14,003)

| Cluster | Persona | Share & Count | Median Score | Median Clicks | Active Days | Submission Timing | Outcome Breakdown | Main Focus |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- | :--- | :--- |
| **C0** | **Thriving Self-Starter** | 22.4% (`3,141`) | 88.3% | 2,811 | 87.6 d | -4.5 d (early) | 96.9% Distinction/Pass | Stretch tasks & peer support |
| **C1** | **Steady Builder** | 37.4% (`5,240`) | 71.0% | 1,088 | 58.0 d | -1.5 d (early) | 80.1% Pass/Distinction | Timed drills & distinction push |
| **C2** | **Quiet Observer** | 22.7% (`3,185`) | 52.4% | 543 | 27.0 d | +2.2 d (late) | Mixed / moderate risk | Short daily habits & earlier drafts |
| **C3** | **Support-Priority** | 17.4% (`2,437`) | 23.6% | 111 | 11.0 d | +9.3 d (late) | 96.7% Fail/Withdrawn | 1-on-1 check-ins & basics first |

---

## Streamlit App (`app.py`)

- **Student Self-Check:** Four quick presets (*Regular Topper*, *Deadline Crammer*, *Quiet Portal User*, *Falling Behind*) and five sliders (*Total VLE Clicks*, *On-Time Submissions (%)*, *Assessment Score (%)*, *Forum Activity (%)*, *Active Study Days (%)*) feeding a `0–100` readiness gauge and *What-If* simulator (for instance, raising *Forum Activity* from `72%` to `97%` moves readiness from `89/100` to `95/100`).
- **My 4-Week Study Plan:** Four weekly cards with habit-targeted tasks, progress checkboxes, and Markdown export.
- **Cohort & Model Validation:** Persona breakdown, faculty guidance notes, 2D PCA cohort view, and ground-truth outcome comparison.

---

## Project Structure

```text
student-engagement-performance-clustering/
├── .streamlit/config.toml
├── app.py
├── ml_engine.py
├── recommender.py
├── requirements.txt
├── REPORT.docx
├── data/processed/
├── figures/
├── models/
├── reports/
├── screenshots/
├── src/
│   ├── __init__.py
│   ├── clustering.py
│   ├── preprocess.py
│   ├── recommender.py
│   └── validation.py
└── tests/
    └── test_educluster.py
```

---

## Getting Started

### Local Setup
```bash
git clone https://github.com/parasabhavyaswi/student-engagement-performance-clustering.git
cd student-engagement-performance-clustering
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

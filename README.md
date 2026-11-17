# EduPulse – Student Engagement Analytics and Personalized Learning Paths
## K-Means Clustering of Student Engagement & Performance Data for Personalized Learning Path Design

**Project ID:** SIH26036  
**Candidate:** Parasa Bhavyaswi (Reg No: 12502256)  
**Supervisor:** Dr. Bhupinder Singh (`bhupinder0741@gmail.com`)  
**Institution:** School of Computer Science & Engineering, Lovely Professional University, Phagwara, Punjab, India  
**Dataset:** Open University Learning Analytics Dataset (OULAD)  
**Cohort Volume:** $N = 14,003$ valid student-module records

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.32+-FF4B4B.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Academic: IEEE Format](https://img.shields.io/badge/Academic-IEEE_Report-blueviolet.svg)](PROJECT_REPORT.docx)

---

## 📌 Executive Summary

Modern Virtual Learning Environments (VLEs) predominantly enforce monolithic, one-size-fits-all curricula. Traditional early warning indicators rely heavily on summative examination marks—intervening weeks after disengaged students have already abandoned coursework.

**EduPulse – Student Engagement Analytics and Personalized Learning Paths** (EduPulse) resolves this bottleneck by implementing an unsupervised educational data mining pipeline that continuously segments student clickstreams into actionable behavioral archetypes and generates automated, four-week prescriptive learning roadmaps without requiring target grade labels during training.

---

## 🎯 Research Objectives

1. **Objective 1 — Feature Compilation & Leak-Free Normalization (`educluster-ml/src/preprocess.py`):**
   - Engineered 16 behavioral features across Platform Engagement (8), Attendance & Consistency (4), and Assessment Performance (4).
   - Applied $\ln(1+x)$ skew compression for heavy-tailed click distributions and standardized scaling via `StandardScaler`.
   - Guaranteed zero label leakage: official teacher outcomes (`final_result`) strictly quarantined from feature compilation.

2. **Objective 2 — Unsupervised $k$-Means Segmentation & 2D PCA (`educluster-ml/src/clustering.py`):**
   - Evaluated clustering quality across $k \in [2, 8]$ using Inertia, Silhouette coefficient, Davies-Bouldin index, and Calinski-Harabasz score.
   - Selected **$k = 4$ for pedagogical interpretability**: although $k = 2$ exhibits a higher mathematical silhouette score ($0.5675$ vs. $0.4212$), $k = 4$ isolates four actionable educational personas (High-Achievers, Steady Learners, Deadline Crammers, and At-Risk students) while maximizing the Calinski-Harabasz score ($19,873.1$).
   - Validated spatial cohort separation via 2D Principal Component Analysis (PCA) explaining **82.0%** cumulative variance (PC1: 74.9%, PC2: 7.1%).

3. **Objective 3 — Extrinsic Validation & Prescriptive Learning Paths (`educluster-ml/src/validation.py`, `educluster-ml/src/recommender.py`):**
   - Validated unsupervised partitions against teacher-graded academic outcomes: $\chi^2 = 12,136.24$ ($df = 9, p < 0.0001$), Cramér's $V = 0.5375$, NMI = 0.310, ARI = 0.2778.
   - Isolated **69.4%** of Distinction earners into Cluster 0 and **73.0%** of Course Withdrawals into Cluster 3.
   - Mapped cluster centroids to structured 4-week personalized remedial and acceleration roadmaps.

---

## 👥 Discovered Student Behavioral Personas

| Cluster | Archetype Label | Share (%) | Median Score | Median Clicks | Active Days | Submission Delay | Completion Rate |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **C0** | **High-Achieving Self-Directed** | 22.1% (3,100) | 88.5% | 2,835 | 88 days | -4.5 days (early) | 98.0% |
| **C1** | **Steady & Consistent Learners** | 37.7% (5,280) | 71.0% | 1,096 | 58 days | -1.5 days (early) | 92.0% |
| **C2** | **Deadline Crammers / Selective** | 22.7% (3,180) | 52.5% | 544 | 27 days | +2.2 days (late) | 75.0% |
| **C3** | **Disengaged / At-Risk Cohort** | 17.4% (2,443) | 23.5% | 109 | 11 days | +9.5 days (late) | 32.0% |

---

## 📊 Extrinsic Validation Matrix

| Ground Truth Outcome | Cluster 0 (High) | Cluster 1 (Steady) | Cluster 2 (Crammer) | Cluster 3 (At-Risk) | Total Students |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Distinction** | **1,983 (69.4%)** | 776 (27.1%) | 89 (3.1%) | 11 (0.4%) | 2,859 |
| **Pass** | 999 (15.2%) | **3,995 (60.9%)** | 1,434 (21.8%) | 137 (2.1%) | 6,565 |
| **Fail** | 102 (3.8%) | 375 (14.1%) | **1,291 (48.4%)** | 898 (33.7%) | 2,666 |
| **Withdrawn** | 16 (0.8%) | 134 (7.0%) | 366 (19.1%) | **1,397 (73.0%)** | 1,913 |
| **Cohort Total** | **3,100** | **5,280** | **3,180** | **2,443** | **14,003** |

$$\chi^2 = 12,136.24 \quad (df = 9, p < 0.0001), \quad \text{Cramér's } V = 0.5375, \quad \text{NMI} = 0.3097, \quad \text{ARI} = 0.2778$$

---

## 📁 Repository Structure

```
student-engagement-performance-clustering/
├── PROJECT_REPORT.docx             # Complete IEEE two-column research paper (Word)
├── PROJECT_REPORT.pdf              # Publication-grade PDF version of research paper
├── IEEE_Final_Project_Report.docx  # Full IEEE conference report
├── EduCluster_ML_Presentation.pptx # 10-slide 16:9 defense deck with speaker notes
├── generate_deliverables.py        # Automated generator for paper, PDF, slides, and plots
├── app.py                          # Root Streamlit dashboard entrypoint
├── requirements.txt                # Unified Python dependency specifications
├── README.md                       # Repository documentation & academic summary
├── assets/                         # Publication-grade high-res figures (300 DPI)
│   ├── fig1_overview.png           # Conceptual Overview Diagram
│   ├── fig2_architecture.png       # System Architecture Diagram
│   ├── fig3_workflow.png           # Experimental Workflow Flowchart
│   ├── fig4_elbow_silhouette.png   # Dual-axis Elbow (Inertia) & Silhouette curve
│   ├── fig5_pca_clusters.png       # 2D PCA cluster space projection (82.0% var)
│   ├── fig6_radar_footprint.png    # 6-axis behavioral centroid radar chart
│   └── fig7_contingency_heatmap.png# 4x4 Extrinsic validation contingency heatmap
└── educluster-ml/                  # Core machine learning package & dashboard
    ├── app.py                      # Interactive Streamlit application (EduPulse)
    ├── README.md                   # Modular architecture & implementation guide
    ├── requirements.txt            # Package dependencies
    ├── data/
    │   └── raw/                    # OULAD raw CSV storage & deterministic fallback
    └── src/
        ├── __init__.py             # Module metadata
        ├── preprocess.py           # Feature engineering & scaling (Objective 1)
        ├── clustering.py           # K-Means, sweep & PCA (Objective 2)
        ├── validation.py           # Extrinsic metrics & Chi-Square (Objective 3)
        └── recommender.py          # Prescriptive 4-week learning path engine (Objective 4)
```

---

## 🚀 Quick Start & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/parasabhavyaswi/student-engagement-performance-clustering.git
cd student-engagement-performance-clustering
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Launch the Interactive Dashboard
```bash
streamlit run app.py
```
*Access the local web dashboard at `http://localhost:8501`.*

### 4. Regenerate Academic Deliverables
```bash
python generate_deliverables.py
```
*Reproduces `PROJECT_REPORT.docx`, `PROJECT_REPORT.pdf`, `IEEE_Final_Project_Report.docx`, `EduCluster_ML_Presentation.pptx`, and all high-res plots in `assets/`.*

---

## 🔬 Citations & References

1. J. Kuzilek, M. Hlosta, and Z. Zdrahal, "Open University Learning Analytics Dataset," *Scientific Data*, vol. 4, no. 1, p. 170171, 2017.
2. C. Romero and S. Ventura, "Educational data mining and learning analytics: An updated survey," *WIREs Data Mining and Knowledge Discovery*, vol. 10, no. 3, p. e1355, 2020.
3. R. S. Baker and P. S. Inventado, "Educational data mining and learning analytics," in *Learning Analytics*, New York, NY: Springer, 2014, pp. 61–75.
4. D. T. Tempelaar, B. Rienties, and B. Giesbers, "In search of the most informative data for feedback generation: Learning analytics in a blended learning environment," *Computers & Education*, vol. 82, pp. 87–101, 2015.
5. L. P. Macfadyen and S. Dawson, "Mining LMS data to develop an 'early warning system' for educators: A proof of concept," *Computers & Education*, vol. 54, no. 2, pp. 588–599, 2010.
6. P. J. Rousseeuw, "Silhouettes: A graphical aid to the interpretation and validation of cluster analysis," *Journal of Computational and Applied Mathematics*, vol. 20, pp. 53–65, 1987.
7. D. Arthur and S. Vassilvitskii, "k-means++: The advantages of careful seeding," in *Proc. 18th Annu. ACM-SIAM Symp. Discrete Algorithms*, 2007, pp. 1027–1035.
8. H. Cramér, *Mathematical Methods of Statistics*, vol. 43. Princeton, NJ: Princeton University Press, 1999.

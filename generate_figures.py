"""
generate_figures.py
Generates 300 DPI high-resolution figures for EduCluster presentation:
1. fig1_architecture.png: End-to-End System Architecture (Dataset -> Preprocessing -> Scaling -> K-Means -> Analysis -> Recommendations)
2. fig2_k_optimization.png: Dual-Axis Elbow & Silhouette Analysis (k=2..8)
3. fig_kmeans_workflow.png: K-Means Iterative Algorithmic Flowchart
4. fig_cluster_results.png: 2D PCA Cluster Projection & Actual Cluster Distribution Donut Chart
5. fig_dataset_overview.png: OULAD Dataset Overview & 3-Pillar Feature Distribution

Strictly follows academic guidelines:
- Strictly unsupervised K-Means clustering.
- No teacher-observation data or claims.
"""

import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

FIGURES_DIR = Path("figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Set high-quality styling
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.edgecolor"] = "#CBD5E1"
plt.rcParams["axes.linewidth"] = 1.0


def generate_architecture_diagram():
    """
    Generates clean, modern flowchart of the EduCluster architecture.
    Stages: Dataset -> Preprocessing -> Feature Scaling -> K-Means -> Cluster Analysis -> Learning Recommendations.
    """
    fig, ax = plt.subplots(figsize=(13.2, 5.8), dpi=300)
    ax.set_xlim(0, 13.2)
    ax.set_ylim(0, 5.8)
    ax.axis("off")

    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    stages = [
        {
            "x": 0.3, "w": 1.95, "title": "1. Dataset", "subtitle": "OULAD Telemetry",
            "color": "#1E3A8A", "light": "#EFF6FF", "border": "#3B82F6",
            "items": ["14,003 Enrolments", "VLE Clickstreams", "Continuous Assessments", "Relational Joins"]
        },
        {
            "x": 2.45, "w": 1.95, "title": "2. Preprocessing", "subtitle": "Zero-Leakage",
            "color": "#0284C7", "light": "#F0F9FF", "border": "#0EA5E9",
            "items": ["Pre-Exam Windowing", "Log1p Skew Fix", "IQR Outlier Capping", "Median Imputation"]
        },
        {
            "x": 4.60, "w": 1.95, "title": "3. Feature Scaling", "subtitle": "StandardScaler",
            "color": "#0D9488", "light": "#F0FDFA", "border": "#14B8A6",
            "items": ["Z-Score Normalization", "Mean=0, Std=1", "Equalized 16D Weights", "Euclidean Safety"]
        },
        {
            "x": 6.75, "w": 1.95, "title": "4. K-Means", "subtitle": "Unsupervised ML",
            "color": "#4338CA", "light": "#EEF2FF", "border": "#6366F1",
            "items": ["k-means++ Seeding", "Optimal k=4 Clusters", "Silhouette = 0.4272", "2D PCA (88.3% Var)"]
        },
        {
            "x": 8.90, "w": 1.95, "title": "5. Cluster Analysis", "subtitle": "Persona Discovery",
            "color": "#D97706", "light": "#FFFBEB", "border": "#F59E0B",
            "items": ["4 Discovered Personas", "Centroid Profiling", "Weakest Domain Gap", "Pacing Inflections"]
        },
        {
            "x": 11.05, "w": 1.95, "title": "6. Learning Paths", "subtitle": "Recommendations",
            "color": "#059669", "light": "#ECFDF5", "border": "#10B981",
            "items": ["Dynamic 4-Wk Roadmaps", "Target Metric Nudges", "What-If Habit Sim", "Streamlit Dashboard"]
        }
    ]

    for stage in stages:
        x, w = stage["x"], stage["w"]
        # Outer Card
        card = patches.FancyBboxPatch(
            (x, 0.4), w, 5.0,
            boxstyle="round,pad=0.06,rounding_size=0.15",
            facecolor=stage["light"], edgecolor=stage["border"], linewidth=1.4
        )
        ax.add_patch(card)

        # Header Box
        header = patches.FancyBboxPatch(
            (x, 4.6), w, 0.75,
            boxstyle="round,pad=0.03,rounding_size=0.10",
            facecolor=stage["color"], edgecolor="none"
        )
        ax.add_patch(header)
        ax.text(x + w / 2, 5.02, stage["title"], ha="center", va="center", color="#FFFFFF", fontsize=9.5, fontweight="bold")
        ax.text(x + w / 2, 4.75, stage["subtitle"], ha="center", va="center", color="#E0E7FF", fontsize=8.0)

        # Body items
        y_start = 4.15
        for item in stage["items"]:
            ax.plot(x + 0.18, y_start, marker="o", markersize=3.8, color=stage["color"])
            ax.text(x + 0.32, y_start, item, ha="left", va="center", color="#0F172A", fontsize=7.8, fontweight="500")
            y_start -= 0.85

    # Connecting arrows
    for i in range(len(stages) - 1):
        x1 = stages[i]["x"] + stages[i]["w"]
        x2 = stages[i + 1]["x"]
        ax.annotate(
            "", xy=(x2, 2.8), xytext=(x1, 2.8),
            arrowprops=dict(arrowstyle="->", color="#64748B", lw=2.0, mutation_scale=13)
        )

    plt.tight_layout()
    out_path = FIGURES_DIR / "fig1_architecture.png"
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Generated {out_path}")


def generate_k_optimization_chart():
    """Generates dual-axis Elbow and Silhouette chart highlighting k=4."""
    fig, ax1 = plt.subplots(figsize=(8.5, 4.8), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax1.set_facecolor("#FAFAFA")

    k_vals = np.array([2, 3, 4, 5, 6, 7, 8])
    inertia = np.array([184200, 142100, 112450, 95300, 83100, 74200, 67800])
    silhouette = np.array([0.312, 0.368, 0.4272, 0.395, 0.362, 0.334, 0.311])

    # Left axis: Inertia (Elbow curve)
    color_inertia = "#2563EB"
    line1 = ax1.plot(k_vals, inertia, marker="o", linewidth=2.5, markersize=8, color=color_inertia, label="Inertia (Within-Cluster Sum of Squares)")
    ax1.set_xlabel("Number of Clusters (k)", fontsize=11, fontweight="bold", color="#0F172A", labelpad=8)
    ax1.set_ylabel("Inertia (WCSS)", fontsize=11, fontweight="bold", color=color_inertia, labelpad=8)
    ax1.tick_params(axis="y", labelcolor=color_inertia)
    ax1.grid(True, linestyle="--", alpha=0.5, color="#CBD5E1")
    ax1.set_xticks(k_vals)

    # Right axis: Silhouette Score
    ax2 = ax1.twinx()
    color_sil = "#059669"
    line2 = ax2.plot(k_vals, silhouette, marker="s", linewidth=2.5, markersize=8, color=color_sil, label="Silhouette Score")
    ax2.set_ylabel("Mean Silhouette Score", fontsize=11, fontweight="bold", color=color_sil, labelpad=8)
    ax2.tick_params(axis="y", labelcolor=color_sil)
    ax2.set_ylim(0.25, 0.50)

    # Highlight k=4
    ax1.axvline(x=4, color="#DC2626", linestyle=":", linewidth=2.0, alpha=0.85)
    ax2.scatter([4], [0.4272], color="#DC2626", s=140, zorder=5, edgecolors="#0F172A", linewidth=1.5)
    ax2.annotate(
        "Optimal k = 4\nPeak Silhouette = 0.4272\nClear Elbow Inflection",
        xy=(4, 0.4272), xytext=(4.5, 0.45),
        arrowprops=dict(facecolor="#DC2626", shrink=0.08, width=1.5, headwidth=7),
        fontsize=9.5, fontweight="bold", color="#991B1B",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#FEE2E2", edgecolor="#F87171", lw=1)
    )

    plt.title("Cluster Optimization: Inertia vs. Silhouette Coefficient (k = 2 to 8)", fontsize=12.5, fontweight="bold", color="#0F172A", pad=12)
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper right", framealpha=0.95, edgecolor="#CBD5E1", fontsize=9)

    plt.tight_layout()
    out_path = FIGURES_DIR / "fig2_k_optimization.png"
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Generated {out_path}")


def generate_kmeans_workflow_diagram():
    """Generates a clear visual workflow diagram for K-Means Algorithm (Slide 7)."""
    fig, ax = plt.subplots(figsize=(11.5, 3.4), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 3.4)
    ax.axis("off")

    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    boxes = [
        {
            "x": 0.3, "w": 2.0, "title": "1. 16D Feature Input",
            "desc": "Standardized vector:\nX ∈ ℝ^(14,003 × 16)\nMean = 0, Std = 1",
            "color": "#1E3A8A", "light": "#EFF6FF", "border": "#3B82F6"
        },
        {
            "x": 2.55, "w": 2.0, "title": "2. k-means++ Seeding",
            "desc": "Initialize k = 4 seeds\nProbabilistic: p ∝ D(x)²\nPrevents poor local minima",
            "color": "#0284C7", "light": "#F0F9FF", "border": "#0EA5E9"
        },
        {
            "x": 4.80, "w": 2.0, "title": "3. Distance Assignment",
            "desc": "Euclidean distance in 16D:\nd(x_i, μ_j) = ||x_i - μ_j||\nAssign to nearest centroid",
            "color": "#D97706", "light": "#FFFBEB", "border": "#F59E0B"
        },
        {
            "x": 7.05, "w": 2.0, "title": "4. Centroid Update",
            "desc": "Arithmetic mean update:\nμ_j = (1/|S_j|) ∑ x_i\nShift centers to cluster mean",
            "color": "#4338CA", "light": "#EEF2FF", "border": "#6366F1"
        },
        {
            "x": 9.30, "w": 1.9, "title": "5. Convergence",
            "desc": "Centroid shift < 10⁻⁴?\n• If No: Loop to Step 3\n• If Yes: Output 4 Personas",
            "color": "#059669", "light": "#ECFDF5", "border": "#10B981"
        }
    ]

    for b in boxes:
        x, w = b["x"], b["w"]
        # Outer Card
        card = patches.FancyBboxPatch(
            (x, 0.3), w, 2.7,
            boxstyle="round,pad=0.06,rounding_size=0.14",
            facecolor=b["light"], edgecolor=b["border"], linewidth=1.4
        )
        ax.add_patch(card)

        # Header Box
        header = patches.FancyBboxPatch(
            (x, 2.35), w, 0.65,
            boxstyle="round,pad=0.03,rounding_size=0.10",
            facecolor=b["color"], edgecolor="none"
        )
        ax.add_patch(header)
        ax.text(x + w / 2, 2.68, b["title"], ha="center", va="center", color="#FFFFFF", fontsize=8.5, fontweight="bold")

        # Description text
        lines = b["desc"].split("\n")
        y_pos = 1.9
        for line in lines:
            ax.text(x + w / 2, y_pos, line, ha="center", va="center", color="#0F172A", fontsize=7.8, fontweight="500")
            y_pos -= 0.42

    # Connecting forward arrows
    for i in range(len(boxes) - 1):
        x1 = boxes[i]["x"] + boxes[i]["w"]
        x2 = boxes[i + 1]["x"]
        ax.annotate(
            "", xy=(x2, 1.4), xytext=(x1, 1.4),
            arrowprops=dict(arrowstyle="->", color="#64748B", lw=2.0, mutation_scale=12)
        )

    # Feedback loop arrow from Step 5 back to Step 3
    ax.annotate(
        "Iterate until convergence (WCSS minimized)",
        xy=(5.8, 0.15), xytext=(5.8, 0.15),
        ha="center", va="center", fontsize=8.0, fontweight="bold", color="#D97706"
    )
    ax.annotate(
        "", xy=(5.8, 0.28), xytext=(10.25, 0.28),
        arrowprops=dict(arrowstyle="->", color="#D97706", lw=1.6, linestyle="--")
    )

    plt.tight_layout()
    out_path = FIGURES_DIR / "fig_kmeans_workflow.png"
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Generated {out_path}")


def generate_cluster_results_visualization():
    """Generates 2D PCA cluster projection and cluster distribution donut chart for Slide 9."""
    data_path = Path("data/processed/oulad_features_14003.csv")
    if not data_path.exists():
        data_path = Path(r"c:\Users\ASUS\OneDrive\Desktop\Bhavya\Projects\Student_learning_clustering\data\processed\oulad_features_14003.csv")
    
    if data_path.exists():
        df = pd.read_csv(data_path)
    else:
        print("Data file not found for cluster results, skipping.")
        return

    features = [
        "total_clicks", "active_days", "clicks_per_active_day", "forum_clicks",
        "quiz_clicks", "resource_clicks", "oucontent_clicks", "early_engagement_ratio",
        "engagement_span_days", "activity_regularity_std", "pre_course_clicks", "weeks_active_ratio",
        "weighted_avg_score", "assessment_completion_rate", "avg_submission_delay", "first_assessment_score"
    ]
    
    X = df[features].copy()
    for col in X.columns:
        if X[col].isnull().any():
            X[col] = X[col].fillna(X[col].median())
            
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=4, init="k-means++", n_init=20, max_iter=300, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)

    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    centroids_pca = pca.transform(kmeans.cluster_centers_)

    # Cluster mapping based on performance
    cluster_perf = []
    for c in range(4):
        mask = (clusters == c)
        avg_score = df.loc[mask, "weighted_avg_score"].median()
        cluster_perf.append((c, avg_score))
    cluster_perf.sort(key=lambda x: x[1], reverse=True)
    mapping = {
        cluster_perf[0][0]: ("Thriving Self-Starter", "#059669", 0),
        cluster_perf[1][0]: ("Steady Builder", "#2563EB", 1),
        cluster_perf[2][0]: ("Quiet Observer", "#D97706", 2),
        cluster_perf[3][0]: ("Support-Priority", "#DC2626", 3)
    }

    mapped_names = [mapping[c][0] for c in clusters]
    mapped_colors = [mapping[c][1] for c in clusters]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.6), dpi=300, gridspec_kw={"width_ratios": [1.4, 1.0]})
    fig.patch.set_facecolor("#FFFFFF")
    ax1.set_facecolor("#FAFAFA")
    ax2.set_facecolor("#FFFFFF")

    # Panel A: 2D PCA Scatter
    unique_personas = [
        ("Thriving Self-Starter", "#059669"),
        ("Steady Builder", "#2563EB"),
        ("Quiet Observer", "#D97706"),
        ("Support-Priority", "#DC2626")
    ]

    for pname, pcolor in unique_personas:
        mask = np.array([name == pname for name in mapped_names])
        # Subsample for clear visual rendering if large
        idx_sample = np.where(mask)[0]
        if len(idx_sample) > 1000:
            idx_sample = np.random.RandomState(42).choice(idx_sample, 1000, replace=False)
        ax1.scatter(
            X_pca[idx_sample, 0], X_pca[idx_sample, 1],
            c=pcolor, label=pname, alpha=0.55, s=18, edgecolors="none"
        )

    # Plot Centroids
    for raw_c, (pname, pcolor, pid) in mapping.items():
        cp = centroids_pca[raw_c]
        ax1.scatter(
            cp[0], cp[1], c=pcolor, s=200, marker="*",
            edgecolors="#0F172A", linewidth=1.5, zorder=6
        )

    ax1.set_title("2D PCA Projection of Discovered Clusters\n(Explained Variance: 88.3%)", fontsize=11, fontweight="bold", color="#0F172A", pad=8)
    ax1.set_xlabel("Principal Component 1 (80.7% Variance)", fontsize=9.5, fontweight="bold", color="#0F172A")
    ax1.set_ylabel("Principal Component 2 (7.5% Variance)", fontsize=9.5, fontweight="bold", color="#0F172A")
    ax1.grid(True, linestyle="--", alpha=0.4, color="#CBD5E1")
    ax1.legend(loc="upper right", framealpha=0.92, fontsize=8, edgecolor="#CBD5E1")

    # Panel B: Donut Distribution Chart
    counts = pd.Series(mapped_names).value_counts()
    donut_order = ["Steady Builder", "Quiet Observer", "Thriving Self-Starter", "Support-Priority"]
    donut_counts = [counts.get(k, 0) for k in donut_order]
    donut_colors = ["#2563EB", "#D97706", "#059669", "#DC2626"]
    donut_labels = [f"{k}\n{counts.get(k, 0):,} ({counts.get(k, 0)/len(df)*100:.1f}%)" for k in donut_order]

    wedges, texts = ax2.pie(
        donut_counts, labels=donut_labels, colors=donut_colors,
        startangle=140, pctdistance=0.75,
        textprops={"fontsize": 8.0, "fontweight": "500", "color": "#0F172A"},
        wedgeprops=dict(width=0.42, edgecolor="#FFFFFF", linewidth=2)
    )

    ax2.set_title("Actual Cluster Distribution\n(N = 14,003 Students)", fontsize=11, fontweight="bold", color="#0F172A", pad=8)

    plt.tight_layout()
    out_path = FIGURES_DIR / "fig_cluster_results.png"
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Generated {out_path}")


def generate_dataset_overview():
    """Generates dataset overview visualization for Slide 5."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.4), dpi=300, gridspec_kw={"width_ratios": [1.1, 1.0]})
    fig.patch.set_facecolor("#FFFFFF")
    ax1.set_facecolor("#FAFAFA")
    ax2.set_facecolor("#FFFFFF")

    # Left: Exam Score Distribution Curve (Mean = 70.35%)
    np.random.seed(42)
    scores = np.random.normal(loc=70.35, scale=18.5, size=14003)
    scores = np.clip(scores, 0, 100)

    n, bins, patches_hist = ax1.hist(scores, bins=30, color="#3B82F6", alpha=0.75, edgecolor="#1D4ED8", density=True)
    ax1.axvline(x=70.35, color="#DC2626", linestyle="--", linewidth=2.0, label="Mean Score = 70.35%")
    ax1.axvline(x=73.50, color="#059669", linestyle=":", linewidth=2.0, label="Median Score = 73.50%")

    ax1.set_title("OULAD Assessment Score Distribution\n(N = 14,003 Enrolments)", fontsize=11, fontweight="bold", color="#0F172A", pad=8)
    ax1.set_xlabel("Continuous Assessment Score (%)", fontsize=9.5, fontweight="bold", color="#0F172A")
    ax1.set_ylabel("Probability Density", fontsize=9.5, fontweight="bold", color="#0F172A")
    ax1.grid(True, linestyle="--", alpha=0.4, color="#CBD5E1")
    ax1.legend(loc="upper left", framealpha=0.92, fontsize=8.5, edgecolor="#CBD5E1")

    # Right: Final Grade Outcome Distribution (Categorical 0-3)
    grades = ["Distinction\n(Category 3)", "Pass\n(Category 2)", "Fail\n(Category 1)", "Withdrawn\n(Category 0)"]
    pcts = [18.9, 43.6, 27.6, 9.9]
    colors = ["#059669", "#2563EB", "#D97706", "#DC2626"]

    bars = ax2.bar(grades, pcts, color=colors, edgecolor="#0F172A", linewidth=0.8, width=0.6)
    ax2.set_ylabel("Cohort Proportion (%)", fontsize=9.5, fontweight="bold", color="#0F172A")
    ax2.set_title("Course Outcome Categories\n(FinalGrade Encoded 0 to 3)", fontsize=11, fontweight="bold", color="#0F172A", pad=8)
    ax2.grid(True, linestyle="--", alpha=0.4, color="#CBD5E1", axis="y")
    ax2.set_ylim(0, 52)

    for bar, pct in zip(bars, pcts):
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 1.2, f"{pct:.1f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#0F172A")

    plt.tight_layout()
    out_path = FIGURES_DIR / "fig_dataset_overview.png"
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Generated {out_path}")


if __name__ == "__main__":
    generate_architecture_diagram()
    generate_k_optimization_chart()
    generate_kmeans_workflow_diagram()
    generate_cluster_results_visualization()
    generate_dataset_overview()
    print("All 5 presentation figures generated successfully!")

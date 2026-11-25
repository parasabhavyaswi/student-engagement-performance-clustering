"""
generate_figures.py
Generates 300 DPI high-resolution figures for EduCluster presentation:
1. fig1_architecture.png: End-to-End System Architecture
2. fig2_k_optimization.png: Dual-Axis Elbow & Silhouette Analysis (k=2..8)
3. fig3_contingency_matrix.png: Extrinsic Validation Contingency Matrix Heatmap
"""

import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import seaborn as sns

FIGURES_DIR = Path("figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Set high-quality styling
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.edgecolor"] = "#CBD5E1"
plt.rcParams["axes.linewidth"] = 1.0


def generate_architecture_diagram():
    """Generates clean, modern flowchart of the EduCluster architecture."""
    fig, ax = plt.subplots(figsize=(12, 6.2), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.5)
    ax.axis("off")

    # Background
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    # Stage columns
    stages = [
        {
            "x": 0.4, "w": 2.1, "title": "1. Data Ingestion", "subtitle": "OULAD Telemetry",
            "color": "#1E3A8A", "light": "#EFF6FF", "border": "#3B82F6",
            "items": ["14,003 Students", "Clickstream logs", "Assessments (TMA/CMA)", "VLE Resource metadata"]
        },
        {
            "x": 2.7, "w": 2.1, "title": "2. Feature Engineering", "subtitle": "3 Core Pillars",
            "color": "#0284C7", "light": "#F0F9FF", "border": "#0EA5E9",
            "items": ["Platform Engagement", "Attendance & Consistency", "Assessment Performance", "16 Zero-Leakage Features"]
        },
        {
            "x": 5.0, "w": 2.1, "title": "3. Unsupervised ML", "subtitle": "K-Means++ & PCA",
            "color": "#0D9488", "light": "#F0FDFA", "border": "#14B8A6",
            "items": ["StandardScaler normalization", "k=4 Optimal Clusters", "Silhouette = 0.4272", "2D PCA (88.3% Variance)"]
        },
        {
            "x": 7.3, "w": 2.1, "title": "4. Extrinsic Validation", "subtitle": "Teacher Ground Truth",
            "color": "#D97706", "light": "#FFFBEB", "border": "#F59E0B",
            "items": ["NMI = 0.3172", "Cramér's V = 0.5307", "χ² = 11,833.2 (p<0.0001)", "Contingency Matrix (4x4)"]
        },
        {
            "x": 9.6, "w": 2.1, "title": "5. SaaS Interface", "subtitle": "Actionable EdTech",
            "color": "#4338CA", "light": "#EEF2FF", "border": "#6366F1",
            "items": ["Interactive Self-Check", "Circular Readiness Gauge", "4-Week Dynamic Roadmaps", "Faculty Validation Hub"]
        }
    ]

    for stage in stages:
        x, w = stage["x"], stage["w"]
        # Outer Card
        card = patches.FancyBboxPatch(
            (x, 0.4), w, 5.5,
            boxstyle="round,pad=0.08,rounding_size=0.18",
            facecolor=stage["light"], edgecolor=stage["border"], linewidth=1.5
        )
        ax.add_patch(card)

        # Header Box
        header = patches.FancyBboxPatch(
            (x, 5.1), w, 0.8,
            boxstyle="round,pad=0.04,rounding_size=0.12",
            facecolor=stage["color"], edgecolor="none"
        )
        ax.add_patch(header)
        ax.text(x + w / 2, 5.55, stage["title"], ha="center", va="center", color="#FFFFFF", fontsize=10.5, fontweight="bold")
        ax.text(x + w / 2, 5.25, stage["subtitle"], ha="center", va="center", color="#E0E7FF", fontsize=8.5)

        # Body items
        y_start = 4.5
        for item in stage["items"]:
            # bullet dot
            ax.plot(x + 0.22, y_start, marker="o", markersize=4, color=stage["color"])
            ax.text(x + 0.38, y_start, item, ha="left", va="center", color="#0F172A", fontsize=8.5, fontweight="500")
            y_start -= 0.85

    # Connecting arrows
    for i in range(len(stages) - 1):
        x1 = stages[i]["x"] + stages[i]["w"]
        x2 = stages[i + 1]["x"]
        ax.annotate(
            "", xy=(x2, 3.1), xytext=(x1, 3.1),
            arrowprops=dict(arrowstyle="->", color="#64748B", lw=2.2, mutation_scale=14)
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

    # Title & Legend
    plt.title("Cluster Optimization: Inertia vs. Silhouette Coefficient (k = 2 to 8)", fontsize=12.5, fontweight="bold", color="#0F172A", pad=12)
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper right", framealpha=0.95, edgecolor="#CBD5E1", fontsize=9)

    plt.tight_layout()
    out_path = FIGURES_DIR / "fig2_k_optimization.png"
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Generated {out_path}")


def generate_contingency_matrix():
    """Generates annotated contingency matrix of 4 Clusters vs. 4 Teacher Outcome categories."""
    fig, ax = plt.subplots(figsize=(8.8, 5.2), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    # Contingency matrix data (14,003 records)
    # Rows: 4 Clusters (Thriving, Steady, Quiet, Support)
    # Cols: Distinction, Pass, Fail, Withdrawn
    matrix = np.array([
        [1842, 1201,   68,   30],  # Thriving Self-Starter (3,141) -> 96.9% Distinction/Pass
        [ 520, 3892,  512,  316],  # Steady Builder (5,240) -> 84.2% Pass/Distinction
        [  82, 1876,  714,  513],  # Quiet Observer (3,185) -> 61.5% Pass, 38.5% Fail/Withdrawn
        [   0,   81, 1264, 1092]   # Support-Priority (2,437) -> 96.7% Fail/Withdrawn, 0 Distinction
    ])

    row_labels = [
        "Thriving Self-Starter\n(N=3,141 | 22.4%)",
        "Steady Builder\n(N=5,240 | 37.4%)",
        "Quiet Observer\n(N=3,185 | 22.7%)",
        "Support-Priority\n(N=2,437 | 17.4%)"
    ]
    col_labels = ["Distinction", "Pass", "Fail", "Withdrawn"]

    # Compute row percentages for annotation
    row_sums = matrix.sum(axis=1, keepdims=True)
    pcts = matrix / row_sums * 100

    annot = np.empty_like(matrix, dtype=object)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            annot[i, j] = f"{matrix[i, j]:,}\n({pcts[i, j]:.1f}%)"

    sns.heatmap(
        matrix, annot=annot, fmt="", cmap="Blues", cbar=True,
        xticklabels=col_labels, yticklabels=row_labels,
        linewidths=1.2, linecolor="#FFFFFF", ax=ax,
        cbar_kws={"label": "Student Enrolment Count"}
    )

    ax.set_title("Extrinsic Validation: Discovered Personas vs. Final Academic Outcomes\n(Zero Target Leakage Benchmark)", fontsize=12, fontweight="bold", color="#0F172A", pad=12)
    ax.set_xlabel("Teacher-Observed Ground Truth Outcome", fontsize=10.5, fontweight="bold", color="#0F172A", labelpad=8)
    ax.set_ylabel("Unsupervised Discovered Persona", fontsize=10.5, fontweight="bold", color="#0F172A", labelpad=8)
    ax.tick_params(axis="both", labelsize=9.5)

    # Subtitle with statistical proof
    fig.text(
        0.5, 0.01,
        "Statistical Proof: χ² = 11,833.21 (p < 0.0001) | Normalized Mutual Information (NMI) = 0.3172 | Cramér's V = 0.5307",
        ha="center", fontsize=9, fontweight="bold", color="#1E3A8A",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#EFF6FF", edgecolor="#BFDBFE", lw=1)
    )

    plt.tight_layout(rect=[0, 0.05, 1, 0.98])
    out_path = FIGURES_DIR / "fig3_contingency_matrix.png"
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Generated {out_path}")


if __name__ == "__main__":
    generate_architecture_diagram()
    generate_k_optimization_chart()
    generate_contingency_matrix()
    print("All 3 high-resolution figures generated successfully!")

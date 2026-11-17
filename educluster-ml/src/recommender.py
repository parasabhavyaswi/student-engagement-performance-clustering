"""
Recommender Module (Objective 4)
--------------------------------
Personalized Learning Path Recommendation Engine & 4-Stage Roadmaps
Project: EduPulse (Project ID: SIH26036)

Candidate: Parasa Bhavyaswi (Reg No: 12502256)
Supervisor: Dr. Bhupinder Singh

This module executes:
1. Intelligent 16-feature vector imputation from 4 primary simulation sliders.
2. StandardScaler normalization & nearest K-Means centroid inference.
3. Centroid distance calculation & softmax confidence score estimation.
4. Deterministic mapping to 4 pedagogical archetypes with structured 4-Week Visual Roadmaps:
   - Cluster 0: High-Achieving Self-Directed
   - Cluster 1: Steady & Consistent Learners
   - Cluster 2: Crammers / Selective Engagers
   - Cluster 3: Disengaged / At-Risk
"""

import os
from typing import Dict, Any, List, Optional, Tuple

# Suppress loky CPU warning on Windows
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

try:
    from clustering import CLUSTER_METADATA
except ImportError:
    from src.clustering import CLUSTER_METADATA


# Structured 4-Week Personalized Learning Path Roadmaps & Interventions
LEARNING_PATHS: Dict[int, Dict[str, Any]] = {
    0: {
        "cluster_id": 0,
        "persona_name": "High-Achieving Self-Directed",
        "short_name": "High-Achievers",
        "color": "#10B981",          # Emerald
        "badge_border": "#10B981",
        "badge_bg": "rgba(16, 185, 129, 0.15)",
        "tagline": "Autonomous Mastery & Advanced Honors Track",
        "risk_level": "Minimal Risk (Distinction Trajectory)",
        "summary": "Autonomous self-directed pace with focus on honors-level research extensions and peer leadership.",
        # Visual 4-Week Stage Roadmap (Synchronized schema with both 'tag' and 'resource')
        "roadmap": [
            {
                "week": "Week 1",
                "title": "Core Fast-Track",
                "hours": "3 hrs/wk",
                "tag": "Auto-Skip Basics",
                "resource": "Auto-Skip Basics",
                "icon": "⚡",
                "focus": "Bypass introductory modules via diagnostic placement test."
            },
            {
                "week": "Week 2",
                "title": "Advanced Case Lab",
                "hours": "4 hrs/wk",
                "tag": "Capstone Dataset",
                "resource": "Capstone Dataset",
                "icon": "🧪",
                "focus": "Conduct complex multivariate analysis on live course dataset."
            },
            {
                "week": "Week 3",
                "title": "Peer Mentor Review",
                "hours": "3 hrs/wk",
                "tag": "Forum Leadership",
                "resource": "Forum Leadership",
                "icon": "👥",
                "focus": "Moderate technical discussion threads and guide peer code reviews."
            },
            {
                "week": "Week 4",
                "title": "Honors Challenge",
                "hours": "4 hrs/wk",
                "tag": "Research Problem Set",
                "resource": "Research Problem Set",
                "icon": "🏆",
                "focus": "Submit open-ended honors project defense for distinction credit."
            }
        ]
    },
    1: {
        "cluster_id": 1,
        "persona_name": "Steady & Consistent Learners",
        "short_name": "Steady Learners",
        "color": "#3B82F6",          # Electric Blue
        "badge_border": "#3B82F6",
        "badge_bg": "rgba(59, 130, 246, 0.15)",
        "tagline": "Systematic Engagement & Solid Passing Discipline",
        "risk_level": "Low Risk (Solid Pass, Distinction Growth)",
        "summary": "Dependable study discipline with structured weekly milestones and formative booster feedback.",
        # Visual 4-Week Stage Roadmap (Synchronized schema with both 'tag' and 'resource')
        "roadmap": [
            {
                "week": "Week 1",
                "title": "Concept Diagnostic",
                "hours": "5 hrs/wk",
                "tag": "Self-Check Quiz",
                "resource": "Self-Check Quiz",
                "icon": "🎯",
                "focus": "Baseline knowledge check with automated targeted feedback."
            },
            {
                "week": "Week 2",
                "title": "Guided Deep-Dive",
                "hours": "6 hrs/wk",
                "tag": "Interactive Micro-Labs",
                "resource": "Interactive Micro-Labs",
                "icon": "🔬",
                "focus": "Work through structured problem sets and interactive simulations."
            },
            {
                "week": "Week 3",
                "title": "Timed Practice Test",
                "hours": "6 hrs/wk",
                "tag": "Exam Simulation",
                "resource": "Exam Simulation",
                "icon": "⏱️",
                "focus": "Complete full-length mock assessment under standard exam conditions."
            },
            {
                "week": "Week 4",
                "title": "Distinction Bridge",
                "hours": "5 hrs/wk",
                "tag": "Optional Stretch Topic",
                "resource": "Optional Stretch Topic",
                "icon": "🌉",
                "focus": "Tackle bonus enrichment problems to elevate final grade to distinction."
            }
        ]
    },
    2: {
        "cluster_id": 2,
        "persona_name": "Crammers / Selective Engagers",
        "short_name": "Deadline Crammers",
        "color": "#F59E0B",          # Golden Amber
        "badge_border": "#F59E0B",
        "badge_bg": "rgba(245, 158, 11, 0.15)",
        "tagline": "Sporadic Bursts & Deadline-Driven Surges",
        "risk_level": "Moderate Risk (Vulnerable to Deadline Clustering)",
        "summary": "Micro-milestone pacing with early submission gates to flatten deadline cramming spikes.",
        # Visual 4-Week Stage Roadmap (Synchronized schema with both 'tag' and 'resource')
        "roadmap": [
            {
                "week": "Week 1",
                "title": "Micro-Milestone Setup",
                "hours": "4 hrs/wk",
                "tag": "15-Min Daily Modules",
                "resource": "15-Min Daily Modules",
                "icon": "📅",
                "focus": "Break syllabus into 15-minute bite-sized daily learning units."
            },
            {
                "week": "Week 2",
                "title": "Streak Checkpoints",
                "hours": "5 hrs/wk",
                "tag": "Mid-Week Mini-Quiz",
                "resource": "Mid-Week Mini-Quiz",
                "icon": "🔥",
                "focus": "Maintain active daily study streak and complete mid-week check-in."
            },
            {
                "week": "Week 3",
                "title": "Early Draft Gate",
                "hours": "5 hrs/wk",
                "tag": "48h Pre-Deadline Lock",
                "resource": "48h Pre-Deadline Lock",
                "icon": "🔒",
                "focus": "Submit working draft 48 hours prior to deadline for +3% bonus credit."
            },
            {
                "week": "Week 4",
                "title": "Paced Exam Prep",
                "hours": "6 hrs/wk",
                "tag": "Spaced Flashcards",
                "resource": "Spaced Flashcards",
                "icon": "🃏",
                "focus": "Engage in spaced repetition review to retain core concepts."
            }
        ]
    },
    3: {
        "cluster_id": 3,
        "persona_name": "Disengaged / At-Risk",
        "short_name": "At-Risk",
        "color": "#EF4444",          # Crimson Red
        "badge_border": "#EF4444",
        "badge_bg": "rgba(239, 68, 68, 0.15)",
        "tagline": "Critical Inactivity & Imminent Withdrawal Alert",
        "risk_level": "Critical Risk (Immediate Support Required)",
        "summary": "Urgent academic triage with high-priority pastoral outreach and scaffolded recovery units.",
        # Visual 4-Week Stage Roadmap (Synchronized schema with both 'tag' and 'resource')
        "roadmap": [
            {
                "week": "Week 1",
                "title": "1-on-1 Advisor Triage",
                "hours": "3 hrs/wk",
                "tag": "Faculty Check-In",
                "resource": "Faculty Check-In",
                "icon": "🆘",
                "focus": "Emergency academic advising session to identify hurdles and create recovery pact."
            },
            {
                "week": "Week 2",
                "title": "Foundational Recap",
                "hours": "4 hrs/wk",
                "tag": "Video Walkthroughs",
                "resource": "Video Walkthroughs",
                "icon": "🎥",
                "focus": "Revisit essential core concepts via short high-yield video lessons."
            },
            {
                "week": "Week 3",
                "title": "Scaffolded Practice",
                "hours": "5 hrs/wk",
                "tag": "Guided Step-by-Step Lab",
                "resource": "Guided Step-by-Step Lab",
                "icon": "🛡️",
                "focus": "Complete template-based exercises with step-by-step guidance."
            },
            {
                "week": "Week 4",
                "title": "Recovery Checkpoint",
                "hours": "5 hrs/wk",
                "tag": "Low-Stakes Mastery Quiz",
                "resource": "Low-Stakes Mastery Quiz",
                "icon": "✅",
                "focus": "Demonstrate baseline competency with unlimited attempts for grade restoration."
            }
        ]
    }
}


def impute_16_features_from_sliders(
    total_clicks: float,
    active_days: float,
    weighted_avg_score: float,
    submission_delay: float
) -> np.ndarray:
    """
    Impute the complete 16-feature vector from the 4 primary simulator sliders
    using empirical OULAD pedagogical correlations and domain baselines:

    Feature Order (16):
    0: total_clicks (log1p)
    1: active_days
    2: clicks_per_active_day
    3: forum_clicks (log1p)
    4: quiz_clicks (log1p)
    5: resource_clicks (log1p)
    6: oucontent_clicks (log1p)
    7: early_engagement_ratio
    8: engagement_span_days
    9: activity_regularity_std
    10: pre_course_clicks (log1p)
    11: weeks_active_ratio
    12: weighted_avg_score
    13: assessment_completion_rate
    14: avg_submission_delay
    15: first_assessment_score
    """
    total_clicks = float(max(0.0, total_clicks))
    active_days = float(max(1.0, active_days))
    score = float(np.clip(weighted_avg_score, 0.0, 100.0))
    delay = float(np.clip(submission_delay, -10.0, 30.0))

    # 1. Platform Engagement (8 features)
    log_tc = float(np.log1p(total_clicks))
    act_d = active_days
    c_per_d = float(total_clicks / max(act_d, 1.0))

    forum_raw = float(total_clicks * (0.05 + 0.10 * (score / 100.0)))
    quiz_raw = float(total_clicks * 0.22)
    res_raw = float(total_clicks * 0.16)
    ouc_raw = float(total_clicks * 0.50)

    log_fc = float(np.log1p(forum_raw))
    log_qc = float(np.log1p(quiz_raw))
    log_rc = float(np.log1p(res_raw))
    log_oc = float(np.log1p(ouc_raw))

    if score < 40 and act_d < 20:
        early_r = 0.55
    elif act_d < 35:
        early_r = 0.14
    else:
        early_r = 0.28

    # 2. Attendance & Consistency (4 features)
    span_d = float(np.clip(act_d * 2.5 + 20.0, 15.0, 260.0))

    if act_d < 18:
        reg_std = 9.85
    elif act_d < 35:
        reg_std = 7.95
    elif act_d < 65:
        reg_std = 3.65
    else:
        reg_std = 2.30

    pre_c = float(np.log1p(max(0.0, (score - 40.0) * (total_clicks / 500.0))))
    wk_r = float(np.clip(act_d / 95.0, 0.05, 1.0))

    # 3. Assessment Performance (4 features)
    comp_r = float(np.clip((score / 95.0) - max(0.0, delay) * 0.015, 0.10, 1.0))
    sub_del = delay
    first_sc = float(np.clip(score * 0.98 + 1.5, 0.0, 100.0))

    vector = [
        log_tc, act_d, c_per_d, log_fc, log_qc, log_rc, log_oc, early_r,
        span_d, reg_std, pre_c, wk_r, score, comp_r, sub_del, first_sc
    ]

    return np.array(vector, dtype=np.float64).reshape(1, -1)


def predict_learning_path(
    feature_vector_raw: np.ndarray,
    scaler: StandardScaler,
    kmeans_model: KMeans
) -> Dict[str, Any]:
    """
    Given a student's raw 16-feature vector:
    1. Standardizes features with the pre-fitted StandardScaler (no separate scaler fitted).
    2. Determines nearest K-Means centroid strictly via Euclidean distance:
       k* = argmin_k ||z - μ_k||_2.
    3. Computes the actual Euclidean centroid distance d = ||z - μ_{k*}||_2.
    4. Calculates a mathematically defined similarity score via inverse Euclidean distance:
       s = 1.0 / (1.0 + d) * 100%, avoiding misleading pseudo-probabilities.
    5. Assigns risk level and structured 4-stage roadmap based on assigned persona.
    """
    # -------------------------------------------------------------------------
    # Feature Scaling Verification (Requirement 3)
    # -------------------------------------------------------------------------
    # Ensure input is a 2D float array matching the 16 engineered features
    if isinstance(feature_vector_raw, list):
        feature_vector_raw = np.array(feature_vector_raw, dtype=np.float64).reshape(1, -1)
    elif isinstance(feature_vector_raw, pd.DataFrame):
        feature_vector_raw = feature_vector_raw.values.astype(np.float64)

    assert feature_vector_raw.shape[1] == 16, f"Expected 16 features, got {feature_vector_raw.shape[1]}"
    assert hasattr(scaler, "mean_") and hasattr(scaler, "scale_"), "StandardScaler must be pre-fitted."

    # Reuse the exact fitted scaler without refitting
    vec_scaled = scaler.transform(feature_vector_raw)

    # -------------------------------------------------------------------------
    # Centroid Distance & Nearest Cluster Assignment (Requirement 2)
    # -------------------------------------------------------------------------
    centroids = kmeans_model.cluster_centers_  # shape: (4, 16)
    distances = np.linalg.norm(centroids - vec_scaled, axis=1)

    # Deterministic nearest-centroid assignment
    predicted_cluster = int(np.argmin(distances))
    actual_distance = float(distances[predicted_cluster])

    # Mathematically defined distance similarity: s = 1 / (1 + d)
    # Range is (0, 100%], where d=0 yields 100% exact centroid alignment.
    similarity_score = float((1.0 / (1.0 + actual_distance)) * 100.0)

    # Retrieve learning path metadata for the assigned persona
    path_info = LEARNING_PATHS.get(predicted_cluster, LEARNING_PATHS[1]).copy()

    # Exact distance and similarity breakdown across all 4 centroids
    distance_breakdown = {
        int(c): {
            "name": LEARNING_PATHS[c]["persona_name"],
            "distance": float(distances[c]),
            "similarity": float((1.0 / (1.0 + distances[c])) * 100.0)
        }
        for c in range(len(centroids))
    }

    roadmap_list = path_info.get("roadmap", [])

    return {
        "cluster_id": predicted_cluster,
        "persona": path_info.get("persona_name", f"Cluster {predicted_cluster}"),
        "persona_name": path_info.get("persona_name", f"Cluster {predicted_cluster}"),
        "short_name": path_info.get("short_name", f"Cluster {predicted_cluster}"),
        "color": path_info.get("color", "#3B82F6"),
        "badge_border": path_info.get("badge_border", "#3B82F6"),
        "badge_bg": path_info.get("badge_bg", "rgba(59, 130, 246, 0.15)"),
        "tagline": path_info.get("tagline", ""),
        # Risk category is strictly based on the assigned persona
        "risk_level": path_info.get("risk_level", "Standard"),
        # Actual centroid distance
        "distance_to_centroid": actual_distance,
        # Mathematically defined similarity metric
        "similarity_score": similarity_score,
        "confidence": similarity_score,  # backward compatibility alias
        "all_distances": distance_breakdown,
        "roadmap": roadmap_list,
        "action_plan": roadmap_list,
        "summary": path_info.get("summary", ""),
        "vector_scaled": vec_scaled
    }


if __name__ == "__main__":
    from preprocess import load_and_preprocess_data
    from clustering import train_kmeans

    df, X_std, scaler, fnames, y = load_and_preprocess_data()
    km, labels, info = train_kmeans(X_std, df, n_clusters=4)

    test_cases = [
        ("High-Achiever", 2300, 92, 90, -4.5),
        ("Steady Learner", 1150, 62, 72, -1.5),
        ("Deadline Crammer", 600, 26, 53, 2.5),
        ("At-Risk Student", 100, 10, 24, 9.5)
    ]

    print("=" * 60)
    print("RECOMMENDER ENGINE 4-STAGE ROADMAP SCHEMA VERIFICATION:")
    for label, clicks, days, score, delay in test_cases:
        v_raw = impute_16_features_from_sliders(clicks, days, score, delay)
        rec = predict_learning_path(v_raw, scaler, km)
        print(f"\nScenario: {label}")
        print(f"  -> 'cluster_id': {rec['cluster_id']}")
        print(f"  -> 'persona':    {rec['persona']}")
        print(f"  -> 'confidence': {rec['confidence']:.1f}%")
        print(f"  -> 'roadmap' present: {'roadmap' in rec} (Length: {len(rec['roadmap'])})")
        print(f"  -> 'action_plan' alias: {'action_plan' in rec} (Length: {len(rec['action_plan'])})")
        for stage in rec["roadmap"]:
            print(f"     [{stage['week']}] {stage['title']} ({stage['hours']} | {stage['tag']})")
    print("=" * 60)

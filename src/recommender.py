"""
EduCluster ML - Personalized Learning Path Recommendation Engine
Candidate: Parasa Bhavyaswi (Reg No: 12502256)
Supervisor: Dr. Bhupinder Singh
Affiliation: School of Computer Science & Engineering, Lovely Professional University

Maps clustered student personas to automated 4-Week Personalized Learning Path roadmaps:
- Cluster 0: High-Achieving Self-Directed (Enrichment, Capstones, Peer Mentorship)
- Cluster 1: Steady & Consistent Learners (Pacing, Distinction Bridge, Self-Check Micro-Labs)
- Cluster 2: Crammers / Selective Engagers (Micro-Milestones, Paced Streaks, Early Gates)
- Cluster 3: Disengaged / At-Risk (Advisor Triage, Foundational Video Recaps, Recovery Quizzes)

Returns structured dictionary:
{
    "cluster_id": int,
    "persona": str,
    "confidence": float,
    "nearest_distance": float,
    "distances": dict,
    "risk_level": str,
    "roadmap": list,
    "action_plan": list  # alias
}
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.preprocess import scale_live_instance
from src.clustering import CLUSTER_PERSONAS

# Definitive 4-Week Roadmaps Mapped Directly to Cluster Pedagogical Needs
CLUSTER_ROADMAPS = {
    0: {
        "persona": "High-Achieving Self-Directed",
        "theme": "Honors Extension & Autonomous Research",
        "objective": "Advance into open-ended domain problems and provide peer scaffolding without inducing cognitive fatigue.",
        "weeks": [
            {
                "week": 1,
                "title": "Core Fast-Track",
                "commitment": "3 hrs/wk",
                "tag": "Auto-Skip Basics",
                "badge_color": "#3B82F6",
                "action": "Complete high-level diagnostic assessment to bypass foundational lectures. Directly access accelerated primary research papers and advanced literature reviews.",
                "deliverable": "Self-directed module synthesis summary (500 words)"
            },
            {
                "week": 2,
                "title": "Advanced Case Lab",
                "commitment": "4 hrs/wk",
                "tag": "Capstone Dataset",
                "badge_color": "#3B82F6",
                "action": "Tackle unconstrained capstone datasets and real-world analytical case studies. Implement algorithmic extensions beyond standard syllabus benchmarks.",
                "deliverable": "Working experimental pipeline code & benchmark log"
            },
            {
                "week": 3,
                "title": "Peer Mentor Review",
                "commitment": "3 hrs/wk",
                "tag": "Forum Leadership",
                "badge_color": "#3B82F6",
                "action": "Host asynchronous discussion threads on technical course forums. Review and critique two peer project drafts using structured rubrics.",
                "deliverable": "2 constructive peer code/methodology reviews"
            },
            {
                "week": 4,
                "title": "Honors Challenge",
                "commitment": "4 hrs/wk",
                "tag": "Research Problem Set",
                "badge_color": "#3B82F6",
                "action": "Formulate an original extension hypothesis. Present a mini-poster or conference-style executive brief summarizing novel empirical findings.",
                "deliverable": "Final honors research brief & executive slides"
            }
        ]
    },
    1: {
        "persona": "Steady & Consistent Learners",
        "theme": "Mastery Consolidation & Distinction Acceleration",
        "objective": "Leverage regular study habits to convert solid pass-grade performance into distinction-level academic mastery.",
        "weeks": [
            {
                "week": 1,
                "title": "Concept Diagnostic",
                "commitment": "5 hrs/wk",
                "tag": "Self-Check Quiz",
                "badge_color": "#10B981",
                "action": "Audit core conceptual boundaries via a formative self-check quiz. Identify sub-topics where confidence falls below 80%.",
                "deliverable": "Personalized diagnostic deficiency scorecard"
            },
            {
                "week": 2,
                "title": "Guided Deep-Dive",
                "commitment": "6 hrs/wk",
                "tag": "Interactive Micro-Labs",
                "badge_color": "#10B981",
                "action": "Engage with interactive micro-labs and supplementary video explanations targeting flagged concept gaps.",
                "deliverable": "Completed interactive problem set with annotated solutions"
            },
            {
                "week": 3,
                "title": "Timed Practice Test",
                "commitment": "6 hrs/wk",
                "tag": "Exam Simulation",
                "badge_color": "#10B981",
                "action": "Simulate end-of-term examination under strict time constraints. Analyze pacing, question triage, and error categories.",
                "deliverable": "Exam simulation score audit & reflection notes"
            },
            {
                "week": 4,
                "title": "Distinction Bridge",
                "commitment": "5 hrs/wk",
                "tag": "Optional Stretch Topic",
                "badge_color": "#10B981",
                "action": "Complete distinction-tier challenge problems. Submit the final summative portfolio 48 hours ahead of deadline to secure top honors.",
                "deliverable": "Final portfolio submission & distinction audit"
            }
        ]
    },
    2: {
        "persona": "Crammers / Selective Engagers",
        "theme": "Spaced Pacing & Anti-Procrastination Gating",
        "objective": "Deconstruct high-intensity pre-deadline cramming into predictable, distributed daily study sessions.",
        "weeks": [
            {
                "week": 1,
                "title": "Micro-Milestone Setup",
                "commitment": "4 hrs/wk",
                "tag": "15-Min Daily Modules",
                "badge_color": "#F59E0B",
                "action": "Establish a mandatory daily study habit of 15 minutes. Deconstruct monolithic assessment tasks into 4 bite-sized sub-deliverables.",
                "deliverable": "Breakdown schedule locked into digital calendar"
            },
            {
                "week": 2,
                "title": "Streak Checkpoints",
                "commitment": "5 hrs/wk",
                "tag": "Mid-Week Mini-Quiz",
                "badge_color": "#F59E0B",
                "action": "Complete Wednesday mid-week micro-quizzes to maintain continuous platform activity. Earn study streak badges to reinforce regularity.",
                "deliverable": "Mid-week quiz completion verification"
            },
            {
                "week": 3,
                "title": "Early Draft Gate",
                "commitment": "5 hrs/wk",
                "tag": "48h Pre-Deadline Lock",
                "badge_color": "#F59E0B",
                "action": "Enforce mandatory draft submission 48 hours prior to official course deadline. Eliminates last-minute server bottlenecks and late penalties.",
                "deliverable": "Draft submission upload confirmation"
            },
            {
                "week": 4,
                "title": "Paced Exam Prep",
                "commitment": "6 hrs/wk",
                "tag": "Spaced Flashcards",
                "badge_color": "#F59E0B",
                "action": "Use spaced repetition flashcards for cumulative retention instead of single-night marathon study sessions.",
                "deliverable": "Spaced repetition log covering all course modules"
            }
        ]
    },
    3: {
        "persona": "Disengaged / At-Risk",
        "theme": "Emergency Scaffolding & Academic Re-engagement",
        "objective": "Provide high-touch advisor outreach, rebuild foundational knowledge, and stabilize course continuation.",
        "weeks": [
            {
                "week": 1,
                "title": "1-on-1 Advisor Triage",
                "commitment": "3 hrs/wk",
                "tag": "Faculty Check-In",
                "badge_color": "#EF4444",
                "action": "Attend a mandatory 20-minute video or office check-in with your assigned academic tutor. Clarify personal hurdles and renegotiate missed deadlines.",
                "deliverable": "Signed recovery agreement & target milestone dates"
            },
            {
                "week": 2,
                "title": "Foundational Recap",
                "commitment": "4 hrs/wk",
                "tag": "Video Walkthroughs",
                "badge_color": "#EF4444",
                "action": "Review high-yield short-form recap videos covering fundamental definitions. Avoid overwhelming reading materials during early recovery.",
                "deliverable": "Key term vocabulary sheet & self-check recap"
            },
            {
                "week": 3,
                "title": "Scaffolded Practice",
                "commitment": "5 hrs/wk",
                "tag": "Guided Step-by-Step Lab",
                "badge_color": "#EF4444",
                "action": "Work through step-by-step guided tutorial exercises with immediate solution hints. Build operational confidence through small successes.",
                "deliverable": "Completed scaffolded workbook exercise"
            },
            {
                "week": 4,
                "title": "Recovery Checkpoint",
                "commitment": "5 hrs/wk",
                "tag": "Low-Stakes Mastery Quiz",
                "badge_color": "#EF4444",
                "action": "Complete a low-stakes mastery quiz with unlimited retakes until achieving 70%. Stabilizes passing trajectory and clears academic hold.",
                "deliverable": "Verified mastery quiz passing certificate"
            }
        ]
    }
}


def predict_and_recommend(
    total_clicks: float,
    active_days: float,
    weighted_avg_score: float,
    avg_submission_delay: float,
    kmeans_model: KMeans,
    scaler: StandardScaler,
    reference_df: pd.DataFrame
) -> Dict[str, Any]:
    """
    Given 4 primary live student metrics, standardizes 16D vector, computes Euclidean
    distance to all 4 cluster centroids, determines nearest persona, computes distance-based
    confidence, and retrieves the personalized 4-week roadmap.
    """
    # Standardize input vector
    x_scaled = scale_live_instance(
        total_clicks=total_clicks,
        active_days=active_days,
        weighted_avg_score=weighted_avg_score,
        avg_submission_delay=avg_submission_delay,
        scaler=scaler,
        reference_df=reference_df
    )

    # Compute Euclidean distance to all 4 cluster centers
    centroids = kmeans_model.cluster_centers_  # (4, 16)
    diffs = centroids - x_scaled
    dists = np.linalg.norm(diffs, axis=1)

    predicted_cluster = int(np.argmin(dists))
    nearest_dist = float(dists[predicted_cluster])

    # Distance-based confidence score: (1/d) / sum(1/d)
    eps = 1e-5
    inv_dists = 1.0 / (dists + eps)
    confidence = float((inv_dists[predicted_cluster] / np.sum(inv_dists)) * 100.0)

    # Retrieve roadmap
    roadmap_info = CLUSTER_ROADMAPS[predicted_cluster]
    persona_meta = CLUSTER_PERSONAS[predicted_cluster]

    distances_dict = {int(i): round(float(dists[i]), 3) for i in range(len(dists))}

    return {
        "cluster_id": predicted_cluster,
        "persona": persona_meta["name"],
        "short_name": persona_meta["short_name"],
        "confidence": round(confidence, 1),
        "nearest_distance": round(nearest_dist, 3),
        "distances": distances_dict,
        "risk_level": persona_meta["risk_level"],
        "color": persona_meta["color"],
        "theme": roadmap_info["theme"],
        "objective": roadmap_info["objective"],
        "roadmap": roadmap_info["weeks"],
        "action_plan": roadmap_info["weeks"],  # Alias required by specification
        "scaled_vector": x_scaled[0]
    }


if __name__ == "__main__":
    from src.preprocess import load_and_preprocess_oulad
    from src.clustering import fit_kmeans_pipeline
    X_scaled, df, y, scaler = load_and_preprocess_oulad()
    km, labels, df_c = fit_kmeans_pipeline(X_scaled, df)
    rec = predict_and_recommend(2500, 85, 88.0, -4.0, km, scaler, df)
    print(f"Predicted Cluster: {rec['cluster_id']} ({rec['persona']}), Confidence: {rec['confidence']}%")
    print(f"Roadmap weeks: {len(rec['roadmap'])}")

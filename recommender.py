"""
recommender.py - SaaS Recommender & Study Roadmap Engine for EduCluster
Client-Ready EdTech SaaS Product Architecture

Features:
1. Quick Demo Presets: "Regular Topper", "Deadline Crammer", "Quiet Portal User", "Falling Behind".
2. Empathetic Strengths & Focus Area synthesis (Plain-English, zero jargon).
3. Clean Comparison Chart (Plotly Grouped Bar & Radar) with light-theme executive styling.
4. Live "What-If" Habit Insight Calculator: Identifies the exact single habit change for maximum tier leap.
5. 4-Week Actionable Study Roadmap (2x2 Grid):
   - Week 1: Habit & Schedule Reset
   - Week 2: Core Concept Practice
   - Week 3: Active Recall & Quiz Sprint
   - Week 4: Exam & Assessment Mastery
6. Personal Study Plan Markdown (.md) Export.
"""

from typing import Dict, Any, List, Tuple
import pandas as pd
import plotly.graph_objects as go

# 4 Clean Demo Presets matching client-ready SaaS specifications
DEMO_PRESETS = {
    "topper": {
        "label": "🌟 Regular Topper",
        "description": "Consistent study rhythm, punctual submissions, and high mastery.",
        "weekly_study_activity": 85.0,
        "ontime_assignment_rate": 95.0,
        "quiz_test_average": 88.0,
        "forum_participation": 72.0,
        "attendance_consistency": 92.0
    },
    "crammer": {
        "label": "⚡ Deadline Crammer",
        "description": "High test ability, but concentrated study bursts and deadline delays.",
        "weekly_study_activity": 42.0,
        "ontime_assignment_rate": 55.0,
        "quiz_test_average": 72.0,
        "forum_participation": 28.0,
        "attendance_consistency": 52.0
    },
    "quiet": {
        "label": "🎧 Quiet Portal User",
        "description": "Capable foundation, but minimal platform clicks and passive habits.",
        "weekly_study_activity": 24.0,
        "ontime_assignment_rate": 50.0,
        "quiz_test_average": 54.0,
        "forum_participation": 15.0,
        "attendance_consistency": 36.0
    },
    "behind": {
        "label": "🆘 Falling Behind",
        "description": "Overdue submissions, missed lectures, and struggling test confidence.",
        "weekly_study_activity": 14.0,
        "ontime_assignment_rate": 20.0,
        "quiz_test_average": 28.0,
        "forum_participation": 8.0,
        "attendance_consistency": 16.0
    }
}

# Plain-English Dimension Titles
DIMENSION_LABELS = {
    "weekly_study_activity": "Weekly Study Activity",
    "ontime_assignment_rate": "On-Time Submissions",
    "quiz_test_average": "Quiz & Test Score",
    "forum_participation": "Class Participation",
    "attendance_consistency": "Attendance Regularity"
}

# Client-friendly Strengths & Opportunities
STRENGTH_INSIGHTS = {
    "quiz_test_average": ("High Conceptual Grasp", "You absorb core concepts effectively and solve exam-style problems with confidence."),
    "ontime_assignment_rate": ("Punctual Coursework Pacing", "Your discipline in beating deadlines prevents backlogs and reduces cognitive stress."),
    "attendance_consistency": ("Reliable Weekly Rhythm", "Your consistent weekly attendance creates a solid operational foundation for long-term retention."),
    "weekly_study_activity": ("Deep Exploration Habits", "You spend quality time reviewing digital learning modules and reference assets."),
    "forum_participation": ("Active Collaboration", "You communicate proactively, asking questions and engaging in peer discussion circles.")
}

GROWTH_INSIGHTS = {
    "quiz_test_average": ("Foundational Recall & Practice", "Work through short self-check practice problem sets to solidify core test accuracy."),
    "ontime_assignment_rate": ("Advance Buffer Scheduling", "Set a personal deadline 48 hours prior to official due dates to eliminate rush errors."),
    "attendance_consistency": ("Daily Micro-Habits", "Aim for a dependable 30-minute study routine on weekdays instead of irregular weekend marathons."),
    "weekly_study_activity": ("Active Portal Engagement", "Complement lecture notes with interactive digital simulations and practice problem sets."),
    "forum_participation": ("Peer Q&A Participation", "Post one clarifying question weekly on discussion boards to build shared accountability.")
}


def diagnose_student_profile(
    persona_id: int,
    inputs: Dict[str, float],
    readiness_score: int
) -> Dict[str, Any]:
    """
    Synthesizes executive diagnosis: Top Strength, #1 Focus Area,
    and single highest-impact What-If improvement recommendation.
    """
    # Identify best and lowest dimensions
    sorted_items = sorted(inputs.items(), key=lambda x: x[1], reverse=True)
    best_key, best_val = sorted_items[0]
    worst_key, worst_val = sorted_items[-1]

    str_title, str_desc = STRENGTH_INSIGHTS.get(best_key, ("Consistent Effort", "Balanced habit portfolio."))
    focus_title, focus_desc = GROWTH_INSIGHTS.get(worst_key, ("Pacing Improvement", "Targeted growth opportunity."))

    # Calculate optimal what-if leap
    target_boost = min(100.0, worst_val + 25.0)
    delta_pts = int(round(0.25 * (target_boost - worst_val)))

    tier_targets = {
        3: ("Quiet Observer", 52),
        2: ("Steady Builder", 70),
        1: ("Thriving Self-Starter", 88),
        0: ("Honors Mastery", 96)
    }
    next_tier_name, next_tier_score = tier_targets.get(persona_id, ("Top Mastery", 95))
    pts_to_next = max(1, next_tier_score - readiness_score)

    if readiness_score + delta_pts >= next_tier_score and persona_id > 0:
        whatif_summary = (
            f"Raising **{DIMENSION_LABELS[worst_key]}** from **{int(worst_val)}%** to **{int(target_boost)}%** (+25%) "
            f"elevates your readiness to **{readiness_score + delta_pts}/100** (+{delta_pts} pts) and "
            f"unlocks the **{next_tier_name}** tier!"
        )
    else:
        whatif_summary = (
            f"Raising **{DIMENSION_LABELS[worst_key]}** from **{int(worst_val)}%** to **{int(target_boost)}%** (+25%) "
            f"boosts your Academic Readiness by **+{delta_pts} points** to **{readiness_score + delta_pts}/100**. "
            f"You will be just **{max(1, pts_to_next - delta_pts)} pts** away from **{next_tier_name}**."
        )

    return {
        "best_key": best_key,
        "best_title": str_title,
        "best_desc": str_desc,
        "best_val": int(best_val),
        "worst_key": worst_key,
        "worst_title": focus_title,
        "worst_desc": focus_desc,
        "worst_val": int(worst_val),
        "whatif_summary": whatif_summary,
        "next_tier_name": next_tier_name,
        "pts_to_next": pts_to_next
    }


def create_comparison_chart(inputs: Dict[str, float]) -> go.Figure:
    """
    Creates a clean, executive grouped bar comparison chart designed
    specifically for the polished light theme (#FFFFFF card surface).
    Compares 'Your Current Habits' vs 'Top-Performer Target' with zero overlap.
    """
    labels = [
        "Study Activity",
        "On-Time Rate",
        "Quiz & Test",
        "Participation",
        "Attendance"
    ]
    keys = [
        "weekly_study_activity",
        "ontime_assignment_rate",
        "quiz_test_average",
        "forum_participation",
        "attendance_consistency"
    ]

    student_vals = [inputs[k] for k in keys]
    target_vals = [88.0, 95.0, 90.0, 80.0, 92.0]  # Thriving Self-Starter benchmark

    fig = go.Figure()

    # Target Benchmark (Soft slate background bars)
    fig.add_trace(go.Bar(
        x=labels,
        y=target_vals,
        name="Top-Performer Target",
        marker=dict(color="#E2E8F0", line=dict(color="#CBD5E1", width=1)),
        text=[f"{int(v)}%" for v in target_vals],
        textposition="outside",
        textfont=dict(size=11, color="#64748B", family="Inter, sans-serif")
    ))

    # Your Current Habits (Royal Blue highlight bars)
    fig.add_trace(go.Bar(
        x=labels,
        y=student_vals,
        name="Your Current Habits",
        marker=dict(color="#2563EB", line=dict(color="#1D4ED8", width=1.5)),
        text=[f"{int(v)}%" for v in student_vals],
        textposition="inside",
        textfont=dict(size=11, color="#FFFFFF", family="Inter, sans-serif", weight="bold")
    ))

    fig.update_layout(
        barmode="group",
        bargap=0.25,
        bargroupgap=0.1,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        margin=dict(l=10, r=10, t=10, b=10),
        height=320,
        yaxis=dict(
            range=[0, 115],
            tickvals=[0, 25, 50, 75, 100],
            ticktext=["0%", "25%", "50%", "75%", "100%"],
            tickfont=dict(size=10, color="#64748B"),
            gridcolor="#F1F5F9",
            zeroline=False
        ),
        xaxis=dict(
            tickfont=dict(size=11, color="#0F172A", family="Inter, sans-serif"),
            linecolor="#E2E8F0"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
            font=dict(size=11, color="#334155")
        )
    )

    return fig


# Tailored 4-Week Study Plans structured in 4 clean themes
STUDY_PLAN_TEMPLATES = {
    0: {  # Thriving Self-Starter
        "weeks": [
            {
                "week_num": 1,
                "title": "Week 1: Habit & Schedule Reset",
                "tagline": "Prerequisite fast-tracking & honors elective selection",
                "tasks": [
                    {"id": "c0_w1_1", "task": "Accelerate through foundational unit refresh via diagnostic quiz.", "time": "2.0 hrs", "type": "Self-Directed"},
                    {"id": "c0_w1_2", "task": "Select advanced case problem (real-world dataset modeling).", "time": "3.0 hrs", "type": "Honors Lab"},
                    {"id": "c0_w1_3", "task": "Confirm weekly research advisory office-hour slot.", "time": "1.0 hr", "type": "Faculty Sync"}
                ]
            },
            {
                "week_num": 2,
                "title": "Week 2: Core Concept Practice",
                "tagline": "Independent algorithmic modeling & deep inquiry",
                "tasks": [
                    {"id": "c0_w2_1", "task": "Implement algorithmic benchmarking on honors capstone dataset.", "time": "3.5 hrs", "type": "Deep Inquiry"},
                    {"id": "c0_w2_2", "task": "Draft 3-page technical brief evaluating algorithm edge cases.", "time": "2.5 hrs", "type": "Writing"},
                    {"id": "c0_w2_3", "task": "Submit Week 2 deliverable 48 hours in advance of deadline.", "time": "1.5 hrs", "type": "Pacing"}
                ]
            },
            {
                "week_num": 3,
                "title": "Week 3: Active Recall & Quiz Sprint",
                "tagline": "Peer mentoring & reciprocal code reviews",
                "tasks": [
                    {"id": "c0_w3_1", "task": "Facilitate a 45-minute peer problem-solving study circle.", "time": "2.0 hrs", "type": "Mentorship"},
                    {"id": "c0_w3_2", "task": "Complete comprehensive timed problem sprint with zero notes.", "time": "2.5 hrs", "type": "Sprint"},
                    {"id": "c0_w3_3", "task": "Conduct code quality reviews for two peer submissions.", "time": "1.5 hrs", "type": "Peer Review"}
                ]
            },
            {
                "week_num": 4,
                "title": "Week 4: Exam & Assessment Mastery",
                "tagline": "Portfolio defense & capstone presentation",
                "tasks": [
                    {"id": "c0_w4_1", "task": "Record 5-minute executive demo of capstone project.", "time": "2.0 hrs", "type": "Showcase"},
                    {"id": "c0_w4_2", "task": "Publish clean GitHub repository with reproducible documentation.", "time": "2.0 hrs", "type": "Open Source"},
                    {"id": "c0_w4_3", "task": "Complete end-of-term honors self-assessment reflection.", "time": "1.0 hr", "type": "Reflection"}
                ]
            }
        ]
    },
    1: {  # Steady Builder
        "weeks": [
            {
                "week_num": 1,
                "title": "Week 1: Habit & Schedule Reset",
                "tagline": "Habit audit & high-yield diagnostic baseline",
                "tasks": [
                    {"id": "c1_w1_1", "task": "Complete self-paced diagnostic to pinpoint 2 concept growth areas.", "time": "2.0 hrs", "type": "Diagnostic"},
                    {"id": "c1_w1_2", "task": "Block a dedicated 45-minute daily study window in calendar.", "time": "1.0 hr", "type": "Routine"},
                    {"id": "c1_w1_3", "task": "Solve 5 practice problems targeting your lowest quiz topic.", "time": "2.5 hrs", "type": "Skill Build"}
                ]
            },
            {
                "week_num": 2,
                "title": "Week 2: Core Concept Practice",
                "tagline": "Guided micro-labs & early submission pacing",
                "tasks": [
                    {"id": "c1_w2_1", "task": "Work through 2 guided interactive micro-labs with step checks.", "time": "3.0 hrs", "type": "Guided Lab"},
                    {"id": "c1_w2_2", "task": "Submit Week 2 coursework draft 48 hours prior to midnight deadline.", "time": "2.0 hrs", "type": "Pacing Goal"},
                    {"id": "c1_w2_3", "task": "Post 1 thoughtful question or answer on the course forum.", "time": "1.0 hr", "type": "Participation"}
                ]
            },
            {
                "week_num": 3,
                "title": "Week 3: Active Recall & Quiz Sprint",
                "tagline": "Timed practice drills & mistake analysis",
                "tasks": [
                    {"id": "c1_w3_1", "task": "Complete a 60-minute timed mock test under exam conditions.", "time": "2.5 hrs", "type": "Timed Drill"},
                    {"id": "c1_w3_2", "task": "Create mistake log and review fixes with a study partner.", "time": "2.0 hrs", "type": "Review"},
                    {"id": "c1_w3_3", "task": "Refactor submission code for clean formatting and comments.", "time": "1.5 hrs", "type": "Polish"}
                ]
            },
            {
                "week_num": 4,
                "title": "Week 4: Exam & Assessment Mastery",
                "tagline": "Distinction push & full term synthesis",
                "tasks": [
                    {"id": "c1_w4_1", "task": "Synthesize a 1-page visual cheat sheet of key formulas.", "time": "2.0 hrs", "type": "Cheat Sheet"},
                    {"id": "c1_w4_2", "task": "Attempt 1 honors stretch problem to test deep comprehension.", "time": "2.5 hrs", "type": "Stretch"},
                    {"id": "c1_w4_3", "task": "Verify all submission receipts and milestone checkboxes.", "time": "1.0 hr", "type": "Verification"}
                ]
            }
        ]
    },
    2: {  # Quiet Observer
        "weeks": [
            {
                "week_num": 1,
                "title": "Week 1: Habit & Schedule Reset",
                "tagline": "Low-friction micro-habits & advance reminder setup",
                "tasks": [
                    {"id": "c2_w1_1", "task": "Set 72-hour and 24-hour advance submission calendar alerts.", "time": "0.5 hr", "type": "Anti-Cram"},
                    {"id": "c2_w1_2", "task": "Complete three short 10-minute micro-quizzes across the week.", "time": "1.5 hrs", "type": "Micro-Habit"},
                    {"id": "c2_w1_3", "task": "Download and bookmark core digital reading slides for offline use.", "time": "1.0 hr", "type": "Prep"}
                ]
            },
            {
                "week_num": 2,
                "title": "Week 2: Core Concept Practice",
                "tagline": "Interactive modules & mid-week milestone lock",
                "tasks": [
                    {"id": "c2_w2_1", "task": "Work through interactive module with embedded knowledge checks.", "time": "2.5 hrs", "type": "Active Study"},
                    {"id": "c2_w2_2", "task": "Submit completed assignment draft 24 hours ahead of deadline.", "time": "2.0 hrs", "type": "Buffer Goal"},
                    {"id": "c2_w2_3", "task": "Browse forum threads and upvote 3 high-value student replies.", "time": "0.5 hr", "type": "Light Engage"}
                ]
            },
            {
                "week_num": 3,
                "title": "Week 3: Active Recall & Quiz Sprint",
                "tagline": "Study buddy accountability & active retrieval",
                "tasks": [
                    {"id": "c2_w3_1", "task": "Pair with a study partner for a 45-minute problem-solving sync.", "time": "1.5 hrs", "type": "Accountability"},
                    {"id": "c2_w3_2", "task": "Attempt 5 past exam questions with closed notes.", "time": "2.5 hrs", "type": "Active Recall"},
                    {"id": "c2_w3_3", "task": "Review graded coursework feedback and correct top 2 errors.", "time": "1.5 hrs", "type": "Feedback"}
                ]
            },
            {
                "week_num": 4,
                "title": "Week 4: Exam & Assessment Mastery",
                "tagline": "Spaced repetition & panic-free early submission",
                "tasks": [
                    {"id": "c2_w4_1", "task": "Complete flashcard review deck for core unit definitions.", "time": "1.5 hrs", "type": "Retention"},
                    {"id": "c2_w4_2", "task": "Submit final assessment 48 hours prior to closing window.", "time": "2.0 hrs", "type": "Early Submit"},
                    {"id": "c2_w4_3", "task": "Log weekly study hours to reinforce consistent pacing victory.", "time": "0.5 hr", "type": "Review"}
                ]
            }
        ]
    },
    3: {  # Support-Priority Learner
        "weeks": [
            {
                "week_num": 1,
                "title": "Week 1: Habit & Schedule Reset",
                "tagline": "Empathetic outreach & diagnostic simplification",
                "tasks": [
                    {"id": "c3_w1_1", "task": "Schedule 15-minute supportive check-in with assigned faculty mentor.", "time": "1.0 hr", "type": "Mentor Sync"},
                    {"id": "c3_w1_2", "task": "Complete simplified 10-question prerequisite concept check.", "time": "1.5 hrs", "type": "Diagnostic"},
                    {"id": "c3_w1_3", "task": "Establish a distraction-free 20-minute daily study habit.", "time": "1.5 hrs", "type": "Daily Habit"}
                ]
            },
            {
                "week_num": 2,
                "title": "Week 2: Core Concept Practice",
                "tagline": "Step-by-step guided examples & tutoring support",
                "tasks": [
                    {"id": "c3_w2_1", "task": "Work through 3 scaffolded problems with full video walkthroughs.", "time": "2.5 hrs", "type": "Guided Steps"},
                    {"id": "c3_w2_2", "task": "Submit overdue coursework draft with teaching assistant assistance.", "time": "2.0 hrs", "type": "Recovery"},
                    {"id": "c3_w2_3", "task": "Message teaching assistant with 2 specific concept questions.", "time": "0.5 hr", "type": "Help-Seeking"}
                ]
            },
            {
                "week_num": 3,
                "title": "Week 3: Active Recall & Quiz Sprint",
                "tagline": "Confidence-building progressive problem sets",
                "tasks": [
                    {"id": "c3_w3_1", "task": "Solve 5 foundational Level-1 problems and verify answers.", "time": "2.0 hrs", "type": "Confidence"},
                    {"id": "c3_w3_2", "task": "Attend 1 virtual peer tutoring or drop-in help session.", "time": "1.5 hrs", "type": "Peer Support"},
                    {"id": "c3_w3_3", "task": "Review passing rubric criteria with academic coach.", "time": "1.0 hr", "type": "Strategy"}
                ]
            },
            {
                "week_num": 4,
                "title": "Week 4: Exam & Assessment Mastery",
                "tagline": "Essential credit completion & forward planning",
                "tasks": [
                    {"id": "c3_w4_1", "task": "Submit complete end-of-module coursework to secure pass grade.", "time": "3.0 hrs", "type": "Milestone"},
                    {"id": "c3_w4_2", "task": "Conduct end-of-month progress review with faculty mentor.", "time": "1.0 hr", "type": "Review"},
                    {"id": "c3_w4_3", "task": "Create customized maintenance calendar for upcoming semester.", "time": "1.0 hr", "type": "Forward Plan"}
                ]
            }
        ]
    }
}


def get_tailored_study_plan(persona_id: int) -> Dict[str, Any]:
    """Returns the 4-week tailored study plan for the given persona."""
    return STUDY_PLAN_TEMPLATES.get(persona_id, STUDY_PLAN_TEMPLATES[1])


def generate_plan_markdown(
    student_name: str,
    persona_name: str,
    readiness_score: int,
    study_plan: Any,
    checkbox_states: Dict[str, bool]
) -> str:
    """Generates a clean, professional Markdown study plan for download."""
    weeks = study_plan["weeks"] if isinstance(study_plan, dict) and "weeks" in study_plan else study_plan
    total_tasks = sum(len(w["tasks"]) for w in weeks)
    done_tasks = sum(1 for w in weeks for t in w["tasks"] if checkbox_states.get(t["id"], False))
    pct = int(round((done_tasks / max(total_tasks, 1)) * 100))

    md = [
        f"# 🎓 EduCluster Personalized Study Plan",
        f"**Student:** {student_name} | **Assigned Persona:** {persona_name} | **Readiness Score:** {readiness_score}/100",
        f"**Plan Completion:** {done_tasks}/{total_tasks} Tasks Finished ({pct}%)\n",
        "---",
        "## 📌 Personalized 4-Week Strategy",
        "This roadmap is algorithmically designed to reinforce your key academic strengths and eliminate your primary bottleneck through structured, high-yield weekly actions.\n",
        "---"
    ]

    for week in weeks:
        md.append(f"\n### 🗓️ {week['title']}")
        tagline = week.get("tagline", week.get("focus", ""))
        if tagline:
            md.append(f"*{tagline}*\n")
        for t in week["tasks"]:
            is_done = checkbox_states.get(t["id"], False)
            box = "[x]" if is_done else "[ ]"
            t_time = t.get("time", t.get("hours", ""))
            t_type = t.get("type", t.get("tag", ""))
            md.append(f"- {box} **{t['task']}** `({t_time})` — *{t_type}*")

    md.append("\n---\n*Generated by EduCluster — Personalized Learning Path Engine.*")
    return "\n".join(md)


# -----------------------------------------------------------------------------
# Backwards-Compatible Aliases for Test Suite
# -----------------------------------------------------------------------------
STUDENT_PRESETS = DEMO_PRESETS
PERSONA_ROADMAPS = STUDY_PLAN_TEMPLATES
generate_roadmap_markdown = generate_plan_markdown


def generate_student_feedback(persona_id: int, student_radar: Dict[str, float], readiness_score: int) -> Dict[str, Any]:
    """Adapter for test suite backward compatibility."""
    key_mapping = {
        "Study Activity": "weekly_study_activity",
        "On-Time Rate": "ontime_assignment_rate",
        "Quiz & Test Score": "quiz_test_average",
        "Class Participation": "forum_participation",
        "Attendance Regularity": "attendance_consistency"
    }
    inputs = {key_mapping.get(k, k): v for k, v in student_radar.items()}
    diag = diagnose_student_profile(persona_id, inputs, readiness_score)
    inv_map = {v: k for k, v in key_mapping.items()}
    return {
        "best_dimension": inv_map.get(diag["best_key"], diag["best_key"]),
        "strength_title": diag["best_title"],
        "strength_text": diag["best_desc"],
        "growth_dimension": inv_map.get(diag["worst_key"], diag["worst_key"]),
        "growth_title": diag["worst_title"],
        "growth_text": diag["worst_desc"],
        "whatif_summary": diag["whatif_summary"]
    }


def create_habit_radar_chart(student_radar: Dict[str, float], peer_radar: Dict[str, float], target_radar: Dict[str, float]) -> go.Figure:
    """Adapter for test suite backward compatibility."""
    key_mapping = {
        "Study Activity": "weekly_study_activity",
        "On-Time Rate": "ontime_assignment_rate",
        "Quiz & Test Score": "quiz_test_average",
        "Class Participation": "forum_participation",
        "Attendance Regularity": "attendance_consistency"
    }
    inputs = {key_mapping.get(k, k): v for k, v in student_radar.items()}
    return create_comparison_chart(inputs)


def generate_roadmap_csv(persona_name: str, roadmap_weeks: List[Dict[str, Any]], checked_tasks: Dict[str, bool]) -> str:
    """Generates a CSV export of the roadmap."""
    rows = []
    for week in roadmap_weeks:
        for t in week["tasks"]:
            rows.append({
                "Week": f"Week {week['week_num']}",
                "Theme": week["title"],
                "Task_Description": t["task"],
                "Estimated_Hours": t.get("time", t.get("hours", "")),
                "Category_Tag": t.get("type", t.get("tag", "")),
                "Completed": "Yes" if checked_tasks.get(t["id"], False) else "No"
            })
    return pd.DataFrame(rows).to_csv(index=False)


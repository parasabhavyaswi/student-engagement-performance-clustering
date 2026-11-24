"""
recommender.py - Target-User-First Recommender & Study Roadmap Engine for EduCluster (SIH26036)

Provides student-first personalized learning design:
1. 1-Click Learning Style Presets for instant check-in.
2. Personalized Strengths & Growth Opportunity synthesis in supportive, empathetic language.
3. Dark-theme Plotly Polar Habit Radar Chart comparing "You Today" vs "Peer Group Average" vs "Target Benchmark".
4. Tailored 4-Week Actionable Study Roadmaps with task checkboxes, live progress tracking, and .md / .csv downloads.
"""

from typing import Dict, Any, List, Tuple
import pandas as pd
import plotly.graph_objects as go

# 1-Click Student Presets for quick check-in
STUDENT_PRESETS = {
    "regular": {
        "label": "🌱 I study regularly",
        "description": "Consistent weekly study, reliable attendance, and balanced assignment pacing.",
        "weekly_study_activity": 68.0,
        "ontime_assignment_rate": 90.0,
        "quiz_test_average": 76.0,
        "forum_participation": 55.0,
        "attendance_consistency": 82.0
    },
    "crammer": {
        "label": "⚡ I cram before deadlines",
        "description": "Solid test grasp, but concentrated study bursts and occasional deadline rushes.",
        "weekly_study_activity": 42.0,
        "ontime_assignment_rate": 58.0,
        "quiz_test_average": 70.0,
        "forum_participation": 28.0,
        "attendance_consistency": 50.0
    },
    "quiet": {
        "label": "🎧 I rarely open the portal",
        "description": "Capable of passing, but low platform interaction and passive learning habits.",
        "weekly_study_activity": 22.0,
        "ontime_assignment_rate": 45.0,
        "quiz_test_average": 52.0,
        "forum_participation": 14.0,
        "attendance_consistency": 34.0
    },
    "falling_behind": {
        "label": "🆘 I'm falling behind",
        "description": "Struggling with assignment deadlines, missed sessions, or concept gaps.",
        "weekly_study_activity": 14.0,
        "ontime_assignment_rate": 20.0,
        "quiz_test_average": 30.0,
        "forum_participation": 8.0,
        "attendance_consistency": 18.0
    }
}

# Dimension human names and coaching tips
DIMENSION_NAMES = {
    "Study Activity": "Weekly Study Activity",
    "On-Time Rate": "On-Time Assignment Submissions",
    "Quiz & Test Score": "Quiz & Test Mastery",
    "Class Participation": "Class & Forum Participation",
    "Attendance Regularity": "Weekly Attendance & Rhythm"
}

STRENGTH_DESCRIPTIONS = {
    "Quiz & Test Score": "Exceptional Concept Mastery — You absorb technical material effectively and perform strongly on problem sets.",
    "On-Time Rate": "Punctual Submission Pacing — Your discipline with coursework deadlines prevents academic stress and backlogs.",
    "Attendance Regularity": "Steady Routine — Your week-over-week attendance gives you a dependable foundation for sustained progress.",
    "Study Activity": "Deep Exploratory Drive — You spend ample time reviewing digital materials and engaging with course assets.",
    "Class Participation": "Collaborative Spirit — You actively seek peer feedback and contribute meaningfully to classroom discussions."
}

GROWTH_DESCRIPTIONS = {
    "Quiz & Test Score": "Targeted Concept Diagnostics — Focus on foundational recall quizzes and practice problems to boost exam confidence.",
    "On-Time Rate": "Buffer Scheduling — Aim to complete submissions 48 hours before deadlines to eliminate last-minute stress.",
    "Attendance Regularity": "Daily Micro-Habits — Establish a fixed 30-minute daily study block rather than irregular weekend marathons.",
    "Study Activity": "Active Portal Engagement — Supplement lectures with interactive micro-labs and downloadable practice datasets.",
    "Class Participation": "Collaborative Check-Ins — Post one question per week on the student forum or attend peer study circles."
}

# Comprehensive 4-Week Actionable Roadmaps tailored by persona
PERSONA_ROADMAPS = {
    0: {  # Thriving Self-Starter
        "theme": "Honors Acceleration & Capstone Leadership",
        "weeks": [
            {
                "week_num": 1,
                "title": "Week 1: Core Fast-Track & Advanced Electives",
                "focus": "Fast-track prerequisites and select research-grade challenge electives.",
                "tasks": [
                    {"id": "c0_w1_1", "task": "Test out of foundational units via accelerated diagnostic module.", "hours": "2.0 hrs", "tag": "Self-Directed"},
                    {"id": "c0_w1_2", "task": "Select advanced case problem (real-world dataset modeling).", "hours": "3.5 hrs", "tag": "Research Lab"},
                    {"id": "c0_w1_3", "task": "Establish weekly mentor office-hour sync for honors prospectus.", "hours": "1.0 hr", "tag": "Faculty Sync"}
                ]
            },
            {
                "week_num": 2,
                "title": "Week 2: Deep-Dive Inquiry & Methodological Rigor",
                "focus": "Implement independent solutions and benchmark against literature standards.",
                "tasks": [
                    {"id": "c0_w2_1", "task": "Run comparative algorithmic benchmarks on capstone challenge.", "hours": "4.0 hrs", "tag": "Deep Inquiry"},
                    {"id": "c0_w2_2", "task": "Draft 3-page technical brief evaluating trade-offs and edge cases.", "hours": "3.0 hrs", "tag": "Technical Writing"},
                    {"id": "c0_w2_3", "task": "Share code notebook with peer review circle for optimization.", "hours": "1.5 hrs", "tag": "Peer Review"}
                ]
            },
            {
                "week_num": 3,
                "title": "Week 3: Peer Mentorship & Collaborative Review",
                "focus": "Consolidate learning through teaching and reciprocal code critique.",
                "tasks": [
                    {"id": "c0_w3_1", "task": "Host a 45-minute peer problem-solving circle for struggling peers.", "hours": "2.0 hrs", "tag": "Peer Mentorship"},
                    {"id": "c0_w3_2", "task": "Conduct code and proof-reading review for two peer submissions.", "hours": "2.5 hrs", "tag": "Collaborative Review"},
                    {"id": "c0_w3_3", "task": "Incorporate faculty feedback into final presentation slide deck.", "hours": "2.0 hrs", "tag": "Revision"}
                ]
            },
            {
                "week_num": 4,
                "title": "Week 4: Capstone Showcase & Portfolio Defense",
                "focus": "Finalize deliverable presentation, interactive demo, and portfolio archive.",
                "tasks": [
                    {"id": "c0_w4_1", "task": "Record 5-minute executive demo of your completed project.", "hours": "2.5 hrs", "tag": "Showcase"},
                    {"id": "c0_w4_2", "task": "Publish reproducible GitHub repository with documentation.", "hours": "2.0 hrs", "tag": "Open Source"},
                    {"id": "c0_w4_3", "task": "Draft personal learning reflection on algorithmic decision-making.", "hours": "1.5 hrs", "tag": "Meta-Learning"}
                ]
            }
        ]
    },
    1: {  # Steady Builder
        "theme": "Rhythm Stabilization & Stretch Challenges",
        "weeks": [
            {
                "week_num": 1,
                "title": "Week 1: Habit Audit & High-Yield Diagnostic",
                "focus": "Review study routines and pinpoint 2 conceptual areas for grade expansion.",
                "tasks": [
                    {"id": "c1_w1_1", "task": "Complete self-paced knowledge diagnostic on previous unit topics.", "hours": "2.5 hrs", "tag": "Diagnostic"},
                    {"id": "c1_w1_2", "task": "Schedule fixed 45-minute daily study window in calendar.", "hours": "1.0 hr", "tag": "Routine Setup"},
                    {"id": "c1_w1_3", "task": "Solve 5 practice problems targeting your lowest quiz topic.", "hours": "3.0 hrs", "tag": "Skill Building"}
                ]
            },
            {
                "week_num": 2,
                "title": "Week 2: Guided Problem Mastery & Stretch Labs",
                "focus": "Tackle intermediate difficulty problem sets with early submission pacing.",
                "tasks": [
                    {"id": "c1_w2_1", "task": "Work through 2 guided interactive micro-labs with step-by-step checks.", "hours": "3.5 hrs", "tag": "Guided Lab"},
                    {"id": "c1_w2_2", "task": "Submit Week 2 coursework 48 hours prior to official deadline.", "hours": "2.5 hrs", "tag": "Pacing Goal"},
                    {"id": "c1_w2_3", "task": "Formulate 1 discussion prompt on the community question board.", "hours": "1.0 hr", "tag": "Active Inquiry"}
                ]
            },
            {
                "week_num": 3,
                "title": "Week 3: Timed Practice & Feedback Integration",
                "focus": "Simulate exam-condition problem solving to build speed and reduce errors.",
                "tasks": [
                    {"id": "c1_w3_1", "task": "Complete a 60-minute timed mock test under exam conditions.", "hours": "2.5 hrs", "tag": "Timed Mock"},
                    {"id": "c1_w3_2", "task": "Review mistake log with a peer study partner or teaching assistant.", "hours": "2.0 hrs", "tag": "Targeted Review"},
                    {"id": "c1_w3_3", "task": "Refactor submission code for clean formatting and comments.", "hours": "1.5 hrs", "tag": "Code Polish"}
                ]
            },
            {
                "week_num": 4,
                "title": "Week 4: Comprehensive Review & Distinction Push",
                "focus": "Synthesize core semester units to convert steady performance into honors.",
                "tasks": [
                    {"id": "c1_w4_1", "task": "Synthesize 1-page visual cheat sheet summarizing key theorems.", "hours": "2.5 hrs", "tag": "Cheat Sheet"},
                    {"id": "c1_w4_2", "task": "Attempt 1 honors stretch challenge to test conceptual boundaries.", "hours": "3.0 hrs", "tag": "Stretch Challenge"},
                    {"id": "c1_w4_3", "task": "Verify all end-of-module milestones and submission receipts.", "hours": "1.0 hr", "tag": "Milestone Check"}
                ]
            }
        ]
    },
    2: {  # Quiet Observer / Deadline Crammer
        "theme": "Pacing Optimization & Micro-Engagement",
        "weeks": [
            {
                "week_num": 1,
                "title": "Week 1: Low-Stakes Engagement & Deadline Buffer",
                "focus": "Break study sessions into low-friction 20-minute daily blocks.",
                "tasks": [
                    {"id": "c2_w1_1", "task": "Set up a 3-day advance submission reminder on your mobile calendar.", "hours": "0.5 hr", "tag": "Anti-Cram"},
                    {"id": "c2_w1_2", "task": "Complete 3 short 10-minute micro-quizzes across the week.", "hours": "2.0 hrs", "tag": "Micro-Habits"},
                    {"id": "c2_w1_3", "task": "Bookmark core digital textbook chapters for quick offline reading.", "hours": "1.5 hrs", "tag": "Resource Prep"}
                ]
            },
            {
                "week_num": 2,
                "title": "Week 2: Interactive Modules & Mid-Week Milestone",
                "focus": "Transition from passive slide reading to active problem synthesis.",
                "tasks": [
                    {"id": "c2_w2_1", "task": "Complete interactive module with embedded self-assessment checks.", "hours": "3.0 hrs", "tag": "Active Learning"},
                    {"id": "c2_w2_2", "task": "Submit assignment draft at least 24 hours ahead of midnight deadline.", "hours": "2.5 hrs", "tag": "Buffer Goal"},
                    {"id": "c2_w2_3", "task": "Read top 3 forum discussions and upvote helpful answers.", "hours": "1.0 hr", "tag": "Light Engagement"}
                ]
            },
            {
                "week_num": 3,
                "title": "Week 3: Peer Study Check-In & Practice Exam",
                "focus": "Increase study accountability through structured peer or buddy check-in.",
                "tasks": [
                    {"id": "c2_w3_1", "task": "Pair with a study buddy for a 45-minute shared problem session.", "hours": "2.0 hrs", "tag": "Accountability"},
                    {"id": "c2_w3_2", "task": "Attempt past-paper questions without looking at solution guides.", "hours": "3.0 hrs", "tag": "Active Recall"},
                    {"id": "c2_w3_3", "task": "Review graded coursework feedback and highlight top 2 fixes.", "hours": "1.5 hrs", "tag": "Feedback Loop"}
                ]
            },
            {
                "week_num": 4,
                "title": "Week 4: Synthesis & Consistent Retention",
                "focus": "Consolidate learning steadily without resorting to overnight cramming.",
                "tasks": [
                    {"id": "c2_w4_1", "task": "Complete spaced-repetition flashcard deck for module keywords.", "hours": "2.0 hrs", "tag": "Memory Retention"},
                    {"id": "c2_w4_2", "task": "Finalize module portfolio 48 hours before final submission window.", "hours": "2.5 hrs", "tag": "Early Submission"},
                    {"id": "c2_w4_3", "task": "Log study hours across the week to celebrate consistent pacing.", "hours": "0.5 hr", "tag": "Reflection"}
                ]
            }
        ]
    },
    3: {  # Support-Priority Learner
        "theme": "Foundational Scaffolding & Academic Recovery",
        "weeks": [
            {
                "week_num": 1,
                "title": "Week 1: Empathetic Reset & Diagnostic Scaffolding",
                "focus": "Relieve overwhelm through clear, simplified task lists and mentor contact.",
                "tasks": [
                    {"id": "c3_w1_1", "task": "Schedule 15-minute supportive check-in with your assigned faculty mentor.", "hours": "1.0 hr", "tag": "Mentor Connect"},
                    {"id": "c3_w1_2", "task": "Complete short 10-question diagnostic to identify key prerequisite gaps.", "hours": "1.5 hrs", "tag": "Gap Analysis"},
                    {"id": "c3_w1_3", "task": "Establish a small daily 20-minute study goal with zero distractions.", "hours": "1.5 hrs", "tag": "Achievable Habit"}
                ]
            },
            {
                "week_num": 2,
                "title": "Week 2: Guided Prerequisite Re-enforcement",
                "focus": "Master fundamental building-block concepts using step-by-step guided examples.",
                "tasks": [
                    {"id": "c3_w2_1", "task": "Work through 3 scaffolded examples with full solution walkthroughs.", "hours": "3.0 hrs", "tag": "Guided Steps"},
                    {"id": "c3_w2_2", "task": "Submit overdue or upcoming assignment with assistance from tutoring center.", "hours": "2.5 hrs", "tag": "Submission Recovery"},
                    {"id": "c3_w2_3", "task": "Message teaching assistant with 2 specific questions on lecture concepts.", "hours": "1.0 hr", "tag": "Help-Seeking"}
                ]
            },
            {
                "week_num": 3,
                "title": "Week 3: Confidence-Building Problem Sets",
                "focus": "Solve progressive practice problems starting from easy to build self-efficacy.",
                "tasks": [
                    {"id": "c3_w3_1", "task": "Complete 5 level-1 practice problems and verify answers independently.", "hours": "2.5 hrs", "tag": "Confidence Boost"},
                    {"id": "c3_w3_2", "task": "Attend virtual peer drop-in tutoring or study lounge session.", "hours": "2.0 hrs", "tag": "Peer Support"},
                    {"id": "c3_w3_3", "task": "Review passing rubric requirements with faculty advisor.", "hours": "1.0 hr", "tag": "Passing Strategy"}
                ]
            },
            {
                "week_num": 4,
                "title": "Week 4: Essential Milestone Completion & Safety Net",
                "focus": "Secure all necessary credits for course completion and academic progression.",
                "tasks": [
                    {"id": "c3_w4_1", "task": "Submit complete end-of-module portfolio meeting passing thresholds.", "hours": "3.5 hrs", "tag": "Core Milestone"},
                    {"id": "c3_w4_2", "task": "Conduct end-of-month progress review with student success coach.", "hours": "1.0 hr", "tag": "Success Review"},
                    {"id": "c3_w4_3", "task": "Create personalized maintenance plan for upcoming course semester.", "hours": "1.5 hrs", "tag": "Forward Planning"}
                ]
            }
        ]
    }
}


def generate_student_feedback(
    persona_id: int,
    student_radar: Dict[str, float],
    readiness_score: int
) -> Dict[str, Any]:
    """
    Synthesizes encouraging, human-centered feedback cards identifying the student's
    top strength and #1 growth opportunity based on their radar dimensions.
    """
    # Find dimension with highest and lowest score
    sorted_dims = sorted(student_radar.items(), key=lambda x: x[1], reverse=True)
    best_dim, best_val = sorted_dims[0]
    growth_dim, growth_val = sorted_dims[-1]

    # Friendly strength and growth text
    strength_title = DIMENSION_NAMES.get(best_dim, best_dim)
    strength_text = STRENGTH_DESCRIPTIONS.get(best_dim, f"High proficiency in {best_dim} ({best_val}%). Keep leveraging this foundation!")

    growth_title = DIMENSION_NAMES.get(growth_dim, growth_dim)
    growth_text = GROWTH_DESCRIPTIONS.get(growth_dim, f"Targeted improvement in {growth_dim} ({growth_val}%) will create your biggest academic lift.")

    # Next tier threshold
    tier_thresholds = {
        3: {"target_name": "Quiet Observer", "target_score": 52, "needed": max(1, 52 - readiness_score)},
        2: {"target_name": "Steady Builder", "target_score": 70, "needed": max(1, 70 - readiness_score)},
        1: {"target_name": "Thriving Self-Starter", "target_score": 88, "needed": max(1, 88 - readiness_score)},
        0: {"target_name": "Honors Research Fellow", "target_score": 95, "needed": max(1, 95 - readiness_score)}
    }
    tier_info = tier_thresholds.get(persona_id, tier_thresholds[1])

    return {
        "best_dimension": best_dim,
        "best_value": best_val,
        "strength_title": strength_title,
        "strength_text": strength_text,
        "growth_dimension": growth_dim,
        "growth_value": growth_val,
        "growth_title": growth_title,
        "growth_text": growth_text,
        "next_tier_name": tier_info["target_name"],
        "next_tier_score": tier_info["target_score"],
        "points_needed": tier_info["needed"]
    }


def create_habit_radar_chart(
    student_radar: Dict[str, float],
    peer_radar: Dict[str, float],
    target_radar: Dict[str, float]
) -> go.Figure:
    """
    Renders a high-contrast dark-mode Plotly polar radar chart comparing
    'You Today' vs 'Peer Group Average' vs 'Target Benchmark'.
    """
    categories = list(student_radar.keys())
    # Close the loop for polar plot
    cat_loop = categories + [categories[0]]

    val_student = [student_radar[c] for c in categories] + [student_radar[categories[0]]]
    val_peer = [peer_radar[c] for c in categories] + [peer_radar[categories[0]]]
    val_target = [target_radar[c] for c in categories] + [target_radar[categories[0]]]

    fig = go.Figure()

    # Target Benchmark (Outer ideal boundary)
    fig.add_trace(go.Scatterpolar(
        r=val_target,
        theta=cat_loop,
        mode="lines",
        name="Target Benchmark",
        line=dict(color="#10B981", width=2, dash="dash"),
        hoverinfo="r+theta"
    ))

    # Peer Group Average (Middle reference)
    fig.add_trace(go.Scatterpolar(
        r=val_peer,
        theta=cat_loop,
        mode="lines",
        name="Peer Group Average",
        line=dict(color="#A855F7", width=2, dash="dot"),
        hoverinfo="r+theta"
    ))

    # You Today (Highlight area)
    fig.add_trace(go.Scatterpolar(
        r=val_student,
        theta=cat_loop,
        fill="toself",
        name="You Today",
        line=dict(color="#38BDF8", width=3),
        fillcolor="rgba(56, 189, 248, 0.25)",
        hoverinfo="r+theta"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[20, 40, 60, 80, 100],
                ticktext=["20%", "40%", "60%", "80%", "100%"],
                tickfont=dict(size=10, color="#94A3B8"),
                gridcolor="#1E293B",
                linecolor="#334155"
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color="#E2E8F0", family="Inter, sans-serif"),
                gridcolor="#1E293B",
                linecolor="#334155"
            ),
            bgcolor="rgba(17, 24, 39, 0.85)"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=30, b=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.22,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color="#CBD5E1")
        ),
        height=380
    )

    return fig


def generate_roadmap_markdown(
    student_name: str,
    persona_name: str,
    readiness_score: int,
    roadmap_weeks: List[Dict[str, Any]],
    checked_tasks: Dict[str, bool]
) -> str:
    """Generates an exportable Markdown study plan document with progress checkboxes."""
    total_tasks = sum(len(w["tasks"]) for w in roadmap_weeks)
    done_tasks = sum(1 for w in roadmap_weeks for t in w["tasks"] if checked_tasks.get(t["id"], False))
    pct = int(round((done_tasks / max(total_tasks, 1)) * 100))

    lines = [
        f"# 🎓 EduCluster Personalized Study Plan",
        f"**Learner:** {student_name} | **Persona:** {persona_name} | **Current Readiness Score:** {readiness_score}/100",
        f"**Plan Completion:** {done_tasks}/{total_tasks} Tasks Completed ({pct}%)\n",
        f"---",
        f"## 📌 Overview & Study Philosophy",
        f"This 4-week structured plan is algorithmically customized to reinforce your top academic strengths and systematically elevate your lowest-scoring study habits with structured, high-yield micro-actions.\n",
        f"---"
    ]

    for week in roadmap_weeks:
        lines.append(f"\n### 🗓️ {week['title']}")
        lines.append(f"*{week['focus']}*\n")
        for t in week["tasks"]:
            is_done = checked_tasks.get(t["id"], False)
            box = "[x]" if is_done else "[ ]"
            lines.append(f"- {box} **{t['task']}** `({t['hours']})` — *{t['tag']}*")

    lines.append("\n---\n*Generated by EduCluster ML (SIH26036) — Personalized Learning Path Design Engine.*")
    return "\n".join(lines)


def generate_roadmap_csv(
    persona_name: str,
    roadmap_weeks: List[Dict[str, Any]],
    checked_tasks: Dict[str, bool]
) -> str:
    """Generates an exportable CSV string of the student's study roadmap."""
    rows = []
    for week in roadmap_weeks:
        for t in week["tasks"]:
            rows.append({
                "Week": f"Week {week['week_num']}",
                "Theme": week["title"],
                "Task_Description": t["task"],
                "Estimated_Hours": t["hours"],
                "Category_Tag": t["tag"],
                "Completed": "Yes" if checked_tasks.get(t["id"], False) else "No"
            })
    df = pd.DataFrame(rows)
    return df.to_csv(index=False)

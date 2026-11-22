"""
EduPulse - Data Validation Module
Project ID: SIH26036
Performs comprehensive data auditing, relational integrity checks, duplicate detection,
missing-value analysis, and exclusion accounting across all seven OULAD tables.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.data_loader import load_raw_table, verify_raw_dataset

logger = logging.getLogger(__name__)


def audit_raw_tables() -> Dict[str, Any]:
    """
    Performs auditing on all raw tables to calculate exact counts, nulls, and anomalies.
    """
    audit = {}

    # 1. Row counts & files
    ver = verify_raw_dataset(config.RAW_DATA_DIR)
    audit["file_verification"] = ver

    # 2. Student Info Audit
    info = load_raw_table("studentInfo")
    audit["studentInfo"] = {
        "total_rows": len(info),
        "unique_students": int(info["id_student"].nunique()),
        "unique_enrolments": int(info.groupby(["id_student", "code_module", "code_presentation"]).ngroups),
        "duplicate_enrolments": int(info.duplicated(subset=["id_student", "code_module", "code_presentation"]).sum()),
        "null_counts": info.isnull().sum().to_dict(),
        "final_result_distribution": info["final_result"].value_counts().to_dict()
    }

    # 3. Courses Audit
    courses = load_raw_table("courses")
    audit["courses"] = {
        "total_courses": len(courses),
        "modules": courses["code_module"].unique().tolist(),
        "presentations": courses["code_presentation"].unique().tolist(),
        "length_min": int(courses["module_presentation_length"].min()),
        "length_max": int(courses["module_presentation_length"].max())
    }

    # 4. Assessments Audit
    assessments = load_raw_table("assessments")
    numeric_date = pd.to_numeric(assessments["date"], errors="coerce")
    audit["assessments"] = {
        "total_assessments": len(assessments),
        "type_counts": assessments["assessment_type"].value_counts().to_dict(),
        "missing_deadlines_count": int(numeric_date.isna().sum()),
        "missing_deadline_types": assessments[numeric_date.isna()]["assessment_type"].value_counts().to_dict(),
        "zero_weight_count": int((assessments["weight"] == 0).sum())
    }

    # 5. Student Assessment Audit
    sa = load_raw_table("studentAssessment")
    numeric_score = pd.to_numeric(sa["score"], errors="coerce")
    audit["studentAssessment"] = {
        "total_submissions": len(sa),
        "unique_students": int(sa["id_student"].nunique()),
        "non_numeric_scores": int(numeric_score.isna().sum()),
        "score_min": float(numeric_score.min()),
        "score_max": float(numeric_score.max()),
        "is_banked_count": int((sa["is_banked"] == 1).sum())
    }

    # 6. Student Registration Audit
    reg = load_raw_table("studentRegistration")
    audit["studentRegistration"] = {
        "total_registrations": len(reg),
        "unique_students": int(reg["id_student"].nunique()),
        "missing_reg_dates": int(reg["date_registration"].isna().sum()),
        "unregistered_count": int(reg["date_unregistration"].notna().sum())
    }

    # 7. VLE Resource Metadata Audit
    vle = load_raw_table("vle")
    audit["vle"] = {
        "total_resources": len(vle),
        "activity_types": vle["activity_type"].value_counts().to_dict()
    }

    return audit


def calculate_enrolment_exclusions() -> Dict[str, Any]:
    """
    Computes exact enrolment-level overlaps, exclusions, and reasons across
    studentInfo, studentVle, and studentAssessment.
    """
    info = load_raw_table("studentInfo")
    courses = load_raw_table("courses")
    assessments = load_raw_table("assessments")
    sa = load_raw_table("studentAssessment")

    # Enrolments in info
    info_enrolments = set(zip(info["id_student"], info["code_module"], info["code_presentation"]))
    total_enrolments = len(info_enrolments)
    unique_students_total = int(info["id_student"].nunique())

    # VLE enrolments
    df_vle = pd.read_csv(config.RAW_DATA_DIR / "studentVle.csv", usecols=["id_student", "code_module", "code_presentation"])
    vle_enrolments = set(zip(df_vle["id_student"], df_vle["code_module"], df_vle["code_presentation"]))
    vle_students = set(df_vle["id_student"])

    # SA enrolments (via assessments join)
    sa_merged = pd.merge(sa, assessments, on="id_assessment", how="inner")
    sa_enrolments = set(zip(sa_merged["id_student"], sa_merged["code_module"], sa_merged["code_presentation"]))

    # Calculations
    students_without_vle = unique_students_total - len(vle_students.intersection(set(info["id_student"])))
    enrolments_without_vle = len(info_enrolments - vle_enrolments)
    enrolments_without_assessments = len(info_enrolments - sa_enrolments)
    enrolments_without_both = len(info_enrolments - vle_enrolments - sa_enrolments)

    both_present = vle_enrolments.intersection(sa_enrolments).intersection(info_enrolments)

    # Missing due dates or invalid scores among the intersection
    assessments["numeric_date"] = pd.to_numeric(assessments["date"], errors="coerce")
    sa["numeric_score"] = pd.to_numeric(sa["score"], errors="coerce")
    merged_sub = pd.merge(sa, assessments, on="id_assessment", how="inner")
    merged_sub["delay"] = merged_sub["date_submitted"] - merged_sub["numeric_date"]

    # Check which enrolments in both_present have all valid features
    merged_sub["valid_score"] = merged_sub["numeric_score"].notna()
    merged_sub["score_w"] = np.where(merged_sub["valid_score"], merged_sub["numeric_score"] * merged_sub["weight"], 0.0)
    merged_sub["w_used"] = np.where(merged_sub["valid_score"], merged_sub["weight"], 0.0)

    sa_agg = merged_sub.groupby(["id_student", "code_module", "code_presentation"]).agg(
        total_score_w=("score_w", "sum"),
        total_weight=("w_used", "sum"),
        mean_score_raw=("numeric_score", "mean"),
        mean_delay=("delay", "mean")
    ).reset_index()
    sa_agg["weighted_score"] = np.where(sa_agg["total_weight"] > 0, sa_agg["total_score_w"] / sa_agg["total_weight"], sa_agg["mean_score_raw"])

    # Merge with info
    valid_mask = sa_agg["weighted_score"].notna() & sa_agg["mean_delay"].notna()
    sa_valid_enrols = set(zip(sa_agg.loc[valid_mask, "id_student"], sa_agg.loc[valid_mask, "code_module"], sa_agg.loc[valid_mask, "code_presentation"]))

    valid_clustering_enrolments = len(both_present.intersection(sa_valid_enrols))
    total_excluded = total_enrolments - valid_clustering_enrolments

    # Exclusions breakdown
    excluded_reasons = {
        "no_vle_activity": enrolments_without_vle,
        "no_assessments_submitted": enrolments_without_assessments,
        "neither_vle_nor_assessments": enrolments_without_both,
        "vle_present_no_assessments": len(vle_enrolments - sa_enrolments),
        "assessments_present_no_vle": len(sa_enrolments - vle_enrolments),
        "missing_assessment_scores_or_deadlines": len(both_present - sa_valid_enrols)
    }

    result = {
        "total_student_enrolments": total_enrolments,
        "unique_student_ids": unique_students_total,
        "valid_clustering_enrolments": valid_clustering_enrolments,
        "valid_enrolments_percentage": round((valid_clustering_enrolments / total_enrolments) * 100, 2),
        "total_excluded_records": total_excluded,
        "excluded_percentage": round((total_excluded / total_enrolments) * 100, 2),
        "students_without_vle_activity": students_without_vle,
        "enrolments_without_vle_activity": enrolments_without_vle,
        "excluded_reasons": excluded_reasons
    }

    with open(config.CLEANING_METADATA_FILE, "w") as fp:
        json.dump(result, fp, indent=2)

    return result


if __name__ == "__main__":
    print("Auditing raw tables...")
    audit = audit_raw_tables()
    print("Files verified:", audit["file_verification"]["is_valid"])
    print("\nCalculating exclusions...")
    excl = calculate_enrolment_exclusions()
    print("Total enrolments:", excl["total_student_enrolments"])
    print("Valid enrolments:", excl["valid_clustering_enrolments"])
    print("Total excluded:", excl["total_excluded_records"])
    print("Reasons:", excl["excluded_reasons"])

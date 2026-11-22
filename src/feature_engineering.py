"""
EduPulse - Feature Engineering Module
Project ID: SIH26036
Extracts, transforms, and validates the four core features required for K-Means clustering
from the genuine OULAD tables at the enrolment level (id_student, code_module, code_presentation).
"""

import os
import sys
import logging
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import numpy as np
import pandas as pd

# Suppress Windows loky core count warning
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent if "__file__" in locals() else Path.cwd()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.data_loader import load_raw_table

logger = logging.getLogger(__name__)


def extract_vle_features(vle_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Feature 1: total_clicks = SUM(sum_click) from studentVle.csv
    Feature 2: active_days = COUNT(DISTINCT date WHERE sum_click > 0) from studentVle.csv
    Aggregated strictly per student-course-presentation enrolment.
    """
    logger.info("Extracting VLE features from studentVle.csv...")
    if vle_df is None:
        vle_path = config.RAW_DATA_DIR / config.RAW_FILES["studentVle"]
        vle_df = pd.read_csv(
            vle_path,
            usecols=["id_student", "code_module", "code_presentation", "date", "sum_click"]
        )

    # Clean clicks
    vle_df["sum_click"] = pd.to_numeric(vle_df["sum_click"], errors="coerce").fillna(0)

    # 1. Total platform clicks: SUM(sum_click)
    clicks = (
        vle_df.groupby(["id_student", "code_module", "code_presentation"])["sum_click"]
        .sum()
        .rename("total_clicks")
    )

    # 2. Active learning days: distinct dates with positive activity (sum_click > 0)
    pos_activity = vle_df[vle_df["sum_click"] > 0]
    active_days = (
        pos_activity.drop_duplicates(subset=["id_student", "code_module", "code_presentation", "date"])
        .groupby(["id_student", "code_module", "code_presentation"])
        .size()
        .rename("active_days")
    )

    vle_features = pd.concat([clicks, active_days], axis=1).reset_index()
    logger.info("Extracted VLE features for %d active enrolments", len(vle_features))
    return vle_features


def extract_assessment_features(
    sa_df: Optional[pd.DataFrame] = None,
    assess_df: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Feature 3: weighted_avg_score = SUM(score * weight) / SUM(valid weights)
               (do not impute missing scores as 0)
    Feature 4: submission_delay = MEAN(date_submitted - date) over valid deadlines
               (exclude missing dates, date == -1, and is_banked == 1; do not invent dates)
    Aggregated strictly per student-course-presentation enrolment.
    """
    logger.info("Extracting assessment features from studentAssessment and assessments...")
    if sa_df is None:
        sa_df = load_raw_table("studentAssessment")
    if assess_df is None:
        assess_df = load_raw_table("assessments")

    # Clean and parse numeric values
    assess_df = assess_df.copy()
    sa_df = sa_df.copy()
    assess_df["due_date"] = pd.to_numeric(assess_df["date"], errors="coerce")
    sa_df["numeric_score"] = pd.to_numeric(sa_df["score"], errors="coerce")
    sa_df["is_banked_val"] = pd.to_numeric(sa_df["is_banked"], errors="coerce").fillna(0)

    # Merge on id_assessment
    merged = pd.merge(sa_df, assess_df, on="id_assessment", how="inner")

    # Score calculation: do not impute missing scores as 0
    valid_score_mask = merged["numeric_score"].notna()
    merged["score_times_weight"] = np.where(
        valid_score_mask, merged["numeric_score"] * merged["weight"], 0.0
    )
    merged["weight_used"] = np.where(valid_score_mask, merged["weight"], 0.0)

    # Submission delay calculation:
    # Exclude missing due_date, due_date == -1, is_banked == 1, and missing date_submitted
    valid_delay_mask = (
        merged["due_date"].notna() &
        (merged["due_date"] != -1) &
        (merged["is_banked_val"] != 1) &
        merged["date_submitted"].notna()
    )
    merged["delay"] = np.where(valid_delay_mask, merged["date_submitted"] - merged["due_date"], np.nan)

    # Vectorized GroupBy aggregation per enrolment
    agg = merged.groupby(["id_student", "code_module", "code_presentation"]).agg(
        total_score_weight=("score_times_weight", "sum"),
        total_weight_used=("weight_used", "sum"),
        mean_score_raw=("numeric_score", "mean"),
        mean_submission_delay=("delay", "mean"),
        submissions_count=("id_assessment", "count"),
        valid_scores_count=("numeric_score", "count"),
        valid_delays_count=("delay", "count")
    ).reset_index()

    # If official weights sum > 0, use weighted score; fallback to arithmetic mean of valid scores
    agg["weighted_avg_score"] = np.where(
        agg["total_weight_used"] > 0,
        agg["total_score_weight"] / agg["total_weight_used"],
        agg["mean_score_raw"]
    )

    # Ensure valid weighted scores are clamped between 0 and 100
    agg["weighted_avg_score"] = agg["weighted_avg_score"].clip(lower=0.0, upper=100.0)

    # Submission delay alias
    agg["submission_delay"] = agg["mean_submission_delay"]
    agg["weighted_score"] = agg["weighted_avg_score"]

    logger.info("Extracted assessment features for %d enrolments", len(agg))
    return agg


def build_integrated_dataset(save_processed: bool = True) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Integrates all seven tables into a clean, enrolment-level dataset with exactly
    the four core features and student metadata.
    
    Rules enforced:
    1. studentVle and studentAssessment aggregated separately at enrolment level.
    2. Left-join onto studentInfo + studentRegistration + courses with zero row multiplication.
    3. Retain enrolments with 0 VLE clicks as total_clicks=0, active_days=0.
    4. Exclude enrolments lacking valid graded assessments or valid timed submissions.
    5. Log exact exclusion counts and reasons into data/processed/pipeline_audit.json.
    6. Save processed dataset to data/processed/oulad_clustered_enrolments.csv.
    """
    info = load_raw_table("studentInfo")
    courses = load_raw_table("courses")
    reg = load_raw_table("studentRegistration")

    initial_enrolment_count = len(info)
    logger.info("Starting integration with %d enrolments from studentInfo", initial_enrolment_count)

    # Assert no duplicates in studentInfo primary key
    dup_enrolments = int(info.duplicated(subset=["id_student", "code_module", "code_presentation"]).sum())
    assert dup_enrolments == 0, f"Critical: Found {dup_enrolments} duplicate enrolments in studentInfo!"

    vle_features = extract_vle_features()
    assessment_features = extract_assessment_features()

    # 1. Join courses metadata
    df = pd.merge(info, courses, on=["code_module", "code_presentation"], how="left")
    assert len(df) == initial_enrolment_count, f"Row multiplication on courses join: {len(df)} != {initial_enrolment_count}"

    # 2. Join registration metadata
    df = pd.merge(df, reg, on=["code_module", "code_presentation", "id_student"], how="left")
    assert len(df) == initial_enrolment_count, f"Row multiplication on registration join: {len(df)} != {initial_enrolment_count}"

    # 3. Join VLE features (left join - retain enrolments with 0 VLE clicks)
    df = pd.merge(df, vle_features, on=["code_module", "code_presentation", "id_student"], how="left")
    assert len(df) == initial_enrolment_count, f"Row multiplication on VLE join: {len(df)} != {initial_enrolment_count}"

    # Retain enrolments with 0 VLE clicks as total_clicks=0, active_days=0
    df["total_clicks"] = df["total_clicks"].fillna(0.0).astype(float)
    df["active_days"] = df["active_days"].fillna(0.0).astype(float)

    # 4. Join assessment features
    df = pd.merge(df, assessment_features, on=["code_module", "code_presentation", "id_student"], how="left")
    assert len(df) == initial_enrolment_count, f"Row multiplication on assessment join: {len(df)} != {initial_enrolment_count}"

    # Audit exclusions
    has_valid_score = df["weighted_avg_score"].notna()
    has_valid_delay = df["submission_delay"].notna()
    valid_mask = has_valid_score & has_valid_delay

    excluded_df = df[~valid_mask]
    valid_df = df[valid_mask].copy()

    # Log-transform clicks for model training (preserves raw clicks for reporting & UI)
    valid_df["log1p_total_clicks"] = np.log1p(valid_df["total_clicks"])

    # Ensure aliases are present on valid_df
    valid_df["weighted_score"] = valid_df["weighted_avg_score"]
    valid_df["mean_submission_delay"] = valid_df["submission_delay"]

    audit_summary = {
        "initial_total_enrolments": initial_enrolment_count,
        "total_student_enrolments": initial_enrolment_count,
        "unique_students": int(info["id_student"].nunique()),
        "unique_student_ids": int(info["id_student"].nunique()),
        "valid_clustering_enrolments": len(valid_df),
        "total_excluded_enrolments": len(excluded_df),
        "total_excluded_records": len(excluded_df),
        "valid_percentage": round((len(valid_df) / initial_enrolment_count) * 100, 2),
        "valid_enrolments_percentage": round((len(valid_df) / initial_enrolment_count) * 100, 2),
        "excluded_percentage": round((len(excluded_df) / initial_enrolment_count) * 100, 2),
        "enrolments_with_zero_vle_clicks_retained": int((valid_df["total_clicks"] == 0).sum()),
        "total_zero_vle_enrolments_in_cohort": int((df["total_clicks"] == 0).sum()),
        "enrolments_without_vle_activity": int((df["total_clicks"] == 0).sum()),
        "excluded_reasons": {
            "lacking_both_score_and_delay": int((~has_valid_score & ~has_valid_delay).sum()),
            "lacking_valid_score_only": int((~has_valid_score & has_valid_delay).sum()),
            "lacking_valid_timed_delay_only": int((has_valid_score & ~has_valid_delay).sum()),
            "no_assessments_submitted": int((~has_valid_score & ~has_valid_delay).sum()),
            "neither_vle_nor_assessments": int(((df["total_clicks"] == 0) & ~has_valid_score & ~has_valid_delay).sum())
        },
        "excluded_by_final_result": excluded_df["final_result"].value_counts().to_dict(),
        "valid_by_final_result": valid_df["final_result"].value_counts().to_dict()
    }

    if save_processed:
        config.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
        # Save both oulad_clustered_enrolments.csv and oulad_features_processed.csv
        valid_df.to_csv(config.PROCESSED_CLUSTERED_FILE, index=False)
        valid_df.to_csv(config.PROCESSED_FEATURES_FILE, index=False)
        
        import json
        with open(config.PIPELINE_AUDIT_FILE, "w") as fp:
            json.dump(audit_summary, fp, indent=2)
        with open(config.CLEANING_METADATA_FILE, "w") as fp:
            json.dump(audit_summary, fp, indent=2)

        logger.info(
            "Saved processed dataset with %d valid enrolments to %s and %s",
            len(valid_df),
            config.PROCESSED_CLUSTERED_FILE,
            config.PROCESSED_FEATURES_FILE
        )
        logger.info("Saved pipeline audit to %s", config.PIPELINE_AUDIT_FILE)

    return valid_df, audit_summary


if __name__ == "__main__":
    df, audit = build_integrated_dataset(save_processed=True)
    print("\nDataset Engineering Complete:")
    print("Valid Enrolments:", len(df))
    print("Audit Summary:", audit)

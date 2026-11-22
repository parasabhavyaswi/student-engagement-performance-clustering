"""
EduPulse - Data Loader Module
Project ID: SIH26036
Handles downloading, integrity verification, and safe loading of the genuine OULAD dataset.
"""

import os
import sys
import urllib.request
import zipfile
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

EXPECTED_COLUMNS = {
    "assessments.csv": ["code_module", "code_presentation", "id_assessment", "assessment_type", "date", "weight"],
    "courses.csv": ["code_module", "code_presentation", "module_presentation_length"],
    "studentAssessment.csv": ["id_assessment", "id_student", "date_submitted", "is_banked", "score"],
    "studentInfo.csv": ["code_module", "code_presentation", "id_student", "gender", "region", "highest_education", "imd_band", "age_band", "num_of_prev_attempts", "studied_credits", "disability", "final_result"],
    "studentRegistration.csv": ["code_module", "code_presentation", "id_student", "date_registration", "date_unregistration"],
    "studentVle.csv": ["code_module", "code_presentation", "id_student", "id_site", "date", "sum_click"],
    "vle.csv": ["id_site", "code_module", "code_presentation", "activity_type", "week_from", "week_to"]
}


def download_oulad_dataset(dest_dir: Path = config.RAW_DATA_DIR, force: bool = False) -> bool:
    """
    Downloads and extracts the genuine Open University Learning Analytics Dataset (OULAD)
    if the 7 required CSV files are not already present.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    all_present = all((dest_dir / fname).exists() for fname in config.RAW_FILES.values())

    if all_present and not force:
        logger.info("All 7 raw OULAD CSV files already exist in %s", dest_dir)
        return True

    zip_target = dest_dir / "OULAD.zip"
    downloaded = False

    for url in config.OULAD_DOWNLOAD_URLS:
        try:
            logger.info("Attempting download from %s...", url)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=60) as resp, open(zip_target, "wb") as out_f:
                while chunk := resp.read(1024 * 512):
                    out_f.write(chunk)
            logger.info("Successfully downloaded archive to %s (%d bytes)", zip_target, zip_target.stat().st_size)
            downloaded = True
            break
        except Exception as e:
            logger.warning("Failed downloading from %s: %s", url, e)

    if not downloaded:
        raise RuntimeError(
            "Could not automatically download the OULAD dataset. Please place the 7 genuine CSV files "
            f"directly inside {dest_dir}"
        )

    # Extract all CSVs
    logger.info("Extracting CSV files from %s...", zip_target)
    with zipfile.ZipFile(zip_target, "r") as z:
        for member in z.infolist():
            base_name = os.path.basename(member.filename)
            if base_name in config.RAW_FILES.values():
                target_path = dest_dir / base_name
                with z.open(member) as source, open(target_path, "wb") as target:
                    target.write(source.read())
                logger.info("Extracted %s (%d bytes)", base_name, target_path.stat().st_size)

    return True


def verify_raw_dataset(dest_dir: Path = config.RAW_DATA_DIR) -> Dict[str, Any]:
    """
    Verifies that all 7 CSV files exist, are readable, non-empty, and preserve original columns.
    Returns a verification summary dictionary.
    """
    summary = {
        "is_valid": True,
        "files": {},
        "errors": []
    }

    for key, fname in config.RAW_FILES.items():
        fpath = dest_dir / fname
        if not fpath.exists():
            summary["is_valid"] = False
            summary["errors"].append(f"Missing file: {fname}")
            continue

        size = fpath.stat().st_size
        if size == 0:
            summary["is_valid"] = False
            summary["errors"].append(f"File is empty: {fname}")
            continue

        try:
            # Read header
            df_head = pd.read_csv(fpath, nrows=5)
            actual_cols = list(df_head.columns)
            expected_cols = EXPECTED_COLUMNS[fname]
            cols_match = (actual_cols == expected_cols)

            if not cols_match:
                summary["is_valid"] = False
                summary["errors"].append(f"Columns mismatch in {fname}. Expected: {expected_cols}, got: {actual_cols}")

            # Count rows
            if fname == "studentVle.csv":
                with open(fpath, "rb") as fp:
                    row_count = sum(1 for _ in fp) - 1
            else:
                row_count = len(pd.read_csv(fpath))

            summary["files"][fname] = {
                "exists": True,
                "size_bytes": size,
                "row_count": row_count,
                "columns": actual_cols,
                "columns_valid": cols_match
            }
        except Exception as e:
            summary["is_valid"] = False
            summary["errors"].append(f"Error reading {fname}: {str(e)}")

    return summary


def load_raw_table(table_key: str, dest_dir: Path = config.RAW_DATA_DIR, nrows: Optional[int] = None) -> pd.DataFrame:
    """
    Loads a specific raw OULAD table by key name (e.g., 'studentInfo', 'courses').
    """
    if table_key not in config.RAW_FILES:
        raise KeyError(f"Unknown table key: {table_key}. Expected one of {list(config.RAW_FILES.keys())}")

    fname = config.RAW_FILES[table_key]
    fpath = dest_dir / fname
    if not fpath.exists():
        download_oulad_dataset(dest_dir)

    return pd.read_csv(fpath, nrows=nrows)


def load_all_raw_tables(dest_dir: Path = config.RAW_DATA_DIR, vle_nrows: Optional[int] = None) -> Dict[str, pd.DataFrame]:
    """
    Loads all seven raw OULAD tables into a dictionary.
    """
    tables = {}
    for key in config.RAW_FILES.keys():
        nrows = vle_nrows if key == "studentVle" else None
        logger.info("Loading %s...", key)
        tables[key] = load_raw_table(key, dest_dir=dest_dir, nrows=nrows)
    return tables


if __name__ == "__main__":
    download_oulad_dataset()
    ver = verify_raw_dataset()
    print("Verification Summary:")
    print("Valid:", ver["is_valid"])
    for f, d in ver["files"].items():
        print(f"  - {f}: {d['row_count']:,} rows, {d['size_bytes']:,} bytes")

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from config import BINARY_TARGET, DATA_FILE, LOCAL_CLASS_FILES, MULTICLASS_TARGET


def load_dataset(csv_path: Path = DATA_FILE) -> pd.DataFrame:
    """Load the TON_IoT dataset.

    Preferred input is data/dataset_cleaned.csv. If that file is missing,
    the loader falls back to the local class CSVs: DDOS.csv, DOS.csv,
    and Normal.csv.
    """
    if csv_path.exists():
        df = pd.read_csv(csv_path, low_memory=False)
        df.columns = df.columns.str.strip()
        return df

    available_class_files = {
        class_name: path
        for class_name, path in LOCAL_CLASS_FILES.items()
        if path.exists()
    }

    if available_class_files:
        return load_local_class_csvs(available_class_files)

    expected_files = "\n".join(str(path) for path in LOCAL_CLASS_FILES.values())
    raise FileNotFoundError(
        f"Dataset not found at {csv_path}.\n\n"
        "Place dataset_cleaned.csv in the data folder, or place these local "
        f"class CSVs in the project root:\n{expected_files}"
    )


def load_local_class_csvs(class_files: dict[str, Path]) -> pd.DataFrame:
    """Load and combine per-class TON_IoT CSV files."""
    frames: list[pd.DataFrame] = []

    for class_name, path in class_files.items():
        frame = pd.read_csv(path, low_memory=False)
        frame.columns = frame.columns.str.strip()

        if MULTICLASS_TARGET not in frame.columns:
            frame[MULTICLASS_TARGET] = class_name

        if BINARY_TARGET not in frame.columns:
            frame[BINARY_TARGET] = 0 if class_name == "normal" else 1

        frame[MULTICLASS_TARGET] = frame[MULTICLASS_TARGET].astype(str).str.strip().str.lower()
        frame[BINARY_TARGET] = frame[BINARY_TARGET].astype(int)

        frames.append(frame)

    if not frames:
        raise FileNotFoundError("No local class CSV files were found.")

    df = pd.concat(frames, ignore_index=True)
    df.columns = df.columns.str.strip()
    return df


def validate_target_columns(df: pd.DataFrame, task: str) -> str:
    """Return the target column name for the selected task."""
    target_col = BINARY_TARGET if task == "binary" else MULTICLASS_TARGET
    if target_col not in df.columns:
        available = ", ".join(df.columns)
        raise ValueError(
            f"Target column '{target_col}' was not found. Available columns: {available}"
        )
    return target_col


def sample_dataframe(
    df: pd.DataFrame, sample_size: int | None, random_state: int
) -> pd.DataFrame:
    """Return a random sample for faster experiments."""
    if sample_size is None or sample_size <= 0 or sample_size >= len(df):
        return df
    return df.sample(n=sample_size, random_state=random_state).reset_index(drop=True)


def print_dataset_summary(df: pd.DataFrame) -> None:
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")
    print("\nColumns:")
    print(", ".join(df.columns))

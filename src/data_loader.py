from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from config import BINARY_TARGET, DATA_FILE, MULTICLASS_TARGET


def load_dataset(csv_path: Path = DATA_FILE) -> pd.DataFrame:
    """Load the TON_IoT cleaned CSV file."""
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {csv_path}. "
            "Download dataset_cleaned.csv from Kaggle and place it in the data folder."
        )

    df = pd.read_csv(csv_path)
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

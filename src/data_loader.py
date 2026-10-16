from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from config import (
    BINARY_TARGET,
    DATA_FILE,
    LOCAL_CLASS_FILES,
    MULTICLASS_TARGET,
    TEST_DATA_FILE,
    TRAIN_DATA_FILE,
)


def load_dataset(csv_path: Path = DATA_FILE) -> pd.DataFrame:
    """Load the TON_IoT dataset.

    Preferred input is data/dataset.csv. If that file is missing,
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
        "Place dataset.csv in the data folder, or place these local "
        f"class CSVs in the project root:\n{expected_files}"
    )


def sample_large_csv(path: Path, sample_size: int, random_state: int) -> pd.DataFrame:
    """Reservoir sample lines from a large CSV without loading all rows into RAM."""
    import io
    import random
    rng = random.Random(random_state)
    sample_lines: list[str] = []
    with path.open("r", encoding="utf-8") as f:
        header = f.readline()
        for idx, line in enumerate(f):
            if idx < sample_size:
                sample_lines.append(line)
            else:
                j = rng.randint(0, idx)
                if j < sample_size:
                    sample_lines[j] = line

    buffer = io.StringIO(header + "".join(sample_lines))
    df = pd.read_csv(buffer, low_memory=False)
    df.columns = df.columns.str.strip()
    return df


def load_train_test_datasets(
    train_path: Path = TRAIN_DATA_FILE,
    test_path: Path = TEST_DATA_FILE,
    train_sample_size: int | None = None,
    test_sample_size: int | None = None,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the pre-split train and test datasets.
    
    Supports optional reservoir downsampling to accommodate memory limits.
    """
    if not train_path.exists():
        raise FileNotFoundError(f"Training dataset not found at {train_path}")
    if not test_path.exists():
        raise FileNotFoundError(f"Test dataset not found at {test_path}")

    train_size_mb = train_path.stat().st_size / (1024 * 1024)
    if train_sample_size and train_sample_size > 0 and train_size_mb > 100:
        train_df = sample_large_csv(train_path, train_sample_size, random_state)
    else:
        train_df = pd.read_csv(train_path, low_memory=False)
        train_df.columns = train_df.columns.str.strip()
        if train_sample_size and 0 < train_sample_size < len(train_df):
            train_df = train_df.sample(n=train_sample_size, random_state=random_state).reset_index(drop=True)

    test_size_mb = test_path.stat().st_size / (1024 * 1024)
    if test_sample_size and test_sample_size > 0 and test_size_mb > 100:
        test_df = sample_large_csv(test_path, test_sample_size, random_state)
    else:
        test_df = pd.read_csv(test_path, low_memory=False)
        test_df.columns = test_df.columns.str.strip()
        if test_sample_size and 0 < test_sample_size < len(test_df):
            test_df = test_df.sample(n=test_sample_size, random_state=random_state).reset_index(drop=True)

    return train_df, test_df


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

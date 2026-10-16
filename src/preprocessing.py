from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, LabelEncoder, OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from config import (
    BINARY_TARGET,
    HIGH_CARDINALITY_NAME_HINTS,
    MAX_CATEGORICAL_UNIQUE_RATIO,
    MAX_CATEGORICAL_UNIQUE_VALUES,
    MULTICLASS_TARGET,
    RANDOM_STATE,
    TEST_SIZE,
)
from src.data_loader import validate_target_columns


def cast_values_to_string(values: Any) -> Any:
    """Convert categorical matrix values to strings for stable encoding."""
    return values.astype(str)


def infer_columns_to_drop(
    df: pd.DataFrame,
    target_col: str,
    extra_drop_columns: list[str] | None = None,
) -> list[str]:
    """Find columns that should not be used as model features."""
    target_columns = {BINARY_TARGET, MULTICLASS_TARGET}
    columns_to_drop = set(target_columns - {target_col})

    if extra_drop_columns:
        columns_to_drop.update(extra_drop_columns)

    for column in df.columns:
        if column == target_col:
            continue

        lower_name = column.lower()
        unique_count = df[column].nunique(dropna=True)
        unique_ratio = unique_count / max(len(df), 1)

        if df[column].isna().all():
            columns_to_drop.add(column)
            continue

        if any(hint in lower_name for hint in HIGH_CARDINALITY_NAME_HINTS):
            columns_to_drop.add(column)
            continue

        if not pd.api.types.is_numeric_dtype(df[column]):
            if (
                unique_ratio > MAX_CATEGORICAL_UNIQUE_RATIO
                or unique_count > MAX_CATEGORICAL_UNIQUE_VALUES
            ):
                columns_to_drop.add(column)

    return [column for column in df.columns if column in columns_to_drop]


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    """Create preprocessing for numeric and categorical columns."""
    numeric_features = X.select_dtypes(include=[np.number, "bool"]).columns.tolist()
    categorical_features = [
        column for column in X.columns if column not in numeric_features
    ]

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "to_string",
                FunctionTransformer(
                    cast_values_to_string,
                    feature_names_out="one-to-one",
                ),
            ),
            (
                "encoder",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_features),
            ("cat", categorical_pipeline, categorical_features),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def prepare_train_test_data(
    df: pd.DataFrame,
    task: str,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
    drop_columns: list[str] | None = None,
) -> dict[str, Any]:
    """Create train-test split, label encoding, and preprocessing objects."""
    target_col = validate_target_columns(df, task)
    inferred_drop_columns = infer_columns_to_drop(df, target_col, drop_columns)

    working_df = df.drop(columns=inferred_drop_columns, errors="ignore").copy()
    working_df = working_df.dropna(subset=[target_col])

    X = working_df.drop(columns=[target_col])
    y_raw = working_df[target_col].astype(str)

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    preprocessor = build_preprocessor(X_train)

    return {
        "X_train_raw": X_train,
        "X_test_raw": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "label_encoder": label_encoder,
        "preprocessor": preprocessor,
        "target_col": target_col,
        "dropped_columns": inferred_drop_columns,
        "feature_columns": X.columns.tolist(),
        "class_names": label_encoder.classes_.tolist(),
    }


def prepare_split_datasets(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    task: str,
    drop_columns: list[str] | None = None,
) -> dict[str, Any]:
    """Prepare pre-split train and test datasets with a shared preprocessor and label encoder."""
    target_col = validate_target_columns(train_df, task)
    inferred_drop_columns = infer_columns_to_drop(train_df, target_col, drop_columns)

    working_train = train_df.drop(columns=inferred_drop_columns, errors="ignore").dropna(subset=[target_col]).copy()
    working_test = test_df.drop(columns=inferred_drop_columns, errors="ignore").dropna(subset=[target_col]).copy()

    X_train = working_train.drop(columns=[target_col])
    y_train_raw = working_train[target_col].astype(str)

    X_test = working_test.drop(columns=[target_col])
    y_test_raw = working_test[target_col].astype(str)

    label_encoder = LabelEncoder()
    y_train = label_encoder.fit_transform(y_train_raw)
    y_test = label_encoder.transform(y_test_raw)

    preprocessor = build_preprocessor(X_train)

    return {
        "X_train_raw": X_train,
        "X_test_raw": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "label_encoder": label_encoder,
        "preprocessor": preprocessor,
        "target_col": target_col,
        "dropped_columns": inferred_drop_columns,
        "feature_columns": X_train.columns.tolist(),
        "class_names": label_encoder.classes_.tolist(),
    }


def transform_features(preprocessor: ColumnTransformer, X: pd.DataFrame) -> np.ndarray:
    """Transform features and always return a dense float32 array."""
    X_transformed = preprocessor.transform(X)
    if hasattr(X_transformed, "toarray"):
        X_transformed = X_transformed.toarray()
    return X_transformed.astype(np.float32)


def fit_transform_features(
    preprocessor: ColumnTransformer, X: pd.DataFrame
) -> np.ndarray:
    X_transformed = preprocessor.fit_transform(X)
    if hasattr(X_transformed, "toarray"):
        X_transformed = X_transformed.toarray()
    return X_transformed.astype(np.float32)

from __future__ import annotations

import argparse
import ipaddress
import json
import sys
from pathlib import Path
from typing import Any

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    auc,
    classification_report,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, label_binarize

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from config import FIGURES_DIR, MODELS_DIR, RANDOM_STATE, REPORTS_DIR
from src.utils import ensure_project_dirs, print_section


CLASS_ORDER = ["normal", "dos", "ddos"]
TARGET_COLUMN = "type"
LEAKAGE_COLUMNS = ["label"]
BINARY_TARGET_COLUMN = "label"
IP_COLUMN_NAMES = {
    "src_ip",
    "dst_ip",
    "source_ip",
    "destination_ip",
    "id.orig_h",
    "id.resp_h",
    "orig_h",
    "resp_h",
}


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


def ip_to_integer_parts(value: Any) -> tuple[float, float]:
    """Convert IPv4/IPv6 text to high/low numeric parts."""
    if pd.isna(value):
        return -1.0, -1.0

    text = str(value).strip()
    if not text or text == "-":
        return -1.0, -1.0

    try:
        numeric_ip = int(ipaddress.ip_address(text))
    except ValueError:
        return -1.0, -1.0

    high = numeric_ip >> 64
    low = numeric_ip & ((1 << 64) - 1)
    return float(high), float(low)


def is_ip_column(column: str) -> bool:
    lower_name = column.lower()
    return lower_name in IP_COLUMN_NAMES or lower_name.endswith("_ip")


def load_network_dataset(
    path: Path,
    sample_size: int | None,
    random_state: int,
) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    df.columns = df.columns.str.strip()

    if sample_size is not None and 0 < sample_size < len(df):
        df = df.sample(n=sample_size, random_state=random_state).reset_index(drop=True)

    return df


def normalize_target(value: Any) -> str:
    text = str(value).strip().lower()
    if text == "ddos":
        return "ddos"
    if text == "dos":
        return "dos"
    if text == "normal":
        return "normal"
    return text


def normalize_binary_label(value: Any) -> str:
    text = str(value).strip().lower()
    if text in {"0", "normal", "benign"}:
        return "normal"
    if text in {"1", "attack", "malicious"}:
        return "attack"
    return text


def compute_distribution_counts(df: pd.DataFrame) -> dict[str, dict[str, int]]:
    distributions: dict[str, dict[str, int]] = {}

    if BINARY_TARGET_COLUMN in df.columns:
        binary_counts = (
            df[BINARY_TARGET_COLUMN]
            .map(normalize_binary_label)
            .value_counts()
            .sort_index()
        )
        distributions["binary"] = {
            str(label): int(count) for label, count in binary_counts.items()
        }

    if TARGET_COLUMN in df.columns:
        multiclass_counts = (
            df[TARGET_COLUMN]
            .map(normalize_target)
            .value_counts()
            .sort_index()
        )
        distributions["multiclass"] = {
            str(label): int(count) for label, count in multiclass_counts.items()
        }

    return distributions


def save_distribution_plot(
    counts: dict[str, int],
    title: str,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    labels = list(counts)
    values = list(counts.values())

    plt.figure(figsize=(8, 5))
    sns.barplot(x=labels, y=values, hue=labels, palette="viridis", legend=False)
    plt.title(title)
    plt.xlabel("Class")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def preprocess_dataset(
    df: pd.DataFrame,
    target_column: str = TARGET_COLUMN,
) -> tuple[pd.DataFrame, np.ndarray, dict[str, Any]]:
    if target_column not in df.columns:
        available_columns = ", ".join(df.columns)
        raise ValueError(
            f"Target column '{target_column}' was not found. "
            f"Available columns: {available_columns}"
        )

    original_shape = df.shape
    df = df.drop_duplicates().reset_index(drop=True)
    duplicate_rows_removed = original_shape[0] - len(df)

    df[target_column] = df[target_column].map(normalize_target)
    unexpected_classes = sorted(set(df[target_column].dropna()) - set(CLASS_ORDER))
    if unexpected_classes:
        raise ValueError(
            "This workflow expects only Normal, DoS, and DDoS classes. "
            f"Unexpected classes: {unexpected_classes}"
        )

    target_mapping = {class_name: index for index, class_name in enumerate(CLASS_ORDER)}
    y = df[target_column].map(target_mapping).to_numpy(dtype=np.int64)

    drop_columns = [target_column]
    drop_columns.extend(column for column in LEAKAGE_COLUMNS if column in df.columns)
    X = df.drop(columns=drop_columns, errors="ignore").copy()

    ip_columns = [column for column in X.columns if is_ip_column(column)]
    for column in ip_columns:
        parts = X[column].map(ip_to_integer_parts)
        X[f"{column}_high"] = parts.map(lambda value: value[0]).astype(np.float64)
        X[f"{column}_low"] = parts.map(lambda value: value[1]).astype(np.float64)
        X = X.drop(columns=[column])

    categorical_columns = [
        column for column in X.columns if not pd.api.types.is_numeric_dtype(X[column])
    ]
    label_encoders: dict[str, LabelEncoder] = {}
    for column in categorical_columns:
        encoder = LabelEncoder()
        values = X[column].fillna("missing").astype(str)
        X[column] = encoder.fit_transform(values)
        label_encoders[column] = encoder

    for column in X.columns:
        if not pd.api.types.is_numeric_dtype(X[column]):
            X[column] = pd.to_numeric(X[column], errors="coerce")

    X = X.replace([np.inf, -np.inf], np.nan).fillna(-1)

    constant_columns = [
        column for column in X.columns if X[column].nunique(dropna=False) <= 1
    ]
    X = X.drop(columns=constant_columns)

    metadata = {
        "original_shape": original_shape,
        "processed_shape": X.shape,
        "duplicate_rows_removed": duplicate_rows_removed,
        "ip_columns": ip_columns,
        "categorical_columns": categorical_columns,
        "constant_columns": constant_columns,
        "dropped_columns": drop_columns + constant_columns,
        "feature_columns": X.columns.tolist(),
        "class_names": CLASS_ORDER,
        "target_mapping": target_mapping,
        "label_encoders": label_encoders,
    }

    return X, y, metadata


def build_random_forest(args: argparse.Namespace) -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=args.n_estimators,
        criterion=args.criterion,
        min_samples_split=args.min_samples_split,
        min_samples_leaf=args.min_samples_leaf,
        max_depth=args.max_depth,
        max_features=args.max_features,
        bootstrap=args.bootstrap,
        class_weight=args.class_weight,
        n_jobs=args.n_jobs,
        random_state=args.random_state,
    )


def compute_summary_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_score: np.ndarray | None,
) -> dict[str, float | None]:
    metrics: dict[str, float | None] = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(
            precision_score(y_true, y_pred, average="macro", zero_division=0)
        ),
        "precision_weighted": float(
            precision_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "recall_macro": float(
            recall_score(y_true, y_pred, average="macro", zero_division=0)
        ),
        "recall_weighted": float(
            recall_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_weighted": float(
            f1_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "mcc": float(matthews_corrcoef(y_true, y_pred)),
        "roc_auc_ovr_macro": None,
        "roc_auc_ovr_weighted": None,
    }

    if y_score is not None:
        try:
            metrics["roc_auc_ovr_macro"] = float(
                roc_auc_score(y_true, y_score, multi_class="ovr", average="macro")
            )
            metrics["roc_auc_ovr_weighted"] = float(
                roc_auc_score(y_true, y_score, multi_class="ovr", average="weighted")
            )
        except ValueError:
            pass

    return metrics


def format_summary_metrics(metrics: dict[str, float | None]) -> str:
    lines = ["Summary metrics:"]
    for key, value in metrics.items():
        formatted = "N/A" if value is None else f"{value:.6f}"
        lines.append(f"{key}: {formatted}")
    return "\n".join(lines)


def save_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    matrix = confusion_matrix(y_true, y_pred, labels=list(range(len(CLASS_ORDER))))

    plt.figure(figsize=(8, 6))
    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=CLASS_ORDER,
        yticklabels=CLASS_ORDER,
    )
    plt.title("Random Forest Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def save_feature_importance(
    model: RandomForestClassifier,
    feature_columns: list[str],
    csv_path: Path,
    figure_path: Path,
    top_n: int,
) -> None:
    importance_df = (
        pd.DataFrame(
            {
                "feature": feature_columns,
                "importance": model.feature_importances_,
            }
        )
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    importance_df.to_csv(csv_path, index=False)

    top_features = importance_df.head(top_n)
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 8))
    sns.barplot(data=top_features, x="importance", y="feature")
    plt.title(f"Top {top_n} Random Forest Feature Importances")
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.tight_layout()
    plt.savefig(figure_path, dpi=160)
    plt.close()


def save_roc_curves(
    y_true: np.ndarray,
    y_score: np.ndarray,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    classes = list(range(len(CLASS_ORDER)))
    y_bin = label_binarize(y_true, classes=classes)

    plt.figure(figsize=(8, 6))
    for i, class_name in enumerate(CLASS_ORDER):
        fpr, tpr, _ = roc_curve(y_bin[:, i], y_score[:, i])
        auc_score = auc(fpr, tpr)
        plt.plot(fpr, tpr, label=f"{class_name} (AUC = {auc_score:.3f})")

    plt.plot([0, 1], [0, 1], "k--", linewidth=0.8)
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curves — One-vs-Rest per Class")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def make_json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, LabelEncoder):
        return value.classes_.tolist()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, tuple):
        return [make_json_safe(item) for item in value]
    if isinstance(value, list):
        return [make_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(key): make_json_safe(item) for key, item in value.items()}
    return value


def save_json_report(data: dict[str, Any], path: Path) -> None:
    serializable = make_json_safe(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(serializable, file, indent=2)


def run_workflow(args: argparse.Namespace) -> None:
    ensure_project_dirs()

    print_section("Step 1: Load Dataset")
    df = load_network_dataset(args.dataset, args.sample_size, args.random_state)
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")
    distributions = compute_distribution_counts(df)
    if "binary" in distributions:
        save_distribution_plot(
            distributions["binary"],
            "Binary Class Distribution",
            FIGURES_DIR / "rf_workflow_binary_class_distribution.png",
        )
    if "multiclass" in distributions:
        save_distribution_plot(
            distributions["multiclass"],
            "Multiclass Distribution: Normal, DoS, DDoS",
            FIGURES_DIR / "rf_workflow_multiclass_distribution.png",
        )

    print_section("Step 2: Preprocess Data")
    X, y, metadata = preprocess_dataset(df, args.target)
    print(f"Removed duplicate rows: {metadata['duplicate_rows_removed']:,}")
    print(f"Converted IP columns: {', '.join(metadata['ip_columns']) or 'none'}")
    print(f"Label encoded columns: {len(metadata['categorical_columns'])}")
    print(f"Removed constant columns: {len(metadata['constant_columns'])}")
    print(f"Final feature count: {X.shape[1]:,}")

    print_section("Step 3: Train-Test Split")
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=args.test_size,
        random_state=args.random_state,
        stratify=y,
    )
    print(f"Training rows: {len(X_train):,}")
    print(f"Testing rows: {len(X_test):,}")

    print_section("Step 4: Train Random Forest")
    model = build_random_forest(args)
    model.fit(X_train, y_train)

    print_section("Step 5: Evaluate Model")
    y_pred = model.predict(X_test)
    y_score = model.predict_proba(X_test) if hasattr(model, "predict_proba") else None
    report_dict = classification_report(
        y_test,
        y_pred,
        labels=list(range(len(CLASS_ORDER))),
        target_names=CLASS_ORDER,
        output_dict=True,
        zero_division=0,
    )
    report_text = classification_report(
        y_test,
        y_pred,
        labels=list(range(len(CLASS_ORDER))),
        target_names=CLASS_ORDER,
        zero_division=0,
    )
    summary_metrics = compute_summary_metrics(y_test, y_pred, y_score)
    report_text = f"{report_text}\n\n{format_summary_metrics(summary_metrics)}\n"
    print(report_text)

    print_section("Step 6: Find Important Features")
    save_feature_importance(
        model,
        metadata["feature_columns"],
        REPORTS_DIR / "rf_workflow_feature_importance.csv",
        FIGURES_DIR / "rf_workflow_feature_importance.png",
        args.top_features,
    )
    print(
        "Saved feature importance CSV: "
        f"{REPORTS_DIR / 'rf_workflow_feature_importance.csv'}"
    )

    if y_score is not None:
        save_roc_curves(
            y_test,
            y_score,
            FIGURES_DIR / "rf_workflow_roc_curves.png",
        )

    report_path = REPORTS_DIR / "rf_workflow_classification_report.txt"
    report_path.write_text(report_text, encoding="utf-8")

    run_config = {
        "dataset_path": str(args.dataset),
        "random_state": args.random_state,
        "test_size": args.test_size,
        "sample_size": args.sample_size,
        "class_names": CLASS_ORDER,
        "target_mapping": metadata["target_mapping"],
        "feature_count": X.shape[1],
        "feature_columns": metadata["feature_columns"],
        "ip_columns": metadata["ip_columns"],
        "categorical_columns": metadata["categorical_columns"],
        "constant_columns_removed": metadata["constant_columns"],
        "dropped_columns": metadata["dropped_columns"],
        "original_shape": list(metadata["original_shape"]),
        "processed_shape": list(metadata["processed_shape"]),
        "duplicate_rows_removed": metadata["duplicate_rows_removed"],
    }

    save_json_report(
        {
            "run_config": run_config,
            "classification_report": report_dict,
            "summary_metrics": summary_metrics,
            "class_distributions": distributions,
        },
        REPORTS_DIR / "rf_workflow_summary.json",
    )
    save_json_report(run_config, REPORTS_DIR / "rf_workflow_run_config.json")
    save_confusion_matrix(
        y_test,
        y_pred,
        FIGURES_DIR / "rf_workflow_confusion_matrix.png",
    )

    print_section("Step 7: Save Trained Model")
    model_bundle = {
        "model": model,
        "target_column": args.target,
        "class_names": CLASS_ORDER,
        "target_mapping": metadata["target_mapping"],
        "feature_columns": metadata["feature_columns"],
        "ip_columns": metadata["ip_columns"],
        "categorical_columns": metadata["categorical_columns"],
        "label_encoders": metadata["label_encoders"],
        "constant_columns": metadata["constant_columns"],
        "dropped_columns": metadata["dropped_columns"],
        "summary_metrics": summary_metrics,
        "run_config": run_config,
    }
    model_path = MODELS_DIR / "rf_network_classifier.joblib"
    joblib.dump(model_bundle, model_path)
    print(f"Saved model: {model_path}")
    print(f"Saved report: {report_path}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Classify Normal, DoS, and DDoS network traffic with the final Random Forest workflow."
    )
    parser.add_argument("--dataset", type=Path, default=ROOT / "data" / "dataset.csv")
    parser.add_argument("--target", default=TARGET_COLUMN)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=RANDOM_STATE)
    parser.add_argument("--sample-size", type=int, default=None)
    parser.add_argument("--n-estimators", type=int, default=200)
    parser.add_argument(
        "--criterion",
        choices=["gini", "entropy", "log_loss"],
        default="gini",
    )
    parser.add_argument("--min-samples-split", type=int, default=2)
    parser.add_argument("--min-samples-leaf", type=int, default=1)
    parser.add_argument("--max-depth", type=int, default=None)
    parser.add_argument("--max-features", default="sqrt")
    parser.add_argument("--bootstrap", type=parse_bool, default=True)
    parser.add_argument(
        "--class-weight",
        choices=["balanced", "balanced_subsample"],
        default="balanced",
    )
    parser.add_argument("--n-jobs", type=int, default=-1)
    parser.add_argument("--top-features", type=int, default=25)
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    run_workflow(args)


if __name__ == "__main__":
    main()

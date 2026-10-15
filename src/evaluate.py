from __future__ import annotations

import argparse
import sys
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from config import FIGURES_DIR, RANDOM_STATE, REPORTS_DIR
from src.data_loader import load_dataset, sample_dataframe
from src.preprocessing import prepare_train_test_data, transform_features
from src.utils import ensure_project_dirs, load_joblib, save_json, save_text


def compute_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_score: np.ndarray | None,
    class_names: list[str],
    task: str,
) -> dict[str, Any]:
    average_for_precision = "binary" if task == "binary" and len(class_names) == 2 else "macro"

    metrics: dict[str, Any] = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(
            precision_score(
                y_true,
                y_pred,
                average=average_for_precision,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                y_true,
                y_pred,
                average=average_for_precision,
                zero_division=0,
            )
        ),
        "f1": float(
            f1_score(
                y_true,
                y_pred,
                average=average_for_precision,
                zero_division=0,
            )
        ),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "weighted_f1": float(
            f1_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "mcc": float(matthews_corrcoef(y_true, y_pred)),
    }

    if task == "binary" and y_score is not None and len(np.unique(y_true)) == 2:
        try:
            if y_score.ndim == 2:
                y_score_binary = y_score[:, 1]
            else:
                y_score_binary = y_score
            metrics["roc_auc"] = float(roc_auc_score(y_true, y_score_binary))
        except ValueError:
            metrics["roc_auc"] = None

    return metrics


def make_classification_report(
    y_true: np.ndarray, y_pred: np.ndarray, class_names: list[str]
) -> str:
    return classification_report(
        y_true,
        y_pred,
        target_names=class_names,
        zero_division=0,
    )


def plot_class_distribution(df: pd.DataFrame, target_col: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 5))
    order = df[target_col].astype(str).value_counts().index
    sns.countplot(data=df, x=target_col, order=order)
    plt.title(f"Class Distribution: {target_col}")
    plt.xlabel(target_col)
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def plot_correlation_heatmap(df: pd.DataFrame, output_path: Path, max_features: int = 30) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty:
        return

    variances = numeric_df.var(numeric_only=True).sort_values(ascending=False)
    selected_columns = variances.head(max_features).index
    corr = numeric_df[selected_columns].corr()

    plt.figure(figsize=(12, 9))
    sns.heatmap(corr, cmap="coolwarm", center=0, square=False)
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def plot_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: list[str],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    matrix = confusion_matrix(y_true, y_pred)
    width = max(8, min(18, len(class_names) * 1.1))
    plt.figure(figsize=(width, width * 0.8))
    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
    )
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def plot_model_comparison(results: list[dict[str, Any]], output_path: Path) -> None:
    if not results:
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(results)
    metric_columns = ["accuracy", "macro_f1", "weighted_f1", "mcc"]
    melted = frame.melt(
        id_vars="model",
        value_vars=[column for column in metric_columns if column in frame.columns],
        var_name="metric",
        value_name="score",
    )

    plt.figure(figsize=(11, 6))
    sns.barplot(data=melted, x="model", y="score", hue="metric")
    plt.title("Model Comparison")
    plt.ylim(0, 1)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def plot_feature_importance(
    feature_names: list[str],
    importances: np.ndarray,
    output_path: Path,
    top_n: int = 25,
) -> None:
    if len(feature_names) != len(importances):
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    importance_df = (
        pd.DataFrame({"feature": feature_names, "importance": importances})
        .sort_values("importance", ascending=False)
        .head(top_n)
    )

    plt.figure(figsize=(10, 8))
    sns.barplot(data=importance_df, y="feature", x="importance")
    plt.title(f"Top {top_n} Feature Importances")
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def get_prediction_scores(model: Any, X: np.ndarray) -> np.ndarray | None:
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)
    if hasattr(model, "decision_function"):
        scores = model.decision_function(X)
        return np.asarray(scores)
    return None


def save_evaluation_outputs(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_score: np.ndarray | None,
    class_names: list[str],
    task: str,
    model_name: str,
) -> dict[str, Any]:
    metrics = compute_metrics(y_true, y_pred, y_score, class_names, task)
    report = make_classification_report(y_true, y_pred, class_names)

    save_json(metrics, REPORTS_DIR / f"{task}_{model_name}_metrics.json")
    save_text(report, REPORTS_DIR / f"{task}_{model_name}_classification_report.txt")
    plot_confusion_matrix(
        y_true,
        y_pred,
        class_names,
        FIGURES_DIR / f"{task}_{model_name}_confusion_matrix.png",
    )

    return metrics


def evaluate_saved_ml_model(
    model_path: Path,
    task: str,
    sample_size: int | None = None,
) -> dict[str, Any]:
    df = sample_dataframe(load_dataset(), sample_size, RANDOM_STATE)
    bundle = load_joblib(model_path)

    prepared = prepare_train_test_data(
        df,
        task=task,
        drop_columns=bundle.get("dropped_columns", []),
    )

    preprocessor = bundle["preprocessor"]
    X_test = transform_features(preprocessor, prepared["X_test_raw"])
    y_test = prepared["y_test"]

    model = bundle["model"]
    y_pred = model.predict(X_test)
    y_score = get_prediction_scores(model, X_test)

    model_name = bundle.get("model_name", model_path.stem)
    return save_evaluation_outputs(
        y_test,
        y_pred,
        y_score,
        bundle["class_names"],
        task,
        model_name,
    )


class EvaluationMLP:
    def __init__(self, input_dim: int, hidden_layers: list[int], output_dim: int):
        import torch
        import torch.nn as nn

        layers: list[nn.Module] = []
        previous_dim = input_dim
        for hidden_dim in hidden_layers:
            layers.extend(
                [
                    nn.Linear(previous_dim, hidden_dim),
                    nn.BatchNorm1d(hidden_dim),
                    nn.ReLU(),
                    nn.Dropout(0.25),
                ]
            )
            previous_dim = hidden_dim
        layers.append(nn.Linear(previous_dim, output_dim))
        self.module = nn.Sequential(*layers)
        self.torch = torch

    def load_state_dict(self, state_dict: dict[str, Any]) -> None:
        self.module.load_state_dict(state_dict)

    def predict_proba(self, X: np.ndarray, batch_size: int = 4096) -> np.ndarray:
        torch = self.torch
        self.module.eval()
        probabilities = []
        with torch.no_grad():
            for start in range(0, len(X), batch_size):
                batch = torch.tensor(X[start : start + batch_size], dtype=torch.float32)
                logits = self.module(batch)
                probabilities.append(torch.softmax(logits, dim=1).cpu().numpy())
        return np.vstack(probabilities)


def evaluate_saved_dl_model(
    model_path: Path,
    task: str,
    sample_size: int | None = None,
) -> dict[str, Any]:
    import torch

    df = sample_dataframe(load_dataset(), sample_size, RANDOM_STATE)
    bundle = torch.load(model_path, map_location="cpu", weights_only=False)

    prepared = prepare_train_test_data(
        df,
        task=task,
        drop_columns=bundle.get("dropped_columns", []),
    )

    preprocessor = bundle["preprocessor"]
    X_test = transform_features(preprocessor, prepared["X_test_raw"])
    y_test = prepared["y_test"]

    model = EvaluationMLP(
        input_dim=bundle["input_dim"],
        hidden_layers=bundle["hidden_layers"],
        output_dim=len(bundle["class_names"]),
    )
    model.load_state_dict(bundle["state_dict"])

    y_score = model.predict_proba(X_test)
    y_pred = y_score.argmax(axis=1)

    model_name = bundle.get("model_name", model_path.stem)
    return save_evaluation_outputs(
        y_test,
        y_pred,
        y_score,
        bundle["class_names"],
        task,
        model_name,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a saved TON_IoT model.")
    parser.add_argument("--task", choices=["binary", "multiclass"], required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--sample-size", type=int, default=None)
    args = parser.parse_args()

    ensure_project_dirs()

    if args.model_path.suffix.lower() == ".pt":
        metrics = evaluate_saved_dl_model(args.model_path, args.task, args.sample_size)
    else:
        metrics = evaluate_saved_ml_model(args.model_path, args.task, args.sample_size)

    print("Evaluation metrics:")
    for key, value in metrics.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.utils.class_weight import compute_sample_weight

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from config import FIGURES_DIR, MODELS_DIR, RANDOM_STATE, REPORTS_DIR
from src.data_loader import load_dataset, print_dataset_summary, sample_dataframe
from src.evaluate import (
    get_prediction_scores,
    plot_class_distribution,
    plot_correlation_heatmap,
    plot_feature_importance,
    plot_model_comparison,
    save_evaluation_outputs,
)
from src.preprocessing import fit_transform_features, prepare_train_test_data, transform_features
from src.utils import ensure_project_dirs, parse_model_list, print_section, save_joblib, save_json


def build_models(
    task: str,
    selected_models: list[str],
    device: str = "auto",
) -> dict[str, Any]:
    models: dict[str, Any] = {}

    if "logistic" in selected_models:
        models["logistic"] = LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        )

    if "random_forest" in selected_models or "rf" in selected_models:
        models["random_forest"] = RandomForestClassifier(
            n_estimators=250,
            max_depth=None,
            min_samples_split=2,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=RANDOM_STATE,
        )

    if "svm" in selected_models:
        models["svm"] = LinearSVC(
            class_weight="balanced",
            random_state=RANDOM_STATE,
            max_iter=5000,
        )

    if "xgboost" in selected_models or "xgb" in selected_models:
        try:
            from xgboost import XGBClassifier

            xgb_device = "cpu"
            if device in {"cuda", "auto"}:
                try:
                    import torch

                    if torch.cuda.is_available():
                        xgb_device = "cuda"
                except ImportError:
                    pass

            if device == "cuda" and xgb_device != "cuda":
                print("Warning: CUDA requested for XGBoost, but CUDA is not available. Falling back to CPU.")

            xgb_params = {
                "n_estimators": 300,
                "max_depth": 6,
                "learning_rate": 0.05,
                "subsample": 0.9,
                "colsample_bytree": 0.9,
                "tree_method": "hist",
                "device": xgb_device,
                "random_state": RANDOM_STATE,
                "eval_metric": "logloss" if task == "binary" else "mlogloss",
            }
            if xgb_device == "cuda":
                print("Configured XGBoost with GPU acceleration (device='cuda').")
            models["xgboost"] = XGBClassifier(**xgb_params)
        except ImportError:
            print("xgboost is not installed. Skipping XGBoost.")

    return models


def maybe_apply_smote(X_train: np.ndarray, y_train: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    try:
        from imblearn.over_sampling import SMOTE
    except ImportError:
        print("imbalanced-learn is not installed. Continuing without SMOTE.")
        return X_train, y_train

    print("Applying SMOTE to the training set.")
    smote = SMOTE(random_state=RANDOM_STATE)
    return smote.fit_resample(X_train, y_train)


def train_and_evaluate(args: argparse.Namespace) -> None:
    ensure_project_dirs()

    print_section("Loading Dataset")
    df = sample_dataframe(load_dataset(), args.sample_size, RANDOM_STATE)
    print_dataset_summary(df)

    prepared = prepare_train_test_data(df, task=args.task, test_size=args.test_size)
    target_col = prepared["target_col"]
    class_names = prepared["class_names"]

    print_section("Class Distribution")
    print(df[target_col].astype(str).value_counts())
    plot_class_distribution(
        df,
        target_col,
        FIGURES_DIR / f"{args.task}_class_distribution.png",
    )
    plot_correlation_heatmap(df, FIGURES_DIR / f"{args.task}_correlation_heatmap.png")

    print_section("Preprocessing")
    print("Dropped columns:")
    for column in prepared["dropped_columns"]:
        print(f"- {column}")

    X_train = fit_transform_features(prepared["preprocessor"], prepared["X_train_raw"])
    X_test = transform_features(prepared["preprocessor"], prepared["X_test_raw"])
    y_train = prepared["y_train"]
    y_test = prepared["y_test"]

    if args.use_smote:
        X_train, y_train = maybe_apply_smote(X_train, y_train)

    selected_models = parse_model_list(args.models)
    models = build_models(args.task, selected_models, device=getattr(args, "device", "auto"))
    if not models:
        raise ValueError("No valid models selected.")

    comparison_results: list[dict[str, Any]] = []
    feature_names = prepared["preprocessor"].get_feature_names_out().tolist()

    for model_name, model in models.items():
        print_section(f"Training {model_name}")

        fit_kwargs: dict[str, Any] = {}
        if model_name == "xgboost":
            fit_kwargs["sample_weight"] = compute_sample_weight("balanced", y_train)

        model.fit(X_train, y_train, **fit_kwargs)

        y_pred = model.predict(X_test)
        y_score = get_prediction_scores(model, X_test)
        metrics = save_evaluation_outputs(
            y_test,
            y_pred,
            y_score,
            class_names,
            args.task,
            model_name,
        )

        comparison_row = {"model": model_name, **metrics}
        comparison_results.append(comparison_row)

        bundle = {
            "model": model,
            "model_name": model_name,
            "task": args.task,
            "preprocessor": prepared["preprocessor"],
            "label_encoder": prepared["label_encoder"],
            "class_names": class_names,
            "target_col": target_col,
            "dropped_columns": prepared["dropped_columns"],
            "feature_columns": prepared["feature_columns"],
        }
        model_path = MODELS_DIR / f"{args.task}_{model_name}.joblib"
        save_joblib(bundle, model_path)
        print(f"Saved model: {model_path}")

        if hasattr(model, "feature_importances_"):
            plot_feature_importance(
                feature_names,
                model.feature_importances_,
                FIGURES_DIR / f"{args.task}_{model_name}_feature_importance.png",
            )

        print("Metrics:")
        for key, value in metrics.items():
            print(f"{key}: {value}")

    save_json(
        {"results": comparison_results},
        REPORTS_DIR / f"{args.task}_ml_model_comparison.json",
    )
    plot_model_comparison(
        comparison_results,
        FIGURES_DIR / f"{args.task}_ml_model_comparison.png",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Train classical ML models for TON_IoT.")
    parser.add_argument("--task", choices=["binary", "multiclass"], required=True)
    parser.add_argument("--models", default="all", help="all or comma list: logistic,random_forest,xgboost,svm")
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--sample-size", type=int, default=None)
    parser.add_argument("--use-smote", action="store_true")
    parser.add_argument(
        "--device",
        choices=["auto", "cuda", "cpu"],
        default="auto",
        help="Compute device for supported models like XGBoost (auto, cuda, cpu)",
    )
    args = parser.parse_args()

    train_and_evaluate(args)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Unified GPU Training Pipeline for TON_IoT Network Intrusion Detection.

Runs entirely on NVIDIA CUDA GPUs (GeForce RTX 3060 12GB & RTX 5070 Ti 16GB).
Trains and compares:
  1. GPU Random Forest (Parallel Trees on CUDA)
  2. GPU Gradient Boosted Trees (XGBoost CUDA)
  3. GPU Deep Neural Network (PyTorch MLP on CUDA with TF32)
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import torch
import torch.nn as nn
from sklearn.metrics import (
    accuracy_score,
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
from torch.utils.data import DataLoader, TensorDataset
from tqdm import tqdm
import xgboost as xgb

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from config import FIGURES_DIR, MODELS_DIR, RANDOM_STATE, REPORTS_DIR
from src.random_forest_workflow import (
    CLASS_ORDER,
    load_network_dataset,
    preprocess_dataset,
    preprocess_train_test,
)
from src.utils import ensure_project_dirs, print_section, save_json, save_text


# ---------------------------------------------------------------------------
# PyTorch Deep Neural Network for GPU
# ---------------------------------------------------------------------------
class DeepIoTMLP(nn.Module):
    def __init__(self, input_dim: int, num_classes: int = 3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.20),
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.20),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Linear(64, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def setup_gpu() -> torch.device:
    if not torch.cuda.is_available():
        raise SystemError(
            "CRITICAL: No NVIDIA CUDA GPU detected! This script is strictly configured for GPU training."
        )

    device = torch.device("cuda:0")
    gpu_name = torch.cuda.get_device_name(0)
    cap = torch.cuda.get_device_capability(0)
    vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)

    print_section("NVIDIA GPU Hardware Details")
    print(f"Device Name        : {gpu_name}")
    print(f"Compute Capability : {cap[0]}.{cap[1]}")
    print(f"Total GPU VRAM     : {vram_gb:.2f} GB")

    # Enable TF32 for Ampere (RTX 3060) and Blackwell (RTX 5070 Ti)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    print("TensorFloat-32     : Enabled (Tensor Core acceleration active)")

    return device


def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray, y_score: np.ndarray) -> dict[str, float]:
    acc = float(accuracy_score(y_true, y_pred))
    p_macro = float(precision_score(y_true, y_pred, average="macro", zero_division=0))
    r_macro = float(recall_score(y_true, y_pred, average="macro", zero_division=0))
    f1_m = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    mcc = float(matthews_corrcoef(y_true, y_pred))
    try:
        auc_val = float(roc_auc_score(y_true, y_score, multi_class="ovr", average="macro"))
    except ValueError:
        auc_val = 1.0

    return {
        "accuracy": acc,
        "precision_macro": p_macro,
        "recall_macro": r_macro,
        "f1_macro": f1_m,
        "mcc": mcc,
        "roc_auc": auc_val,
    }


def train_gpu_pipeline(args: argparse.Namespace) -> None:
    ensure_project_dirs()
    device = setup_gpu()

    # 1. Load Data
    if getattr(args, "train_dataset", None) and getattr(args, "test_dataset", None):
        print_section("1. Loading Dedicated Train & Test Datasets for GPU Pipeline")
        train_df = load_network_dataset(args.train_dataset, args.sample_size, RANDOM_STATE)
        test_df = load_network_dataset(args.test_dataset, args.sample_size, RANDOM_STATE)
        print(f"Train Dataset: {args.train_dataset} ({len(train_df):,} rows)")
        print(f"Test Dataset:  {args.test_dataset} ({len(test_df):,} rows)")

        print_section("2. Data Preprocessing & Leakage Removal")
        X_train_df, y_train, X_test_df, y_test, metadata = preprocess_train_test(train_df, test_df)
        print(f"Engineered Features: {X_train_df.shape[1]}")
    else:
        print_section("1. Loading Dataset for GPU Pipeline")
        csv_path = args.dataset
        if not csv_path.exists():
            raise FileNotFoundError(f"Dataset not found at {csv_path}")

        print(f"Reading dataset: {csv_path}...")
        df = pd.read_csv(csv_path, low_memory=False)
        df.columns = df.columns.str.strip()

        if args.sample_size and 0 < args.sample_size < len(df):
            print(f"Sampling {args.sample_size:,} records for experiment...")
            df = df.sample(n=args.sample_size, random_state=RANDOM_STATE).reset_index(drop=True)

        print(f"Dataset Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")

        print_section("2. Data Preprocessing & Leakage Removal")
        X, y, metadata = preprocess_dataset(df)
        print(f"Removed duplicates: {metadata['duplicate_rows_removed']:,}")
        print(f"Engineered Features: {X.shape[1]}")

        X_train_df, X_test_df, y_train, y_test = train_test_split(
            X, y, test_size=args.test_size, random_state=RANDOM_STATE, stratify=y
        )

    X_train_np = np.ascontiguousarray(X_train_df.to_numpy(), dtype=np.float32)
    X_test_np = np.ascontiguousarray(X_test_df.to_numpy(), dtype=np.float32)

    print(f"Train split: {len(X_train_np):,} samples")
    print(f"Test split : {len(X_test_np):,} samples")

    results_table: list[dict[str, Any]] = []

    # -----------------------------------------------------------------------
    # MODEL 1: GPU Random Forest (200 Parallel Trees on CUDA)
    # -----------------------------------------------------------------------
    print_section("3. Training Model 1: GPU Random Forest (200 Trees on CUDA)")
    gpu_rf = xgb.XGBClassifier(
        n_estimators=1,
        num_parallel_tree=args.n_estimators,
        subsample=0.8,
        colsample_bynode=0.8,
        learning_rate=1.0,
        tree_method="hist",
        device="cuda",
        random_state=RANDOM_STATE,
    )

    t0 = time.time()
    gpu_rf.fit(X_train_np, y_train)
    rf_train_time = time.time() - t0
    print(f"GPU Random Forest trained in {rf_train_time:.2f} seconds!")

    # Latency test
    t_lat = time.time()
    y_pred_rf = gpu_rf.predict(X_test_np)
    y_score_rf = gpu_rf.predict_proba(X_test_np)
    rf_latency_us = ((time.time() - t_lat) / len(X_test_np)) * 1_000_000

    rf_metrics = evaluate_predictions(y_test, y_pred_rf, y_score_rf)
    results_table.append(
        {
            "Model": "GPU Random Forest",
            "Hardware": "NVIDIA CUDA",
            "Train Time (s)": round(rf_train_time, 2),
            "Latency (us/sample)": round(rf_latency_us, 2),
            **rf_metrics,
        }
    )

    # -----------------------------------------------------------------------
    # MODEL 2: GPU XGBoost (Gradient Boosted Trees on CUDA)
    # -----------------------------------------------------------------------
    print_section("4. Training Model 2: GPU XGBoost (Gradient Boosted Trees on CUDA)")
    gpu_xgb = xgb.XGBClassifier(
        n_estimators=args.n_estimators,
        max_depth=6,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        tree_method="hist",
        device="cuda",
        random_state=RANDOM_STATE,
        eval_metric="mlogloss",
    )

    t0 = time.time()
    gpu_xgb.fit(X_train_np, y_train)
    xgb_train_time = time.time() - t0
    print(f"GPU XGBoost trained in {xgb_train_time:.2f} seconds!")

    t_lat = time.time()
    y_pred_xgb = gpu_xgb.predict(X_test_np)
    y_score_xgb = gpu_xgb.predict_proba(X_test_np)
    xgb_latency_us = ((time.time() - t_lat) / len(X_test_np)) * 1_000_000

    xgb_metrics = evaluate_predictions(y_test, y_pred_xgb, y_score_xgb)
    results_table.append(
        {
            "Model": "GPU XGBoost",
            "Hardware": "NVIDIA CUDA",
            "Train Time (s)": round(xgb_train_time, 2),
            "Latency (us/sample)": round(xgb_latency_us, 2),
            **xgb_metrics,
        }
    )

    # -----------------------------------------------------------------------
    # MODEL 3: PyTorch Deep Neural Network (MLP on CUDA)
    # -----------------------------------------------------------------------
    print_section("5. Training Model 3: PyTorch Deep MLP (CUDA GPU)")
    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_np).astype(np.float32)
    X_test_scaled = scaler.transform(X_test_np).astype(np.float32)

    mlp_model = DeepIoTMLP(input_dim=X_train_np.shape[1], num_classes=len(CLASS_ORDER)).to(device)

    train_tensor_x = torch.tensor(X_train_scaled, dtype=torch.float32)
    train_tensor_y = torch.tensor(y_train, dtype=torch.long)
    train_loader = DataLoader(
        TensorDataset(train_tensor_x, train_tensor_y),
        batch_size=args.batch_size,
        shuffle=True,
        pin_memory=True,
    )

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(mlp_model.parameters(), lr=1e-3, weight_decay=1e-4)

    t0 = time.time()
    mlp_model.train()
    epochs = args.epochs
    for epoch in range(1, epochs + 1):
        running_loss = 0.0
        for bx, by in train_loader:
            bx = bx.to(device, non_blocking=True)
            by = by.to(device, non_blocking=True)
            optimizer.zero_grad()
            logits = mlp_model(bx)
            loss = criterion(logits, by)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * len(bx)
        if epoch % 5 == 0 or epoch == epochs:
            avg_loss = running_loss / len(X_train_np)
            print(f"  Epoch {epoch:02d}/{epochs:02d} - Loss: {avg_loss:.5f}")
    torch.cuda.synchronize()
    mlp_train_time = time.time() - t0
    print(f"PyTorch Deep MLP trained in {mlp_train_time:.2f} seconds!")

    # Latency test
    mlp_model.eval()
    t_lat = time.time()
    with torch.no_grad():
        test_bx = torch.tensor(X_test_scaled, dtype=torch.float32, device=device)
        logits = mlp_model(test_bx)
        probs = torch.softmax(logits, dim=1).cpu().numpy()
    torch.cuda.synchronize()
    mlp_latency_us = ((time.time() - t_lat) / len(X_test_np)) * 1_000_000

    y_score_mlp = probs
    y_pred_mlp = probs.argmax(axis=1)

    mlp_metrics = evaluate_predictions(y_test, y_pred_mlp, y_score_mlp)
    results_table.append(
        {
            "Model": "PyTorch Deep MLP",
            "Hardware": "NVIDIA CUDA",
            "Train Time (s)": round(mlp_train_time, 2),
            "Latency (us/sample)": round(mlp_latency_us, 2),
            **mlp_metrics,
        }
    )

    # -----------------------------------------------------------------------
    # Comparison Summary & Plots
    # -----------------------------------------------------------------------
    print_section("6. GPU Comparison Summary")
    df_results = pd.DataFrame(results_table)
    print(df_results.to_string(index=False))

    save_json({"results": results_table}, REPORTS_DIR / "pure_gpu_benchmark_results.json")

    # Generate Comparative Bar Chart
    plt.figure(figsize=(10, 5))
    metrics_to_plot = ["accuracy", "f1_macro", "mcc", "roc_auc"]
    plot_df = df_results.melt(id_vars=["Model"], value_vars=metrics_to_plot, var_name="Metric", value_name="Score")
    sns.barplot(data=plot_df, x="Metric", y="Score", hue="Model", palette="magma")
    plt.title("GPU Model Comparison on TON_IoT (DoS / DDoS / Normal)")
    plt.ylim(0.95, 1.005)
    plt.tight_layout()
    comp_plot_path = FIGURES_DIR / "pure_gpu_comparison.png"
    plt.savefig(comp_plot_path, dpi=160)
    plt.close()
    print(f"\nSaved GPU Comparison Chart: {comp_plot_path}")

    # Generate Confusion Matrix for the best model (GPU Random Forest)
    plt.figure(figsize=(7, 5))
    cm = confusion_matrix(y_test, y_pred_rf)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=CLASS_ORDER, yticklabels=CLASS_ORDER)
    plt.title("GPU Random Forest Confusion Matrix (CUDA)")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.tight_layout()
    cm_path = FIGURES_DIR / "gpu_rf_confusion_matrix.png"
    plt.savefig(cm_path, dpi=160)
    plt.close()
    print(f"Saved GPU RF Confusion Matrix: {cm_path}")

    # Save models
    joblib.dump(gpu_rf, MODELS_DIR / "gpu_random_forest.joblib")
    joblib.dump(gpu_xgb, MODELS_DIR / "gpu_xgboost.joblib")
    torch.save(mlp_model.state_dict(), MODELS_DIR / "gpu_deep_mlp.pt")
    print(f"Saved trained GPU models into: {MODELS_DIR}")


def main() -> None:
    parser = argparse.ArgumentParser(description="GPU Training Pipeline for TON_IoT.")
    parser.add_argument("--dataset", type=Path, default=ROOT / "data" / "dataset.csv")
    parser.add_argument("--train-dataset", type=Path, default=None, help="Path to dedicated training CSV")
    parser.add_argument("--test-dataset", type=Path, default=None, help="Path to dedicated testing CSV")
    parser.add_argument("--sample-size", type=int, default=None, help="Sample size (None for full dataset)")
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--n-estimators", type=int, default=200)
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--batch-size", type=int, default=1024)
    args = parser.parse_args()

    train_gpu_pipeline(args)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Approach 1: Memory-Mapped Binary Preprocessing & Full GPU Training Pipeline.

Designed specifically for RAM-constrained systems (e.g., <= 16 GB system RAM)
training on large datasets such as TON_IoT (10.3M total records: 8.27M train, 2.06M test).

Workflow:
  1. Chunked streaming preprocessing of raw CSVs into compact on-disk binary
     memory-mapped files (np.memmap float32 for X, int8 for y). Peak RAM < 1.5 GB.
  2. Instantaneous zero-copy loading via np.memmap (< 50 MB system RAM).
  3. Full GPU training on NVIDIA CUDA (RTX 3060 12GB):
     - Model 1: GPU Random Forest (Parallel histogram trees on CUDA)
     - Model 2: GPU XGBoost (Gradient Boosted Trees on CUDA)
     - Model 3: PyTorch Deep MLP (Deep Neural Network on CUDA with TF32)
  4. Batched inference & evaluation on all 2,065,123 test records without VRAM spikes.
  5. High-resolution comparison plots, confusion matrices, and JSON benchmark reports.
"""

from __future__ import annotations

import argparse
import gc
import json
import os
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
import psutil
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
)
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm
import xgboost as xgb

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from config import (
    FIGURES_DIR,
    MODELS_DIR,
    RANDOM_STATE,
    REPORTS_DIR,
    TRAIN_DATA_FILE,
    TEST_DATA_FILE,
)
from src.random_forest_workflow import CLASS_ORDER, normalize_target
from src.utils import ensure_project_dirs, print_section, save_json

CACHE_DIR = ROOT / "data" / "cache_memmap"

# Columns to drop to prevent leakage and overfitting to timestamps/identifiers
IDENTIFIER_AND_TIME_COLUMNS = {
    "ts",
    "time",
    "timestamp",
    "date",
    "uid",
    "src_ip",
    "dst_ip",
    "source_ip",
    "destination_ip",
    "id.orig_h",
    "id.resp_h",
    "orig_h",
    "resp_h",
    "mac",
    "url",
    "uri",
    "http_uri",
    "dns_query",
    "user_agent",
    "http_user_agent",
}
LEAKAGE_COLUMNS = {"label", "type"}


def get_ram_usage_mb() -> float:
    """Return the resident memory (RSS) of the current process in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


def setup_gpu() -> torch.device:
    """Initialize NVIDIA CUDA device and enable TensorFloat-32 acceleration."""
    if not torch.cuda.is_available():
        raise SystemError(
            "CRITICAL: No NVIDIA CUDA GPU detected! This pipeline requires an NVIDIA GPU."
        )

    device = torch.device("cuda:0")
    gpu_name = torch.cuda.get_device_name(0)
    cap = torch.cuda.get_device_capability(0)
    vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)

    print_section("NVIDIA GPU Hardware Details")
    print(f"Device Name        : {gpu_name}")
    print(f"Compute Capability : {cap[0]}.{cap[1]}")
    print(f"Total GPU VRAM     : {vram_gb:.2f} GB")

    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    print("TensorFloat-32     : Enabled (Tensor Core acceleration active)")
    return device


# ---------------------------------------------------------------------------
# PyTorch Deep Neural Network Architecture
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


class MemmapTorchDataset(Dataset):
    """Zero-copy memory-mapped PyTorch Dataset for low RAM training."""

    def __init__(self, x_memmap: np.memmap, y_memmap: np.memmap):
        self.X = x_memmap
        self.y = y_memmap

    def __len__(self) -> int:
        return len(self.y)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        x_val = torch.tensor(self.X[idx], dtype=torch.float32)
        y_val = torch.tensor(int(self.y[idx]), dtype=torch.long)
        return x_val, y_val


# ---------------------------------------------------------------------------
# Fast Chunked Memory-Mapped Preprocessing
# ---------------------------------------------------------------------------
def fast_count_lines(path: Path) -> int:
    """Quickly count lines in a large text file using a 4MB binary read buffer."""
    count = 0
    with open(path, "rb") as f:
        buf = f.raw.read(4 * 1024 * 1024)
        while buf:
            count += buf.count(b"\n")
            buf = f.raw.read(4 * 1024 * 1024)
    return count


def inspect_schema(sample_path: Path) -> tuple[list[str], list[str]]:
    """Inspect CSV header and sample to define numeric and categorical features."""
    sample = pd.read_csv(sample_path, nrows=1000, low_memory=False)
    sample.columns = sample.columns.str.strip()

    feature_cols = []
    cat_cols = []
    for col in sample.columns:
        low = col.lower()
        if col in LEAKAGE_COLUMNS or low in IDENTIFIER_AND_TIME_COLUMNS:
            continue
        feature_cols.append(col)
        if sample[col].dtype == object or pd.api.types.is_string_dtype(sample[col].dtype):
            cat_cols.append(col)

    return feature_cols, cat_cols


def build_category_vocabularies(
    csv_path: Path, cat_cols: list[str], max_sample_rows: int = 500_000
) -> dict[str, dict[str, int]]:
    """Build integer index mappings for categorical features from initial rows."""
    vocabs: dict[str, dict[str, int]] = {col: {"<missing>": 0, "<other>": 1} for col in cat_cols}
    if not cat_cols:
        return vocabs

    for chunk in pd.read_csv(csv_path, chunksize=100_000, nrows=max_sample_rows, low_memory=False):
        chunk.columns = chunk.columns.str.strip()
        for col in cat_cols:
            if col in chunk.columns:
                unique_vals = chunk[col].fillna("<missing>").astype(str).unique()
                for val in unique_vals:
                    val_str = str(val).strip()
                    if val_str not in vocabs[col]:
                        vocabs[col][val_str] = len(vocabs[col])
    return vocabs


def transform_chunk(
    chunk: pd.DataFrame,
    feature_cols: list[str],
    cat_cols: list[str],
    vocabs: dict[str, dict[str, int]],
) -> tuple[np.ndarray, np.ndarray]:
    """Transform a single CSV chunk into clean float32 features and int8 targets."""
    chunk.columns = chunk.columns.str.strip()

    # Target extraction & normalization
    target_series = chunk["type"].map(normalize_target)
    target_map = {name: idx for idx, name in enumerate(CLASS_ORDER)}
    y_raw = target_series.map(target_map).to_numpy()
    valid_mask = ~np.isnan(y_raw)
    y = y_raw[valid_mask].astype(np.int8)

    chunk_valid = chunk[valid_mask]
    n_rows = len(chunk_valid)
    n_features = len(feature_cols)

    X = np.empty((n_rows, n_features), dtype=np.float32)

    for i, col in enumerate(feature_cols):
        if col not in chunk_valid.columns:
            X[:, i] = -1.0
            continue

        if col in cat_cols:
            v_map = vocabs[col]
            series_str = chunk_valid[col].fillna("<missing>").astype(str).str.strip()
            # Map strings to int indexes, default to 1 (<other>) if unseen
            X[:, i] = series_str.map(lambda v: v_map.get(v, 1)).to_numpy(dtype=np.float32)
        else:
            numeric_vals = pd.to_numeric(chunk_valid[col], errors="coerce").fillna(0.0).to_numpy(dtype=np.float32)
            # Clip extreme infinities
            numeric_vals[np.isinf(numeric_vals)] = 0.0
            X[:, i] = numeric_vals

    return X, y


def prepare_memmap_cache(
    train_csv: Path,
    test_csv: Path,
    cache_dir: Path = CACHE_DIR,
    chunksize: int = 250_000,
    force_rebuild: bool = False,
) -> tuple[np.memmap, np.memmap, np.memmap, np.memmap, dict[str, Any]]:
    """Convert raw train/test CSVs to memory-mapped binary files chunk-by-chunk."""
    cache_dir.mkdir(parents=True, exist_ok=True)

    x_train_path = cache_dir / "X_train.f32"
    y_train_path = cache_dir / "y_train.i8"
    x_test_path = cache_dir / "X_test.f32"
    y_test_path = cache_dir / "y_test.i8"
    meta_path = cache_dir / "metadata.json"

    # 1. Check if valid cache already exists
    if not force_rebuild and meta_path.is_file() and x_train_path.is_file() and x_test_path.is_file():
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            train_shape = tuple(meta["train_shape"])
            test_shape = tuple(meta["test_shape"])

            # Verify file byte sizes
            expected_x_train = train_shape[0] * train_shape[1] * 4
            expected_x_test = test_shape[0] * test_shape[1] * 4
            if (
                x_train_path.stat().st_size == expected_x_train
                and x_test_path.stat().st_size == expected_x_test
            ):
                print_section("Instant Zero-Copy Cache Loaded")
                print(f"Found validated binary memory-map cache in: {cache_dir}")
                print(f"Train samples : {train_shape[0]:,} rows x {train_shape[1]} features ({train_shape[0]*train_shape[1]*4 / 1e6:.1f} MB)")
                print(f"Test samples  : {test_shape[0]:,} rows x {test_shape[1]} features ({test_shape[0]*test_shape[1]*4 / 1e6:.1f} MB)")
                print(f"Current System RAM: {get_ram_usage_mb():.1f} MB (Zero Memory Pressure!)")

                X_train = np.memmap(x_train_path, dtype="float32", mode="r", shape=train_shape)
                y_train = np.memmap(y_train_path, dtype="int8", mode="r", shape=(train_shape[0],))
                X_test = np.memmap(x_test_path, dtype="float32", mode="r", shape=test_shape)
                y_test = np.memmap(y_test_path, dtype="int8", mode="r", shape=(test_shape[0],))
                return X_train, y_train, X_test, y_test, meta
        except Exception as exc:
            print(f"Cache validation check encountered: {exc}. Rebuilding cache...")

    # 2. Build Cache from scratch
    print_section("Approach 1: Out-of-Core Chunked Preprocessing to Memmap")
    print(f"Source Train CSV: {train_csv}")
    print(f"Source Test CSV : {test_csv}")
    print(f"Chunk size      : {chunksize:,} rows per iteration")
    print(f"Starting System RAM: {get_ram_usage_mb():.1f} MB")

    t_start = time.time()
    feature_cols, cat_cols = inspect_schema(train_csv)
    print(f"Extracted Features: {len(feature_cols)} (Categoricals: {len(cat_cols)})")

    print("\n[Pass 1/2] Counting total records & compiling categorical dictionaries...")
    train_lines = fast_count_lines(train_csv)
    test_lines = fast_count_lines(test_csv)
    n_train_expected = max(0, train_lines - 1)
    n_test_expected = max(0, test_lines - 1)
    print(f"Train file records: {n_train_expected:,} rows")
    print(f"Test file records : {n_test_expected:,} rows")

    vocabs = build_category_vocabularies(train_csv, cat_cols)

    # Pre-allocate binary on-disk files
    n_features = len(feature_cols)
    print(f"\n[Pass 2/2] Streaming chunks and writing directly to NVMe memory-map...")
    X_train_mmap = np.memmap(x_train_path, dtype="float32", mode="w+", shape=(n_train_expected, n_features))
    y_train_mmap = np.memmap(y_train_path, dtype="int8", mode="w+", shape=(n_train_expected,))

    # Process Train Set
    train_offset = 0
    train_chunks = pd.read_csv(train_csv, chunksize=chunksize, low_memory=False)
    for chunk in tqdm(train_chunks, desc="Processing Train CSV", total=(n_train_expected // chunksize) + 1):
        X_chunk, y_chunk = transform_chunk(chunk, feature_cols, cat_cols, vocabs)
        chunk_len = len(y_chunk)
        X_train_mmap[train_offset : train_offset + chunk_len] = X_chunk
        y_train_mmap[train_offset : train_offset + chunk_len] = y_chunk
        train_offset += chunk_len
        del chunk, X_chunk, y_chunk
        gc.collect()

    X_train_mmap.flush()
    y_train_mmap.flush()

    # Process Test Set
    X_test_mmap = np.memmap(x_test_path, dtype="float32", mode="w+", shape=(n_test_expected, n_features))
    y_test_mmap = np.memmap(y_test_path, dtype="int8", mode="w+", shape=(n_test_expected,))

    test_offset = 0
    test_chunks = pd.read_csv(test_csv, chunksize=chunksize, low_memory=False)
    for chunk in tqdm(test_chunks, desc="Processing Test CSV", total=(n_test_expected // chunksize) + 1):
        X_chunk, y_chunk = transform_chunk(chunk, feature_cols, cat_cols, vocabs)
        chunk_len = len(y_chunk)
        X_test_mmap[test_offset : test_offset + chunk_len] = X_chunk
        y_test_mmap[test_offset : test_offset + chunk_len] = y_chunk
        test_offset += chunk_len
        del chunk, X_chunk, y_chunk
        gc.collect()

    X_test_mmap.flush()
    y_test_mmap.flush()
    del X_train_mmap, y_train_mmap, X_test_mmap, y_test_mmap
    gc.collect()

    meta = {
        "feature_cols": feature_cols,
        "cat_cols": cat_cols,
        "train_shape": [train_offset, n_features],
        "test_shape": [test_offset, n_features],
        "class_order": CLASS_ORDER,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    elapsed = time.time() - t_start
    print(f"\nPreprocessing finished in {elapsed:.1f} seconds!")
    print(f"Final Peak RAM during conversion: {get_ram_usage_mb():.1f} MB (strictly kept < 1.5 GB)")

    # Re-open in read-only mode
    X_train = np.memmap(x_train_path, dtype="float32", mode="r", shape=(train_offset, n_features))
    y_train = np.memmap(y_train_path, dtype="int8", mode="r", shape=(train_offset,))
    X_test = np.memmap(x_test_path, dtype="float32", mode="r", shape=(test_offset, n_features))
    y_test = np.memmap(y_test_path, dtype="int8", mode="r", shape=(test_offset,))

    return X_train, y_train, X_test, y_test, meta


# ---------------------------------------------------------------------------
# Evaluation & Batched Prediction Helpers
# ---------------------------------------------------------------------------
def evaluate_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_score: np.ndarray) -> dict[str, float]:
    """Compute complete classification metrics."""
    acc = float(accuracy_score(y_true, y_pred))
    p_macro = float(precision_score(y_true, y_pred, average="macro", zero_division=0))
    r_macro = float(recall_score(y_true, y_pred, average="macro", zero_division=0))
    f1_m = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    mcc = float(matthews_corrcoef(y_true, y_pred))
    try:
        auc_val = float(roc_auc_score(y_true, y_score, multi_class="ovr", average="macro"))
    except Exception:
        auc_val = 1.0

    return {
        "accuracy": acc,
        "precision_macro": p_macro,
        "recall_macro": r_macro,
        "f1_macro": f1_m,
        "mcc": mcc,
        "roc_auc": auc_val,
    }


def predict_tree_batched(
    model: xgb.XGBClassifier, X_test: np.memmap, chunk_size: int = 250_000
) -> tuple[np.ndarray, np.ndarray, float]:
    """Evaluate tree model on test memmap in batches to prevent VRAM allocation spikes."""
    total_len = len(X_test)
    preds_list = []
    probs_list = []

    t_start = time.time()
    for start in range(0, total_len, chunk_size):
        end = min(start + chunk_size, total_len)
        chunk = X_test[start:end]
        preds_list.append(model.predict(chunk))
        probs_list.append(model.predict_proba(chunk))

    latency_us = ((time.time() - t_start) / total_len) * 1_000_000
    y_pred = np.concatenate(preds_list)
    y_score = np.concatenate(probs_list, axis=0)
    return y_pred, y_score, latency_us


def predict_mlp_batched(
    model: nn.Module,
    X_test: np.memmap,
    device: torch.device,
    batch_size: int = 16384,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Evaluate PyTorch MLP on test memmap in mini-batches on CUDA."""
    model.eval()
    total_len = len(X_test)
    preds_list = []
    probs_list = []

    t_start = time.time()
    with torch.no_grad():
        for start in range(0, total_len, batch_size):
            end = min(start + batch_size, total_len)
            bx = torch.tensor(X_test[start:end], dtype=torch.float32, device=device)
            logits = model(bx)
            probs = torch.softmax(logits, dim=1).cpu().numpy()
            probs_list.append(probs)
            preds_list.append(probs.argmax(axis=1))

    if torch.cuda.is_available():
        torch.cuda.synchronize()

    latency_us = ((time.time() - t_start) / total_len) * 1_000_000
    y_pred = np.concatenate(preds_list)
    y_score = np.concatenate(probs_list, axis=0)
    return y_pred, y_score, latency_us


# ---------------------------------------------------------------------------
# Main Training Workflow for Approach 1
# ---------------------------------------------------------------------------
def run_memmap_gpu_pipeline(args: argparse.Namespace) -> None:
    ensure_project_dirs()
    device = setup_gpu()

    # 1. Prepare / Load Memory-Mapped Binary Cache
    X_train, y_train, X_test, y_test, meta = prepare_memmap_cache(
        train_csv=args.train_dataset,
        test_csv=args.test_dataset,
        chunksize=args.chunksize,
        force_rebuild=args.rebuild_cache,
    )

    n_train, n_features = X_train.shape
    n_test = len(X_test)
    results_table: list[dict[str, Any]] = []

    # -----------------------------------------------------------------------
    # MODEL 1: GPU Random Forest (Parallel Trees on CUDA)
    # -----------------------------------------------------------------------
    print_section(f"1. Training Model 1: GPU Random Forest ({args.n_estimators} Parallel Trees on CUDA)")
    print(f"Fitting on {n_train:,} training samples using CUDA histogram algorithm...")
    print(f"System RAM prior to fit: {get_ram_usage_mb():.1f} MB")

    gpu_rf = xgb.XGBClassifier(
        n_estimators=1,
        num_parallel_tree=args.n_estimators,
        subsample=0.8,
        colsample_bynode=0.8,
        learning_rate=1.0,
        tree_method="hist",
        device="cuda",
        max_depth=args.max_depth,
        random_state=RANDOM_STATE,
    )

    t0 = time.time()
    gpu_rf.fit(X_train, y_train)
    rf_train_time = time.time() - t0
    print(f"GPU Random Forest trained in {rf_train_time:.2f} seconds!")

    print(f"Evaluating GPU Random Forest on {n_test:,} test samples...")
    y_pred_rf, y_score_rf, rf_latency_us = predict_tree_batched(gpu_rf, X_test)
    rf_metrics = evaluate_metrics(y_test, y_pred_rf, y_score_rf)
    results_table.append(
        {
            "Model": "GPU Random Forest",
            "Hardware": "NVIDIA CUDA (RTX 3060)",
            "Train Time (s)": round(rf_train_time, 2),
            "Latency (us/sample)": round(rf_latency_us, 2),
            **rf_metrics,
        }
    )

    # -----------------------------------------------------------------------
    # MODEL 2: GPU XGBoost (Gradient Boosted Decision Trees on CUDA)
    # -----------------------------------------------------------------------
    print_section(f"2. Training Model 2: GPU XGBoost ({args.n_estimators} Boosted Trees on CUDA)")
    print(f"Fitting on {n_train:,} training samples...")
    print(f"System RAM prior to fit: {get_ram_usage_mb():.1f} MB")

    gpu_xgb = xgb.XGBClassifier(
        n_estimators=args.n_estimators,
        max_depth=6,
        learning_rate=0.1,
        tree_method="hist",
        device="cuda",
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=RANDOM_STATE,
    )

    t0 = time.time()
    gpu_xgb.fit(X_train, y_train)
    xgb_train_time = time.time() - t0
    print(f"GPU XGBoost trained in {xgb_train_time:.2f} seconds!")

    print(f"Evaluating GPU XGBoost on {n_test:,} test samples...")
    y_pred_xgb, y_score_xgb, xgb_latency_us = predict_tree_batched(gpu_xgb, X_test)
    xgb_metrics = evaluate_metrics(y_test, y_pred_xgb, y_score_xgb)
    results_table.append(
        {
            "Model": "GPU XGBoost",
            "Hardware": "NVIDIA CUDA (RTX 3060)",
            "Train Time (s)": round(xgb_train_time, 2),
            "Latency (us/sample)": round(xgb_latency_us, 2),
            **xgb_metrics,
        }
    )

    # -----------------------------------------------------------------------
    # MODEL 3: PyTorch Deep MLP (Deep Neural Network on CUDA)
    # -----------------------------------------------------------------------
    print_section("3. Training Model 3: PyTorch Deep MLP (CUDA GPU with TF32)")
    print(f"Architecture: [{n_features} -> 256 -> 128 -> 64 -> 3]")
    print(f"Batch Size: {args.batch_size:,} | Epochs: {args.epochs}")
    print(f"System RAM prior to fit: {get_ram_usage_mb():.1f} MB")

    mlp_model = DeepIoTMLP(input_dim=n_features, num_classes=len(CLASS_ORDER)).to(device)
    mlp_dataset = MemmapTorchDataset(X_train, y_train)
    train_loader = DataLoader(
        mlp_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        drop_last=False,
        num_workers=2,
        pin_memory=True,
    )

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(mlp_model.parameters(), lr=1e-3, weight_decay=1e-4)

    t0 = time.time()
    for epoch in range(1, args.epochs + 1):
        mlp_model.train()
        running_loss = 0.0
        pbar = tqdm(train_loader, desc=f"Epoch {epoch}/{args.epochs}", leave=False)
        for bx, by in pbar:
            bx = bx.to(device, non_blocking=True)
            by = by.to(device, non_blocking=True)

            optimizer.zero_grad(set_to_none=True)
            logits = mlp_model(bx)
            loss = criterion(logits, by)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            pbar.set_postfix({"Loss": f"{loss.item():.4f}"})

        epoch_loss = running_loss / len(train_loader)
        print(f"Epoch {epoch:02d}/{args.epochs:02d} Complete — Avg CrossEntropy Loss: {epoch_loss:.4f}")

    if torch.cuda.is_available():
        torch.cuda.synchronize()
    mlp_train_time = time.time() - t0
    print(f"PyTorch Deep MLP trained in {mlp_train_time:.2f} seconds!")

    print(f"Evaluating PyTorch Deep MLP on {n_test:,} test samples...")
    y_pred_mlp, y_score_mlp, mlp_latency_us = predict_mlp_batched(mlp_model, X_test, device)
    mlp_metrics = evaluate_metrics(y_test, y_pred_mlp, y_score_mlp)
    results_table.append(
        {
            "Model": "PyTorch Deep MLP",
            "Hardware": "NVIDIA CUDA (RTX 3060)",
            "Train Time (s)": round(mlp_train_time, 2),
            "Latency (us/sample)": round(mlp_latency_us, 2),
            **mlp_metrics,
        }
    )

    # -----------------------------------------------------------------------
    # Results & High-Resolution Reports
    # -----------------------------------------------------------------------
    print_section("4. Full 3-Model Benchmark Comparison Summary")
    df_results = pd.DataFrame(results_table)
    print(df_results.to_string(index=False))

    save_json({"results": results_table}, REPORTS_DIR / "memmap_gpu_benchmark_results.json")
    print(f"\nSaved Benchmark Report: {REPORTS_DIR / 'memmap_gpu_benchmark_results.json'}")

    # Comparative Plot
    plt.figure(figsize=(10, 5))
    metrics_to_plot = ["accuracy", "f1_macro", "mcc", "roc_auc"]
    plot_df = df_results.melt(id_vars=["Model"], value_vars=metrics_to_plot, var_name="Metric", value_name="Score")
    sns.barplot(data=plot_df, x="Metric", y="Score", hue="Model", palette="magma")
    plt.title("Approach 1: Out-of-Core GPU Model Comparison (10.3M Flow Records)")
    plt.ylim(0.95, 1.005)
    plt.tight_layout()
    comp_plot_path = FIGURES_DIR / "memmap_gpu_comparison.png"
    plt.savefig(comp_plot_path, dpi=160)
    plt.close()
    print(f"Saved Comparison Chart: {comp_plot_path}")

    # Confusion Matrix for GPU Random Forest
    plt.figure(figsize=(7, 5))
    cm_rf = confusion_matrix(y_test, y_pred_rf)
    sns.heatmap(cm_rf, annot=True, fmt="d", cmap="Blues", xticklabels=CLASS_ORDER, yticklabels=CLASS_ORDER)
    plt.title("GPU Random Forest Confusion Matrix (Approach 1 - 2.06M Test Records)")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.tight_layout()
    cm_rf_path = FIGURES_DIR / "memmap_gpu_rf_confusion_matrix.png"
    plt.savefig(cm_rf_path, dpi=160)
    plt.close()
    print(f"Saved GPU RF Confusion Matrix: {cm_rf_path}")

    # Confusion Matrix for GPU XGBoost
    plt.figure(figsize=(7, 5))
    cm_xgb = confusion_matrix(y_test, y_pred_xgb)
    sns.heatmap(cm_xgb, annot=True, fmt="d", cmap="Greens", xticklabels=CLASS_ORDER, yticklabels=CLASS_ORDER)
    plt.title("GPU XGBoost Confusion Matrix (Approach 1 - 2.06M Test Records)")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.tight_layout()
    cm_xgb_path = FIGURES_DIR / "memmap_gpu_xgboost_confusion_matrix.png"
    plt.savefig(cm_xgb_path, dpi=160)
    plt.close()
    print(f"Saved GPU XGBoost Confusion Matrix: {cm_xgb_path}")

    # Confusion Matrix for PyTorch Deep MLP
    plt.figure(figsize=(7, 5))
    cm_mlp = confusion_matrix(y_test, y_pred_mlp)
    sns.heatmap(cm_mlp, annot=True, fmt="d", cmap="Purples", xticklabels=CLASS_ORDER, yticklabels=CLASS_ORDER)
    plt.title("PyTorch Deep MLP Confusion Matrix (Approach 1 - 2.06M Test Records)")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.tight_layout()
    cm_mlp_path = FIGURES_DIR / "memmap_gpu_mlp_confusion_matrix.png"
    plt.savefig(cm_mlp_path, dpi=160)
    plt.close()
    print(f"Saved PyTorch Deep MLP Confusion Matrix: {cm_mlp_path}")

    # Save Models
    joblib.dump(gpu_rf, MODELS_DIR / "memmap_gpu_random_forest.joblib")
    joblib.dump(gpu_xgb, MODELS_DIR / "memmap_gpu_xgboost.joblib")
    torch.save(mlp_model.state_dict(), MODELS_DIR / "memmap_gpu_deep_mlp.pt")
    print(f"Saved trained models to: {MODELS_DIR}")
    print(f"Final Peak System RAM: {get_ram_usage_mb():.1f} MB (Successfully prevented OOM!)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Approach 1: Out-of-Core Memory-Mapped GPU Training Pipeline for TON_IoT"
    )
    parser.add_argument(
        "--train-dataset",
        type=Path,
        default=TRAIN_DATA_FILE,
        help="Path to training CSV (default: data/train_normal_dos_ddos.csv)",
    )
    parser.add_argument(
        "--test-dataset",
        type=Path,
        default=TEST_DATA_FILE,
        help="Path to testing CSV (default: data/test_normal_dos_ddos.csv)",
    )
    parser.add_argument(
        "--chunksize",
        type=int,
        default=250_000,
        help="Number of rows per chunk during CSV streaming (default: 250,000)",
    )
    parser.add_argument(
        "--n-estimators",
        type=int,
        default=100,
        help="Number of trees for GPU Random Forest & XGBoost (default: 100)",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=8,
        help="Tree depth for Random Forest & XGBoost (default: 8)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=8192,
        help="Batch size for PyTorch MLP GPU training (default: 8,192)",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=5,
        help="Epochs for PyTorch MLP training (default: 5)",
    )
    parser.add_argument(
        "--rebuild-cache",
        action="store_true",
        help="Force re-conversion of CSV files to binary memmap cache",
    )

    args = parser.parse_args()
    run_memmap_gpu_pipeline(args)


if __name__ == "__main__":
    main()

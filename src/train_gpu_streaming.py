#!/usr/bin/env python3
"""Out-of-core CUDA MLP training for large pre-split TON_IoT CSVs.

CSV chunks are transformed on CPU and copied to CUDA one mini-batch at a time.
This intentionally trains the neural MLP only: sklearn-style/XGBoost tree fits
in the original comparison pipeline require the complete feature matrix.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import time
from pathlib import Path
from typing import Iterator

import joblib
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, f1_score, matthews_corrcoef,
                             precision_score, recall_score, roc_auc_score)
from sklearn.preprocessing import StandardScaler

from src.random_forest_workflow import CLASS_ORDER, is_ip_column, normalize_target
from src.train_gpu import DeepIoTMLP, setup_gpu
from config import MODELS_DIR, REPORTS_DIR
from src.utils import ensure_project_dirs

LEAKAGE = {"label", "type"}
# Identifier and free-text columns are excluded, matching the project's
# high-cardinality filtering intent without scanning whole files into memory.
DROP_NAME_HINTS = ("uid", "id.orig_h", "id.resp_h", "orig_h", "resp_h",
                   "src_ip", "dst_ip", "source_ip", "destination_ip",
                   "mac", "timestamp", "time", "ts", "date", "url",
                   "uri", "query", "dns", "host", "domain", "user_agent")


def read_header(path: Path) -> list[str]:
    columns = list(pd.read_csv(path, nrows=0).columns.str.strip())
    if "type" not in columns:
        raise ValueError(f"Target column 'type' missing from {path}")
    return columns


def make_feature_schema(path: Path, chunksize: int) -> tuple[list[str], list[str]]:
    columns = read_header(path)
    sample = next(pd.read_csv(path, chunksize=chunksize, low_memory=False))
    sample.columns = sample.columns.str.strip()
    names, categorical = [], []
    for col in columns:
        low = col.lower()
        if col in LEAKAGE or any(hint in low for hint in DROP_NAME_HINTS):
            continue
        if sample[col].dtype == object or pd.api.types.is_string_dtype(sample[col].dtype):
            # IP address features are converted to two numeric halves.
            if is_ip_column(col):
                names.extend([f"{col}_high", f"{col}_low"])
            else:
                names.append(col)
                categorical.append(col)
        else:
            names.append(col)
    return names, categorical


def ip_parts(value: object) -> tuple[float, float]:
    if pd.isna(value):
        return -1.0, -1.0
    try:
        number = int(ipaddress.ip_address(str(value).strip()))
        return float(number >> 64), float(number & ((1 << 64) - 1))
    except ValueError:
        return -1.0, -1.0


def transform_chunk(chunk: pd.DataFrame, features: list[str],
                    categorical: list[str]) -> tuple[np.ndarray, np.ndarray]:
    chunk.columns = chunk.columns.str.strip()
    labels = chunk["type"].map(normalize_target)
    unknown = sorted(set(labels.dropna()) - set(CLASS_ORDER))
    if unknown:
        raise ValueError(f"Unexpected target classes: {unknown}")
    mapped = labels.map({name: i for i, name in enumerate(CLASS_ORDER)})
    valid = mapped.notna().to_numpy()
    y = mapped[valid].to_numpy(dtype=np.int64)
    out: dict[str, np.ndarray] = {}
    for col in chunk.columns:
        if col in LEAKAGE or col not in features and col not in categorical:
            continue
        if col in categorical:
            vals = chunk[col].fillna("<missing>").astype(str)
            # Stable bounded hashing avoids a corpus-wide category dictionary.
            hashed = pd.util.hash_pandas_object(vals, index=False).to_numpy(dtype=np.uint64)
            out[col] = (hashed % 16_777_213).astype(np.float32)
        elif is_ip_column(col) and f"{col}_high" in features:
            parts = chunk[col].map(ip_parts)
            out[f"{col}_high"] = np.fromiter((v[0] for v in parts), dtype=np.float32, count=len(chunk))
            out[f"{col}_low"] = np.fromiter((v[1] for v in parts), dtype=np.float32, count=len(chunk))
        elif col in features:
            out[col] = pd.to_numeric(chunk[col], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(-1).to_numpy(dtype=np.float32)
    X = np.column_stack([out.get(col, np.full(len(chunk), -1, dtype=np.float32)) for col in features])
    return np.ascontiguousarray(X[valid], dtype=np.float32), y


def iter_csv(path: Path, features: list[str], categorical: list[str],
             chunksize: int) -> Iterator[tuple[np.ndarray, np.ndarray]]:
    for chunk in pd.read_csv(path, chunksize=chunksize, low_memory=False):
        X, y = transform_chunk(chunk, features, categorical)
        if len(y):
            yield X, y


def main() -> None:
    parser = argparse.ArgumentParser(description="Memory-bounded CUDA MLP training from CSV chunks")
    parser.add_argument("--train-dataset", type=Path, required=True)
    parser.add_argument("--test-dataset", type=Path, required=True)
    parser.add_argument("--chunksize", type=int, default=50_000, help="CSV rows held at once on CPU")
    parser.add_argument("--batch-size", type=int, default=8192, help="Rows copied to GPU per step")
    parser.add_argument("--epochs", type=int, default=5)
    args = parser.parse_args()
    if args.chunksize < 1 or args.batch_size < 1 or args.epochs < 1:
        parser.error("chunksize, batch-size and epochs must be positive")
    for path in (args.train_dataset, args.test_dataset):
        if not path.is_file():
            raise FileNotFoundError(path)

    ensure_project_dirs()
    device = setup_gpu()
    features, categorical = make_feature_schema(args.train_dataset, args.chunksize)
    print(f"Features: {len(features)}; CSV chunk: {args.chunksize:,}; GPU batch: {args.batch_size:,}")
    print("Pass 1/2: fitting streaming feature scaler on training chunks...")
    scaler = StandardScaler()
    train_rows = 0
    for X, _ in iter_csv(args.train_dataset, features, categorical, args.chunksize):
        scaler.partial_fit(X)
        train_rows += len(X)
    if not train_rows:
        raise ValueError("No valid training rows found")

    model = DeepIoTMLP(len(features), len(CLASS_ORDER)).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    loss_fn = torch.nn.CrossEntropyLoss()
    start = time.time()
    for epoch in range(1, args.epochs + 1):
        model.train()
        seen, loss_sum = 0, 0.0
        for X, y in iter_csv(args.train_dataset, features, categorical, args.chunksize):
            X = scaler.transform(X).astype(np.float32, copy=False)
            order = np.random.permutation(len(y))
            for begin in range(0, len(y), args.batch_size):
                idx = order[begin:begin + args.batch_size]
                bx = torch.from_numpy(X[idx]).to(device)
                by = torch.from_numpy(y[idx]).to(device)
                optimizer.zero_grad(set_to_none=True)
                loss = loss_fn(model(bx), by)
                loss.backward()
                optimizer.step()
                loss_sum += loss.item() * len(idx)
                seen += len(idx)
        print(f"Epoch {epoch}/{args.epochs}: loss={loss_sum / max(seen, 1):.5f}; rows={seen:,}")

    print("Evaluating held-out test CSV in chunks...")
    model.eval()
    true_chunks, pred_chunks, score_chunks = [], [], []
    with torch.no_grad():
        for X, y in iter_csv(args.test_dataset, features, categorical, args.chunksize):
            X = scaler.transform(X).astype(np.float32, copy=False)
            for begin in range(0, len(y), args.batch_size):
                bx = torch.from_numpy(X[begin:begin + args.batch_size]).to(device)
                probs = torch.softmax(model(bx), dim=1).cpu().numpy()
                score_chunks.append(probs)
                pred_chunks.append(probs.argmax(axis=1))
                true_chunks.append(y[begin:begin + args.batch_size])
    yt, yp = np.concatenate(true_chunks), np.concatenate(pred_chunks)
    scores = np.concatenate(score_chunks)
    metrics = {
        "accuracy": float(accuracy_score(yt, yp)),
        "precision_macro": float(precision_score(yt, yp, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(yt, yp, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(yt, yp, average="macro", zero_division=0)),
        "mcc": float(matthews_corrcoef(yt, yp)),
        "roc_auc_ovr_macro": float(roc_auc_score(yt, scores, multi_class="ovr", average="macro")),
    }
    report = {
        "approach": "out-of-core chunked CSV + CUDA mini-batch MLP",
        "model": "DeepIoTMLP",
        "train_rows": train_rows,
        "test_rows": int(len(yt)),
        "feature_count": len(features),
        "chunksize": args.chunksize,
        "batch_size": args.batch_size,
        "epochs": args.epochs,
        "classes": CLASS_ORDER,
        "metrics": metrics,
        "confusion_matrix": confusion_matrix(yt, yp, labels=range(len(CLASS_ORDER))).tolist(),
        "classification_report": classification_report(yt, yp, labels=range(len(CLASS_ORDER)), target_names=CLASS_ORDER, output_dict=True, zero_division=0),
        "training_seconds": time.time() - start,
        "duplicates_removed": "No global deduplication; would require external disk-backed deduplication.",
    }
    torch.save({"state_dict": model.cpu().state_dict(), "input_dim": len(features), "classes": CLASS_ORDER}, MODELS_DIR / "gpu_deep_mlp_streaming.pt")
    joblib.dump({"scaler": scaler, "features": features, "categorical_hash_features": categorical}, MODELS_DIR / "gpu_deep_mlp_streaming_preprocessing.joblib")
    (REPORTS_DIR / "gpu_streaming_metrics.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(metrics, indent=2))
    print(f"Saved model and preprocessing metadata to {MODELS_DIR}; metrics to {REPORTS_DIR}")


if __name__ == "__main__":
    main()

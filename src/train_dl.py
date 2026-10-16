from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn
from sklearn.utils.class_weight import compute_class_weight
from torch.utils.data import DataLoader, TensorDataset
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from config import FIGURES_DIR, MODELS_DIR, RANDOM_STATE
from src.data_loader import (
    load_dataset,
    load_train_test_datasets,
    print_dataset_summary,
    sample_dataframe,
)
from src.evaluate import (
    plot_class_distribution,
    plot_correlation_heatmap,
    save_evaluation_outputs,
)
from src.preprocessing import (
    fit_transform_features,
    prepare_split_datasets,
    prepare_train_test_data,
    transform_features,
)
from src.utils import ensure_project_dirs, print_section, set_random_seed


class MLP(nn.Module):
    def __init__(self, input_dim: int, hidden_layers: list[int], output_dim: int):
        super().__init__()
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
        self.network = nn.Sequential(*layers)

    def forward(self, X: torch.Tensor) -> torch.Tensor:
        return self.network(X)


def parse_hidden_layers(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def make_data_loader(
    X: np.ndarray,
    y: np.ndarray,
    batch_size: int,
    shuffle: bool,
    pin_memory: bool = False,
) -> DataLoader:
    dataset = TensorDataset(
        torch.tensor(X, dtype=torch.float32),
        torch.tensor(y, dtype=torch.long),
    )
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, pin_memory=pin_memory)


def predict_probabilities(
    model: MLP,
    X: np.ndarray,
    device: torch.device,
    batch_size: int,
) -> np.ndarray:
    model.eval()
    probabilities = []

    with torch.no_grad():
        for start in range(0, len(X), batch_size):
            batch = torch.tensor(
                X[start : start + batch_size],
                dtype=torch.float32,
                device=device,
            )
            logits = model(batch)
            probabilities.append(torch.softmax(logits, dim=1).cpu().numpy())

    return np.vstack(probabilities)


def train_one_epoch(
    model: MLP,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
) -> float:
    model.train()
    total_loss = 0.0

    for X_batch, y_batch in tqdm(loader, desc="Training", leave=False):
        X_batch = X_batch.to(device)
        y_batch = y_batch.to(device)

        optimizer.zero_grad()
        logits = model(X_batch)
        loss = criterion(logits, y_batch)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * len(X_batch)

    return total_loss / len(loader.dataset)


def train_dl(args: argparse.Namespace) -> None:
    ensure_project_dirs()
    set_random_seed(RANDOM_STATE)

    if getattr(args, "train_dataset", None) and getattr(args, "test_dataset", None):
        print_section("Loading Dedicated Train & Test Datasets")
        train_df, test_df = load_train_test_datasets(
            train_path=args.train_dataset,
            test_path=args.test_dataset,
            train_sample_size=args.sample_size,
            test_sample_size=int(args.sample_size * 0.25) if args.sample_size else None,
            random_state=RANDOM_STATE,
        )
        print_dataset_summary(train_df)
        prepared = prepare_split_datasets(train_df, test_df, task=args.task)
        df_for_plotting = train_df
    else:
        print_section("Loading Dataset")
        df = sample_dataframe(load_dataset(), args.sample_size, RANDOM_STATE)
        print_dataset_summary(df)
        prepared = prepare_train_test_data(df, task=args.task, test_size=args.test_size)
        df_for_plotting = df

    target_col = prepared["target_col"]
    class_names = prepared["class_names"]

    print_section("Class Distribution")
    print(df_for_plotting[target_col].astype(str).value_counts())
    plot_class_distribution(
        df_for_plotting,
        target_col,
        FIGURES_DIR / f"{args.task}_class_distribution.png",
    )
    plot_correlation_heatmap(df_for_plotting, FIGURES_DIR / f"{args.task}_correlation_heatmap.png")

    print_section("Preprocessing")
    print("Dropped columns:")
    for column in prepared["dropped_columns"]:
        print(f"- {column}")

    X_train = fit_transform_features(prepared["preprocessor"], prepared["X_train_raw"])
    X_test = transform_features(prepared["preprocessor"], prepared["X_test_raw"])
    y_train = prepared["y_train"]
    y_test = prepared["y_test"]

    device_choice = getattr(args, "device", "auto")
    if device_choice == "cpu":
        device = torch.device("cpu")
    elif device_choice == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA was explicitly requested via --device cuda, but CUDA is not available.")
        device = torch.device("cuda")
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if device.type == "cuda":
        gpu_name = torch.cuda.get_device_name(0)
        gpu_mem = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        cap = torch.cuda.get_device_capability(0)
        print(f"CUDA acceleration enabled: {gpu_name} ({gpu_mem:.2f} GB VRAM, Compute Capability {cap[0]}.{cap[1]})")
        # Enable TF32 for Ampere (RTX 3060) and Blackwell (RTX 5070 Ti)
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
    else:
        print("Using CPU device.")

    hidden_layers = parse_hidden_layers(args.hidden_layers)
    model = MLP(
        input_dim=X_train.shape[1],
        hidden_layers=hidden_layers,
        output_dim=len(class_names),
    ).to(device)

    class_weights = compute_class_weight(
        class_weight="balanced",
        classes=np.unique(y_train),
        y=y_train,
    )
    class_weights_tensor = torch.tensor(
        class_weights,
        dtype=torch.float32,
        device=device,
    )

    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=1e-4)

    train_loader = make_data_loader(
        X_train,
        y_train,
        args.batch_size,
        shuffle=True,
        pin_memory=(device.type == "cuda"),
    )

    print_section("Training MLP")
    for epoch in range(1, args.epochs + 1):
        loss = train_one_epoch(model, train_loader, criterion, optimizer, device)
        print(f"Epoch {epoch:03d}/{args.epochs} - loss: {loss:.5f}")

    y_score = predict_probabilities(model, X_test, device, args.batch_size)
    y_pred = y_score.argmax(axis=1)

    metrics = save_evaluation_outputs(
        y_test,
        y_pred,
        y_score,
        class_names,
        args.task,
        "mlp",
    )

    model_path = MODELS_DIR / f"{args.task}_mlp.pt"
    torch.save(
        {
            "state_dict": model.cpu().state_dict(),
            "model_name": "mlp",
            "task": args.task,
            "input_dim": X_train.shape[1],
            "hidden_layers": hidden_layers,
            "preprocessor": prepared["preprocessor"],
            "label_encoder": prepared["label_encoder"],
            "class_names": class_names,
            "target_col": target_col,
            "dropped_columns": prepared["dropped_columns"],
            "feature_columns": prepared["feature_columns"],
        },
        model_path,
    )

    print(f"Saved model: {model_path}")
    print("Metrics:")
    for key, value in metrics.items():
        print(f"{key}: {value}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a PyTorch MLP for TON_IoT.")
    parser.add_argument("--task", choices=["binary", "multiclass"], required=True)
    parser.add_argument("--dataset", type=Path, default=None, help="Path to single dataset CSV")
    parser.add_argument("--train-dataset", type=Path, default=None, help="Path to dedicated training CSV")
    parser.add_argument("--test-dataset", type=Path, default=None, help="Path to dedicated testing CSV")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--hidden-layers", default="256,128")
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--sample-size", type=int, default=None)
    parser.add_argument(
        "--device",
        choices=["auto", "cuda", "cpu"],
        default="auto",
        help="Device to use for training (auto, cuda, cpu)",
    )
    args = parser.parse_args()

    train_dl(args)


if __name__ == "__main__":
    main()

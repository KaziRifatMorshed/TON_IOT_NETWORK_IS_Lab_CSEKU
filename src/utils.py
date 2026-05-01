from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from config import FIGURES_DIR, MODELS_DIR, OUTPUTS_DIR, REPORTS_DIR, RANDOM_STATE


def ensure_project_dirs() -> None:
    """Create project output folders if they do not exist."""
    for path in [MODELS_DIR, OUTPUTS_DIR, FIGURES_DIR, REPORTS_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def set_random_seed(seed: int = RANDOM_STATE) -> None:
    random.seed(seed)
    np.random.seed(seed)

    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


def save_json(data: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def save_text(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        file.write(text)


def save_joblib(obj: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(obj, path)


def load_joblib(path: Path) -> Any:
    return joblib.load(path)


def parse_model_list(value: str) -> list[str]:
    if value.lower() == "all":
        return ["logistic", "random_forest", "xgboost"]
    return [item.strip().lower() for item in value.split(",") if item.strip()]


def print_section(title: str) -> None:
    line = "=" * len(title)
    print(f"\n{title}\n{line}")

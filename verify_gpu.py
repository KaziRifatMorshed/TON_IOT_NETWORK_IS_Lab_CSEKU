#!/usr/bin/env python3
"""Cross-platform GPU and Hardware Verification Utility for TON_IoT Intrusion Detection.

Validates GPU acceleration (PyTorch CUDA, XGBoost CUDA, Scikit-learn multi-threading)
on Manjaro Linux, Ubuntu Linux, and Windows for NVIDIA RTX 3060 and RTX 5070 Ti.
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys


def print_header(title: str) -> None:
    sep = "=" * 70
    print(f"\n{sep}\n  {title}\n{sep}")


def check_system_info() -> dict[str, str]:
    print_header("1. System & Environment Information")
    info = {
        "OS": platform.system(),
        "OS Release": platform.release(),
        "Platform": platform.platform(),
        "Python Version": platform.python_version(),
        "Python Executable": sys.executable,
        "In Virtual Environment": str(hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)),
    }
    for k, v in info.items():
        print(f"  {k:<25}: {v}")
    return info


def check_nvidia_smi() -> bool:
    print_header("2. NVIDIA Driver Check (nvidia-smi)")
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            check=True,
        )
        lines = result.stdout.strip().splitlines()
        for idx, line in enumerate(lines):
            parts = [p.strip() for p in line.split(",")]
            gpu_name = parts[0] if len(parts) > 0 else "Unknown"
            driver_ver = parts[1] if len(parts) > 1 else "Unknown"
            mem_total = parts[2] if len(parts) > 2 else "Unknown"
            print(f"  GPU #{idx} Name              : {gpu_name}")
            print(f"  NVIDIA Driver Version    : {driver_ver}")
            print(f"  VRAM Total (nvidia-smi)  : {mem_total}")

            # Specific advice for RTX 50-series (Blackwell) vs RTX 30-series (Ampere)
            if "5070" in gpu_name or "5080" in gpu_name or "5090" in gpu_name:
                print(f"  Architecture Detected    : NVIDIA Blackwell (SM 12.0 / RTX 50-series)")
                try:
                    major_ver = int(driver_ver.split(".")[0])
                    if major_ver < 570:
                        print("  [WARNING] RTX 50-series GPUs require NVIDIA driver >= 570.xx.")
                    else:
                        print("  [OK] NVIDIA driver version supports RTX 50-series Blackwell architecture.")
                except ValueError:
                    pass
            elif "3060" in gpu_name or "30" in gpu_name:
                print(f"  Architecture Detected    : NVIDIA Ampere (SM 8.6 / RTX 30-series)")
                print("  [OK] RTX 30-series Ampere GPU fully supported.")

        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  [WARNING] 'nvidia-smi' command not found or failed.")
        print("            Ensure NVIDIA proprietary drivers are installed on this system.")
        return False


def check_pytorch_cuda() -> bool:
    print_header("3. PyTorch CUDA Acceleration Check")
    try:
        import torch
    except ImportError:
        print("  [FAIL] PyTorch is not installed in this environment.")
        print("         Run setup scripts to install PyTorch with CUDA support.")
        return False

    print(f"  PyTorch Version          : {torch.__version__}")
    print(f"  PyTorch Built with CUDA  : {torch.version.cuda or 'CPU-only'}")
    cuda_ok = torch.cuda.is_available()
    print(f"  torch.cuda.is_available(): {cuda_ok}")

    if not cuda_ok:
        print("  [FAIL] PyTorch cannot access CUDA GPU.")
        print("         If using RTX 5070 Ti, ensure PyTorch with CUDA 12.8+ / Blackwell support is installed.")
        return False

    count = torch.cuda.device_count()
    print(f"  CUDA Devices Found       : {count}")
    for idx in range(count):
        device_name = torch.cuda.get_device_name(idx)
        cap = torch.cuda.get_device_capability(idx)
        vram_gb = torch.cuda.get_device_properties(idx).total_memory / (1024**3)
        print(f"    Device {idx} Name        : {device_name}")
        print(f"    Compute Capability     : {cap[0]}.{cap[1]}")
        print(f"    Total VRAM             : {vram_gb:.2f} GB")

        # TensorFloat-32 Check for Ampere (sm_86) and Blackwell (sm_120)
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        print(f"    TensorFloat-32 (TF32)  : Enabled (accelerates matmul on Ampere/Blackwell)")

        # Run real GPU tensor calculation test
        try:
            x = torch.randn(2048, 2048, device=f"cuda:{idx}", dtype=torch.float32)
            y = torch.matmul(x, x)
            torch.cuda.synchronize(idx)
            print(f"    CUDA Matmul Test (2048x2048): PASSED (result shape {list(y.shape)})")
        except Exception as exc:
            print(f"    [FAIL] CUDA kernel execution failed: {exc}")
            if cap[0] >= 12 or (cap[0] == 10 and cap[1] == 0):
                print("           Note: For RTX 50-series Blackwell GPUs, PyTorch with CUDA 12.8+ (sm_120) is required.")
            return False

    print("  [OK] PyTorch CUDA verification passed.")
    return True


def check_xgboost_gpu() -> bool:
    print_header("4. XGBoost GPU (CUDA) Check")
    try:
        import numpy as np
        import xgboost as xgb
    except ImportError:
        print("  [WARNING] XGBoost or NumPy is not installed.")
        return False

    print(f"  XGBoost Version          : {xgb.__version__}")
    try:
        # Fast dummy train on GPU
        X_dummy = np.random.randn(200, 10).astype(np.float32)
        y_dummy = np.random.randint(0, 2, size=200)

        clf = xgb.XGBClassifier(
            n_estimators=10,
            max_depth=3,
            tree_method="hist",
            device="cuda",
            random_state=42,
        )
        clf.fit(X_dummy, y_dummy)
        preds = clf.predict(X_dummy)
        print("  XGBoost device='cuda' Fit : PASSED (GPU histogram tree building active)")
        print("  [OK] XGBoost GPU verification passed.")
        return True
    except Exception as exc:
        print(f"  [INFO] XGBoost GPU acceleration test failed or not supported by current wheel: {exc}")
        print("         XGBoost will fall back to CPU multi-threading automatically.")
        return False


def check_sklearn_cpu() -> bool:
    print_header("5. Scikit-Learn Random Forest (Multi-Core CPU) Check")
    try:
        import multiprocessing
        import sklearn
        from sklearn.ensemble import RandomForestClassifier
    except ImportError:
        print("  [FAIL] Scikit-learn is not installed.")
        return False

    cpu_cores = multiprocessing.cpu_count()
    print(f"  Scikit-Learn Version     : {sklearn.__version__}")
    print(f"  Available CPU Threads    : {cpu_cores} (utilized via n_jobs=-1)")
    print("  [OK] Scikit-Learn Random Forest is ready for parallel processing.")
    return True


def main() -> int:
    check_system_info()
    has_nvidia = check_nvidia_smi()
    torch_ok = check_pytorch_cuda()
    xgb_ok = check_xgboost_gpu()
    sklearn_ok = check_sklearn_cpu()

    print_header("Verification Summary")
    if torch_ok:
        print("  [SUCCESS] GPU acceleration is fully active and validated for this environment!")
        print("            - Deep Learning (PyTorch MLP): GPU Accelerated")
        if xgb_ok:
            print("            - Classical ML (XGBoost): GPU Accelerated (device='cuda')")
        print("            - Random Forest: Multi-threaded CPU (n_jobs=-1)")
        print("\n  You can now run any workflow:")
        print("    python -m src.random_forest_workflow")
        print("    python -m src.train_dl --task binary --device cuda")
        print("    python -m src.train_ml --task binary --models xgboost --device cuda")
        return 0
    else:
        print("  [NOTICE] GPU acceleration was not confirmed. Please see troubleshooting in README.md.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

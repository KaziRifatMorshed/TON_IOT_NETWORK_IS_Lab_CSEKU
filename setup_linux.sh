#!/usr/bin/env bash
# ==============================================================================
# Linux Setup Script for TON IoT Intrusion Detection
# Tested on:
#   - Manjaro Linux (Kernel 6.x+, RTX 3060 12GB)
#   - Ubuntu Linux 22.04 / 24.04 LTS (RTX 5070 Ti 16GB)
# ==============================================================================

set -e

echo "========================================================================"
echo "  TON IoT Network IDS: Linux Environment Setup"
echo "  Target GPUs: NVIDIA RTX 3060 (12GB) / RTX 5070 Ti (16GB)"
echo "========================================================================"

# 1. Check Python
PYTHON_BIN=""
for cmd in python3.13 python3.12 python3.11 python3.10 python3 python; do
    if command -v "$cmd" &>/dev/null; then
        VERSION=$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        MAJOR=$("$cmd" -c 'import sys; print(sys.version_info.major)')
        MINOR=$("$cmd" -c 'import sys; print(sys.version_info.minor)')
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 10 ]; then
            PYTHON_BIN="$cmd"
            echo "[OK] Found compatible Python: $PYTHON_BIN (Python $VERSION)"
            break
        fi
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo "[ERROR] No Python >= 3.10 found on this system."
    echo "Please install Python 3.10 or newer (e.g., sudo pacman -S python on Manjaro, or sudo apt install python3 python3-venv on Ubuntu)."
    exit 1
fi

# 2. Check NVIDIA GPU & Architecture
DETECTED_GPU="none"
if command -v nvidia-smi &>/dev/null; then
    GPU_INFO=$(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader | head -n 1)
    echo "[OK] Detected GPU: $GPU_INFO"
    if echo "$GPU_INFO" | grep -iqE "5070|5080|5090"; then
        DETECTED_GPU="blackwell"
        echo "[INFO] RTX 50-series (Blackwell) GPU detected! Installing PyTorch with CUDA 12.8+ support."
    elif echo "$GPU_INFO" | grep -iqE "3060|3070|3080|3090"; then
        DETECTED_GPU="ampere"
        echo "[INFO] RTX 30-series (Ampere) GPU detected! Fully supported with CUDA."
    fi
else
    echo "[WARNING] nvidia-smi not detected. Proceeding with standard setup."
fi

# 3. Create or reuse Virtual Environment (.venv)
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] Creating virtual environment in $VENV_DIR..."
    "$PYTHON_BIN" -m venv "$VENV_DIR" || "$PYTHON_BIN" -m venv --without-pip "$VENV_DIR"
fi

# Determine venv python path
VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

# Ensure pip is up to date
"$VENV_PYTHON" -m ensurepip --upgrade 2>/dev/null || true
"$VENV_PYTHON" -m pip install --upgrade "pip<26" setuptools wheel

# 4. Install PyTorch with CUDA acceleration
echo "[INFO] Installing PyTorch with CUDA acceleration..."
# Using --extra-index-url ensures sm_120 Blackwell (RTX 5070 Ti) and sm_86 Ampere (RTX 3060) both get CUDA wheels
if [ "$DETECTED_GPU" = "blackwell" ]; then
    "$VENV_PYTHON" -m pip install "torch>=2.4.0" --extra-index-url https://download.pytorch.org/whl/cu128 || \
    "$VENV_PYTHON" -m pip install "torch>=2.4.0" --extra-index-url https://download.pytorch.org/whl/cu126 || \
    "$VENV_PYTHON" -m pip install torch
else
    "$VENV_PYTHON" -m pip install torch || \
    "$VENV_PYTHON" -m pip install "torch>=2.1.0" --extra-index-url https://download.pytorch.org/whl/cu126
fi

# 5. Install all other project requirements
echo "[INFO] Installing project dependencies from requirements.txt..."
"$VENV_PYTHON" -m pip install -r requirements.txt

# 6. Verify Hardware & GPU Acceleration
echo ""
echo "========================================================================"
echo "  Running Verification Utility..."
echo "========================================================================"
"$VENV_PYTHON" verify_gpu.py

echo ""
echo "========================================================================"
echo "  Setup Complete!"
echo "  To activate your environment in terminal:"
echo "    source .venv/bin/activate"
echo "  To run training:"
echo "    .venv/bin/python -m src.random_forest_workflow"
echo "    .venv/bin/python -m src.train_dl --task binary --device cuda"
echo "    .venv/bin/python -m src.train_ml --task binary --models xgboost --device cuda"
echo "========================================================================"

# ==============================================================================
# Windows PowerShell Setup Script for TON IoT Intrusion Detection
# Target GPU: NVIDIA RTX 5070 Ti (16GB Blackwell) / RTX 3060 (12GB Ampere)
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  TON IoT Network IDS: Windows PowerShell Environment Setup" -ForegroundColor Cyan
Write-Host "  Target GPUs: NVIDIA RTX 5070 Ti (16GB) / RTX 3060 (12GB)" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan

# 1. Create virtual environment
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "[INFO] Creating virtual environment in .venv..." -ForegroundColor Yellow
    python -m venv .venv
}

$venvPython = ".venv\Scripts\python.exe"

# 2. Update pip
Write-Host "[INFO] Updating pip and core build tools..." -ForegroundColor Yellow
& $venvPython -m ensurepip --upgrade
& $venvPython -m pip install --upgrade "pip<26" setuptools wheel

# 3. Install PyTorch with CUDA acceleration (CUDA 12.8 / 12.6)
Write-Host "[INFO] Installing PyTorch with CUDA acceleration for RTX GPUs..." -ForegroundColor Yellow
try {
    & $venvPython -m pip install "torch>=2.4.0" --extra-index-url https://download.pytorch.org/whl/cu128
} catch {
    Write-Host "[WARNING] cu128 wheel install failed, attempting cu126 fallback..." -ForegroundColor Yellow
    & $venvPython -m pip install "torch>=2.4.0" --extra-index-url https://download.pytorch.org/whl/cu126
}

# 4. Install requirements
Write-Host "[INFO] Installing dependencies from requirements.txt..." -ForegroundColor Yellow
& $venvPython -m pip install -r requirements.txt

# 5. Run GPU verification utility
Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  Running Verification Utility..." -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
& $venvPython verify_gpu.py

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Green
Write-Host "  Setup complete." -ForegroundColor Green
Write-Host "  To run training in PowerShell:" -ForegroundColor White
Write-Host "    .\.venv\Scripts\python.exe -m src.random_forest_workflow" -ForegroundColor White
Write-Host "    .\.venv\Scripts\python.exe -m src.train_dl --task binary --device cuda" -ForegroundColor White
Write-Host "    .\.venv\Scripts\python.exe -m src.train_ml --task binary --models xgboost --device cuda" -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Green

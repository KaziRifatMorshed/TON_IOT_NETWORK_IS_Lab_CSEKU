@echo off
setlocal enabledelayedexpansion

REM ==============================================================================
REM Windows CMD Setup Script for TON IoT Intrusion Detection
REM Target GPU: NVIDIA RTX 5070 Ti (16GB Blackwell) / RTX 3060 (12GB Ampere)
REM ==============================================================================

echo ========================================================================
echo   TON IoT Network IDS: Windows CMD Environment Setup
echo   Target GPUs: NVIDIA RTX 5070 Ti (16GB) / RTX 3060 (12GB)
echo ========================================================================

REM 1. Create virtual environment if it does not exist
if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Creating virtual environment in .venv...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment. Ensure Python 3.10+ is installed and on PATH.
        exit /b 1
    )
)

REM 2. Ensure pip and tools are up to date
echo [INFO] Updating pip and core build tools...
".venv\Scripts\python.exe" -m ensurepip --upgrade >nul 2>&1
".venv\Scripts\python.exe" -m pip install --upgrade "pip<26" setuptools wheel
if errorlevel 1 exit /b 1

REM 3. Install PyTorch with CUDA acceleration (CUDA 12.8+ for RTX 5070 Ti Blackwell and RTX 3060)
echo [INFO] Installing PyTorch with CUDA acceleration for NVIDIA RTX GPUs...
".venv\Scripts\python.exe" -m pip install "torch>=2.4.0" --extra-index-url https://download.pytorch.org/whl/cu128
if errorlevel 1 (
    echo [WARNING] cu128 wheel download failed, attempting cu126 fallback...
    ".venv\Scripts\python.exe" -m pip install "torch>=2.4.0" --extra-index-url https://download.pytorch.org/whl/cu126
)

REM 4. Install remaining project requirements
echo [INFO] Installing project dependencies from requirements.txt...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

REM 5. Run GPU verification utility
echo.
echo ========================================================================
echo   Running Verification Utility...
echo ========================================================================
".venv\Scripts\python.exe" verify_gpu.py

echo.
echo ========================================================================
echo   Setup complete.
echo   To run training in Windows CMD:
echo     .venv\Scripts\python.exe -m src.random_forest_workflow
echo     .venv\Scripts\python.exe -m src.train_dl --task binary --device cuda
echo     .venv\Scripts\python.exe -m src.train_ml --task binary --models xgboost --device cuda
echo ========================================================================

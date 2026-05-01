@echo off
setlocal

REM Create and install the project environment from Windows CMD.
REM This script intentionally uses ".venv\Scripts\python.exe -m pip"
REM instead of plain "pip" so broken global pip launchers are ignored.

if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
    if errorlevel 1 exit /b 1
)

".venv\Scripts\python.exe" -m ensurepip --upgrade
if errorlevel 1 exit /b 1

".venv\Scripts\python.exe" -m pip install --upgrade "pip<26"
if errorlevel 1 exit /b 1

".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

echo.
echo Setup complete.
echo Run training with:
echo .venv\Scripts\python.exe -m src.train_ml --task binary


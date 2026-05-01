$ErrorActionPreference = "Stop"

# Create and install the project environment from Windows PowerShell.
# This script intentionally uses ".venv\Scripts\python.exe -m pip"
# instead of plain "pip" so broken global pip launchers are ignored.

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
}

.\.venv\Scripts\python.exe -m ensurepip --upgrade
.\.venv\Scripts\python.exe -m pip install --upgrade "pip<26"
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host ""
Write-Host "Setup complete."
Write-Host "Run training with:"
Write-Host ".\.venv\Scripts\python.exe -m src.train_ml --task binary"


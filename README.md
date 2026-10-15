# TON IoT Network Intrusion Detection
### Information Security Lab (Lab #7) — Khulna University (CSEKU)
**Instructor**: Dr. Anupam Kumar Bairagi  
**Presenters**: Md Siam Ahmed (230202) & Kazi Rifat Morshed (230220)  

🌐 **[Live Presentation Slides (GitHub Pages)](https://kazirifatmorshed.github.io/TON_IOT_NETWORK_IS_Lab_CSEKU/)** | 📘 **[Comprehensive Lab #7 Guide & Viva Q&A](LAB7_INSTRUCTIONS_AND_PRESENTATION_GUIDE.md)**

---

Random Forest based intrusion detection workflow for the TON_IoT network dataset, with full 100% pure GPU acceleration for Deep Learning (PyTorch MLP), Classical ML (XGBoost CUDA), and ensemble learning.

The primary workflow classifies network traffic into:

- `normal` (Benign IoT telemetry)
- `dos` (Denial of Service single-source flood)
- `ddos` (Distributed Denial of Service botnet flood)

It loads `data/dataset.csv`, preprocesses network features, eliminates target leakage (`label`), trains classifiers, evaluates performance, and outputs high-resolution figures and reports.

---

## Interactive Presentation (Live & Offline)

- **🌐 Live on GitHub Pages**: [https://kazirifatmorshed.github.io/TON_IOT_NETWORK_IS_Lab_CSEKU/](https://kazirifatmorshed.github.io/TON_IOT_NETWORK_IS_Lab_CSEKU/)
- **📁 Standalone Offline Presentation**: Open `docs/index.html` directly in any web browser (all animations and transitions are embedded Base64 Data URIs; no internet or backend server required).
- **Interactive Fullscreen Mode**:
  ```bash
  conda activate manim_env
  ./presentation/render_presentation.sh present
  ```
- **Re-render / Export Slides**:
  ```bash
  ./presentation/render_presentation.sh html     # Quick export
  ./presentation/render_presentation.sh full-hd  # 1080p60 Full-HD export
  ```

---

## Supported Hardware & Tested Platforms

This repository is optimized and tested for:

1. **Manjaro Linux (Arch-based)**
   - **GPU**: NVIDIA GeForce RTX 3060 12 GB (Ampere, Compute Capability 8.6)
   - **Driver / CUDA**: NVIDIA Driver 550+ / 610+ (CUDA 12.x / 13.x)
   - **Python**: 3.10 – 3.13+

2. **Project Mate PC – Dual Boot (Ubuntu Linux & Windows)**
   - **GPU**: NVIDIA GeForce RTX 5070 Ti 16 GB (Blackwell, Compute Capability 12.0)
   - **Driver / CUDA**: NVIDIA Driver >= 570.xx (CUDA >= 12.8 required for Blackwell SM 12.0)
   - **Ubuntu**: 22.04 / 24.04 LTS
   - **Windows**: Windows 10 / 11 (CMD & PowerShell)

---

## Project Structure

```text
.
|-- README.md
|-- LAB7_INSTRUCTIONS_AND_PRESENTATION_GUIDE.md # Complete lab explanation & viva blueprint
|-- requirements.txt
|-- setup_linux.sh               # Automated setup for Manjaro & Ubuntu
|-- setup_windows_cmd.bat        # Automated setup for Windows CMD
|-- setup_windows_powershell.ps1 # Automated setup for Windows PowerShell
|-- verify_gpu.py                # Hardware & GPU validation tool
|-- config.py
|-- .github/workflows/
|   `-- pages.yml                # Automatic deployment to GitHub Pages
|-- docs/
|   |-- .nojekyll
|   `-- index.html               # 1.2MB Standalone Reveal.js slide deck
|-- presentation/
|   |-- presentation_slides.py   # Manim Slides animated source code
|   |-- render_presentation.sh   # Render & preview helper script
|   `-- *.png / *.pdf            # University logos and graphics
|-- data/
|   |-- .gitkeep
|   `-- dataset.csv              # local dataset
|-- Dataset Details/
|   `-- Ton_IoT Network Dataset.pdf
|-- src/
|   |-- data_loader.py
|   |-- preprocessing.py
|   |-- random_forest_workflow.py # primary workflow (GPU & CPU)
|   |-- train_gpu.py             # 100% Pure GPU unified pipeline
|   |-- train_ml.py              # ML experiments (with XGBoost GPU)
|   |-- train_dl.py              # PyTorch MLP (with CUDA GPU)
|   |-- evaluate.py
|   `-- utils.py
|-- tests/
|   `-- test_random_forest_workflow.py
|-- models/
`-- outputs/
    |-- figures/
    `-- reports/
```

---

## Dataset

Expected dataset path:

```text
data/dataset.csv
```

The CSV must contain the TON_IoT network records and a `type` column with the three classes used by this workflow: `normal`, `dos`, and `ddos`.

If `data/dataset.csv` is missing, `src/data_loader.py` can also combine local root-level class files named:

- `DDOS.csv`
- `DOS.csv`
- `Normal.csv`

---

## Installation & Setup

### 1. Linux Setup (Manjaro & Ubuntu)

Make the script executable and run:

```bash
chmod +x setup_linux.sh
./setup_linux.sh
```

#### Manual Linux Setup:

```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Upgrade pip
pip install --upgrade "pip<26" setuptools wheel

# 3. Install PyTorch with CUDA acceleration
# For RTX 3060 (Ampere) or RTX 5070 Ti (Blackwell):
pip install "torch>=2.4.0" --extra-index-url https://download.pytorch.org/whl/cu128

# 4. Install project requirements
pip install -r requirements.txt

# 5. Verify GPU installation
python verify_gpu.py
```

> **Ubuntu / RTX 5070 Ti Driver Note**: Ensure your Ubuntu has NVIDIA driver >= 570 installed (`sudo apt install nvidia-driver-570` or higher). Verify with `nvidia-smi`.

---

### 2. Windows Setup (Dual Boot PC)

#### Option A: Windows CMD
Run Command Prompt **in the project directory**:

```cmd
setup_windows_cmd.bat
```

#### Option B: Windows PowerShell
Run PowerShell **in the project directory**:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\setup_windows_powershell.ps1
```

#### Manual Windows Setup:

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install --upgrade "pip<26" setuptools wheel
pip install "torch>=2.4.0" --extra-index-url https://download.pytorch.org/whl/cu128
pip install -r requirements.txt
python verify_gpu.py
```

---

## Hardware & GPU Verification

Run the built-in diagnostic utility to verify Python, NVIDIA drivers, CUDA PyTorch acceleration (including TF32 on Ampere & Blackwell), XGBoost GPU tree building, and multi-threaded CPU support:

On Linux:
```bash
.venv/bin/python verify_gpu.py
```

On Windows:
```cmd
.venv\Scripts\python.exe verify_gpu.py
```

Expected output:
```text
======================================================================
  Verification Summary
======================================================================
  [SUCCESS] GPU acceleration is fully active and validated for this environment!
            - Deep Learning (PyTorch MLP): GPU Accelerated
            - Classical ML (XGBoost): GPU Accelerated (device='cuda')
            - Random Forest: Multi-threaded CPU (n_jobs=-1)
```

---

## Running the Workflows

### 1. 100% Pure GPU Unified Pipeline (Recommended)

Trains and evaluates **GPU Random Forest**, **GPU XGBoost**, and **PyTorch Deep MLP** entirely on your NVIDIA CUDA GPU (RTX 3060 / RTX 5070 Ti) with zero CPU model training:

- Linux:
  ```bash
  # Fast run (50,000 samples, ~3 seconds):
  .venv/bin/python -m src.train_gpu --sample-size 50000 --epochs 10

  # Full 300,000 dataset run:
  .venv/bin/python -m src.train_gpu --epochs 15
  ```
- Windows:
  ```cmd
  REM Fast run (50,000 samples):
  .venv\Scripts\python.exe -m src.train_gpu --sample-size 50000 --epochs 10

  REM Full 300,000 dataset run:
  .venv\Scripts\python.exe -m src.train_gpu --epochs 15
  ```

---

### 2. Primary Random Forest Workflow (with GPU Support)

Full run on NVIDIA GPU:

- Linux:
  ```bash
  .venv/bin/python -m src.random_forest_workflow --device cuda
  ```
- Windows:
  ```cmd
  .venv\Scripts\python.exe -m src.random_forest_workflow --device cuda
  ```

Fast smoke test (sample size 3,000):

- Linux:
  ```bash
  .venv/bin/python -m src.random_forest_workflow --sample-size 3000 --n-estimators 20 --n-jobs -1
  ```
- Windows:
  ```cmd
  .venv\Scripts\python.exe -m src.random_forest_workflow --sample-size 3000 --n-estimators 20 --n-jobs -1
  ```

---

### 2. Deep Learning (PyTorch MLP with GPU Acceleration)

Train deep learning MLP on the RTX 3060 (12GB) or RTX 5070 Ti (16GB):

- Linux:
  ```bash
  .venv/bin/python -m src.train_dl --task binary --device cuda --epochs 20 --batch-size 512
  .venv/bin/python -m src.train_dl --task multiclass --device cuda --epochs 20 --batch-size 512
  ```
- Windows:
  ```cmd
  .venv\Scripts\python.exe -m src.train_dl --task binary --device cuda --epochs 20 --batch-size 512
  .venv\Scripts\python.exe -m src.train_dl --task multiclass --device cuda --epochs 20 --batch-size 512
  ```

---

### 3. Classical ML Experiments (with XGBoost GPU Acceleration)

Train classical ML models (XGBoost on GPU, Random Forest on multi-core CPU):

- Linux:
  ```bash
  .venv/bin/python -m src.train_ml --task binary --models xgboost --device cuda
  .venv/bin/python -m src.train_ml --task multiclass --models xgboost --device cuda
  ```
- Windows:
  ```cmd
  .venv\Scripts\python.exe -m src.train_ml --task binary --models xgboost --device cuda
  .venv\Scripts\python.exe -m src.train_ml --task multiclass --models xgboost --device cuda
  ```

---

## Running Unit Tests

Run the test suite to verify preprocessing, parameter defaults, and metric generation:

- Linux:
  ```bash
  .venv/bin/python -m unittest discover -s tests
  ```
- Windows:
  ```cmd
  .venv\Scripts\python.exe -m unittest discover -s tests
  ```

---

## Workflow Outputs

Generated files are ignored by git:

- **Trained Models**:
  - `models/rf_network_classifier.joblib`
  - `models/binary_mlp.pt` / `models/multiclass_mlp.pt`
  - `models/binary_xgboost.joblib`
- **Reports**:
  - `outputs/reports/rf_workflow_classification_report.txt`
  - `outputs/reports/rf_workflow_summary.json`
  - `outputs/reports/rf_workflow_run_config.json`
  - `outputs/reports/rf_workflow_feature_importance.csv`
- **Figures**:
  - `outputs/figures/rf_workflow_binary_class_distribution.png`
  - `outputs/figures/rf_workflow_multiclass_distribution.png`
  - `outputs/figures/rf_workflow_confusion_matrix.png`
  - `outputs/figures/rf_workflow_feature_importance.png`
  - `outputs/figures/rf_workflow_roc_curves.png`

---

## Troubleshooting & FAQ

### RTX 5070 Ti (Blackwell) compatibility
- **Symptom**: `CUDA error: no kernel image is available for execution on the device`
- **Cause**: Older PyTorch wheels (compiled for CUDA 11.x or 12.1/12.4) lack SM 12.0 (Blackwell) machine code.
- **Fix**: Reinstall PyTorch using CUDA 12.8:
  ```bash
  pip install --force-reinstall "torch>=2.4.0" --extra-index-url https://download.pytorch.org/whl/cu128
  ```
- **Driver**: Ensure the host NVIDIA driver is >= 570.xx (check with `nvidia-smi`).

### Manjaro / Wayland Qt Platform Plugin Warning
- The codebase automatically sets `matplotlib.use("Agg")` to ensure headless rendering without attempting to load Qt/Wayland display plugins.

### Out of Memory or Slow Training
- For Random Forest, use `--sample-size 50000` or specify `--n-jobs -1` to utilize all CPU cores.
- For PyTorch MLP, adjust `--batch-size 1024` or `2048` to take full advantage of 12GB (RTX 3060) or 16GB (RTX 5070 Ti) VRAM.

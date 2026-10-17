# Lab #7: TON_IoT Network Intrusion Detection
## Comprehensive Project Guide & Presentation Blueprint
**Course**: Information Security Lab (CSEKU)  
**Instructor**: Dr. Anupam Kumar Bairagi  
**Assignment**: *Classify DoS / DDoS / Normal traffic & prepare a presentation based on your work.*

---

## Table of Contents
1. [TL;DR — The Assignment in 60 Seconds](#1-tldr--the-assignment-in-60-seconds)
2. [Complete Workflow At-A-Glance (End-to-End Flowchart)](#2-complete-workflow-at-a-glance-end-to-end-flowchart)
3. [What Exactly Will You Produce? (Every Output, Explained)](#3-what-exactly-will-you-produce-every-output-explained)
4. [Understanding the Problem & Dataset](#4-understanding-the-problem--dataset)
5. [Step-by-Step Technical Execution](#5-step-by-step-technical-execution)
6. [What You Show in the Presentation (Output → Slide Mapping)](#6-what-you-show-in-the-presentation-output--slide-mapping)
7. [Slide-by-Slide Presentation Blueprint (12 Slides)](#7-slide-by-slide-presentation-blueprint-12-slides)
8. [Presentation Script & Speaking Notes](#8-presentation-script--speaking-notes)
9. [Expected Viva / Defense Questions by Dr. Anupam Kumar Bairagi](#9-expected-viva--defense-questions-by-dr-anupam-kumar-bairagi)
10. [Commands Cheatsheet](#10-commands-cheatsheet)
11. [Interactive Presentation Slides & GitHub Pages Deployment](#11-interactive-presentation-slides--github-pages-deployment)

---

## 1. TL;DR — The Assignment in 60 Seconds

> [!IMPORTANT]
> **Your teacher asked you to do TWO things:**
> 1. **Build a classifier** — Take the TON_IoT network dataset → clean it → train ML/DL models → classify traffic as `Normal`, `DoS`, or `DDoS`.
> 2. **Present your work** — Make a presentation showing your data pipeline, model choices, results (accuracy, confusion matrix, ROC curves, feature importance), and conclusions.

**What you physically deliver:**
- ✅ **Working code** in this repository (already done — the `src/` scripts).
- ✅ **Trained model files** saved in `models/` (already generated).
- ✅ **Result figures & reports** in `outputs/` (already generated).
- ✅ **A presentation** (PowerPoint / Google Slides / the interactive HTML slides in `docs/`).
- ✅ **A live demo or screenshot walkthrough** showing the scripts actually ran and produced results.

---

## 2. Complete Workflow At-A-Glance (End-to-End Flowchart)

This is everything you do, from start to finish, in order:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    COMPLETE ASSIGNMENT WORKFLOW                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  PHASE 1: SETUP                                                         │
│  ─────────────────                                                      │
│  ① Clone the repository                                                │
│  ② Run setup_linux.sh (installs Python venv + dependencies)            │
│  ③ Run verify_gpu.py (confirms NVIDIA GPU + CUDA is working)           │
│  ④ Place dataset.csv in data/ (already present)                        │
│                                                                         │
│                          ▼                                              │
│                                                                         │
│  PHASE 2: RUN THE TRAINING PIPELINE                                    │
│  ──────────────────────────────────────                                 │
│  ⑤ Run the GPU training pipeline:                                      │
│     .venv/bin/python -m src.train_gpu --epochs 15                      │
│                                                                         │
│     This single command does ALL of the following automatically:        │
│     ┌─────────────────────────────────────────────────────────┐         │
│     │ a) Loads data/dataset.csv (300,000 rows × 46 columns)  │         │
│     │ b) Removes 50,267 duplicate rows                       │         │
│     │ c) Drops 'label' column (prevents data leakage)        │         │
│     │ d) Converts IP addresses → 64-bit numerical integers   │         │
│     │ e) Encodes categorical columns (protocol, conn_state)  │         │
│     │ f) Replaces missing values with -1                     │         │
│     │ g) Removes zero-variance columns                       │         │
│     │ h) Splits data: 80% train / 20% test (stratified)     │         │
│     │ i) Trains GPU Random Forest (200 trees on CUDA)        │         │
│     │ j) Trains GPU XGBoost (gradient boosted trees on CUDA) │         │
│     │ k) Trains PyTorch Deep MLP (neural network on CUDA)    │         │
│     │ l) Evaluates all 3 models on the test set              │         │
│     └─────────────────────────────────────────────────────────┘         │
│                                                                         │
│  ⑥ (Optional) Run the standalone Random Forest workflow:               │
│     .venv/bin/python -m src.random_forest_workflow --device cuda        │
│     → Produces additional ROC curves & feature importance chart         │
│                                                                         │
│                          ▼                                              │
│                                                                         │
│  PHASE 3: COLLECT YOUR OUTPUTS                                          │
│  ────────────────────────────                                           │
│  ⑦ Check outputs/figures/  → All charts & plots (PNG images)           │
│  ⑧ Check outputs/reports/  → All numeric results (JSON, CSV, TXT)     │
│  ⑨ Check models/           → All saved trained models                  │
│                                                                         │
│                          ▼                                              │
│                                                                         │
│  PHASE 4: BUILD YOUR PRESENTATION                                       │
│  ────────────────────────────────                                       │
│  ⑩ Copy the output figures into your PowerPoint/Google Slides          │
│  ⑪ Fill in the numbers from the JSON/TXT reports                       │
│  ⑫ Follow the 12-slide blueprint below                                 │
│                                                                         │
│                          ▼                                              │
│                                                                         │
│  PHASE 5: PRESENT & DEFEND                                              │
│  ─────────────────────────                                              │
│  ⑬ Present the slides to Dr. Anupam Kumar Bairagi                     │
│  ⑭ Answer viva questions (prepared answers below)                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. What Exactly Will You Produce? (Every Output, Explained)

Here is an **exhaustive inventory** of every single file your scripts generate. This is what "the outputs of this work" means concretely:

### 📊 A. Figures (Visual Outputs — PNG Images)

These go directly into your presentation slides:

| # | File | What It Shows | Which Slide? |
|:-:|:-----|:--------------|:-------------|
| 1 | `outputs/figures/rf_workflow_multiclass_distribution.png` | Bar chart of the 3-class breakdown: 100K Normal, 100K DoS, 100K DDoS | **Slide 4** |
| 2 | `outputs/figures/rf_workflow_binary_class_distribution.png` | Bar chart of binary split: 200K Attack vs 100K Normal | Slide 4 (optional, supplementary) |
| 3 | `outputs/figures/rf_workflow_confusion_matrix.png` | 3×3 heatmap showing how many Normal/DoS/DDoS samples were correctly vs incorrectly classified | **Slide 8** |
| 4 | `outputs/figures/gpu_rf_confusion_matrix.png` | Same confusion matrix from the GPU pipeline run | Slide 8 (alternative) |
| 5 | `outputs/figures/rf_workflow_roc_curves.png` | ROC curves (True Positive Rate vs False Positive Rate) for all 3 classes + macro/micro averages | **Slide 9** |
| 6 | `outputs/figures/rf_workflow_feature_importance.png` | Horizontal bar chart ranking the top features (conn_state, src_port, ts, etc.) by Gini importance | **Slide 10** |
| 7 | `outputs/figures/pure_gpu_comparison.png` | Side-by-side bar chart comparing GPU Random Forest vs GPU XGBoost vs PyTorch MLP (accuracy, F1, training time) | **Slide 7** |
| 8 | `outputs/figures/binary_correlation_heatmap.png` | Correlation heatmap of all features (used for exploratory data analysis) | Slide 4 (optional deep-dive) |

### 📝 B. Reports (Numeric Outputs — JSON, CSV, TXT)

These provide the exact numbers you cite in your slides and viva:

| # | File | What It Contains | How You Use It |
|:-:|:-----|:-----------------|:---------------|
| 1 | `outputs/reports/rf_workflow_classification_report.txt` | Per-class precision, recall, F1-score, and overall accuracy (sklearn format) | Copy numbers into **Slide 7** results table |
| 2 | `outputs/reports/rf_workflow_summary.json` | Complete JSON with all metrics: accuracy=99.99%, MCC=0.9999, ROC-AUC=1.0, class distributions, run config | Reference for filling any slide |
| 3 | `outputs/reports/rf_workflow_feature_importance.csv` | Ranked list of all 45 features with their Gini importance scores | Reference for **Slide 10** discussion |
| 4 | `outputs/reports/rf_workflow_run_config.json` | Exact experiment configuration: dataset path, train/test split ratio, feature list, dropped columns, duplicate count | Reference for **Slide 5** preprocessing discussion |
| 5 | `outputs/reports/pure_gpu_benchmark_results.json` | Benchmark table: training time, inference latency, accuracy, F1, MCC, ROC-AUC for all 3 GPU models | Copy numbers into **Slide 7** & **Slide 11** |

### 🧠 C. Trained Models (Serialized Model Files)

These prove your models actually trained and can make predictions:

| # | File | What It Is | Size |
|:-:|:-----|:-----------|:-----|
| 1 | `models/rf_network_classifier.joblib` | Primary Random Forest (200 trees), trained on full dataset | ~703 KB |
| 2 | `models/gpu_random_forest.joblib` | GPU-accelerated Random Forest | ~661 KB |
| 3 | `models/gpu_xgboost.joblib` | GPU-accelerated XGBoost (gradient boosted trees) | ~557 KB |
| 4 | `models/gpu_deep_mlp.pt` | PyTorch Deep MLP neural network weights | ~228 KB |

### 🌐 D. Presentation Assets

| # | File | What It Is |
|:-:|:-----|:-----------|
| 1 | `docs/index.html` | Interactive Reveal.js HTML5 presentation (deployable to GitHub Pages) |
| 2 | `presentation/ton_iot_presentation.html` | Manim-rendered presentation with video transitions |
| 3 | `presentation/ton_iot_presentation_assets/*.mp4` | Animated slide transition videos |

### 📋 E. Summary: What Does "The Output" Actually Look Like?

> [!NOTE]
> **When your teacher says "show me what you did", here is exactly what you show:**
>
> 1. **A bar chart** showing the dataset has 3 balanced classes (100K each)
> 2. **A confusion matrix** showing the model correctly classifies nearly every sample
> 3. **ROC curves** proving the model has near-perfect discrimination (AUC = 1.0)
> 4. **A feature importance chart** revealing which network features detect attacks
> 5. **A results table** with numbers: 99.99% accuracy, 99.99% F1-score, 0.9999 MCC
> 6. **A GPU comparison chart** showing all 3 models trained in seconds
> 7. **The terminal output** or JSON reports as evidence the code actually ran

---

## 4. Understanding the Problem & Dataset

### Dataset Specifications

This project accommodates two dataset configurations:

#### Option A: Dedicated 8.2M / 2.0M Pre-Split Datasets (Recommended for Rigorous Evaluation)
- Extracted directly from the full TON_IoT network capture (`dataset_cleaned.csv`):
  - **Total 3-Class Records**: `10,336,716` network flows
  - **Train Set (80%)**: `data/train_normal_dos_ddos.csv` (**8,271,593 rows**, ~1.2 GB)
  - **Test Set (20%)**: `data/test_normal_dos_ddos.csv` (**2,065,123 rows**, ~293 MB)
  - **Combined 3-Class Source**: `data/dataset_normal_dos_ddos.csv` (10,336,716 rows, ~1.5 GB)
  - **Class Counts**:
    - `ddos`: 6,165,008 samples
    - `dos`: 3,375,328 samples
    - `normal`: 796,380 samples

#### Option B: Standard Benchmark Subset
- **File**: `data/dataset.csv`
- **Total Records**: `300,000` network flows
- **Feature Count**: `46` raw attributes (collected via Zeek/Bro Network Security Monitor)
- **Class Balance**: Perfectly balanced across 3 classes:
  - `normal`: 100,000 samples (33.33%)
  - `dos`: 100,000 samples (33.33%)
  - `ddos`: 100,000 samples (33.33%)

### Key Features Explained
| Feature Group | Column Names | Meaning in IoT Intrusion Detection |
| :--- | :--- | :--- |
| **Flow Identifiers** | `src_ip`, `dst_ip`, `src_port`, `dst_port`, `protocol` | Identifies endpoints. Attackers often randomize source ports or target common service ports (e.g., HTTP 80, MQTT 1883). |
| **Timing & Volumes** | `ts`, `duration`, `src_bytes`, `dst_bytes`, `src_pkts`, `dst_pkts` | **Crucial for DoS/DDoS**: Volumetric packet floods result in abnormally high packet rates, microscopic durations, and unbalanced byte ratios. |
| **Connection State** | `conn_state` | Summarizes the TCP handshake (`SF` = Normal established connection; `S0` = SYN sent with no reply, typical in SYN flood DoS/DDoS; `OTH` = midstream anomalies). |
| **Application Layer** | `service`, `dns_*`, `http_*`, `ssl_*` | Identifies higher-level services and anomalies (e.g., failed DNS queries, malformed HTTP requests). |
| **Zeek Anomalies** | `weird_name`, `weird_addl`, `weird_notice` | Zeek protocol violations such as bad TCP/UDP checksums. |
| **Target Labels** | `label`, `type` | `label` is binary (0=Normal, 1=Attack). `type` is multiclass (`normal`, `dos`, `ddos`). |

> **CRITICAL PITFALL (Data Leakage)**:
> In the raw CSV, both `label` and `type` exist. If your model includes the `label` column while predicting `type`, it will achieve a trivial 100% artificial accuracy because `label=0` immediately reveals `type=normal`. **Our preprocessing explicitly drops `label` to ensure zero data leakage.**

---

## 5. Step-by-Step Technical Execution

All scripts are automated and ready in this repository.

### Step 1: Set Up & Verify Environment
On your **Manjaro PC (RTX 3060)**:
```bash
chmod +x setup_linux.sh
./setup_linux.sh
```
On your project mate's **Dual Boot PC (Windows & Ubuntu, RTX 5070 Ti)**:
- **Ubuntu**: `chmod +x setup_linux.sh && ./setup_linux.sh`
- **Windows**: Run `setup_windows_cmd.bat` or `.\setup_windows_powershell.ps1`

Run the verification utility to guarantee GPU acceleration is ready:
```bash
.venv/bin/python verify_gpu.py
```

**What this step produces:** Console output confirming Python version, CUDA availability, GPU name, and VRAM size. Screenshot this for evidence.

---

### Step 2: Run the Unified GPU Training Pipeline (Recommended)
Because both you and your project mate have dedicated NVIDIA GPUs (RTX 3060 12GB & RTX 5070 Ti 16GB), you can run the entire workflow on the GPU:

```bash
# Option A: Run using dedicated 8.2M Train & 2M Test datasets (Sampled or Full):
.venv/bin/python -m src.train_gpu \
  --train-dataset data/train_normal_dos_ddos.csv \
  --test-dataset data/test_normal_dos_ddos.csv \
  --sample-size 100000 --epochs 10

# Option B: Run GPU training on standard dataset (50,000 samples, ~3s):
.venv/bin/python -m src.train_gpu --sample-size 50000 --epochs 10

# Or run GPU training on the entire 300,000 dataset:
.venv/bin/python -m src.train_gpu --epochs 15
```


> [!IMPORTANT]
> **Large-Dataset Execution Strategy (RTX 3060 12GB, 15 GB System RAM): Approach 1 — Memory-Mapped Out-of-Core GPU Pipeline.**
> Running standard Pandas and Scikit-learn directly on 10.3M rows (8.27M train, 2.06M test) causes immediate `SIGKILL` (OOM Killer) because standard Pandas DataFrame representations require 8–12 GB RAM, and CPU-based `RandomForestClassifier` requires >40 GB RAM.
>
> **The Solution (Approach 1):** `src/train_gpu_memmap.py` streams raw CSVs in 250k-row chunks into compact binary on-disk memory-mapped arrays (`float32` for features, `int8` for labels).
> - **Peak Preprocessing RAM:** strictly **< 1.5 GB**.
> - **Zero-Copy Loading:** instantaneously opened with `< 50 MB` RAM overhead.
> - **Full 3-Model GPU Training:** trains **GPU Random Forest** (parallel CUDA trees), **GPU XGBoost** (gradient boosted trees), and **PyTorch Deep MLP** (TensorFloat-32 on CUDA) directly on the full 8.27M training set.
> - **Batched Evaluation:** runs chunked inference over all 2,065,123 test flows with zero VRAM spikes.

#### Running Approach 1 (Full 10.3M Flow Records — Recommended):
```bash
.venv/bin/python -m src.train_gpu_memmap \
  --train-dataset data/train_normal_dos_ddos.csv \
  --test-dataset data/test_normal_dos_ddos.csv \
  --chunksize 250000 --n-estimators 100 --epochs 5
```

*(Note: On the first run, it compiles `data/cache_memmap/`. Subsequent runs detect the validated binary cache and start training immediately in 0.05 seconds with zero preprocessing overhead!)*

#### Alternative: Pure Streaming Pipeline (PyTorch MLP Only)
For ultra-low RAM hardware (< 4 GB RAM), `src.train_gpu_streaming` streams mini-batches directly from CSV to CUDA:

```bash
.venv/bin/python -m src.train_gpu_streaming \
  --train-dataset data/train_normal_dos_ddos.csv \
  --test-dataset data/test_normal_dos_ddos.csv \
  --chunksize 50000 --batch-size 8192 --epochs 5
```

Lower `--chunksize` to reduce system RAM use; lower `--batch-size` if GPU memory is tight. The model is saved as `models/gpu_deep_mlp_streaming.pt`, preprocessing metadata as `models/gpu_deep_mlp_streaming_preprocessing.joblib`, and evaluation metrics as `outputs/reports/gpu_streaming_metrics.json`.

**What this step produces:**
| Output Type | Files Generated |
|:------------|:----------------|
| **Figures** | `outputs/figures/memmap_gpu_comparison.png`, `outputs/figures/memmap_gpu_rf_confusion_matrix.png`, `outputs/figures/memmap_gpu_xgboost_confusion_matrix.png`, `outputs/figures/memmap_gpu_mlp_confusion_matrix.png` |
| **Reports** | `outputs/reports/memmap_gpu_benchmark_results.json` |
| **Models** | `models/memmap_gpu_random_forest.joblib`, `models/memmap_gpu_xgboost.joblib`, `models/memmap_gpu_deep_mlp.pt` |

---

### Step 3: Run the GPU-Accelerated Random Forest Workflow
For the detailed Random Forest analysis with ROC curves and feature importance:

```bash
# Dedicated 8.2M train / 2M test sets (Sampled 100,000 records on CUDA):
.venv/bin/python -m src.random_forest_workflow \
  --train-dataset data/train_normal_dos_ddos.csv \
  --test-dataset data/test_normal_dos_ddos.csv \
  --sample-size 100000 --device cuda

# GPU Random Forest on 50,000 samples (standard dataset):
.venv/bin/python -m src.random_forest_workflow --sample-size 50000 --device cuda

# GPU Random Forest on full 300,000 dataset:
.venv/bin/python -m src.random_forest_workflow --device cuda
```

**What this step produces:**
| Output Type | Files Generated |
|:------------|:----------------|
| **Figures** | `rf_workflow_multiclass_distribution.png`, `rf_workflow_binary_class_distribution.png`, `rf_workflow_confusion_matrix.png`, `rf_workflow_roc_curves.png`, `rf_workflow_feature_importance.png` |
| **Reports** | `rf_workflow_classification_report.txt`, `rf_workflow_summary.json`, `rf_workflow_feature_importance.csv`, `rf_workflow_run_config.json` |
| **Models** | `models/rf_network_classifier.joblib` |

---

### Step 4: Verify All Outputs Exist
```bash
# Check all figures were generated:
ls -la outputs/figures/

# Check all reports were generated:
ls -la outputs/reports/

# Check all models were saved:
ls -la models/
```

> [!TIP]
> **All outputs are already generated in your repository.** You do NOT need to re-run the scripts unless you want fresh results. The existing files in `outputs/` and `models/` are ready to use in your presentation.

---

## 6. What You Show in the Presentation (Output → Slide Mapping)

This is the most important section if you're confused about **"what do I actually show?"**

```
YOUR PRESENTATION = Code Walkthrough + Output Figures + Numbers from Reports
```

Here's exactly what goes where:

| Slide | What You Show | Source File(s) |
|:-----:|:--------------|:---------------|
| **Slide 1** | Title, names, course info | (Just text) |
| **Slide 2** | Problem: IoT devices are vulnerable to DoS/DDoS. Goal: build an IDS classifier | (Just text + optional diagram) |
| **Slide 3** | TON_IoT dataset overview: 300K records, 46 features, Zeek network logs | (Just text + cite the UNSW paper) |
| **Slide 4** | **INSERT:** `rf_workflow_multiclass_distribution.png` — shows the 3 balanced classes | `outputs/figures/rf_workflow_multiclass_distribution.png` |
| **Slide 5** | Preprocessing steps: deduplication (50,267 rows removed), label drop, IP conversion, encoding | Numbers from `rf_workflow_run_config.json` |
| **Slide 6** | Model architectures: Random Forest (200 trees), XGBoost, Deep MLP diagram | (Text + architecture diagram) |
| **Slide 7** | **INSERT:** `pure_gpu_comparison.png` + the results table with accuracy/F1/MCC/time numbers | `outputs/figures/pure_gpu_comparison.png` + `pure_gpu_benchmark_results.json` |
| **Slide 8** | **INSERT:** `rf_workflow_confusion_matrix.png` — the 3×3 prediction matrix | `outputs/figures/rf_workflow_confusion_matrix.png` |
| **Slide 9** | **INSERT:** `rf_workflow_roc_curves.png` — ROC curves with AUC = 1.0 | `outputs/figures/rf_workflow_roc_curves.png` |
| **Slide 10** | **INSERT:** `rf_workflow_feature_importance.png` — top features: conn_state (30.8%), src_port (23.6%), ts (13.9%) | `outputs/figures/rf_workflow_feature_importance.png` + `rf_workflow_feature_importance.csv` |
| **Slide 11** | GPU hardware specs, training times (<2s), inference latency (<1 μs/sample) | Numbers from `pure_gpu_benchmark_results.json` |
| **Slide 12** | Conclusion: 99.99% accuracy, key findings, future work | Summary from `rf_workflow_summary.json` |

> [!IMPORTANT]
> **The 5 key figures you MUST include in your slides:**
> 1. 📊 Class distribution bar chart → proves balanced dataset
> 2. 🔲 Confusion matrix → proves model works correctly
> 3. 📈 ROC curves → proves discriminative power (AUC = 1.0)
> 4. 📉 Feature importance → shows WHAT the model learned
> 5. ⚡ GPU comparison → shows model speed & benchmarks

---

## 7. Slide-by-Slide Presentation Blueprint (12 Slides)

You can build your presentation in PowerPoint, Google Slides, Canva, or LaTeX Beamer using this 12-slide structure:

```
Slide 1: Title & Authors
Slide 2: Problem Statement & Motivation
Slide 3: TON_IoT Dataset Architecture
Slide 4: Class Distribution & Exploratory Analysis
Slide 5: Data Preprocessing & Leakage Prevention Pipeline
Slide 6: Model Architecture & Proposed Methodology
Slide 7: Experimental Performance & Results Matrix
Slide 8: Confusion Matrix Breakdown (Normal vs DoS vs DDoS)
Slide 9: Multi-Class ROC Curves & AUC Analysis
Slide 10: Feature Importance: What Distinguishes Attacks?
Slide 11: Hardware Acceleration & Practical Deployment
Slide 12: Conclusion & Future Scope
```

---

### Detailed Slide Content

#### Slide 1: Title Slide
- **Title**: *IoT Network Intrusion Detection: Classifying DoS, DDoS, and Normal Traffic on the TON_IoT Dataset*
- **Course**: Information Security Lab (Lab #7)
- **Institution**: Discipline of Computer Science and Engineering, Khulna University (CSEKU)
- **Instructor**: Dr. Anupam Kumar Bairagi
- **Presenters**: [Your Name] (Roll: ...) & [Project Mate's Name] (Roll: ...)
- **Date**: October 2026

#### Slide 2: Problem Statement & Motivation
- **The Context**: IoT devices (sensors, smart home, industrial Modbus gateways) have constrained compute power, weak default credentials, and rarely run host antivirus software.
- **The Threat**:
  - **DoS**: Single-source exhaustion of bandwidth or CPU (e.g., SYN floods, HTTP slowloris).
  - **DDoS**: Multi-source, distributed botnet flooding designed to knock critical services offline.
- **The Objective**: Build a robust, real-time Network Intrusion Detection System (NIDS) capable of classifying incoming packet flows into `Normal`, `DoS`, and `DDoS` with high accuracy and low false-positive rates.

#### Slide 3: The TON_IoT Dataset
- **Origin**: UNSW Canberra Cyber (developed by Dr. Nour Moustafa, 2021).
- **Architecture**: Realistic heterogeneous testbed combining Edge, Fog, and Cloud layers.
- **Telemetry Sources**: Zeek (formerly Bro) network analysis engine capturing Layer 3 through Layer 7 protocol flows.
- **Our Dataset Subset**: 300,000 records, 46 attributes covering TCP, UDP, ICMP, DNS, HTTP, and SSL interactions.

#### Slide 4: Dataset Exploration & Class Distribution
- **Class Breakdown**:
  - `Normal`: 100,000 flows (33.33%)
  - `DoS`: 100,000 flows (33.33%)
  - `DDoS`: 100,000 flows (33.33%)
- **Visual**: Insert `outputs/figures/rf_workflow_multiclass_distribution.png`.
- **Takeaway**: A perfectly balanced dataset allows training without artificial oversampling (SMOTE) or class weights bias.

#### Slide 5: Data Preprocessing & Feature Engineering
- **Step 1 - De-duplication**: Identified and dropped 50,267 duplicate network flow captures (300,000 → 249,733 unique rows).
- **Step 2 - Leakage Removal**: Dropped the raw `label` column to prevent target leakage.
- **Step 3 - IP Address Decomposition**: Standard ML models cannot process IP strings like `"192.168.1.152"`. We convert them mathematically into 64-bit high and low numerical integers (`src_ip_high`, `src_ip_low`, `dst_ip_high`, `dst_ip_low`).
- **Step 4 - Categorical Encoding**: Label-encoded protocols (`tcp`, `udp`), services, and Zeek connection states (`conn_state`).
- **Step 5 - Missing Value Imputation**: Zeek logs use `"-"` for empty fields; transformed to numeric `-1` values. Constant columns (zero-variance like `http_referrer`) removed.
- **Final processed shape**: 249,733 rows × 45 features.

#### Slide 6: Proposed Methodology & Model Architecture
- **Primary Model: Random Forest Classifier**:
  - Ensemble of 200 de-correlated Decision Trees.
  - Bootstrap aggregation (Bagging) with square-root feature selection (`max_features='sqrt'`).
  - Gini impurity criterion.
  - Highly resistant to overfitting and capable of handling non-linear boundaries.
- **Comparative Baseline 1: Deep MLP (PyTorch)**:
  - Multi-Layer Perceptron: Input $\rightarrow$ 256 $\rightarrow$ BatchNorm $\rightarrow$ ReLU $\rightarrow$ Dropout(0.25) $\rightarrow$ 128 $\rightarrow$ Output (3 classes).
  - Trained using AdamW optimizer and Cross-Entropy loss with CUDA acceleration.
- **Comparative Baseline 2: XGBoost**:
  - Gradient Boosted Decision Trees utilizing GPU histogram binning (`tree_method='hist'`, `device='cuda'`).

#### Slide 7: Experimental Performance & Results Matrix (GPU Acceleration)
- **Experimental Setup**: Evaluated on NVIDIA GeForce RTX GPUs with TensorFloat-32 (TF32) Tensor Core acceleration.
- **Results Table** (from `pure_gpu_benchmark_results.json`):

| Model | Hardware | Training Time | Inference Latency | Accuracy | Macro F1-Score | MCC | ROC-AUC (OvR) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **GPU Random Forest** | **NVIDIA CUDA** | **1.64 s** | **0.96 $\mu\text{s}$/sample** | **99.99%** | **99.99%** | **0.9999** | **1.0000** |
| **GPU XGBoost** | **NVIDIA CUDA** | **1.11 s** | **0.90 $\mu\text{s}$/sample** | **99.99%** | **99.99%** | **0.9999** | **1.0000** |
| **PyTorch Deep MLP** | **NVIDIA CUDA** | **17.85 s** | **0.10 $\mu\text{s}$/sample** | **99.94%** | **99.94%** | **0.9992** | **1.0000** |

- **Key Takeaways**:
  - **Blazing Fast Training**: Tree models train in under 2 seconds on the GPU.
  - **Ultra-low Latency**: Inference takes $<1\ \mu\text{s}$ per flow — capable of inspecting over **1,000,000 packets per second** at line rate!
  - **Zero CPU Bottleneck**: Data matrix computation and gradient evaluation occur entirely within GPU VRAM.

- **Visual**: Insert `outputs/figures/pure_gpu_comparison.png`.

#### Slide 8: Confusion Matrix Breakdown
- **Visual**: Insert `outputs/figures/rf_workflow_confusion_matrix.png`.
- **Per-Class Breakdown** (from `rf_workflow_summary.json`):
  - **Normal** (19,279 test samples): Precision 100.00%, Recall 100.00%
  - **DoS** (10,668 test samples): Precision 100.00%, Recall 99.98%
  - **DDoS** (20,000 test samples): Precision 99.99%, Recall 100.00%
- **Discussion**: In intrusion detection, False Positives (alert fatigue) and False Negatives (missed intrusions) are dangerous. Our model achieves almost zero errors across both attack categories.

#### Slide 9: ROC Curves & AUC Analysis
- **Visual**: Insert `outputs/figures/rf_workflow_roc_curves.png`.
- **Explanation**:
  - Plots True Positive Rate (Sensitivity) vs False Positive Rate (1 - Specificity) across varying classification thresholds.
  - Macro-average ROC-AUC = **1.00**, Micro-average ROC-AUC = **1.00**.
  - Confirms high discriminative capability across all three classes simultaneously (One-vs-Rest).

#### Slide 10: Feature Importance: What Gives Away Attacks?
- **Visual**: Insert `outputs/figures/rf_workflow_feature_importance.png`.
- **Top 5 Critical Features** (from `rf_workflow_feature_importance.csv`):
  1. `conn_state` (30.77%): TCP handshake state — `S0` (SYN flood) vs `SF` (normal completed connection) is the strongest indicator.
  2. `src_port` (23.57%): Attack tools cycle through ephemeral ports or use fixed source ports.
  3. `ts` (13.93%): Flow timestamp / inter-arrival intervals — attack tools transmit bursts in unnatural periodic patterns.
  4. `dst_port` (8.92%): Targeted service ports differ between attack and normal traffic.
  5. `src_ip_low` (7.48%): Source IP subnet locality — DDoS uses many distributed source IPs vs DoS from a single source.

#### Slide 11: Hardware Acceleration & Deployment
- **Hardware Validated**:
  - Manjaro Linux: NVIDIA GeForce RTX 3060 12 GB (Ampere, TF32 Tensor Cores).
  - Ubuntu & Windows: NVIDIA GeForce RTX 5070 Ti 16 GB (Blackwell, SM 12.0).
- **Latency & Throughput** (from `pure_gpu_benchmark_results.json`):
  - Random Forest inference latency: 0.96 μs per flow ($<1$ microsecond).
  - Throughput: $>1$ million flows per second — suitable for line-rate inspection.
  - Multi-threaded CPU execution also allows deployment on standard IoT gateway routers without requiring a GPU.

#### Slide 12: Conclusion & Future Scope
- **Conclusion**:
  - Successfully classified `Normal`, `DoS`, and `DDoS` network traffic from the TON_IoT dataset with $>99.9\%$ accuracy.
  - Eliminated data leakage and transformed IP strings into structured numerical representations.
  - Discovered that connection states (`conn_state`) and source ports (`src_port`) are the most influential discriminators.
  - All 3 models (Random Forest, XGBoost, Deep MLP) achieve near-perfect performance, with tree-based models training in under 2 seconds.
- **Future Work**:
  - Extend to full multi-class detection (including Backdoor, Ransomware, Scanning, XSS, Injection).
  - Deploy onto lightweight edge hardware (e.g., Raspberry Pi / NVIDIA Jetson) as an active firewall filter.

---

## 8. Presentation Script & Speaking Notes

Use this section as your spoken walkthrough during the presentation.

### Presenter 1 (Introduction & Data Pipeline — Slides 1–5)
> *"Respected Sir and colleagues, good morning. Today we present our work on Lab #7: Network Intrusion Detection using the TON_IoT dataset to classify DoS, DDoS, and Normal traffic.*
>
> *IoT networks are notoriously vulnerable to volumetric denial of service attacks because edge devices lack traditional endpoint defenses. The TON_IoT dataset collected by UNSW Canberra provides realistic Zeek network traces from IoT testbeds.*
>
> *Our dataset contains 300,000 connection records equally divided between Normal, DoS, and DDoS traffic. As you can see in this bar chart [point to Slide 4], the classes are perfectly balanced.*
>
> *Before training any model, our first priority was ensuring clean, leakage-free data. Specifically:
> 1. We removed 50,267 duplicate flow logs, reducing the dataset to 249,733 unique flows.
> 2. We dropped the raw `label` column to avoid trivial target leakage when predicting multi-class `type`.
> 3. We decomposed textual IP addresses into mathematical 64-bit numerical high and low components so machine learning algorithms could process them without losing subnet locality.
> 4. We encoded categorical protocol states and cleaned Zeek missing markers.
>
> *Now, my project partner will explain our model architectures and experimental results."*

### Presenter 2 (Models, Results & Insights — Slides 6–12)
> *"Thank you. For our classification engine, we selected a Random Forest Classifier with 200 estimators, and compared it against a Deep PyTorch MLP and an XGBoost model accelerated on NVIDIA RTX GPUs.*
>
> *As shown in our results matrix [point to Slide 7], GPU Random Forest achieved 99.99% accuracy and a Matthews Correlation Coefficient of 0.9999 on held-out test data. All tree models trained in under 2 seconds on the GPU.*
>
> *In our confusion matrix [point to Slide 8], we observed only 2 misclassifications out of nearly 50,000 test samples. The ROC curves [point to Slide 9] show an AUC of 1.0 for all classes.*
>
> *Looking at our feature importance analysis [point to Slide 10], the most decisive features were connection state (`conn_state` at 30.8%), source port (`src_port` at 23.6%), and flow timestamps (`ts` at 13.9%). For example, SYN flood attacks consistently generated `S0` states—meaning SYN packets sent with no reply—which starkly contrasted with normal established `SF` handshakes.*
>
> *In conclusion, our pipeline provides an accurate, lightweight, and leakage-free intrusion detection workflow that can inspect over 1 million flows per second on GPU hardware. Thank you, and we welcome any questions."*

---

## 9. Expected Viva / Defense Questions by Dr. Anupam Kumar Bairagi

Be prepared to answer these technical questions:

### Q1: "How did you ensure there was no data leakage in your model?"
> **Answer**:  
> *"Sir, the original dataset contains both a binary target column called `label` (0/1) and a multiclass column called `type` (`normal`, `dos`, `ddos`). If we had retained the `label` column as an input feature while predicting `type`, the model would suffer from severe target leakage, because `label=0` directly gives away that the traffic is `normal`. We explicitly dropped `label` before feature preprocessing, along with constant columns. We also performed a stratified train-test split after deduplication."*

### Q2: "What is the technical difference between DoS and DDoS in your dataset?"
> **Answer**:  
> *"In DoS (Denial of Service), the malicious traffic originates from a single attacker source targeting a victim service. In DDoS (Distributed Denial of Service), the traffic is coordinated from multiple distributed IP addresses simultaneously. In our dataset, this difference is evident in the `src_ip_low` distribution and packet inter-arrival patterns (`ts` and packet byte volumes)."*

### Q3: "Why did you convert IP addresses into high and low integer parts rather than one-hot encoding or Label Encoding?"
> **Answer**:  
> *"One-hot encoding IP addresses causes an explosion in dimensionality because there are hundreds of unique IP addresses. LabelEncoding assigns arbitrary nominal integers (1, 2, 3...) that imply an artificial ordinal relationship that doesn't exist. By decomposing IPv4/IPv6 addresses into 64-bit numerical high and low integers using Python's `ipaddress` module, we preserve the exact binary subnet representation of the IP space in a compact 2-feature format."*

### Q4: "Why use Random Forest over a single Decision Tree or SVM?"
> **Answer**:  
> *"A single Decision Tree is prone to high variance and overfitting on noisy network traffic. SVM with non-linear kernels has an $O(n^2)$ to $O(n^3)$ training complexity, making it impractical for 300,000 network flows. Random Forest trains multiple de-correlated decision trees on bootstrap samples using random subsets of features. This ensemble averaging drastically reduces variance, resists outliers, and provides native feature importance scores."*

### Q5: "What does `conn_state` signify, and why is it among the top features?"
> **Answer**:  
> *"In Zeek network monitoring, `conn_state` records the state of the transport connection. For example, `SF` indicates normal SYN-ACK-FIN completion. In DoS and DDoS SYN flood attacks, the attacker intentionally never completes the handshake, leaving connections in the `S0` state (Connection attempt seen, no reply) or `OTH` (midstream traffic). The tree models quickly identify that `S0` corresponds to flood attacks. In fact, `conn_state` is our highest-importance feature at 30.77%."*

### Q6: "Why did you report MCC and Macro F1 rather than just accuracy?"
> **Answer**:  
> *"While our specific subset of 300,000 rows has balanced classes, network intrusion detection in production is typically highly imbalanced (e.g., 99% normal, 1% attack). Accuracy can be misleading in imbalanced contexts. Macro F1 gives equal weight to every class regardless of size, and Matthews Correlation Coefficient (MCC) produces a high score only if predictions perform well across all quadrants of the confusion matrix."*

### Q7: "What preprocessing steps did you perform and in what order?"
> **Answer**:  
> *"In order: (1) Load the raw CSV with 300,000 rows and 46 columns. (2) Remove 50,267 duplicate rows. (3) Drop the `label` column to prevent data leakage and `type` as our target. (4) Convert `src_ip` and `dst_ip` strings into 4 numerical columns (high/low pairs). (5) Label-encode all categorical columns like protocol, service, and conn_state. (6) Replace infinite values and Zeek's '-' missing markers with -1. (7) Remove constant columns like `http_referrer`. (8) Stratified 80/20 train-test split. Final shape: 249,733 rows × 45 features."*

### Q8: "Can you explain your confusion matrix? Were there any misclassifications?"
> **Answer**:  
> *"Yes, there were exactly 2 misclassifications out of 49,947 test samples. Both were DoS samples that were misclassified as DDoS. This makes sense because DoS and DDoS share similar packet flooding characteristics—the key difference being whether the attack comes from one source or many. No normal traffic was ever misclassified as an attack, which is critical for avoiding false alarms in production."*

---

## 10. Commands Cheatsheet (GPU-Accelerated)

### 1. Verify Hardware & GPU Acceleration
```bash
.venv/bin/python verify_gpu.py
```

### 2. Run the Unified GPU Training Pipeline (Recommended)
```bash
# Recommended for full 10.3M records on <= 16GB RAM (Approach 1: Out-of-Core Memory-Map):
.venv/bin/python -m src.train_gpu_memmap \
  --train-dataset data/train_normal_dos_ddos.csv \
  --test-dataset data/test_normal_dos_ddos.csv \
  --chunksize 250000 --n-estimators 100 --epochs 5

# Sampled run on dedicated 8.2M Train & 2.0M Test datasets:
.venv/bin/python -m src.train_gpu \
  --train-dataset data/train_normal_dos_ddos.csv \
  --test-dataset data/test_normal_dos_ddos.csv \
  --sample-size 100000 --epochs 10

# Standard 300,000 dataset (Fast 50,000 samples on CUDA):
.venv/bin/python -m src.train_gpu --sample-size 50000 --epochs 10

# Full run on standard 300,000 samples:
.venv/bin/python -m src.train_gpu --epochs 15
```

### 3. Run GPU-Accelerated Random Forest (200 Parallel Trees on CUDA)
```bash
# Dedicated 8.2M Train & 2.0M Test datasets:
.venv/bin/python -m src.random_forest_workflow \
  --train-dataset data/train_normal_dos_ddos.csv \
  --test-dataset data/test_normal_dos_ddos.csv \
  --sample-size 100000 --device cuda

# Standard dataset (50,000 samples on GPU):
.venv/bin/python -m src.random_forest_workflow --sample-size 50000 --device cuda

# Full 300,000 dataset on GPU:
.venv/bin/python -m src.random_forest_workflow --device cuda
```

### 4. Run PyTorch Deep MLP on GPU
```bash
# Dedicated 8.2M train / 2M test sets:
.venv/bin/python -m src.train_dl --task multiclass \
  --train-dataset data/train_normal_dos_ddos.csv \
  --test-dataset data/test_normal_dos_ddos.csv \
  --device cuda --epochs 20 --batch-size 1024

# Standard dataset:
.venv/bin/python -m src.train_dl --task multiclass --device cuda --epochs 20 --batch-size 1024
```

### 5. Run XGBoost on GPU
```bash
# Dedicated 8.2M train / 2M test sets:
.venv/bin/python -m src.train_ml --task multiclass --models xgboost \
  --train-dataset data/train_normal_dos_ddos.csv \
  --test-dataset data/test_normal_dos_ddos.csv \
  --device cuda

# Standard dataset:
.venv/bin/python -m src.train_ml --task multiclass --models xgboost --device cuda
```

### 6. Run Unit Test Suite
```bash
.venv/bin/python -m unittest discover -s tests
```

---

## 11. Interactive Presentation Slides & GitHub Pages Deployment

### 🌐 Live Online Presentation (Any Device / Anywhere)
Your presentation has been rendered with Manim Slides and compiled into a standalone HTML5 Reveal.js deck hosted via **GitHub Pages**:

🔗 **Live Presentation URL**:  
👉 **`https://kazirifatmorshed.github.io/TON_IOT_NETWORK_IS_Lab_CSEKU/`**

> [!TIP]
> - **Zero Server Dependency**: All high-definition video transitions are embedded directly into `docs/index.html` as Base64 Data URIs.
> - **Controls**:
>   - Press **`Space`** or **`Right Arrow`** to advance animations and slides.
>   - Press **`Left Arrow`** to go back.
>   - Press **`F`** to toggle full-screen mode during the lab defense.
>   - Press **`Esc`** or **`O`** to open the slide overview grid.

---

### 🖥️ Local Presentation Modes

1. **Standalone Offline Browser (No Installation Required)**:
   Simply double-click or open `docs/index.html` in Chrome, Firefox, Edge, or Brave:
   ```bash
   xdg-open docs/index.html   # On Linux
   # OR
   start docs\index.html     # On Windows
   ```

2. **Interactive Window Presentation (via Conda/Manim)**:
   ```bash
   conda activate manim_env
   ./presentation/render_presentation.sh present
   ```

3. **Re-rendering or Updating Slides**:
   ```bash
   # Quick render & regenerate docs/index.html
   ./presentation/render_presentation.sh html

   # Full 1080p60 High-Definition render & regenerate docs/index.html
   ./presentation/render_presentation.sh full-hd
   ```

---

### ⚙️ Enabling GitHub Pages in Repository Settings

Once you push this repository to GitHub, enable GitHub Pages:

1. Open your repository on GitHub: `https://github.com/KaziRifatMorshed/TON_IOT_NETWORK_IS_Lab_CSEKU`
2. Navigate to **Settings** > **Pages** (under the "Code and automation" left sidebar).
3. Under **Build and deployment**:
   - **Method A (Recommended - Automated via Workflow)**:
     - Set **Source** to **`GitHub Actions`**.
     - The included `.github/workflows/pages.yml` will automatically deploy `docs/index.html` on every push to `main`.
   - **Method B (Direct Branch Deployment)**:
     - Set **Source** to **`Deploy from a branch`**.
     - Branch: select **`main`**.
     - Folder: select **`/docs`**.
     - Click **Save**.
4. Within 1–2 minutes, your presentation will be live at:  
   `https://kazirifatmorshed.github.io/TON_IOT_NETWORK_IS_Lab_CSEKU/`

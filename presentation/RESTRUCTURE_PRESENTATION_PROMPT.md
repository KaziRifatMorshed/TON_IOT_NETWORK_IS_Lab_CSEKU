# Prompt: Restructure & Improve the Manim Presentation Slides

> **Purpose**: This document is a detailed prompt/instruction set for an AI assistant (Gemini) to completely rewrite and improve `presentation/presentation_slides.py` — the Manim + Manim-Slides academic presentation for our TON_IoT Network Intrusion Detection lab assignment.

---

## Context

- **Course**: Information Security Lab (Lab #7), CSE Discipline, Khulna University
- **Instructor**: Dr. Anupam Kumar Bairagi, Professor
- **Presenters**: Md Siam Ahmed (230202) & Kazi Rifat Morshed (230220)
- **Assignment**: Classify DoS / DDoS / Normal traffic from the TON_IoT Network dataset & present findings
- **Tech Stack**: Python Manim (Community Edition) + `manim-slides` (Reveal.js export)
- **Rendering**: Via `conda run -n manim_env manim -qh presentation_slides.py TonIoTPresentation`
- **Export**: Via `conda run -n manim_env manim-slides convert TonIoTPresentation ../docs/index.html --one-file -c reveal_theme=white`

---

## What's Wrong with the Current Presentation

The current `presentation/presentation_slides.py` has these problems:

### 1. Wrong / Outdated Numbers
The hardcoded performance numbers in Slide 5 (results table) and Slide 7 (feature importance) do NOT match our actual benchmark outputs. The correct numbers from our actual runs are:

**Correct Results Table** (from `outputs/reports/pure_gpu_benchmark_results.json`):

| Model | Train Time | Latency (μs/sample) | Accuracy | F1 Macro | MCC | ROC-AUC |
|:------|:-----------|:---------------------|:---------|:---------|:----|:--------|
| GPU Random Forest | 1.64 s | 0.96 | 99.99% | 99.99% | 0.9999 | 1.0000 |
| GPU XGBoost | 1.11 s | 0.90 | 99.99% | 99.99% | 0.9999 | 1.0000 |
| PyTorch Deep MLP | 17.85 s | 0.10 | 99.94% | 99.94% | 0.9992 | 1.0000 |

**Correct Feature Importance Ranking** (from `outputs/reports/rf_workflow_feature_importance.csv`):

| Rank | Feature | Importance |
|:-----|:--------|:-----------|
| #1 | conn_state | 30.77% |
| #2 | src_port | 23.57% |
| #3 | ts | 13.93% |
| #4 | dst_port | 8.92% |
| #5 | src_ip_low | 7.48% |

**Correct Confusion Matrix** (from `outputs/reports/rf_workflow_summary.json`, test set of 49,947 samples):

| Class | Test Samples | Precision | Recall |
|:------|:-------------|:----------|:-------|
| Normal | 19,279 | 100.00% | 100.00% |
| DoS | 10,668 | 100.00% | 99.98% |
| DDoS | 20,000 | 99.99% | 100.00% |

**Correct Preprocessing Stats** (from `outputs/reports/rf_workflow_run_config.json`):
- Original shape: 300,000 rows × 46 columns
- Duplicates removed: 50,267
- Processed shape: 249,733 rows × 45 features
- Constant columns removed: `http_referrer`
- Dropped columns: `type` (target), `label` (leakage), `http_referrer` (constant)

### 2. Only 8 Slides — Too Compressed
The current version has only 8 slides, which is too few for a proper lab defense. Our seniors' presentation (by Sarafat Karim & Farid Hossen Rehad, IDs 220216 & 220222) had **12 slides** with much better pacing. We need **12 slides** as well.

### 3. No Actual Figure Images
The current presentation recreates everything in LaTeX/Manim text. But we already have high-quality matplotlib output figures! The presentation should **embed the actual PNG figures** from `outputs/figures/` as `ImageMobject` on the relevant slides. This is more convincing and saves tons of Manim code.

### 4. Confusing Slide Order
The GPU hardware slide comes before the results, which is disorienting. The seniors' flow was much more logical: Problem → Dataset → Class Distribution → Preprocessing → ML Pipeline → Model Details → Results → Confusion Matrix → ROC + Feature Importance → Conclusion.

### 5. Supervisor Info is Wrong
The `.agents.md` file lists `Mr. Sajib Chatterjee` as supervisor. That is **wrong**. The correct instructor/supervisor is:
- **Dr. Anupam Kumar Bairagi**
- **Professor**, Computer Science and Engineering Discipline
- **Khulna University**, Khulna-9208, Bangladesh
- **Role**: Course Instructor & Supervisor

---

## The New 12-Slide Structure (Follow This Exactly)

Model the structure after our seniors' presentation. Here is the exact slide sequence with content specifications:

### Slide 1 — Title / Cover Slide
- **Title**: "TON_IoT Network Traffic Classification Using Random Forest"
- **Subtitle**: "Intrusion Detection Workflow"
- **Footer banner**: "Information Security Laboratory | Khulna University, Khulna"
- **KU emblem** (`ku_emblem_clean.png`) next to the discipline name
- Keep the NVIDIA green theme header/footer from the current design
- Dynamic month/year via `datetime.now().strftime("%B %Y")`

### Slide 2 — Presented By / Presented To
- **Left column — PRESENTED BY**:
  - Md Siam Ahmed, Student ID: 230202
  - Kazi Rifat Morshed, Student ID: 230220
  - Computer Science & Engineering Discipline, Khulna University
  - 4th Year, 1st Semester
- **Right column — PRESENTED TO**:
  - Dr. Anupam Kumar Bairagi, Professor
  - Computer Science & Engineering Discipline, Khulna University, Khulna
  - Course: Information Security Laboratory

### Slide 3 — Problem & Objective
Two-panel layout (like the seniors' slide):
- **Left panel — THE PROBLEM**:
  - Thousands of traffic events arrive every second in IoT/IIoT networks
  - Manual review cannot reliably separate Normal, DoS, and DDoS traffic
  - Attackers disguise malicious flows to resemble legitimate traffic
  - Detection must be fast enough to support real-time response
- **Right panel — OBJECTIVE**:
  - Build an automated multi-class IDS that classifies each flow as: Normal / DoS / DDoS
  - Use Random Forest to learn attack patterns from cleaned network features
  - Save trained model, metrics, figures, and config for repeatable evaluation
  - **Outcome**: A fast, reproducible classifier with near-perfect accuracy

### Slide 4 — Dataset Overview
Table-style layout:
- Dataset: TON_IoT Network Traffic Dataset
- Total Records: 300,000 rows
- After Deduplication: 249,733 rows
- Target Column: `type`
- Selected Classes: normal, dos, ddos
- Final Features: 45 columns after preprocessing
- **Right side**: Feature group summary (Network Identity, Protocol Behavior, Traffic Volume, Timing Features, Application Fields)

### Slide 5 — Class Distribution
- **Embed the actual figures as `ImageMobject`**:
  - Left: `outputs/figures/rf_workflow_binary_class_distribution.png` (Binary: Attack vs Normal)
  - Right: `outputs/figures/rf_workflow_multiclass_distribution.png` (Multiclass: Normal vs DoS vs DDoS)
- Caption: "The dataset provides enough samples for each selected class, supporting stable model training and evaluation."

### Slide 6 — Data Preprocessing Steps
Six-step numbered card layout (like the seniors' slide):
1. **Load Dataset**: Read `data/dataset.csv` and keep selected target classes: normal, dos, ddos
2. **Remove Duplicates**: Drop repeated rows to reduce bias: 300,000 → 249,733 unique flows
3. **Normalize Labels**: Standardize type labels to lowercase and separate target column from features
4. **Encode Fields**: Convert IP addresses into numeric parts (64-bit high/low) and label-encode categorical fields
5. **Clean Matrix**: Replace NaN/Inf with safe numeric values (-1) and remove constant no-signal columns (e.g., `http_referrer`)
6. **Train/Test Split**: 80/20 stratified split with `random_state=42` to preserve class proportions
- **Footer line**: "Result: a clean numeric feature matrix ready for Random Forest training and evaluation."

### Slide 7 — Machine Learning Pipeline
A horizontal **flowchart / pipeline diagram** with numbered stages (like the seniors' 8-stage pipeline):

```
Raw Data → Load Data → Clean Data → Feature Matrix → Train/Test Split → Random Forest → Evaluate → Save Outputs
```

Grouped into 4 phases:
- **DATA INGESTION**: Raw Data → Load Data
- **PREPROCESSING**: Clean Data → Feature Matrix
- **MODELING**: Train/Test Split → Random Forest (200 trees)
- **OUTPUT**: Evaluate → Save (model, reports, figures, config)

Caption: "Model saved as joblib for reuse | Metrics, reports, figures, and run configuration are saved automatically."

### Slide 8 — Random Forest Model
Two-panel layout:
- **Left — WHAT IS RANDOM FOREST?**:
  - Ensemble classifier that trains many Decision Trees and combines their votes
  - WHY IT FITS THIS IDS TASK:
    - Works well on tabular network-flow features
    - Handles numeric + encoded categorical fields
    - Captures nonlinear attack patterns in traffic
    - Balanced class weights reduce class-imbalance bias
    - Feature importance helps explain influential fields
  - "Many trees → majority vote → Normal / DoS / DDoS"
- **Right — MODEL PARAMETERS** (table):
  - n_estimators: 200 (Number of trees)
  - criterion: gini (Split quality)
  - max_depth: None (Grow until pure)
  - max_features: sqrt (Subset per split)
  - min_split: 2
  - min_leaf: 1
  - bootstrap: True (Sample rows per tree)
  - class_weight: balanced (Handle imbalance)
  - n_jobs: -1 (Use all CPU cores)
  - random_state: 42 (Reproducible run)

### Slide 9 — Results & Performance
- **Four headline stat boxes across the top**:
  - 99.99% Accuracy
  - 99.99% Macro F1
  - 99.99% Recall
  - 1.000 ROC-AUC
- **Classification Report Table below**:

| Class | Precision | Recall | F1-Score | Meaning |
|:------|:----------|:-------|:---------|:--------|
| Normal | 100.00% | 100.00% | 100.00% | Benign flow detection |
| DoS | 100.00% | 99.98% | 99.99% | Single-source attack |
| DDoS | 99.99% | 100.00% | 99.99% | Distributed attack |
| Macro Avg | 99.99% | 99.99% | 99.99% | Balanced across classes |

- Caption: "Interpretation: high precision limits false alarms, high recall catches attacks, and macro F1 confirms balanced Normal/DoS/DDoS performance."

### Slide 10 — Confusion Matrix
- **Embed the actual figure**: `outputs/figures/rf_workflow_confusion_matrix.png` as a large `ImageMobject` (left/center)
- **Right side — Reading the Matrix** (text explanation):
  - **Rows**: Actual traffic class
  - **Columns**: Predicted class
  - **Diagonal ✓**: Correct predictions
  - **Off-diagonal ✕**: Misclassifications
  - "Near-perfect diagonal values show the model classifies Normal, DoS, and DDoS traffic with very high accuracy. Minimal off-diagonal errors indicate little class confusion."

### Slide 11 — ROC Curves & Feature Importance
- **Left half**: Embed `outputs/figures/rf_workflow_roc_curves.png` as `ImageMobject`
  - Caption: "Curves close to top-left corner and AUC near 1.000 indicate excellent separation between Normal, DoS, and DDoS classes."
- **Right half**: Embed `outputs/figures/rf_workflow_feature_importance.png` as `ImageMobject`
  - Caption: "Top-ranked traffic fields contribute most to model decisions, making the classifier easier to explain and validate."

### Slide 12 — Thank You / Q&A
- Large centered "Thank You" text
- "Any Questions?" subtitle
- **Repository link**: `https://github.com/KaziRifatMorshed/TON_IOT_NETWORK_IS_Lab_CSEKU`
- Keep it simple and clean

---

## Design & Technical Constraints

### Must Follow (from `.agents.md`)

1. **Color Palette**: Keep the existing NVIDIA-themed light color palette exactly as defined:
   - `NVIDIA_GREEN = "#76B900"`
   - `NVIDIA_DARK_GREEN = "#265200"`
   - `NVIDIA_ACCENT_GREEN = "#3B7500"`
   - `TEXT_MAIN = "#1A1A1A"`
   - `TEXT_MUTED = "#525B64"`
   - `CARD_BG = "#F8FAFC"`
   - `WHITE_COLOR = "#FFFFFF"`
   - `CARD_BORDER = "#E2E8F0"`

2. **Camera Background**: Always use `ManimColor(CARD_BG)`, never a raw string. Both `config.background_color` and `self.camera.background_color` must be set.

3. **Text Defaults**: Set `Tex.set_default(color=TEXT_MAIN)` and `MathTex.set_default(color=TEXT_MAIN)`.

4. **No Text Ghosting**: Never use `Transform(old_text, new_text)` between text mobjects of different string lengths. Use `FadeOut` + `FadeIn` instead.

5. **Wait before next_slide**: Always add `self.wait(0.2)` at the end of each slide's animation block before calling `self.next_slide()`.

6. **Footer**: Persistent NVIDIA_GREEN footer bar at the bottom with:
   - Left: `Slide X/12 | TON_IoT Network Intrusion Detection`
   - Right: `Md Siam Ahmed (230202), Kazi Rifat Morshed (230220) | {MONTH YEAR}`

7. **Header**: Persistent white header bar at top with:
   - Left: Category breadcrumb in `NVIDIA_DARK_GREEN`
   - Right: `kucse_full_logo.png` logo
   - Green accent stripe along bottom edge of header

8. **Logo Assets** (all in the `presentation/` directory — same working directory as the script):
   - `ku_emblem_clean.png` — KU emblem for title slide
   - `kucse_full_logo.png` — Full CSE discipline logo for content slide headers

### ImageMobject Usage for Output Figures

When embedding figures from `outputs/figures/`, use **relative paths from the presentation directory**:

```python
# From within presentation_slides.py (cwd = presentation/)
img = ImageMobject("../outputs/figures/rf_workflow_confusion_matrix.png")
img.set(height=3.5)  # Control size
```

The figures to embed:
- `../outputs/figures/rf_workflow_multiclass_distribution.png` → Slide 5
- `../outputs/figures/rf_workflow_binary_class_distribution.png` → Slide 5
- `../outputs/figures/rf_workflow_confusion_matrix.png` → Slide 10
- `../outputs/figures/rf_workflow_roc_curves.png` → Slide 11
- `../outputs/figures/rf_workflow_feature_importance.png` → Slide 11

### Animation Guidelines

- **Slide transitions**: Keep them simple — `FadeOut` old content + `FadeIn` new content. Don't over-animate.
- **Within-slide animations**: Use 2–3 `self.play()` calls per slide max:
  1. Header + footer appear
  2. Title + accent line appear
  3. Main content appears (all at once or in 1–2 groups)
- **Don't**: Use `Write()` for long text blocks (it's painfully slow). Use `FadeIn()` instead. Reserve `Write()` only for short titles.
- **Don't**: Use `Create()` for every small line/accent. Batch similar elements.

### Code Structure Guidelines

- Update `TOTAL_SLIDES = 12`
- Keep the existing `build_footer()` and `build_header()` helper functions — they work well
- Reuse the `make_threat_card()` helper for card-style content blocks
- Create a new helper for the 2-column panel layout (Problem/Objective, RF explanation/parameters, etc.)
- Each slide block should have a clear comment header: `# SLIDE N: Title`
- Clean up after each slide: store the content group, then `FadeOut` it at the start of the next slide

---

## File Paths Summary

```
Repository Root: /home/noobcod3r-rtx/Documents/GitHub/TON_IOT_NETWORK_IS_Lab_CSEKU/

File to Modify:
  presentation/presentation_slides.py

Logo Assets (in presentation/):
  presentation/ku_emblem_clean.png
  presentation/kucse_full_logo.png

Output Figures (referenced as ../outputs/figures/ from presentation/):
  outputs/figures/rf_workflow_multiclass_distribution.png
  outputs/figures/rf_workflow_binary_class_distribution.png
  outputs/figures/rf_workflow_confusion_matrix.png
  outputs/figures/rf_workflow_roc_curves.png
  outputs/figures/rf_workflow_feature_importance.png

Reference Data (for correct numbers):
  outputs/reports/pure_gpu_benchmark_results.json
  outputs/reports/rf_workflow_summary.json
  outputs/reports/rf_workflow_feature_importance.csv
  outputs/reports/rf_workflow_run_config.json
  outputs/reports/rf_workflow_classification_report.txt

Senior's Presentation (for structural inspiration):
  Dataset Details/220216_220222.pdf  (12 slides, PptxGenJS-generated)

Design Guide:
  presentation/.agents.md

Render Script:
  presentation/render_presentation.sh
```

---

## Final Checklist for Gemini

Before considering the rewrite done, verify:

- [ ] Exactly 12 slides with `TOTAL_SLIDES = 12`
- [ ] All numbers match the actual benchmark data listed above (NOT the old hardcoded values)
- [ ] Title slide has correct instructor: **Dr. Anupam Kumar Bairagi, Professor**
- [ ] Slide 2 has the "Presented By / Presented To" layout
- [ ] Slides 5, 10, 11 embed actual PNG figures via `ImageMobject("../outputs/figures/...")`
- [ ] Slide 6 has the 6-step preprocessing pipeline (not a wall of text)
- [ ] Slide 7 has the horizontal ML pipeline flowchart
- [ ] Slide 8 explains Random Forest specifically (not GPU hardware)
- [ ] GPU hardware is mentioned briefly in Slide 9 results, not as a standalone slide
- [ ] Feature importance uses correct ranking: conn_state #1 (30.77%), src_port #2 (23.57%), ts #3 (13.93%)
- [ ] Slide 12 is a clean "Thank You / Any Questions?" with the GitHub repo link
- [ ] Camera background uses `ManimColor(CARD_BG)`, not a raw string
- [ ] No `Transform()` between text mobjects — use `FadeOut`/`FadeIn` instead
- [ ] `self.wait(0.2)` before every `self.next_slide()` call
- [ ] Footer shows correct slide number on every slide
- [ ] All `ImageMobject` paths are relative from `presentation/` working directory
- [ ] Code has clear `# SLIDE N: Title` comment blocks
- [ ] The class is still named `TonIoTPresentation` (for render script compatibility)
- [ ] Animations are snappy — no excessive `Write()` on long text blocks

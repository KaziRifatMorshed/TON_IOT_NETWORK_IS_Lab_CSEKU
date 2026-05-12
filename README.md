# TON IoT Network Intrusion Detection

Random Forest based intrusion detection workflow for the TON_IoT network dataset.

The final workflow classifies network traffic into:

- `normal`
- `dos`
- `ddos`

It loads `data/dataset.csv`, preprocesses network features, trains a Random Forest classifier, evaluates the model, and writes reports, plots, and the trained model artifact.

## Project Structure

```text
.
|-- README.md
|-- requirements.txt
|-- setup_windows_cmd.bat
|-- config.py
|-- data/
|   |-- .gitkeep
|   `-- dataset.csv              # local dataset
|-- Dataset Details/
|   `-- Ton_IoT Network Dataset.pdf
|-- src/
|   |-- data_loader.py
|   |-- preprocessing.py
|   |-- random_forest_workflow.py # final workflow
|   |-- train_ml.py              # auxiliary model experiments
|   |-- train_dl.py              # auxiliary MLP experiments
|   |-- evaluate.py
|   `-- utils.py
|-- tests/
|   `-- test_random_forest_workflow.py
|-- models/
`-- outputs/
    |-- figures/
    `-- reports/
```

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

## Setup

Windows CMD:

```cmd
setup_windows_cmd.bat
```

Manual setup:

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
python -m ensurepip --upgrade
python -m pip install --upgrade "pip<26"
python -m pip install -r requirements.txt
```

PowerShell users can run the same environment Python directly:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m ensurepip --upgrade
.\.venv\Scripts\python.exe -m pip install --upgrade "pip<26"
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run Final Random Forest Workflow

Full run:

```cmd
.venv\Scripts\python.exe -m src.random_forest_workflow
```

Fast smoke test:

```cmd
.venv\Scripts\python.exe -m src.random_forest_workflow --sample-size 3000 --n-estimators 20 --n-jobs 1
```

## Workflow Process

`src.random_forest_workflow` performs:

1. Load TON_IoT network data.
2. Save binary and multiclass distribution plots when target columns exist.
3. Remove duplicate rows.
4. Normalize target labels to `normal`, `dos`, and `ddos`.
5. Drop leakage columns such as `label`.
6. Convert IP address columns into numeric high/low parts.
7. Label-encode categorical columns.
8. Replace missing and infinite values.
9. Drop constant columns.
10. Use stratified 80/20 train-test split.
11. Train Random Forest with the default project parameters.
12. Evaluate on the held-out test set.
13. Save model, metrics, plots, feature importance, and run configuration.

## Outputs

Generated files are ignored by git.

Model:

```text
models/rf_network_classifier.joblib
```

Reports:

```text
outputs/reports/rf_workflow_classification_report.txt
outputs/reports/rf_workflow_summary.json
outputs/reports/rf_workflow_run_config.json
outputs/reports/rf_workflow_feature_importance.csv
```

Figures:

```text
outputs/figures/rf_workflow_binary_class_distribution.png
outputs/figures/rf_workflow_multiclass_distribution.png
outputs/figures/rf_workflow_confusion_matrix.png
outputs/figures/rf_workflow_feature_importance.png
outputs/figures/rf_workflow_roc_curves.png
```

## Metrics

The final report includes:

- accuracy
- precision macro and weighted
- recall macro and weighted
- F1 macro and weighted
- ROC-AUC one-vs-rest macro and weighted
- Matthews correlation coefficient
- per-class precision, recall, F1-score, and support

Use macro F1, recall, ROC-AUC, and MCC alongside accuracy because intrusion datasets can be class-imbalanced.

## Tests

Run unit tests:

```cmd
.venv\Scripts\python.exe -m unittest discover -s tests
```

The tests cover:

- default dataset path
- removal of the tuning CLI
- default Random Forest parameters
- metric generation
- preprocessing leakage removal
- distribution counts
- ROC curve output
- run configuration structure

## Auxiliary Scripts

These scripts remain available for experiments, but they are not the final workflow:

```cmd
.venv\Scripts\python.exe -m src.train_ml --task binary
.venv\Scripts\python.exe -m src.train_ml --task multiclass
.venv\Scripts\python.exe -m src.train_dl --task binary --epochs 20 --batch-size 512
.venv\Scripts\python.exe -m src.evaluate --task binary --model-path models\binary_random_forest.joblib
```

## Troubleshooting

`FileNotFoundError: Dataset not found`

Place the dataset at:

```text
data/dataset.csv
```

`ModuleNotFoundError`

Reinstall dependencies inside the virtual environment:

```cmd
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`Fatal error in launcher`

Run pip through Python:

```cmd
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

NumPy, pandas, or sklearn binary import errors:

```cmd
rmdir /s /q .venv
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade "pip<26"
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Out-of-memory or slow training:

```cmd
.venv\Scripts\python.exe -m src.random_forest_workflow --sample-size 50000 --n-jobs 1
```

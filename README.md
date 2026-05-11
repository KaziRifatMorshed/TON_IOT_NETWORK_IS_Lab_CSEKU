# TON_IoT Network Intrusion Detection

This project is a complete Python ML/DL pipeline for intrusion detection on the TON_IoT Network dataset using `dataset_cleaned.csv`.

TON_IoT is an IoT/IIoT cybersecurity dataset designed for AI-based intrusion detection systems. This project focuses on network traffic classification with two supervised tasks:

- Binary classification using `label`: normal vs attack
- Multi-class classification using `type`: attack category

Supported attack context includes DoS, DDoS, Backdoor, Injection, Scanning, MITM, Ransomware, XSS, and Password attacks.

## Folder Structure

```text
.
|-- README.md
|-- requirements.txt
|-- requirements-notebooks.txt
|-- requirements-kaggle.txt
|-- config.py
|-- setup_windows_cmd.bat
|-- setup_windows_powershell.ps1
|-- data/
|   `-- dataset_cleaned.csv
|-- src/
|   |-- __init__.py
|   |-- data_loader.py
|   |-- preprocessing.py
|   |-- train_ml.py
|   |-- train_dl.py
|   |-- evaluate.py
|   `-- utils.py
|-- notebooks/
|   |-- 01_exploration.ipynb
|   `-- 02_training.ipynb
|-- models/
`-- outputs/
    |-- figures/
    `-- reports/
```

## Dataset

Download the Kaggle dataset from:

https://www.kaggle.com/datasets/profulina/ton-iot/versions/5?select=dataset_cleaned.csv

Recommended Kaggle file layout:

```text
data/dataset_cleaned.csv
```

This project also supports your local split CSV layout. Place these files in the project root:

```text
DDOS.csv
DOS.csv
Normal.csv
```

If `data/dataset_cleaned.csv` is missing, the loader automatically combines those three files and uses their existing `label` and `type` columns.

Optional Kaggle CLI download:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-kaggle.txt
kaggle datasets download -d profulina/ton-iot -p data --unzip
```

If Kaggle downloads more than one file, make sure `dataset_cleaned.csv` is directly inside the `data/` folder.

## Setup on Windows CMD

Recommended one-command setup:

```cmd
setup_windows_cmd.bat
```

Manual CMD setup:

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
python -m ensurepip --upgrade
python -m pip install --upgrade "pip<26"
python -m pip install -r requirements.txt
```

You can also skip activation entirely and use the venv Python directly:

```cmd
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m src.train_ml --task binary
```

Optional notebook support:

```cmd
.venv\Scripts\python.exe -m pip install -r requirements-notebooks.txt
.venv\Scripts\python.exe -m ipykernel install --user --name ton-iot-ids --display-name "TON IoT IDS"
```

## Setup on Windows PowerShell

Recommended one-command setup:

```powershell
.\setup_windows_powershell.ps1
```

Manual PowerShell setup:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m ensurepip --upgrade
python -m pip install --upgrade "pip<26"
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1
```

## Train Classical ML Models

Binary classification:

```cmd
.venv\Scripts\python.exe -m src.train_ml --task binary
```

Multi-class classification:

```cmd
.venv\Scripts\python.exe -m src.train_ml --task multiclass
```

Train selected models only:

```cmd
.venv\Scripts\python.exe -m src.train_ml --task binary --models logistic,random_forest,xgboost
```

Try SMOTE for class imbalance:

```cmd
.venv\Scripts\python.exe -m src.train_ml --task multiclass --use-smote
```

Train SVM on a smaller sample:

```cmd
.venv\Scripts\python.exe -m src.train_ml --task binary --models svm --sample-size 20000
```

## Run the PDF Random Forest Workflow

The workflow from `Network Classification Workflow.pdf` is implemented as a dedicated
three-class Random Forest script for `normal`, `dos`, and `ddos` traffic. It removes
duplicates, converts IP addresses to numeric high/low parts, label-encodes categorical
columns, removes constant columns, performs an 80/20 stratified split, evaluates with
precision/recall/F1/support, writes feature importance, and saves the trained model.

Run the full dataset:

```cmd
.venv\Scripts\python.exe -m src.random_forest_workflow
```

Run with GridSearchCV hyperparameter tuning:

```cmd
.venv\Scripts\python.exe -m src.random_forest_workflow --tune
```

Smoke-test quickly on a smaller sample:

```cmd
.venv\Scripts\python.exe -m src.random_forest_workflow --sample-size 3000 --n-estimators 20 --n-jobs 1
```

Workflow outputs:

- `models/rf_network_classifier.joblib`
- `outputs/reports/rf_workflow_classification_report.txt`
- `outputs/reports/rf_workflow_summary.json`
- `outputs/reports/rf_workflow_feature_importance.csv`
- `outputs/figures/rf_workflow_confusion_matrix.png`
- `outputs/figures/rf_workflow_feature_importance.png`

## Train Deep Learning Model

Binary MLP:

```cmd
.venv\Scripts\python.exe -m src.train_dl --task binary --epochs 20 --batch-size 512
```

Multi-class MLP:

```cmd
.venv\Scripts\python.exe -m src.train_dl --task multiclass --epochs 30 --batch-size 512
```

Use a custom hidden layer layout:

```cmd
.venv\Scripts\python.exe -m src.train_dl --task multiclass --hidden-layers 256,128,64
```

## Evaluate a Saved Model

Classical ML model:

```cmd
.venv\Scripts\python.exe -m src.evaluate --task binary --model-path models\binary_random_forest.joblib
```

Deep learning model:

```cmd
.venv\Scripts\python.exe -m src.evaluate --task multiclass --model-path models\multiclass_mlp.pt
```

## Expected Outputs

Training and evaluation create:

- Trained models in `models/`
- Metrics JSON files in `outputs/reports/`
- Classification reports in `outputs/reports/`
- Class distribution plots in `outputs/figures/`
- Correlation heatmaps in `outputs/figures/`
- Confusion matrices in `outputs/figures/`
- Model comparison charts in `outputs/figures/`
- Feature importance charts for Random Forest and XGBoost when available

## Preprocessing

The pipeline:

- Checks that `dataset_cleaned.csv` exists
- Strips whitespace from column names
- Handles missing numeric values with median imputation
- Handles missing categorical values with most-frequent imputation
- Drops target-leaking columns not used by the active task
- Drops common high-cardinality identifier columns such as IPs, UIDs, timestamps, URLs, DNS queries, and host fields
- Drops very high-cardinality categorical columns by unique-value ratio
- Encodes categorical features with `OneHotEncoder`
- Scales numeric features with `StandardScaler`
- Uses stratified train-test split with `random_state=42`

## Models

Classical ML:

- Logistic Regression
- Random Forest
- XGBoost if installed
- Linear SVM when requested

Deep Learning:

- PyTorch MLP for tabular feature vectors

Class imbalance is handled with balanced class weights for compatible ML models and weighted cross-entropy loss for PyTorch.

## Evaluation Metrics

The project reports:

- Accuracy
- Precision
- Recall
- F1-score
- Macro F1
- Weighted F1
- Matthews Correlation Coefficient
- Confusion Matrix
- Classification Report
- ROC-AUC for binary classification when probabilities or decision scores are available

Accuracy alone can be misleading on intrusion detection datasets, so use macro F1, weighted F1, recall, and MCC when comparing models.

## Troubleshooting

`FileNotFoundError: Dataset not found`

Place the CSV at:

```text
data/dataset_cleaned.csv
```

`ModuleNotFoundError`

Make sure your virtual environment is activated and reinstall dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Windows long path error while installing Jupyter

If setup fails inside `jupyterlab_widgets` or a path under `.venv\share\jupyter\labextensions`, skip notebook dependencies and use the command-line scripts. The default `requirements.txt` no longer installs Jupyter packages.

For notebooks, either enable Windows Long Path support or move the project to a shorter path such as:

```text
C:\ton-iot
```

NumPy / pandas / sklearn binary import errors

If you see messages about a package compiled against NumPy 1.x while NumPy 2.x is installed, recreate the virtual environment and reinstall this project's pinned requirements:

```powershell
deactivate
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade "pip<26"
python -m pip install -r requirements.txt
```

If you are using CMD, do not run `Activate.ps1`. Use:

```cmd
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

If `pip install ...` says `Fatal error in launcher`, run pip through Python:

```cmd
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`xgboost is not installed`

The training script skips XGBoost automatically if the package is unavailable. Install it with:

```powershell
.\.venv\Scripts\python.exe -m pip install xgboost
```

Out-of-memory errors

Use a smaller sample while testing:

```cmd
.venv\Scripts\python.exe -m src.train_ml --task binary --sample-size 50000
.venv\Scripts\python.exe -m src.train_dl --task binary --sample-size 50000
```

Slow SVM training

SVM can be slow on large tabular datasets. Use `--sample-size` or prefer Logistic Regression, Random Forest, and XGBoost.

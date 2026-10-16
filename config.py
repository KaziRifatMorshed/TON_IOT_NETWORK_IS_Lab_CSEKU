from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "data"
DATA_FILE = DATA_DIR / "dataset.csv"
TRAIN_DATA_FILE = DATA_DIR / "train_normal_dos_ddos.csv"
TEST_DATA_FILE = DATA_DIR / "test_normal_dos_ddos.csv"
NORMAL_DOS_DDOS_FILE = DATA_DIR / "dataset_normal_dos_ddos.csv"

LOCAL_CLASS_FILES = {
    "ddos": PROJECT_ROOT / "DDOS.csv",
    "dos": PROJECT_ROOT / "DOS.csv",
    "normal": PROJECT_ROOT / "Normal.csv",
}

MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
REPORTS_DIR = OUTPUTS_DIR / "reports"

RANDOM_STATE = 42
TEST_SIZE = 0.2

BINARY_TARGET = "label"
MULTICLASS_TARGET = "type"

ATTACK_CLASSES = [
    "normal",
    "DoS",
    "DDoS",
    "Backdoor",
    "Injection",
    "Scanning",
    "MITM",
    "Ransomware",
    "XSS",
    "Password",
]

HIGH_CARDINALITY_NAME_HINTS = [
    "uid",
    "id.orig_h",
    "id.resp_h",
    "orig_h",
    "resp_h",
    "src_ip",
    "dst_ip",
    "source_ip",
    "destination_ip",
    "ip",
    "mac",
    "timestamp",
    "time",
    "ts",
    "date",
    "url",
    "uri",
    "query",
    "dns",
    "host",
    "domain",
    "user_agent",
]

MAX_CATEGORICAL_UNIQUE_RATIO = 0.5
MAX_CATEGORICAL_UNIQUE_VALUES = 1000

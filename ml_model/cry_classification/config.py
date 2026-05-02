from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
AUGMENTED_DIR = DATA_DIR / "augmented"

FEATURES_DIR = BASE_DIR / "features"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

SAMPLE_RATE = 16000
DURATION_SEC = 3.0
NUM_SAMPLES = int(SAMPLE_RATE * DURATION_SEC)

N_FFT = 512
HOP_LENGTH = 375
N_MELS = 128
N_MFCC = 40
SPECTROGRAM_KEEP_BINS = 57
TARGET_FRAMES = 128

LABELS = ["hungry", "tired", "discomfort", "belly_pain", "diaper", "burping"]
LABEL_TO_ID = {label: idx for idx, label in enumerate(LABELS)}
ID_TO_LABEL = {idx: label for label, idx in LABEL_TO_ID.items()}

RANDOM_SEED = 42

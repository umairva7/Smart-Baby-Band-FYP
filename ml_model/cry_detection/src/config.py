import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
MODELS_DIR = os.path.join(BASE_DIR, '..', 'models')

# Audio Parameters
SAMPLE_RATE = 16000
DURATION = 5 # seconds
N_MFCC = 40 # Number of mel-frequency cepstral coefficients

# Training Parameters
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 0.001
TEST_SPLIT = 0.2
RANDOM_SEED = 42

# Ensure directories exist
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

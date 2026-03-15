import os
import numpy as np
from pathlib import Path
import librosa
from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix, classification_report
import tensorflow as tf
from tensorflow.keras import layers, models
import pickle
import json
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_DIR = Path("../data/raw/model 1/audio")
MODELS_DIR = Path("../models")
LOGS_DIR = Path("../logs")

# Create directories
MODELS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Audio parameters
SAMPLING_RATE = 16000
N_MFCC = 13
FRAMES_PER_SAMPLE = 128  # 2 seconds at 16kHz with 10ms hop
FRAME_LENGTH = int(0.025 * SAMPLING_RATE)  # 25 ms
HOP_LENGTH = int(0.010 * SAMPLING_RATE)  # 10 ms

# Training parameters
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 0.001

# Random seed for reproducibility
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
tf.random.set_seed(RANDOM_SEED)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def log_message(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{timestamp}] {msg}"
    print(full_msg)
    return full_msg


def extract_mfcc(audio_path, target_shape=(FRAMES_PER_SAMPLE, N_MFCC)):
    """
    Extract MFCC features from audio file.

    Args:
        audio_path: Path to audio file
        target_shape: Target shape (frames, coefficients)

    Returns:
        mfcc: (frames, n_mfcc) array or None if error
        valid: Boolean indicating success
    """
    try:
        # Load audio
        y, sr = librosa.load(audio_path, sr=SAMPLING_RATE, duration=3.0)

        # Skip very short audio
        if len(y) < SAMPLING_RATE * 0.5:  # Less than 0.5 sec
            return None, False

        # Extract MFCC
        mfcc = librosa.feature.mfcc(
            y=y,
            sr=SAMPLING_RATE,
            n_mfcc=N_MFCC,
            n_fft=FRAME_LENGTH,
            hop_length=HOP_LENGTH
        )

        # Transpose to (frames, coefficients)
        mfcc = mfcc.T

        # Pad or truncate to target shape
        if mfcc.shape[0] < target_shape[0]:
            pad_width = ((0, target_shape[0] - mfcc.shape[0]), (0, 0))
            mfcc = np.pad(mfcc, pad_width, mode='constant', constant_values=0)
        else:
            mfcc = mfcc[:target_shape[0], :]

        return mfcc.astype(np.float32), True

    except Exception as e:
        return None, False


# ============================================================================
# DATA LOADING
# ============================================================================

def load_split(split_name):
    """
    Load ICSD split (train, validation, or test).

    Args:
        split_name: "train", "validation", or "test"

    Returns:
        X: (n_samples, 128, 13) MFCC features
        y: (n_samples,) labels (1=cry, 0=snoring)
        sample_count: dict with counts per category
    """

    split_dir = DATA_DIR / split_name

    if not split_dir.exists():
        log_message(f"ERROR: Directory not found: {split_dir}")
        return None, None, None

    X = []
    y = []
    sample_count = {
        'cry': 0,
        'snoring': 0,
        'total': 0
    }

    log_message(f"  Searching for audio files in {split_dir}...")
    files = list(split_dir.rglob("*.wav"))
    
    if len(files) == 0:
        log_message(f"ERROR: No .wav files found in {split_dir}")
        return None, None, None

    log_message(f"  Found {len(files)} files. Extracting features...")

    successful = 0
    for i, audio_file in enumerate(files):
        # Infer label from filename
        filename = audio_file.name
        label = None
        if "Infantcry" in filename:
            label = 1
            sample_count['cry'] += 1
        elif "Snoring" in filename:
            label = 0
            sample_count['snoring'] += 1
        
        if label is not None:
            mfcc, valid = extract_mfcc(audio_file)
            if valid:
                X.append(mfcc)
                y.append(label)
                successful += 1

        if (i + 1) % 500 == 0 and len(files) > 500:
            log_message(f"    Processed {i + 1}/{len(files)} files, {successful} successful")

    if len(X) == 0:
        log_message(f"ERROR: No valid audio files processed from {split_dir}")
        return None, None, None

    X = np.array(X)
    y = np.array(y)
    sample_count['total'] = len(X)

    log_message(f"    ✓ Loaded {successful} samples ({sample_count['cry']} cry, {sample_count['snoring']} snoring)")

    return X, y, sample_count


def load_all_splits():
    """Load train, validation, and test sets"""

    log_message("=" * 70)
    log_message("LOADING ICSD DATASET (Using Pre-Made Splits)")
    log_message("=" * 70)

    # Train set
    log_message("\nTRAIN SET:")
    X_train, y_train, train_counts = load_split("train")
    if X_train is None:
        return None

    log_message(f"  Shape: {X_train.shape}")
    log_message(f"  Crying: {np.sum(y_train == 1):5d}, Snoring: {np.sum(y_train == 0):5d}")

    # Validation set
    log_message("\nVALIDATION SET:")
    X_val, y_val, val_counts = load_split("validation")
    if X_val is None:
        return None

    log_message(f"  Shape: {X_val.shape}")
    log_message(f"  Crying: {np.sum(y_val == 1):5d}, Snoring: {np.sum(y_val == 0):5d}")

    # Test set
    log_message("\nTEST SET:")
    X_test, y_test, test_counts = load_split("test")
    if X_test is None:
        return None

    log_message(f"  Shape: {X_test.shape}")
    log_message(f"  Crying: {np.sum(y_test == 1):5d}, Snoring: {np.sum(y_test == 0):5d}")

    return {
        'X_train': X_train, 'y_train': y_train, 'train_counts': train_counts,
        'X_val': X_val, 'y_val': y_val, 'val_counts': val_counts,
        'X_test': X_test, 'y_test': y_test, 'test_counts': test_counts
    }


# ============================================================================
# DATA BALANCING
# ============================================================================

def balance_dataset(X, y):
    """
    Balance dataset by oversampling minority class (crying).

    Why: Real world has ~90% non-cry, but we need ~50-50 for training
    """
    cry_indices = np.where(y == 1)[0]
    non_cry_indices = np.where(y == 0)[0]

    log_message(f"\nBEFORE BALANCING:")
    log_message(f"  Crying:  {len(cry_indices):5d}")
    log_message(f"  Snoring: {len(non_cry_indices):5d}")

    # Oversample minority (crying) to match majority (snoring)
    n_majority = len(non_cry_indices)
    oversample_indices = np.random.choice(cry_indices, size=n_majority, replace=True)
    balanced_indices = np.concatenate([non_cry_indices, oversample_indices])

    # Shuffle
    np.random.shuffle(balanced_indices)

    X_balanced = X[balanced_indices]
    y_balanced = y[balanced_indices]

    log_message(f"\nAFTER BALANCING:")
    log_message(f"  Crying:  {np.sum(y_balanced == 1):5d}")
    log_message(f"  Snoring: {np.sum(y_balanced == 0):5d}")

    return X_balanced, y_balanced


# ============================================================================
# MODEL BUILDING
# ============================================================================

def build_model(input_shape):
    """
    Build CNN model for cry detection.

    Architecture:
      - Input: (128, 13) MFCC features
      - Conv2D 32 filters → Conv2D 64 filters
      - Global average pooling
      - Dense layers with dropout
      - Sigmoid output (binary classification)

    Total parameters: ~40K (fits easily on ESP32)
    """
    model = models.Sequential([
        # Input
        layers.Input(shape=input_shape),
        layers.Reshape((*input_shape, 1)),  # Add channel dimension

        # First convolutional block
        layers.Conv2D(32, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D((2, 1)),

        # Second convolutional block
        layers.Conv2D(64, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D((2, 1)),

        # Global pooling and dense layers
        layers.GlobalAveragePooling2D(),
        layers.Dense(32, activation='relu'),
        layers.Dropout(0.3),

        # Output
        layers.Dense(1, activation='sigmoid')  # Binary classification
    ])

    return model


# ============================================================================
# MODEL TRAINING
# ============================================================================

def train_model(X_train, X_val, y_train, y_val, input_shape):
    """
    Train the CNN model.

    Args:
        X_train, y_train: Training data
        X_val, y_val: Validation data
        input_shape: Shape of input features

    Returns:
        model: Trained model
        history: Training history
    """

    log_message("\n" + "=" * 70)
    log_message("TRAINING CNN MODEL")
    log_message("=" * 70)

    model = build_model(input_shape)

    # Compile
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss='binary_crossentropy',
        metrics=['accuracy',
                 tf.keras.metrics.Precision(name='precision'),
                 tf.keras.metrics.Recall(name='recall')]
    )

    log_message("\nModel Architecture:")
    model.summary()

    # Class weights (adjusted to improve precision)
    class_weights = {0: 1.0, 1: 1.5}  # Between 2.0 and 1.0

    log_message(f"\nTraining Configuration:")
    log_message(f"  Epochs:        {EPOCHS}")
    log_message(f"  Batch size:    {BATCH_SIZE}")
    log_message(f"  Learning rate: {LEARNING_RATE}")
    log_message(f"  Class weights: {class_weights}")

    log_message(f"\nStarting training...")

    # Train
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        class_weight=class_weights,
        verbose=1
    )

    return model, history


# ============================================================================
# MODEL EVALUATION
# ============================================================================

def evaluate_model(model, X_test, y_test):
    """
    Evaluate model on test set.

    Args:
        model: Trained model
        X_test, y_test: Test data

    Returns:
        metrics: dict with F1, precision, recall
    """

    log_message("\n" + "=" * 70)
    log_message("EVALUATION ON TEST SET (ICSD Real Data)")
    log_message("=" * 70)

    # Get predictions
    y_pred_probs = model.predict(X_test).flatten()
    y_pred = (y_pred_probs > 0.5).astype(int)

    # Calculate metrics
    f1 = f1_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)

    log_message(f"\nMetrics:")
    log_message(f"  F1 Score:  {f1:.4f}")
    log_message(f"  Precision: {precision:.4f}")
    log_message(f"  Recall:    {recall:.4f}")

    log_message(f"\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    log_message(f"  True Negatives:  {cm[0, 0]:5d}  |  False Positives: {cm[0, 1]:5d}")
    log_message(f"  False Negatives: {cm[1, 0]:5d}  |  True Positives:  {cm[1, 1]:5d}")

    log_message(f"\nClassification Report:")
    log_message(classification_report(y_test, y_pred, target_names=['Snoring', 'Crying']))

    return {
        'f1': f1,
        'precision': precision,
        'recall': recall,
        'y_pred': y_pred,
        'y_pred_probs': y_pred_probs
    }


# ============================================================================
# SAVE MODELS AND RESULTS
# ============================================================================

def save_model(model, metrics):
    """Save trained model and results"""

    # Save model
    model_path = MODELS_DIR / "cnn_model.h5"
    model.save(model_path)
    log_message(f"\n✓ Model saved to {model_path}")

    # Save metrics
    metrics_path = MODELS_DIR / "training_metrics.json"
    metrics_to_save = {
        'f1_score': float(metrics['f1']),
        'precision': float(metrics['precision']),
        'recall': float(metrics['recall']),
        'timestamp': datetime.now().isoformat(),
        'config': {
            'sampling_rate': SAMPLING_RATE,
            'n_mfcc': N_MFCC,
            'frames_per_sample': FRAMES_PER_SAMPLE,
            'epochs': EPOCHS,
            'batch_size': BATCH_SIZE,
            'learning_rate': LEARNING_RATE
        }
    }

    with open(metrics_path, 'w') as f:
        json.dump(metrics_to_save, f, indent=2)

    log_message(f"✓ Metrics saved to {metrics_path}")

    return model_path


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main training pipeline"""

    log_message("=" * 70)
    log_message("ICSD CRY DETECTION - TRAINING PIPELINE")
    log_message("=" * 70)

    # Check if dataset exists
    if not DATA_DIR.exists():
        log_message(f"\nERROR: Dataset not found at {DATA_DIR}")
        log_message(f"Please ensure your dataset is placed in the 'data/raw/model 1/audio' directory.")
        return

    # Load data
    data = load_all_splits()
    if data is None:
        log_message("\nFailed to load data. Exiting.")
        return

    X_train = data['X_train']
    y_train = data['y_train']
    X_val = data['X_val']
    y_val = data['y_val']
    X_test = data['X_test']
    y_test = data['y_test']

    # Balance training set
    log_message("\n" + "=" * 70)
    log_message("BALANCING TRAINING SET")
    log_message("=" * 70)
    X_train, y_train = balance_dataset(X_train, y_train)

    # Train model
    input_shape = X_train.shape[1:]
    model, history = train_model(X_train, X_val, y_train, y_val, input_shape)

    # Evaluate
    metrics = evaluate_model(model, X_test, y_test)

    # Save
    model_path = save_model(model, metrics)

    # Summary
    log_message("\n" + "=" * 70)
    log_message("TRAINING COMPLETE")
    log_message("=" * 70)
    log_message(f"\nResults:")
    log_message(f"  F1 Score:  {metrics['f1']:.4f}")
    log_message(f"  Precision: {metrics['precision']:.4f}")
    log_message(f"  Recall:    {metrics['recall']:.4f}")
    log_message(f"\nModel saved to: {model_path}")

    if metrics['f1'] < 0.60:
        log_message(f"\n⚠️  F1 score is lower than expected (< 0.60)")
        log_message(f"Consider:")
        log_message(f"  - Increase EPOCHS (currently {EPOCHS})")
        log_message(f"  - Adjust LEARNING_RATE (currently {LEARNING_RATE})")
        log_message(f"  - Check data quality (plot some samples)")
        log_message(f"  - Verify MFCC extraction")
    else:
        log_message(f"\n✅ Training successful!")
        log_message(f"\nNext steps:")
        log_message(f"  1. Run: python ml_model/quantize.py")
        log_message(f"  2. Convert model to TFLite for ESP32")
        log_message(f"  3. Deploy on edge device")


if __name__ == "__main__":
    main()
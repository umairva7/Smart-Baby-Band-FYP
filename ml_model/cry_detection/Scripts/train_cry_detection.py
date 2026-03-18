import os
import numpy as np
from pathlib import Path
from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix, classification_report
import tensorflow as tf
from tensorflow.keras import layers, models, regularizers
import pickle
import json
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

PROCESSED_DIR = Path("../data/processed")
MODELS_DIR = Path("../models/cry_detection")
LOGS_DIR = Path("../logs")

# Create directories
MODELS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Training parameters
BATCH_SIZE = 32
EPOCHS = 100
LEARNING_RATE = 0.0005
PATIENCE_EARLY_STOP = 15
PATIENCE_LR_REDUCE = 7

# Random seed
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


# ============================================================================
# LOAD PREPROCESSED DATA
# ============================================================================

def load_split(split_name):
    """Load preprocessed features from disk."""
    split_dir = PROCESSED_DIR / split_name
    
    X_path = split_dir / f"X_{split_name}.npy"
    y_path = split_dir / f"y_{split_name}.npy"
    
    if not X_path.exists() or not y_path.exists():
        log_message(f"ERROR: Preprocessed files not found for {split_name}")
        log_message(f"  Expected: {X_path}")
        log_message(f"  Expected: {y_path}")
        return None, None
    
    X = np.load(X_path)
    y = np.load(y_path)
    
    log_message(f"  ✓ Loaded {split_name}: X={X.shape}, y={y.shape}")
    log_message(f"    - Crying:  {np.sum(y == 1)}")
    log_message(f"    - Snoring: {np.sum(y == 0)}")
    
    return X, y


def load_all_splits():
    """Load all preprocessed splits."""
    log_message("=" * 70)
    log_message("LOADING PREPROCESSED DATA")
    log_message("=" * 70)

    log_message(f"\nProcessed data directory: {PROCESSED_DIR}")

    # Train set
    log_message("\nTRAIN SET:")
    X_train, y_train = load_split("train")
    if X_train is None:
        return None

    # Validation set
    log_message("\nVALIDATION SET:")
    X_val, y_val = load_split("validation")
    if X_val is None:
        return None

    # Test set
    log_message("\nTEST SET:")
    X_test, y_test = load_split("test")
    if X_test is None:
        return None

    return {
        'X_train': X_train, 'y_train': y_train,
        'X_val': X_val, 'y_val': y_val,
        'X_test': X_test, 'y_test': y_test
    }


# ============================================================================
# DATA BALANCING
# ============================================================================

def balance_dataset(X, y):
    """Balance dataset by oversampling minority class (crying)."""
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

def augment_mfcc(X, y):
    """
    Simple data augmentation for MFCC features.
    Applies stronger time masking, frequency masking, and noise.
    Only used during training — no impact on ESP32 inference.
    """
    X_aug = X.copy()
    n_samples, n_frames, n_mfcc = X.shape
    
    augmented_X = [X]
    augmented_y = [y]
    
    # Time masking: zero out random time segments
    X_time_masked = X.copy()
    for i in range(n_samples):
        mask_len = np.random.randint(10, 30)  # mask 10-30 frames
        mask_start = np.random.randint(0, max(1, n_frames - mask_len))
        X_time_masked[i, mask_start:mask_start + mask_len, :] = 0
    augmented_X.append(X_time_masked)
    augmented_y.append(y)
    
    # Frequency masking: zero out random MFCC bands
    X_freq_masked = X.copy()
    for i in range(n_samples):
        mask_len = np.random.randint(1, 4)  # mask 1-3 coefficients
        mask_start = np.random.randint(0, max(1, n_mfcc - mask_len))
        X_freq_masked[i, :, mask_start:mask_start + mask_len] = 0
    augmented_X.append(X_freq_masked)
    augmented_y.append(y)
    
    # Add stronger gaussian noise
    X_noisy = X + np.random.normal(0, 0.2, X.shape).astype(np.float32)
    augmented_X.append(X_noisy)
    augmented_y.append(y)
    
    X_combined = np.concatenate(augmented_X, axis=0)
    y_combined = np.concatenate(augmented_y, axis=0)
    
    # Shuffle
    indices = np.random.permutation(len(X_combined))
    return X_combined[indices], y_combined[indices]


def build_model(input_shape):
    """
    Build CNN model for ESP32 deployment with HEAVY regularization.
    
    Architecture (ESP32-compatible, NO MEAN/STRIDED_SLICE ops):
      Input (128, 39, 1)  ← 13 MFCC + 13 delta + 13 delta-delta
      - Conv2D(8, L2)   → BN → ReLU → MaxPool(2,2)
      - Conv2D(16, L2)  → BN → ReLU → MaxPool(2,2)
      - Conv2D(16, L2)  → BN → ReLU → MaxPool(2,2)
      - Flatten()       → 1024 features
      - Dense(32, L2)   → ReLU → Dropout(0.5)
      - Dense(16, L2)   → ReLU → Dropout(0.5)
      - Dense(1)        → Sigmoid
    
    Regularization: Heavy L2 (0.002) + strong Dropout (0.5)
    """
    
    l2_reg = regularizers.l2(0.002)
    
    model = models.Sequential([
        # Input with explicit 4D shape
        layers.Input(shape=input_shape),

        # Conv Block 1 - 8 filters
        layers.Conv2D(8, (3, 3), padding='same', kernel_regularizer=l2_reg),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D((2, 2)),

        # Conv Block 2 - 16 filters
        layers.Conv2D(16, (3, 3), padding='same', kernel_regularizer=l2_reg),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D((2, 2)),

        # Conv Block 3 - 16 filters
        layers.Conv2D(16, (3, 3), padding='same', kernel_regularizer=l2_reg),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D((2, 2)),

        # Flatten - Static reshape (NO MEAN, NO GlobalAvgPool!)
        layers.Flatten(), 
        
        # Dense layers with strong dropout
        layers.Dense(32, activation='relu', kernel_regularizer=l2_reg),
        layers.Dropout(0.5),

        layers.Dense(16, activation='relu', kernel_regularizer=l2_reg),
        layers.Dropout(0.5),

        # Output
        layers.Dense(1, activation='sigmoid')
    ])

    return model


# ============================================================================
# MODEL TRAINING
# ============================================================================

def train_model(X_train, X_val, y_train, y_val):
    """Train the CNN model."""

    log_message("\n" + "=" * 70)
    log_message("TRAINING CNN MODEL")
    log_message("=" * 70)

    # Add channel dimension
    X_train = np.expand_dims(X_train, axis=-1)
    X_val = np.expand_dims(X_val, axis=-1)
    
    log_message(f"\nData shapes with channel dimension:")
    log_message(f"  X_train: {X_train.shape}")
    log_message(f"  X_val: {X_val.shape}")

    input_shape = (X_train.shape[1], X_train.shape[2], 1)
    model = build_model(input_shape)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss='binary_crossentropy',
        metrics=['accuracy',
                 tf.keras.metrics.Precision(name='precision'),
                 tf.keras.metrics.Recall(name='recall')]
    )

    log_message("\nModel Architecture:")
    model.summary()

    # No class weights needed - data is already balanced (~50/50)
    log_message(f"\nTraining Configuration:")
    log_message(f"  Epochs:        {EPOCHS}")
    log_message(f"  Batch size:    {BATCH_SIZE}")
    log_message(f"  Learning rate: {LEARNING_RATE}")
    log_message(f"  Early stop patience: {PATIENCE_EARLY_STOP}")
    log_message(f"  LR reduce patience:  {PATIENCE_LR_REDUCE}")

    # Callbacks
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=PATIENCE_EARLY_STOP,
            restore_best_weights=True,
            verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=PATIENCE_LR_REDUCE,
            min_lr=1e-6,
            verbose=1
        )
    ]

    log_message(f"\nStarting training...")

    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        verbose=1
    )

    return model, history


# ============================================================================
# MODEL EVALUATION
# ============================================================================

def evaluate_model(model, X_test, y_test):
    """Evaluate model on test set."""

    log_message("\n" + "=" * 70)
    log_message("EVALUATION ON TEST SET")
    log_message("=" * 70)

    X_test = np.expand_dims(X_test, axis=-1)
    
    log_message(f"\nX_test shape: {X_test.shape}")

    # Get predictions
    y_pred_probs = model.predict(X_test).flatten()
    y_pred = (y_pred_probs > 0.35).astype(int)

    # ==================== DIAGNOSTIC: Prediction Analysis ===================
    log_message(f"\n--- DIAGNOSTIC: Prediction Analysis ---")
    log_message(f"  Prediction distribution: {np.unique(y_pred, return_counts=True)}")
    log_message(f"  Actual label distribution: {np.unique(y_test, return_counts=True)}")
    log_message(f"  Pred probabilities: min={y_pred_probs.min():.4f}, max={y_pred_probs.max():.4f}, "
                f"mean={y_pred_probs.mean():.4f}, std={y_pred_probs.std():.4f}")
    log_message(f"  Predicted as Snoring (0): {np.sum(y_pred == 0)}")
    log_message(f"  Predicted as Crying  (1): {np.sum(y_pred == 1)}")
    if y_pred_probs.std() < 0.01:
        log_message(f"  ⚠ WARNING: All predictions are nearly identical — model did not learn!")
    # ==================== END DIAGNOSTIC ====================================

    # Calculate metrics
    f1 = f1_score(y_test, y_pred, zero_division=0)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)

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
    """Save trained model and results."""

    model_path = MODELS_DIR / "cnn_model-v2.h5"
    model.save(model_path)
    log_message(f"\n✓ Model saved to {model_path}")

    metrics_path = MODELS_DIR / "training_metrics-v2.json"
    metrics_to_save = {
        'f1_score': float(metrics['f1']),
        'precision': float(metrics['precision']),
        'recall': float(metrics['recall']),
        'timestamp': datetime.now().isoformat(),
        'config': {
            'epochs': EPOCHS,
            'batch_size': BATCH_SIZE,
            'learning_rate': LEARNING_RATE
        },
        'esp32_compatible': True,
        'architecture': 'CNN with Flatten (32/64 filters, MaxPool 2,1) - NO MEAN ops',
        'note': 'Uses preprocessed features from ../data/processed/'
    }

    with open(metrics_path, 'w') as f:
        json.dump(metrics_to_save, f, indent=2)

    log_message(f"✓ Metrics saved to {metrics_path}")

    return model_path


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main training pipeline."""

    log_message("=" * 70)
    log_message("CRY DETECTION MODEL TRAINING")
    log_message("Using Preprocessed Features")
    log_message("=" * 70)

    # Load preprocessed data
    data = load_all_splits()
    if data is None:
        log_message("\n✗ Failed to load preprocessed data")
        log_message("\nRun feature extraction first:")
        log_message("  python 1_extract_features.py")
        return False

    X_train = data['X_train']
    y_train = data['y_train']
    X_val = data['X_val']
    y_val = data['y_val']
    X_test = data['X_test']
    y_test = data['y_test']

    # ==================== DIAGNOSTIC: Data Sanity Checks ====================
    log_message("\n" + "=" * 70)
    log_message("DIAGNOSTIC: DATA SANITY CHECKS")
    log_message("=" * 70)

    log_message(f"\n  Label distribution (TRAIN): {np.unique(y_train, return_counts=True)}")
    log_message(f"  Label distribution (VAL):   {np.unique(y_val, return_counts=True)}")
    log_message(f"  Label distribution (TEST):  {np.unique(y_test, return_counts=True)}")

    log_message(f"\n  X_train stats: mean={X_train.mean():.4f}, std={X_train.std():.4f}, "
                f"min={X_train.min():.4f}, max={X_train.max():.4f}")
    log_message(f"  X_train has NaN? {np.isnan(X_train).any()}")
    log_message(f"  X_train has Inf? {np.isinf(X_train).any()}")
    log_message(f"  X_train all zeros? {(X_train == 0).all()}")
    log_message(f"  X_train shape: {X_train.shape}")

    # Check if all samples look the same (features not discriminative)
    if len(X_train) > 1:
        sample_variance = np.var(X_train, axis=0).mean()
        log_message(f"  Mean variance across samples: {sample_variance:.6f}")
        if sample_variance < 1e-6:
            log_message("  ⚠ WARNING: Features have near-zero variance — model cannot learn!")
    # ==================== END DIAGNOSTIC ====================================

    # ==================== FEATURE NORMALIZATION =============================
    log_message("\n" + "=" * 70)
    log_message("NORMALIZING FEATURES")
    log_message("=" * 70)

    train_mean = X_train.mean(axis=0)
    train_std = X_train.std(axis=0) + 1e-8  # avoid division by zero

    X_train = (X_train - train_mean) / train_std
    X_val = (X_val - train_mean) / train_std
    X_test = (X_test - train_mean) / train_std

    log_message(f"  X_train after norm: mean={X_train.mean():.4f}, std={X_train.std():.4f}")
    log_message(f"  X_val   after norm: mean={X_val.mean():.4f}, std={X_val.std():.4f}")
    log_message(f"  X_test  after norm: mean={X_test.mean():.4f}, std={X_test.std():.4f}")

    # Save normalization stats for inference later
    norm_path = MODELS_DIR / "normalization_stats-v2.npz"
    np.savez(norm_path, mean=train_mean, std=train_std)
    log_message(f"  ✓ Normalization stats saved to {norm_path}")
    # ==================== END NORMALIZATION =================================

    # Balance training set
    log_message("\n" + "=" * 70)
    log_message("BALANCING TRAINING SET")
    log_message("=" * 70)
    X_train, y_train = balance_dataset(X_train, y_train)

    # Data augmentation (training only — no impact on ESP32 model)
    log_message("\n" + "=" * 70)
    log_message("DATA AUGMENTATION")
    log_message("=" * 70)
    log_message(f"  Before augmentation: {X_train.shape[0]} samples")
    X_train, y_train = augment_mfcc(X_train, y_train)
    log_message(f"  After augmentation:  {X_train.shape[0]} samples (4x)")
    log_message(f"  Label distribution:  {np.unique(y_train, return_counts=True)}")

    # Train model
    model, history = train_model(X_train, X_val, y_train, y_val)

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

    

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
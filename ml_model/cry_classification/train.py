import os
import json
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.utils.class_weight import compute_class_weight
from model import build_model

FEATURES_DIR = "features/"
MODELS_DIR = "models/"
LOGS_DIR = "logs/"

TARGET_CLASSES = ["hungry", "tired", "discomfort", "belly_pain", "diaper", "burping"]
LABEL_MAP = {label: i for i, label in enumerate(TARGET_CLASSES)}

def load_data(split):
    split_dir = os.path.join(FEATURES_DIR, split)
    if not os.path.exists(split_dir):
        return [], []
        
    X_paths = []
    y = []
    for file in os.listdir(split_dir):
        if file.endswith(".npy"):
            # filename format: label_id.npy
            label_str = file.split("_")[0]
            # Handle cases where label might have an underscore (e.g. belly_pain)
            for cls in TARGET_CLASSES:
                if file.startswith(cls + "_"):
                    label_str = cls
                    break
                    
            if label_str in LABEL_MAP:
                X_paths.append(os.path.join(split_dir, file))
                y.append(LABEL_MAP[label_str])
                
    return X_paths, y

def parse_function(filename, label):
    # Load .npy file
    def _load_npy(f):
        return np.load(f.numpy()).astype(np.float32)
        
    feature = tf.py_function(_load_npy, [filename], tf.float32)
    # Get shape from config or set dynamically. Assuming (305, 128, 1) based on features.py
    feature.set_shape((None, None, None))
    return feature, label

def create_dataset(X_paths, y, batch_size=32, shuffle=False):
    dataset = tf.data.Dataset.from_tensor_slices((X_paths, y))
    if shuffle:
        dataset = dataset.shuffle(buffer_size=len(X_paths))
    dataset = dataset.map(parse_function, num_parallel_calls=tf.data.AUTOTUNE)
    
    # We need to pad or ensure fixed size. Since features.py produces fixed shape, we can just batch.
    dataset = dataset.batch(batch_size)
    dataset = dataset.prefetch(tf.data.AUTOTUNE)
    return dataset

def main():
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # Load paths
    train_paths, train_y = load_data("train")
    val_paths, val_y = load_data("val")
    
    if not train_paths:
        print("Error: No training data found.")
        return
        
    print(f"Loaded {len(train_paths)} train samples and {len(val_paths)} val samples.")
    
    # Compute class weights
    classes = np.unique(train_y)
    weights = compute_class_weight(class_weight='balanced', classes=classes, y=train_y)
    class_weight_dict = {c: w for c, w in zip(classes, weights)}
    print("Class weights:", class_weight_dict)
    
    # Create tf.data.Datasets
    train_ds = create_dataset(train_paths, train_y, batch_size=32, shuffle=True)
    val_ds = create_dataset(val_paths, val_y, batch_size=32, shuffle=False)
    
    # Determine input shape from first batch
    for x, y in train_ds.take(1):
        input_shape = x.shape[1:]
        print("Input shape:", input_shape)
        break
        
    model = build_model(input_shape=input_shape, num_classes=len(TARGET_CLASSES))
    
    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=5, min_lr=1e-6),
        tf.keras.callbacks.ModelCheckpoint(os.path.join(MODELS_DIR, "best_model.h5"), save_best_only=True)
    ]
    
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=100,
        class_weight=class_weight_dict,
        callbacks=callbacks
    )
    
    # Save history
    history_path = os.path.join(LOGS_DIR, "training_history.json")
    with open(history_path, "w") as f:
        json.dump(history.history, f)
    print(f"Training complete. History saved to {history_path}")

if __name__ == "__main__":
    main()

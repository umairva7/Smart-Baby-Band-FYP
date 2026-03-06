import os
import numpy as np
import tensorflow as tf
import src.config as config
from src.dataset import prepare_dataset
from src.model import build_model
from sklearn.model_selection import train_test_split

def train():
    print("Preparing dataset...")
    X, y = prepare_dataset()
    
    if len(X) == 0:
        print("No data found. Please add data to data/raw/")
        return

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=config.TEST_SPLIT, random_state=config.RANDOM_SEED)
    
    # Expand dims if necessary for Conv1D input (if features are 2D)
    # X shape is expected to be (Samples, Time, Features)
    
    print(f"Training data shape: {X_train.shape}")
    input_shape = (X_train.shape[1], X_train.shape[2])
    
    model = build_model(input_shape)
    model.summary()
    
    # Callbacks
    checkpoint_path = os.path.join(config.MODELS_DIR, "cry_detection_model.h5")
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(checkpoint_path, save_best_only=True, monitor='val_loss'),
        tf.keras.callbacks.EarlyStopping(patience=5, monitor='val_loss')
    ]
    
    print("Starting training...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=config.EPOCHS,
        batch_size=config.BATCH_SIZE,
        callbacks=callbacks
    )
    
    print("Training complete. Model saved to", checkpoint_path)

if __name__ == "__main__":
    train()

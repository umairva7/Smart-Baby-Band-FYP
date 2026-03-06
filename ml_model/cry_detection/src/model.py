import tensorflow as tf
from tensorflow.keras import layers, models
import src.config as config

def build_model(input_shape):
    """
    Build a simple CNN model for audio classification.
    """
    model = models.Sequential([
        layers.Input(shape=input_shape),
        
        # First Block
        layers.Conv1D(32, 3, activation='relu', padding='same'),
        layers.MaxPooling1D(2),
        layers.BatchNormalization(),
        
        # Second Block
        layers.Conv1D(64, 3, activation='relu', padding='same'),
        layers.MaxPooling1D(2),
        layers.BatchNormalization(),
        
        # Third Block
        layers.Conv1D(128, 3, activation='relu', padding='same'),
        layers.GlobalAveragePooling1D(),
        
        # Dense Layers
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(1, activation='sigmoid') # Binary classification output (Cry vs Non-Cry)
    ])
    
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=config.LEARNING_RATE),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
    
    return model

if __name__ == "__main__":
    # Example input shape based on MFCC features
    # (Time_steps, Features)
    # Time_steps depends on sample rate, duration, and hop length of MFCC
    # For now, we'll estimate or calculate it dynamically in train.py
    pass

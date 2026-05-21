"""
Script to train the cloud-side binary cry detection model.
"""
import os
import sys
import json
import numpy as np
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, BatchNormalization, ReLU, MaxPool2D, Flatten, Dense, Dropout
from tensorflow.keras.regularizers import l2
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

# Add workspace root to sys.path so ml_model module can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from ml_model.cry_classification.preprocess import preprocess_audio

# TODO: point SPEECH_DIR to your downloaded Mozilla Common Voice clips
SPEECH_DIR = "data/mozilla_common_voice"

def build_model():
    model = Sequential([
        Conv2D(16, (3, 3), padding='same', kernel_regularizer=l2(0.001), input_shape=(128, 128, 1)),
        BatchNormalization(),
        ReLU(),
        MaxPool2D((2, 2)),
        
        Conv2D(32, (3, 3), padding='same', kernel_regularizer=l2(0.001)),
        BatchNormalization(),
        ReLU(),
        MaxPool2D((2, 2)),
        
        Conv2D(32, (3, 3), padding='same', kernel_regularizer=l2(0.001)),
        BatchNormalization(),
        ReLU(),
        MaxPool2D((2, 2)),
        
        Flatten(),
        Dense(32, kernel_regularizer=l2(0.001)),
        ReLU(),
        Dropout(0.3),
        
        Dense(16, kernel_regularizer=l2(0.001)),
        ReLU(),
        Dropout(0.3),
        
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
    return model

def main():
    print("Initializing Cloud Cry Detection Model...")
    model = build_model()
    model.summary()
    
    print("\\nPlease implement data loading here:")
    print("1. Load ICSD dataset (cry=1)")
    print("2. Load ESC-50 and Mozilla Common Voice (cry=0)")
    print("3. Preprocess with preprocess_audio(bytes)")
    print("4. Compute class weights")
    print("5. Run model.fit() with EarlyStopping and ReduceLROnPlateau")
    
    # Save directory
    os.makedirs("models/cloud_detection", exist_ok=True)
    
    # Expected save logic:
    # model.save("models/cloud_detection/cry_detection_cloud.h5")
    # with open("models/cloud_detection/threshold.json", "w") as f:
    #     json.dump({"threshold": 0.5}, f)
        
if __name__ == "__main__":
    main()

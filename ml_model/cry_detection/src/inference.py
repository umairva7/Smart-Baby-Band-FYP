import os
import numpy as np
import tensorflow as tf
import src.config as config
from src.dataset import load_audio, extract_features

class CryDetector:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.path.join(config.MODELS_DIR, "cry_detection_model.h5")
            
        self.model_path = model_path
        self.model = None
        
    def load_model(self):
        if os.path.exists(self.model_path):
            self.model = tf.keras.models.load_model(self.model_path)
            print("Model loaded successfully.")
        else:
            print(f"Model file not found at {self.model_path}")
            
    def predict(self, audio_path):
        if self.model is None:
            self.load_model()
            if self.model is None:
                return "Model not loaded"

        # Preprocess features
        audio = load_audio(audio_path)
        if audio is None:
            return "Error loading audio"
            
        features = extract_features(audio)
        # Add batch dimension: (1, Time, Features)
        features = np.expand_dims(features, axis=0)
        
        prediction = self.model.predict(features)
        probability = prediction[0][0]
        
        label = "Cry" if probability > 0.5 else "Noise/Other"
        return {"label": label, "probability": float(probability)}

if __name__ == "__main__":
    # Example usage
    detector = CryDetector()
    # result = detector.predict("path/to/test/audio.wav")
    # print(result)

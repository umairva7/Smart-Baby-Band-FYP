import os
import numpy as np
import librosa
from sklearn.model_selection import train_test_split
import src.config as config

def load_audio(file_path):
    """
    Load an audio file and resample it to the target sample rate.
    """
    try:
        audio, _ = librosa.load(file_path, sr=config.SAMPLE_RATE, duration=config.DURATION)
        # Pad or truncate to ensure consistent length
        target_length = int(config.SAMPLE_RATE * config.DURATION)
        if len(audio) < target_length:
            audio = np.pad(audio, (0, target_length - len(audio)))
        else:
            audio = audio[:target_length]
        return audio
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def extract_features(audio):
    """
    Extract MFCC features from an audio signal.
    """
    mfcc = librosa.feature.mfcc(y=audio, sr=config.SAMPLE_RATE, n_mfcc=config.N_MFCC)
    return mfcc.T # (Time, N_MFCC)

def prepare_dataset():
    """
    Load data, extract features, and split into train/test sets.
    Assumes data/raw contains subdirectories for classes (e.g., 'cry', 'noise').
    """
    features = []
    labels = []
    
    # Example logic - adjust based on actual data structure
    # for class_name in ['cry', 'noise']:
    #     class_dir = os.path.join(config.RAW_DATA_DIR, class_name)
    #     if not os.path.exists(class_dir): continue
    #     
    #     for file_name in os.listdir(class_dir):
    #         if file_name.endswith('.wav'):
    #             path = os.path.join(class_dir, file_name)
    #             audio = load_audio(path)
    #             if audio is not None:
    #                 feat = extract_features(audio)
    #                 features.append(feat)
    #                 labels.append(1 if class_name == 'cry' else 0)
    
    # Placeholder return
    print("Dataset preparation logic needs to be connected to actual data folders.")
    return np.array(features), np.array(labels)

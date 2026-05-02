import os
import json
import librosa
import numpy as np
import pandas as pd
from tqdm import tqdm

# Config
SR = 16000
DURATION = 3.0
SAMPLES = int(SR * DURATION)
N_FFT = 512
HOP_LENGTH = 375
N_MELS = 128
N_MFCC = 40
FMIN = 0
FMAX = 8000

PROCESSED_DIR = "data/processed/"
FEATURES_DIR = "features/"
MODELS_DIR = "models/"

def extract_features(audio_path):
    # Load audio
    y, sr = librosa.load(audio_path, sr=SR, mono=True)
    if len(y) > SAMPLES:
        y = y[:SAMPLES]
    else:
        y = np.pad(y, (0, max(0, SAMPLES - len(y))), "constant")
        
    # b. Spectrogram (STFT)
    stft = librosa.stft(y, n_fft=N_FFT, hop_length=HOP_LENGTH, window='hann')
    mag_stft = np.abs(stft)
    stft_db = librosa.amplitude_to_db(mag_stft, ref=np.max) # (257, 128)
    
    # c. Mel Spectrogram
    mel = librosa.feature.melspectrogram(y=y, sr=SR, n_fft=N_FFT, hop_length=HOP_LENGTH, 
                                         n_mels=N_MELS, fmin=FMIN, fmax=FMAX)
    mel_db = librosa.power_to_db(mel, ref=np.max) # (128, 128)
    
    # d. MFCC
    mfcc = librosa.feature.mfcc(y=y, sr=SR, n_fft=N_FFT, hop_length=HOP_LENGTH, 
                                n_mfcc=N_MFCC, n_mels=N_MELS, fmin=FMIN, fmax=FMAX)
    mfcc_delta = librosa.feature.delta(mfcc)
    mfcc_delta2 = librosa.feature.delta(mfcc, order=2)
    mfcc_stacked = np.concatenate([mfcc, mfcc_delta, mfcc_delta2], axis=0) # (120, 128)
    
    # e. Efficient Graph construction
    # Remove redundant bins from STFT (keep high freq bins not captured well by Mel)
    # Total shape should be ~305. 128 (mel) + 120 (mfcc) = 248. 305 - 248 = 57 bins.
    # We take the last 57 bins of stft_db.
    stft_high = stft_db[-57:, :]
    
    # Concatenate all
    # To match time frames exactly to 128, since len(y)=48000, 48000//375 = 128 frames (actually 129).
    # We truncate to 128 frames across time axis.
    stft_high = stft_high[:, :128]
    mel_db = mel_db[:, :128]
    mfcc_stacked = mfcc_stacked[:, :128]
    
    if stft_high.shape[1] < 128:
        pad_width = 128 - stft_high.shape[1]
        stft_high = np.pad(stft_high, ((0,0), (0,pad_width)), 'constant')
        mel_db = np.pad(mel_db, ((0,0), (0,pad_width)), 'constant')
        mfcc_stacked = np.pad(mfcc_stacked, ((0,0), (0,pad_width)), 'constant')
        
    combined = np.concatenate([stft_high, mel_db, mfcc_stacked], axis=0) # (305, 128)
    
    # f. Normalize per-channel (here per-feature matrix) to [0, 1]
    # To avoid divide by zero, add epsilon
    min_val = np.min(combined)
    max_val = np.max(combined)
    if max_val > min_val:
        combined = (combined - min_val) / (max_val - min_val)
    else:
        combined = combined - min_val
        
    # g. Add channel dim
    features = np.expand_dims(combined, axis=-1) # (305, 128, 1)
    return features

def main():
    os.makedirs(FEATURES_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    splits_path = os.path.join(PROCESSED_DIR, "splits.csv")
    if not os.path.exists(splits_path):
        print(f"Error: {splits_path} not found. Run dataset.py and augment.py first.")
        return
        
    df = pd.read_csv(splits_path)
    
    shape = None
    
    for split in ["train", "val", "test"]:
        os.makedirs(os.path.join(FEATURES_DIR, split), exist_ok=True)
        split_df = df[df["split"] == split]
        
        for i, row in tqdm(split_df.iterrows(), total=len(split_df), desc=f"Extracting {split}"):
            feat = extract_features(row["filepath"])
            if shape is None:
                shape = feat.shape
                
            filename = f"{row['label']}_{i}.npy"
            out_path = os.path.join(FEATURES_DIR, split, filename)
            np.save(out_path, feat)
            
    # Save config
    config = {
        "sr": SR,
        "duration": DURATION,
        "n_fft": N_FFT,
        "hop_length": HOP_LENGTH,
        "n_mels": N_MELS,
        "n_mfcc": N_MFCC,
        "fmin": FMIN,
        "fmax": FMAX,
        "feature_shape": shape
    }
    with open(os.path.join(MODELS_DIR, "feature_config.json"), "w") as f:
        json.dump(config, f, indent=4)
        
    print(f"Feature extraction complete. Shape: {shape}. Config saved.")

if __name__ == "__main__":
    main()

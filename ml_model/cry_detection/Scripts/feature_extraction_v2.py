"""
Feature Extraction v2: Combined ICSD + ESC-50 Pipeline
=====================================================
MATCHED TO ESP32 HARDWARE PIPELINE (March 2026)

This script extracts MFCC features that are IDENTICAL to how the ESP32
computes them, ensuring zero mismatch between training and inference.

ESP32 Pipeline Parameters (from hardware team's C++ code):
  - 39 raw DCT coefficients (NO deltas)
  - 26 Mel filter banks
  - 512-point FFT
  - Pre-emphasis: 0.97
  - Hamming window
  - Frame length: 400 samples (25ms)
  - Hop length: 160 samples (10ms)
  - 128 frames per sample
  - NO normalization

Datasets:
  1. ICSD (cry + snoring) — existing train/val/test splits
  2. ESC-50 (50 environmental sound categories)

Labels:
  1 = crying (ICSD cry + ESC-50 crying_baby)
  0 = not-crying (ICSD snoring + ALL other ESC-50 categories)
"""

import os
import csv
import numpy as np
from pathlib import Path
import librosa
import pickle
from datetime import datetime

# ============================================================================
# CONFIGURATION — MATCHED TO ESP32 HARDWARE
# ============================================================================

# --- Dataset Paths ---
ICSD_DIR = Path("../data/raw/model 1/audio")
ESC50_DIR = Path("../data/ESC-50-master")
ESC50_AUDIO = ESC50_DIR / "audio"
ESC50_META = ESC50_DIR / "meta" / "esc50.csv"

# --- Output ---
PROCESSED_DIR = Path("../data/processed_v2")

# --- Audio Parameters (MUST match ESP32 exactly) ---
SAMPLING_RATE = 16000
N_MFCC = 39          # ESP32 computes 39 DCT coefficients (not 13+deltas)
N_MELS = 26          # ESP32 uses 26 mel filter banks (not librosa default 128)  
N_FFT = 512          # ESP32 uses 512-point FFT (not 400)
FRAME_LENGTH = 400   # 25ms window
HOP_LENGTH = 160     # 10ms hop
FRAMES_PER_SAMPLE = 128
PREEMPHASIS = 0.97   # ESP32 applies pre-emphasis

# --- ESC-50 Config ---
ESC50_CRY_TARGET = 20  # "crying_baby" class in ESC-50
ESC50_FOLD_MAP = {
    'train': [1, 2, 3],
    'validation': [4],
    'test': [5],
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")


def extract_mfcc_esp32_matched(audio_path, target_frames=FRAMES_PER_SAMPLE):
    """Extract MFCC features IDENTICAL to ESP32 computation.
    
    Key differences from v1:
      - 39 raw DCT coefficients (NO deltas/delta-deltas)
      - 26 mel filters (not 128)
      - 512-point FFT (not 400)
      - Pre-emphasis 0.97
      - Hamming window (not Hann)
      - No normalization
    
    Returns shape: (FRAMES_PER_SAMPLE, 39) = (128, 39)
    """
    try:
        # Load and resample to 16kHz
        y, sr = librosa.load(audio_path, sr=SAMPLING_RATE, duration=3.0)

        # Skip very short audio
        if len(y) < SAMPLING_RATE * 0.5:
            return None

        # --- PRE-EMPHASIS (matches ESP32: y[i] -= 0.97 * y[i-1]) ---
        y = np.append(y[0], y[1:] - PREEMPHASIS * y[:-1])

        # --- MFCC extraction matched to ESP32 ---
        # n_mfcc=39:  extract 39 DCT coefficients directly (ESP32 does this)
        # n_mels=26:  use 26 mel filter banks (ESP32's MEL_FILTERS=26)
        # n_fft=512:  512-point FFT (ESP32's FFT_SIZE=512)
        # window='hamming': match ESP32's Hamming window
        # center=False: ESP32 doesn't center frames
        # win_length=400: actual window is 400 samples, zero-padded to 512
        mfcc = librosa.feature.mfcc(
            y=y,
            sr=SAMPLING_RATE,
            n_mfcc=N_MFCC,         # 39 DCT coefficients
            n_mels=N_MELS,         # 26 mel filter banks
            n_fft=N_FFT,           # 512-point FFT
            hop_length=HOP_LENGTH, # 160 samples
            win_length=FRAME_LENGTH, # 400 sample window
            window='hamming',      # Hamming (not Hann)
            center=False,          # No centering (matches ESP32)
        )
        
        # mfcc shape: (39, frames) → transpose → (frames, 39)
        features = mfcc.T

        # NO DELTAS — ESP32 does not compute deltas

        # Pad or truncate to target frames
        if features.shape[0] < target_frames:
            pad_width = ((0, target_frames - features.shape[0]), (0, 0))
            features = np.pad(features, pad_width, mode='constant')
        else:
            features = features[:target_frames, :]

        return features.astype(np.float32)

    except Exception as e:
        return None


# ============================================================================
# ICSD PROCESSING
# ============================================================================

def process_icsd_split(split_name):
    """Process ICSD train/validation/test split."""
    split_dir = ICSD_DIR / split_name
    if not split_dir.exists():
        log(f"  ⚠ ICSD {split_name} directory not found: {split_dir}")
        return [], [], []

    X, y, sources = [], [], []
    files = list(split_dir.rglob("*.wav"))
    log(f"  Found {len(files)} ICSD files in {split_name}")

    cry_count = snoring_count = skipped = 0
    for i, f in enumerate(files):
        fname = f.name.lower()
        if "infantcry" in fname or "cry" in fname:
            label = 1
        elif "snoring" in fname or "snor" in fname:
            label = 0
        else:
            skipped += 1
            continue

        features = extract_mfcc_esp32_matched(f)
        if features is not None:
            X.append(features)
            y.append(label)
            sources.append(f"ICSD:{f.name}")
            if label == 1:
                cry_count += 1
            else:
                snoring_count += 1

        if (i + 1) % 200 == 0:
            log(f"    Progress: {i+1}/{len(files)}")

    log(f"    ✓ ICSD {split_name}: {cry_count} cry, {snoring_count} snoring, {skipped} skipped")
    return X, y, sources


# ============================================================================
# ESC-50 PROCESSING
# ============================================================================

def load_esc50_metadata():
    """Load ESC-50 metadata CSV."""
    entries = []
    with open(ESC50_META, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entries.append({
                'filename': row['filename'],
                'fold': int(row['fold']),
                'target': int(row['target']),
                'category': row['category'],
            })
    log(f"  Loaded {len(entries)} ESC-50 metadata entries")
    return entries


def process_esc50_split(entries, split_name):
    """Process ESC-50 entries for a given split.
    Labels: crying_baby (target 20) → 1, everything else → 0
    """
    folds = ESC50_FOLD_MAP[split_name]
    split_entries = [e for e in entries if e['fold'] in folds]
    
    X, y, sources = [], [], []
    cry_count = noncry_count = failed = 0
    categories_seen = set()

    for i, entry in enumerate(split_entries):
        audio_path = ESC50_AUDIO / entry['filename']
        if not audio_path.exists():
            failed += 1
            continue

        label = 1 if entry['target'] == ESC50_CRY_TARGET else 0
        
        features = extract_mfcc_esp32_matched(audio_path)
        if features is not None:
            X.append(features)
            y.append(label)
            sources.append(f"ESC50:{entry['category']}:{entry['filename']}")
            categories_seen.add(entry['category'])
            if label == 1:
                cry_count += 1
            else:
                noncry_count += 1

        if (i + 1) % 200 == 0:
            log(f"    Progress: {i+1}/{len(split_entries)}")

    log(f"    ✓ ESC-50 {split_name}: {cry_count} cry, {noncry_count} non-cry "
        f"({len(categories_seen)} categories, {failed} failed)")
    return X, y, sources


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    log("=" * 70)
    log("FEATURE EXTRACTION v2: ICSD + ESC-50 (ESP32-MATCHED)")
    log("=" * 70)
    log(f"\nESP32-matched parameters:")
    log(f"  N_MFCC={N_MFCC}, N_MELS={N_MELS}, N_FFT={N_FFT}")
    log(f"  Pre-emphasis={PREEMPHASIS}, Window=Hamming, Center=False")
    log(f"  Deltas: DISABLED (raw DCT only)")
    log(f"  Normalization: DISABLED (raw values)")

    # Create output directories
    for split in ['train', 'validation', 'test']:
        (PROCESSED_DIR / split).mkdir(parents=True, exist_ok=True)

    # Load ESC-50 metadata once
    log("\n[1/4] Loading ESC-50 metadata...")
    esc50_entries = load_esc50_metadata()

    # Process each split
    for split in ['train', 'validation', 'test']:
        log(f"\n{'=' * 70}")
        log(f"PROCESSING {split.upper()} SPLIT")
        log(f"{'=' * 70}")

        # --- ICSD ---
        log(f"\n  [ICSD]")
        icsd_X, icsd_y, icsd_src = process_icsd_split(split)

        # --- ESC-50 ---
        log(f"\n  [ESC-50]")
        esc_X, esc_y, esc_src = process_esc50_split(esc50_entries, split)

        # --- Combine ---
        all_X = icsd_X + esc_X
        all_y = icsd_y + esc_y
        all_src = icsd_src + esc_src

        if len(all_X) == 0:
            log(f"  ✗ No valid samples for {split}!")
            continue

        X = np.array(all_X)
        y = np.array(all_y)

        # Shuffle deterministically
        indices = np.random.RandomState(42).permutation(len(X))
        X = X[indices]
        y = y[indices]
        all_src = [all_src[i] for i in indices]

        # --- Stats ---
        n_cry = int(np.sum(y == 1))
        n_noncry = int(np.sum(y == 0))
        log(f"\n  COMBINED {split.upper()}:")
        log(f"    Total samples: {len(X)}")
        log(f"    Crying (1):    {n_cry}")
        log(f"    Not-cry (0):   {n_noncry}")
        log(f"    Shape:         {X.shape}")
        log(f"    Ratio cry/total: {n_cry/len(X)*100:.1f}%")
        log(f"    Feature range: [{X.min():.2f}, {X.max():.2f}]")

        # --- Save ---
        out_dir = PROCESSED_DIR / split
        np.save(out_dir / f"X_{split}.npy", X)
        np.save(out_dir / f"y_{split}.npy", y)
        
        metadata = {
            'split': split,
            'n_samples': len(X),
            'n_cry': n_cry,
            'n_noncry': n_noncry,
            'shape': X.shape,
            'sources': all_src,
            'sampling_rate': SAMPLING_RATE,
            'n_mfcc': N_MFCC,
            'n_mels': N_MELS,
            'n_fft': N_FFT,
            'preemphasis': PREEMPHASIS,
            'window': 'hamming',
            'center': False,
            'deltas': False,
            'normalization': None,
            'frames_per_sample': FRAMES_PER_SAMPLE,
            'datasets': ['ICSD', 'ESC-50'],
            'esp32_matched': True,
        }
        with open(out_dir / f"metadata_{split}.pkl", 'wb') as f:
            pickle.dump(metadata, f)

        log(f"    ✓ Saved to {out_dir}/")

    # --- Summary ---
    log(f"\n{'=' * 70}")
    log("FEATURE EXTRACTION COMPLETE (ESP32-MATCHED)")
    log(f"{'=' * 70}")
    log(f"\nOutput: {PROCESSED_DIR}/")
    log(f"\n⚠ IMPORTANT: Training script must:")
    log(f"  1. Read from {PROCESSED_DIR}/ (not processed/)")
    log(f"  2. NOT apply normalization (ESP32 doesn't normalize)")
    log(f"  3. Input shape = (128, 39, 1)")


if __name__ == "__main__":
    main()

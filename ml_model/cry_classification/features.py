import argparse
from pathlib import Path

import json

import librosa
import numpy as np
import pandas as pd

from config import (
    DATA_DIR,
    FEATURES_DIR,
    HOP_LENGTH,
    MODELS_DIR,
    N_FFT,
    N_MELS,
    N_MFCC,
    NUM_SAMPLES,
    SAMPLE_RATE,
    SPECTROGRAM_KEEP_BINS,
    TARGET_FRAMES,
)


def fix_frames(feature: np.ndarray, target_frames: int) -> np.ndarray:
    return librosa.util.fix_length(feature, size=target_frames, axis=1)


def extract_features(audio_path: Path) -> np.ndarray:
    audio, _ = librosa.load(audio_path, sr=SAMPLE_RATE, mono=True)
    audio = librosa.util.fix_length(audio, size=NUM_SAMPLES)

    stft = librosa.stft(audio, n_fft=N_FFT, hop_length=HOP_LENGTH, window="hann")
    spec = np.abs(stft)
    spec_db = librosa.amplitude_to_db(spec, ref=np.max)

    mel = librosa.feature.melspectrogram(
        y=audio,
        sr=SAMPLE_RATE,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
        n_mels=N_MELS,
        fmin=0,
        fmax=SAMPLE_RATE // 2,
    )
    mel_db = librosa.power_to_db(mel, ref=np.max)

    mfcc = librosa.feature.mfcc(
        y=audio,
        sr=SAMPLE_RATE,
        n_mfcc=N_MFCC,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
    )
    delta = librosa.feature.delta(mfcc)
    delta2 = librosa.feature.delta(mfcc, order=2)
    mfcc_block = np.vstack([mfcc, delta, delta2])

    spec_db = fix_frames(spec_db, TARGET_FRAMES)
    mel_db = fix_frames(mel_db, TARGET_FRAMES)
    mfcc_block = fix_frames(mfcc_block, TARGET_FRAMES)

    keep_bins = min(SPECTROGRAM_KEEP_BINS, spec_db.shape[0])
    spec_keep = spec_db[-keep_bins:, :]

    combined = np.vstack([spec_keep, mel_db, mfcc_block])

    min_val = float(combined.min())
    max_val = float(combined.max())
    if max_val > min_val:
        combined = (combined - min_val) / (max_val - min_val)
    else:
        combined = np.zeros_like(combined)

    return combined.astype(np.float32)[..., np.newaxis]


def save_feature_config(feature_shape: tuple[int, ...], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    config = {
        "sample_rate": SAMPLE_RATE,
        "duration_sec": NUM_SAMPLES / SAMPLE_RATE,
        "n_fft": N_FFT,
        "hop_length": HOP_LENGTH,
        "n_mels": N_MELS,
        "n_mfcc": N_MFCC,
        "spectrogram_keep_bins": SPECTROGRAM_KEEP_BINS,
        "target_frames": TARGET_FRAMES,
        "feature_shape": list(feature_shape),
    }
    output_path.write_text(json.dumps(config, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract features for cry classification.")
    parser.add_argument("--splits-path", type=Path, default=DATA_DIR / "splits.csv")
    parser.add_argument("--features-dir", type=Path, default=FEATURES_DIR)
    parser.add_argument("--config-path", type=Path, default=MODELS_DIR / "feature_config.json")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    df = pd.read_csv(args.splits_path)
    if "filepath" not in df.columns:
        raise SystemExit("splits.csv is missing the filepath column.")

    feature_paths: list[str] = []
    feature_shape: tuple[int, ...] | None = None

    for idx, row in df.iterrows():
        split = row.get("split", "train")
        label = row["label"]
        out_dir = args.features_dir / split
        out_dir.mkdir(parents=True, exist_ok=True)

        out_path = out_dir / f"{label}_{idx:06d}.npy"
        if out_path.exists() and not args.overwrite:
            feature = np.load(out_path)
        else:
            feature = extract_features(Path(row["filepath"]))
            np.save(out_path, feature)

        if feature_shape is None:
            feature_shape = feature.shape

        feature_paths.append(str(out_path))

    df["feature_path"] = feature_paths
    df.to_csv(args.splits_path, index=False)

    if feature_shape is None:
        raise SystemExit("No features were generated.")

    save_feature_config(feature_shape, args.config_path)
    print(f"Saved features and updated {args.splits_path}")


if __name__ == "__main__":
    main()

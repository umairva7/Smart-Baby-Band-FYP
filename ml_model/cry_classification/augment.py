import argparse
import random
from pathlib import Path

import librosa
import numpy as np
import pandas as pd
import soundfile as sf

from config import (
    AUGMENTED_DIR,
    DATA_DIR,
    NUM_SAMPLES,
    RANDOM_SEED,
    RAW_DIR,
    SAMPLE_RATE,
)


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def load_audio(path: Path) -> np.ndarray:
    audio, _ = librosa.load(path, sr=SAMPLE_RATE, mono=True)
    if audio.size == 0:
        return audio
    return audio


def normalize_audio(audio: np.ndarray) -> np.ndarray:
    peak = np.max(np.abs(audio)) if audio.size else 0
    return audio / peak if peak > 0 else audio


def add_noise_at_snr(audio: np.ndarray, noise: np.ndarray, snr_db: float) -> np.ndarray:
    signal_power = np.mean(audio ** 2) + 1e-12
    noise_power = np.mean(noise ** 2) + 1e-12
    scale = np.sqrt(signal_power / (10 ** (snr_db / 10) * noise_power))
    return audio + noise * scale


def time_mask(audio: np.ndarray, min_pct: float, max_pct: float) -> np.ndarray:
    if audio.size == 0:
        return audio
    mask_len = int(len(audio) * random.uniform(min_pct, max_pct))
    if mask_len <= 0:
        return audio
    start = random.randint(0, max(0, len(audio) - mask_len))
    audio = audio.copy()
    audio[start : start + mask_len] = 0
    return audio


def augment_audio(audio: np.ndarray, noise_paths: list[Path]) -> np.ndarray:
    rate = random.uniform(0.85, 1.15)
    audio = librosa.effects.time_stretch(audio, rate)

    steps = random.uniform(-2.0, 2.0)
    audio = librosa.effects.pitch_shift(audio, sr=SAMPLE_RATE, n_steps=steps)

    audio = librosa.util.fix_length(audio, size=NUM_SAMPLES)

    if noise_paths:
        noise_path = random.choice(noise_paths)
        noise = load_audio(noise_path)
        noise = librosa.util.fix_length(noise, size=NUM_SAMPLES)
        snr_db = random.uniform(10.0, 20.0)
        audio = add_noise_at_snr(audio, noise, snr_db)

    audio = time_mask(audio, min_pct=0.05, max_pct=0.15)
    audio = normalize_audio(audio)
    return audio


def iter_noise_files(noise_dir: Path) -> list[Path]:
    if not noise_dir.exists():
        return []
    return list(noise_dir.rglob("*.wav"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline audio augmentation.")
    parser.add_argument("--splits-path", type=Path, default=DATA_DIR / "splits.csv")
    parser.add_argument("--processed-dir", type=Path, default=PROCESSED_DIR)
    parser.add_argument("--augmented-dir", type=Path, default=AUGMENTED_DIR)
    parser.add_argument("--noise-dir", type=Path, default=RAW_DIR / "esc50")
    parser.add_argument("--target-per-class", type=int, default=1500)
    args = parser.parse_args()

    set_seed(RANDOM_SEED)

    df = pd.read_csv(args.splits_path)
    if "split" not in df.columns:
        raise SystemExit("splits.csv is missing the split column.")

    train_df = df[df["split"] == "train"].copy()
    if "is_augmented" in train_df.columns:
        augmented_mask = train_df["is_augmented"].astype(str).str.lower().isin(["true", "1", "yes"])
        train_df = train_df[~augmented_mask]

    if train_df.empty:
        raise SystemExit("No training samples found.")

    noise_paths = iter_noise_files(args.noise_dir)
    if not noise_paths:
        print("Warning: no noise files found, skipping noise augmentation.")

    args.augmented_dir.mkdir(parents=True, exist_ok=True)

    counts = train_df["label"].value_counts().to_dict()
    new_rows = []
    counter = 0

    for label, count in counts.items():
        target = args.target_per_class
        to_create = max(0, target - count)
        if to_create == 0:
            continue

        class_rows = train_df[train_df["label"] == label].reset_index(drop=True)
        for _ in range(to_create):
            row = class_rows.iloc[random.randrange(len(class_rows))]
            audio = load_audio(Path(row["filepath"]))
            if audio.size == 0:
                continue
            augmented = augment_audio(audio, noise_paths)
            out_name = f"aug_{label}_{counter:06d}.wav"
            out_path = args.augmented_dir / out_name
            sf.write(out_path, augmented, SAMPLE_RATE)
            counter += 1

            new_rows.append(
                {
                    "filepath": str(out_path),
                    "label": label,
                    "split": "train",
                    "source_dataset": row.get("source_dataset", "augmented"),
                    "is_augmented": True,
                }
            )

    if not new_rows:
        print("No augmentation needed.")
        return

    new_df = pd.DataFrame(new_rows)
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(args.splits_path, index=False)
    print(f"Added {len(new_rows)} augmented samples.")


if __name__ == "__main__":
    main()

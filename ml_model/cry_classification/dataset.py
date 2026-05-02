import argparse
import random
from pathlib import Path

import librosa
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import soundfile as sf
from sklearn.model_selection import train_test_split

from config import (
    AUGMENTED_DIR,
    DATA_DIR,
    LABELS,
    LOGS_DIR,
    NUM_SAMPLES,
    PROCESSED_DIR,
    RANDOM_SEED,
    RAW_DIR,
    SAMPLE_RATE,
)

DROP_KEYWORDS = {"awake", "hug"}
LABEL_KEYWORDS = {
    "hungry": ["hungry", "hunger"],
    "tired": ["tired", "sleepy", "sleep"],
    "discomfort": ["discomfort", "discomf"],
    "belly_pain": ["belly_pain", "bellypain", "belly", "colic", "stomach"],
    "diaper": ["diaper", "nappy", "wet"],
    "burping": ["burp", "burping"],
}


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def iter_audio_files(root: Path) -> list[Path]:
    exts = ["wav", "mp3", "flac", "ogg", "m4a"]
    files: list[Path] = []
    for ext in exts:
        files.extend(root.rglob(f"*.{ext}"))
    return files


def detect_label(text: str) -> str | None:
    lowered = text.lower()
    if any(key in lowered for key in DROP_KEYWORDS):
        return None
    for label, keywords in LABEL_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return label
    return None


def process_audio(path: Path, top_db: int) -> np.ndarray | None:
    audio, _ = librosa.load(path, sr=SAMPLE_RATE, mono=True)
    audio, _ = librosa.effects.trim(audio, top_db=top_db)
    if audio.size == 0:
        return None
    audio = librosa.util.fix_length(audio, size=NUM_SAMPLES)
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak
    return audio


def collect_dac(dac_dir: Path) -> list[tuple[Path, str, str]]:
    entries: list[tuple[Path, str, str]] = []
    for path in iter_audio_files(dac_dir):
        label = detect_label(path.stem)
        if label:
            entries.append((path, label, "dac"))
    return entries


def collect_baby_crying(baby_dir: Path) -> list[tuple[Path, str, str]]:
    entries: list[tuple[Path, str, str]] = []
    for path in iter_audio_files(baby_dir):
        label = detect_label(path.parent.name)
        if label:
            entries.append((path, label, "baby_crying"))
    return entries


def build_splits(df: pd.DataFrame, seed: int) -> pd.DataFrame:
    counts = df["label"].value_counts()
    stratify = df["label"] if counts.min() >= 3 else None

    train_df, temp_df = train_test_split(
        df,
        test_size=0.2,
        stratify=stratify,
        random_state=seed,
    )

    stratify_temp = temp_df["label"] if stratify is not None else None
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.5,
        stratify=stratify_temp,
        random_state=seed,
    )

    train_df = train_df.copy()
    val_df = val_df.copy()
    test_df = test_df.copy()

    train_df["split"] = "train"
    val_df["split"] = "val"
    test_df["split"] = "test"

    return pd.concat([train_df, val_df, test_df], ignore_index=True)


def plot_distribution(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    counts = df["label"].value_counts().reindex(LABELS, fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 4))
    counts.plot(kind="bar", ax=ax, color="#4c72b0")
    ax.set_title("Class distribution")
    ax.set_xlabel("Label")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare cry classification dataset.")
    parser.add_argument("--dac-dir", type=Path, default=RAW_DIR / "donate_a_cry")
    parser.add_argument("--baby-dir", type=Path, default=RAW_DIR / "baby_crying")
    parser.add_argument("--processed-dir", type=Path, default=PROCESSED_DIR)
    parser.add_argument("--splits-path", type=Path, default=DATA_DIR / "splits.csv")
    parser.add_argument("--plot-path", type=Path, default=LOGS_DIR / "class_distribution.png")
    parser.add_argument("--top-db", type=int, default=20)
    args = parser.parse_args()

    set_seed(RANDOM_SEED)

    args.processed_dir.mkdir(parents=True, exist_ok=True)
    AUGMENTED_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    entries: list[tuple[Path, str, str]] = []
    if args.dac_dir.exists():
        entries.extend(collect_dac(args.dac_dir))
    if args.baby_dir.exists():
        entries.extend(collect_baby_crying(args.baby_dir))

    if not entries:
        raise SystemExit("No audio files found. Check raw dataset paths.")

    records = []
    for idx, (path, label, source) in enumerate(entries):
        audio = process_audio(path, top_db=args.top_db)
        if audio is None:
            continue
        out_name = f"{source}_{label}_{idx:06d}.wav"
        out_path = args.processed_dir / out_name
        sf.write(out_path, audio, SAMPLE_RATE)
        records.append(
            {
                "filepath": str(out_path),
                "label": label,
                "source_dataset": source,
                "is_augmented": False,
            }
        )

    df = pd.DataFrame(records)
    if df.empty:
        raise SystemExit("No valid audio after processing.")

    df = build_splits(df, RANDOM_SEED)
    df.to_csv(args.splits_path, index=False)

    plot_distribution(df, args.plot_path)
    print(df["label"].value_counts())
    print(f"Saved splits to {args.splits_path}")


if __name__ == "__main__":
    main()

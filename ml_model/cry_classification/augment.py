"""Offline data augmentation for the train split.

The plan calls for a 4x expansion (1 original + 3 augmented variants) of the
training split only. Validation and test rows are left untouched to keep the
evaluation metrics honest.

Each augmented variant randomly applies one of:
    - time stretch with rate in U(0.8, 1.2)
    - pitch shift with n_steps in U(-2, +2) semitones
    - both, applied sequentially (stretch first, then pitch shift)

The result is re-padded / truncated to a fixed 3-second window so the
augmented files are drop-in replacements for the originals.

Run as a script::

    python -m cry_classification.augment
"""

from __future__ import annotations

import csv
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

from dataset import (
    LABELS,
    PROCESSED_DIR,
    PROJECT_ROOT,
    RANDOM_SEED,
    SPLITS_CSV,
    SR,
    TARGET_SAMPLES,
)

NUM_VARIANTS: int = 3
STRETCH_RANGE: tuple[float, float] = (0.8, 1.2)
PITCH_RANGE: tuple[float, float] = (-2.0, 2.0)


def _fix_length(y: np.ndarray) -> np.ndarray:
    if y.size < TARGET_SAMPLES:
        return np.pad(y, (0, TARGET_SAMPLES - y.size))
    return y[:TARGET_SAMPLES]


def _augment_once(y: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    mode = rng.integers(0, 3)  # 0=stretch, 1=pitch, 2=both
    out = y.astype(np.float32, copy=True)
    if mode in (0, 2):
        rate = float(rng.uniform(*STRETCH_RANGE))
        out = librosa.effects.time_stretch(out, rate=rate)
    if mode in (1, 2):
        steps = float(rng.uniform(*PITCH_RANGE))
        out = librosa.effects.pitch_shift(out, sr=SR, n_steps=steps)
    return _fix_length(out).astype(np.float32, copy=False)


def _read_splits(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run dataset.make_splits() first."
        )
    with path.open("r") as fh:
        return list(csv.DictReader(fh))


def _resolve(path_str: str) -> Path:
    p = Path(path_str)
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    return p


def _relpath(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path.resolve())


def expand_train(splits_csv: Path = SPLITS_CSV, *, num_variants: int = NUM_VARIANTS,
                 seed: int = RANDOM_SEED) -> Path:
    """Generate augmented variants for every train row and rewrite splits.csv.

    Idempotent at the file level: if an augmented WAV already exists on disk
    it is not regenerated, and ``splits.csv`` is rebuilt to reflect both
    originals and augmented files exactly once.
    """
    rng = np.random.default_rng(seed)
    rows = _read_splits(splits_csv)

    train_rows = [r for r in rows if r["split"] == "train"]
    other_rows = [r for r in rows if r["split"] != "train"]

    augmented: list[dict[str, str]] = []
    written = 0
    skipped = 0
    failed = 0

    for row in train_rows:
        src = _resolve(row["path"])
        label = row["label"]
        if not src.exists():
            print(f"[expand_train] missing source {src}")
            failed += 1
            continue

        for variant_idx in range(1, num_variants + 1):
            dst = src.with_name(f"{src.stem}_aug{variant_idx}.wav")
            if dst.exists():
                augmented.append(
                    {"path": _relpath(dst), "label": label, "split": "train"}
                )
                skipped += 1
                continue
            try:
                y, _ = librosa.load(str(src), sr=SR, mono=True)
                y_aug = _augment_once(y, rng)
                sf.write(str(dst), y_aug, SR, subtype="PCM_16")
                augmented.append(
                    {"path": _relpath(dst), "label": label, "split": "train"}
                )
                written += 1
            except Exception as exc:  # pragma: no cover - defensive logging
                print(f"[expand_train] FAILED {src} variant {variant_idx}: {exc}")
                failed += 1

    # Rebuild splits.csv: originals (all splits) + augmented (train only).
    with splits_csv.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["path", "label", "split"])
        for row in train_rows + augmented + other_rows:
            writer.writerow([row["path"], row["label"], row["split"]])

    _print_summary(train_rows, augmented, other_rows, written, skipped, failed)
    return splits_csv


def _print_summary(
    train_rows: list[dict[str, str]],
    augmented: list[dict[str, str]],
    other_rows: list[dict[str, str]],
    written: int,
    skipped: int,
    failed: int,
) -> None:
    n_train_orig = len(train_rows)
    n_aug = len(augmented)
    n_total_train = n_train_orig + n_aug
    n_val = sum(1 for r in other_rows if r["split"] == "val")
    n_test = sum(1 for r in other_rows if r["split"] == "test")

    print(
        f"[expand_train] written={written} skipped={skipped} failed={failed}"
    )
    print(
        f"[expand_train] train: {n_train_orig} originals + {n_aug} augmented "
        f"= {n_total_train} (val={n_val}, test={n_test})"
    )

    print("[expand_train] per-class train counts (incl. augmented):")
    for label in LABELS:
        n_orig = sum(1 for r in train_rows if r["label"] == label)
        n_a = sum(1 for r in augmented if r["label"] == label)
        print(f"  {label:<12} orig={n_orig:>4} aug={n_a:>4} total={n_orig + n_a:>4}")


def main() -> None:
    expand_train()


if __name__ == "__main__":
    main()

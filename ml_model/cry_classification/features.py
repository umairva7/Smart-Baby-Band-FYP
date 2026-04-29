"""Feature extraction for the cry classification model.

Each WAV is converted into a single ``(128, 128, 2)`` float32 tensor:

    Channel 0 -> mel spectrogram (128 mel bins x 128 time frames, dB-scaled)
    Channel 1 -> MFCC stack (40 coeffs + delta + delta-delta) resized to 128x128

Per-channel z-score normalization is applied using statistics computed from
the training split only; the stats are persisted to ``features/norm_stats.npz``
so inference paths can reuse them.

Run as a script::

    python -m cry_classification.features
"""

from __future__ import annotations

import csv
from pathlib import Path

import librosa
import numpy as np
from scipy.ndimage import zoom

from dataset import (
    LABEL_TO_INDEX,
    PROJECT_ROOT,
    SPLITS_CSV,
    SR,
    TARGET_SAMPLES,
)

# ---------------------------------------------------------------------------
# Feature parameters
# ---------------------------------------------------------------------------

N_MELS: int = 128
N_FFT: int = 2048
HOP_LENGTH: int = 375  # ~129 frames for a 3s @ 16kHz clip
N_MFCC: int = 40
TARGET_HW: tuple[int, int] = (128, 128)
INPUT_CHANNELS: int = 2

FEATURES_DIR: Path = PROJECT_ROOT / "features"
NORM_STATS_PATH: Path = FEATURES_DIR / "norm_stats.npz"


# ---------------------------------------------------------------------------
# Single-clip feature extraction
# ---------------------------------------------------------------------------


def _resize(arr: np.ndarray, target: tuple[int, int]) -> np.ndarray:
    """Resize a 2D array to ``target`` using cubic ``scipy.ndimage.zoom``."""
    h, w = arr.shape
    th, tw = target
    if (h, w) == (th, tw):
        return arr.astype(np.float32, copy=False)
    return zoom(arr, (th / h, tw / w), order=3).astype(np.float32, copy=False)


def _load_audio(path: Path) -> np.ndarray:
    y, _ = librosa.load(str(path), sr=SR, mono=True)
    if y.size < TARGET_SAMPLES:
        y = np.pad(y, (0, TARGET_SAMPLES - y.size))
    else:
        y = y[:TARGET_SAMPLES]
    return y.astype(np.float32, copy=False)


def extract_features(wav: np.ndarray | Path | str) -> np.ndarray:
    """Compute the ``(128, 128, 2)`` feature tensor for a single clip.

    ``wav`` may be a numpy waveform (assumed 16 kHz mono, 3 s) or a path to a
    WAV file that will be loaded and length-normalized first.
    """
    if isinstance(wav, (str, Path)):
        y = _load_audio(Path(wav))
    else:
        y = np.asarray(wav, dtype=np.float32)
        if y.size < TARGET_SAMPLES:
            y = np.pad(y, (0, TARGET_SAMPLES - y.size))
        else:
            y = y[:TARGET_SAMPLES]

    mel = librosa.feature.melspectrogram(
        y=y,
        sr=SR,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
        n_mels=N_MELS,
        power=2.0,
    )
    mel_db = librosa.power_to_db(mel, ref=np.max).astype(np.float32)
    mel_db = _resize(mel_db, TARGET_HW)

    mfcc = librosa.feature.mfcc(
        y=y,
        sr=SR,
        n_mfcc=N_MFCC,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
    ).astype(np.float32)
    delta = librosa.feature.delta(mfcc).astype(np.float32)
    delta2 = librosa.feature.delta(mfcc, order=2).astype(np.float32)
    mfcc_stack = np.vstack([mfcc, delta, delta2])  # (120, T)
    mfcc_resized = _resize(mfcc_stack, TARGET_HW)

    return np.stack([mel_db, mfcc_resized], axis=-1).astype(np.float32)


# ---------------------------------------------------------------------------
# Cache builder
# ---------------------------------------------------------------------------


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


def _compute_split(rows: list[dict[str, str]]) -> tuple[np.ndarray, np.ndarray]:
    n = len(rows)
    X = np.empty((n, TARGET_HW[0], TARGET_HW[1], INPUT_CHANNELS), dtype=np.float32)
    y = np.empty(n, dtype=np.int64)
    for i, row in enumerate(rows):
        path = _resolve(row["path"])
        X[i] = extract_features(path)
        y[i] = LABEL_TO_INDEX[row["label"]]
        if (i + 1) % 200 == 0 or i == n - 1:
            print(f"    progress {i + 1}/{n}")
    return X, y


def _normalize_inplace(X: np.ndarray, mean: np.ndarray, std: np.ndarray) -> None:
    eps = 1e-6
    for c in range(X.shape[-1]):
        X[..., c] = (X[..., c] - mean[c]) / (std[c] + eps)


def build_feature_cache(splits_csv: Path = SPLITS_CSV) -> Path:
    """Compute and save per-split ``X_*.npy`` / ``y_*.npy`` caches.

    The training split is processed first so its per-channel mean/std can be
    used to z-score normalize all three splits consistently.
    """
    rows = _read_splits(splits_csv)

    by_split: dict[str, list[dict[str, str]]] = {"train": [], "val": [], "test": []}
    for row in rows:
        if row["split"] not in by_split:
            continue
        by_split[row["split"]].append(row)

    for split, items in by_split.items():
        if not items:
            raise RuntimeError(f"No rows found for split={split} in {splits_csv}")

    FEATURES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[features] computing TRAIN ({len(by_split['train'])} samples)")
    X_train, y_train = _compute_split(by_split["train"])

    mean = X_train.mean(axis=(0, 1, 2)).astype(np.float32)
    std = X_train.std(axis=(0, 1, 2)).astype(np.float32)
    np.savez(NORM_STATS_PATH, mean=mean, std=std)
    print(f"[features] saved norm stats -> {NORM_STATS_PATH} mean={mean} std={std}")

    _normalize_inplace(X_train, mean, std)
    np.save(FEATURES_DIR / "X_train.npy", X_train)
    np.save(FEATURES_DIR / "y_train.npy", y_train)
    print(f"[features] saved X_train{X_train.shape} y_train{y_train.shape}")
    del X_train, y_train

    for split in ("val", "test"):
        print(f"[features] computing {split.upper()} ({len(by_split[split])} samples)")
        X, y = _compute_split(by_split[split])
        _normalize_inplace(X, mean, std)
        np.save(FEATURES_DIR / f"X_{split}.npy", X)
        np.save(FEATURES_DIR / f"y_{split}.npy", y)
        print(f"[features] saved X_{split}{X.shape} y_{split}{y.shape}")

    return FEATURES_DIR


def load_norm_stats(path: Path = NORM_STATS_PATH) -> tuple[np.ndarray, np.ndarray]:
    data = np.load(path)
    return data["mean"], data["std"]


def main() -> None:
    build_feature_cache()


if __name__ == "__main__":
    main()

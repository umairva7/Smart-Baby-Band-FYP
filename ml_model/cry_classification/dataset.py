"""Dataset preparation for the cry classification model.

Responsibilities:
    1. Walk the two raw datasets (DonateACry + baby-crying), apply label
       harmonization to a final set of 5 classes, dropping
       ``awake``, ``burping`` and ``belly_pain``.
    2. Resample every clip to 16 kHz mono, trim leading/trailing silence,
       and pad / truncate to a fixed 3-second window. Output is written to
       ``data/processed/<label>/<stem>.wav`` and is idempotent.
    3. Generate a stratified 80/10/10 train/val/test split and persist it
       to ``data/processed/splits.csv``.

Run as a script::

    python -m cry_classification.dataset
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

import librosa
import numpy as np
import soundfile as sf
from sklearn.model_selection import train_test_split

# ---------------------------------------------------------------------------
# Shared constants (re-imported by other modules)
# ---------------------------------------------------------------------------

LABELS: list[str] = ["hungry", "tired", "discomfort", "diaper", "hug"]
LABEL_TO_INDEX: dict[str, int] = {name: i for i, name in enumerate(LABELS)}

SR: int = 16_000
DURATION: float = 3.0
TARGET_SAMPLES: int = int(SR * DURATION)
TRIM_TOP_DB: int = 30
RANDOM_SEED: int = 42

# Map from source folder name -> harmonized label, or ``None`` to skip.
LABEL_MAP: dict[str, str | None] = {
    # DonateACry corpus
    "hungry": "hungry",
    "tired": "tired",
    "discomfort": "discomfort",
    "burping": None,
    "belly_pain": None,
    # baby-crying corpus
    "sleepy": "tired",
    "uncomfortable": "discomfort",
    "diaper": "diaper",
    "hug": "hug",
    "awake": None,
}

PROJECT_ROOT: Path = Path(__file__).resolve().parent
RAW_DIR: Path = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR: Path = PROJECT_ROOT / "data" / "processed"
SPLITS_CSV: Path = PROCESSED_DIR / "splits.csv"

DONATEACRY_ROOT: Path = (
    RAW_DIR
    / "donateacry-corpus-master"
    / "donateacry_corpus_cleaned_and_updated_data"
)
BABY_CRYING_TRAIN: Path = RAW_DIR / "baby-crying" / "train"


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def discover_raw() -> list[tuple[Path, str]]:
    """Return ``[(path, harmonized_label), ...]`` from both raw datasets.

    Folders mapped to ``None`` (``awake``, ``burping``, ``belly_pain``) are
    silently skipped. Folders with no mapping at all raise to surface
    unexpected dataset shape changes.
    """

    rows: list[tuple[Path, str]] = []

    for root in (DONATEACRY_ROOT, BABY_CRYING_TRAIN):
        if not root.exists():
            print(f"[discover_raw] WARNING: missing root {root}")
            continue
        for class_dir in sorted(p for p in root.iterdir() if p.is_dir()):
            src_label = class_dir.name
            if src_label not in LABEL_MAP:
                raise ValueError(
                    f"Unknown source label '{src_label}' in {class_dir}. "
                    f"Update LABEL_MAP in dataset.py."
                )
            target = LABEL_MAP[src_label]
            if target is None:
                continue
            for wav in sorted(class_dir.glob("*.wav")):
                rows.append((wav, target))

    return rows


# ---------------------------------------------------------------------------
# Audio normalization (resample / trim / pad)
# ---------------------------------------------------------------------------


def _load_normalize(path: Path) -> np.ndarray:
    """Load ``path``, resample to 16 kHz mono, silence-trim, pad/truncate to 3s."""
    y, _ = librosa.load(str(path), sr=SR, mono=True)
    if y.size == 0:
        return np.zeros(TARGET_SAMPLES, dtype=np.float32)

    y_trim, _ = librosa.effects.trim(y, top_db=TRIM_TOP_DB)
    if y_trim.size == 0:
        y_trim = y

    if y_trim.size < TARGET_SAMPLES:
        y_trim = np.pad(y_trim, (0, TARGET_SAMPLES - y_trim.size))
    else:
        y_trim = y_trim[:TARGET_SAMPLES]

    return y_trim.astype(np.float32, copy=False)


def _processed_path(label: str, src: Path) -> Path:
    """Compute the destination filename for a processed clip.

    The source dataset (``donateacry`` vs ``babycrying``) is encoded in the
    output stem so files coming from different corpora cannot collide.
    """
    if "donateacry" in str(src):
        prefix = "donateacry"
    elif "baby-crying" in str(src):
        prefix = "babycrying"
    else:
        prefix = "src"
    return PROCESSED_DIR / label / f"{prefix}_{src.stem}.wav"


def prepare_processed(rows: Iterable[tuple[Path, str]] | None = None) -> list[tuple[Path, str]]:
    """Resample/trim/pad every raw clip into ``data/processed/<label>/``.

    Returns the list of ``(processed_path, label)`` rows. Idempotent: clips
    that already exist on disk are not re-processed.
    """
    if rows is None:
        rows = discover_raw()

    for label in LABELS:
        (PROCESSED_DIR / label).mkdir(parents=True, exist_ok=True)

    out: list[tuple[Path, str]] = []
    skipped = 0
    written = 0
    failed = 0

    for src, label in rows:
        dst = _processed_path(label, src)
        if dst.exists():
            out.append((dst, label))
            skipped += 1
            continue
        try:
            y = _load_normalize(src)
            if np.abs(y).max() < 1e-4 or np.sqrt(np.mean(y**2)) < 1e-4:
                print(f"[prepare_processed] SKIPPING {src.name} (too quiet/empty)")
                skipped += 1
                continue
            sf.write(str(dst), y, SR, subtype="PCM_16")
            out.append((dst, label))
            written += 1
        except Exception as exc:  # pragma: no cover - defensive logging
            print(f"[prepare_processed] FAILED {src}: {exc}")
            failed += 1

    print(
        f"[prepare_processed] wrote={written} skipped={skipped} failed={failed} "
        f"total_kept={len(out)}"
    )
    return out


# ---------------------------------------------------------------------------
# Stratified splits
# ---------------------------------------------------------------------------


def _corpus(path: str | Path) -> str:
    p = str(path).lower()
    if "donateacry" in p:
        return "donateacry"
    if "babycrying" in p or "baby-crying" in p:
        return "babycrying"
    return "unknown"


def make_splits(
    rows: list[tuple[Path, str]] | None = None,
    *,
    val_size: float = 0.10,
    test_size: float = 0.10,
    seed: int = RANDOM_SEED,
    strategy: str = "stratified",  # can be "cross_corpus"
    test_corpus: str = "donateacry",
    downsample_corpus: bool = True,
) -> Path:
    """Write a stratified 80/10/10 ``splits.csv`` next to processed audio.

    Format: ``path,label,split`` where ``split`` is one of
    ``train|val|test`` and ``path`` is relative to the project root.
    """
    if rows is None:
        rows = []
        for label in LABELS:
            for wav in sorted((PROCESSED_DIR / label).glob("*.wav")):
                rows.append((wav, label))

    if not rows:
        raise RuntimeError(
            "No processed clips found. Run prepare_processed() first."
        )

    # Report corpus balance
    print("[make_splits] Initial corpus distribution by class:")
    from collections import defaultdict
    counts = defaultdict(int)
    for path, label in rows:
        counts[(label, _corpus(path))] += 1
    
    corpora_names = sorted(list(set(_corpus(p) for p, _ in rows)))
    header = f"  {'label':<12}" + "".join([f" {c:>12}" for c in corpora_names])
    print(header)
    for label in LABELS:
        row_str = f"  {label:<12}"
        for c in corpora_names:
            row_str += f" {counts[(label, c)]:>12}"
        print(row_str)

    if downsample_corpus and strategy == "stratified":
        balanced_rows = []
        grouped = defaultdict(list)
        for path, label in rows:
            grouped[(label, _corpus(path))].append((path, label))
        
        for label in LABELS:
            c_for_label = [c for (l, c) in grouped.keys() if l == label]
            if not c_for_label:
                continue
            if len(c_for_label) > 1:
                min_count = min(len(grouped[(label, c)]) for c in c_for_label)
            else:
                min_count = len(grouped[(label, c_for_label[0])])
            
            rng = np.random.default_rng(seed)
            for c in c_for_label:
                samples = grouped[(label, c)]
                rng.shuffle(samples)
                balanced_rows.extend(samples[:min_count])
        rows = balanced_rows
        print(f"[make_splits] Downsampled to {len(rows)} clips for corpus balance.")

    paths = np.array([str(p) for p, _ in rows])
    labels = np.array([lbl for _, lbl in rows])

    if strategy == "cross_corpus":
        corpora = np.array([_corpus(p) for p in paths])
        test_mask = corpora == test_corpus
        p_test = paths[test_mask]
        y_test = labels[test_mask]
        
        p_rem = paths[~test_mask]
        y_rem = labels[~test_mask]
        
        if len(p_rem) == 0:
            raise ValueError(f"No samples left for train/val after holding out {test_corpus}")
            
        p_train, p_val, y_train, y_val = train_test_split(
            p_rem, y_rem,
            test_size=val_size / (1.0 - test_size),
            random_state=seed,
            stratify=y_rem
        )
    else:
        p_train_val, p_test, y_train_val, y_test = train_test_split(
            paths,
            labels,
            test_size=test_size,
            random_state=seed,
            stratify=labels,
        )
        val_relative = val_size / (1.0 - test_size)
        p_train, p_val, y_train, y_val = train_test_split(
            p_train_val,
            y_train_val,
            test_size=val_relative,
            random_state=seed,
            stratify=y_train_val,
        )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with SPLITS_CSV.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["path", "label", "split"])
        for path, label in zip(p_train, y_train):
            writer.writerow([_relpath(path), label, "train"])
        for path, label in zip(p_val, y_val):
            writer.writerow([_relpath(path), label, "val"])
        for path, label in zip(p_test, y_test):
            writer.writerow([_relpath(path), label, "test"])

    _print_split_summary(y_train, y_val, y_test)
    print(f"[make_splits] wrote {SPLITS_CSV}")
    return SPLITS_CSV


def _relpath(path: str | Path) -> str:
    p = Path(path).resolve()
    try:
        return str(p.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(p)


def _print_split_summary(y_train: np.ndarray, y_val: np.ndarray, y_test: np.ndarray) -> None:
    print("[make_splits] class distribution")
    print(f"  {'label':<12} {'train':>6} {'val':>5} {'test':>5}")
    for label in LABELS:
        n_tr = int(np.sum(y_train == label))
        n_va = int(np.sum(y_val == label))
        n_te = int(np.sum(y_test == label))
        print(f"  {label:<12} {n_tr:>6} {n_va:>5} {n_te:>5}")
    print(f"  {'TOTAL':<12} {len(y_train):>6} {len(y_val):>5} {len(y_test):>5}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    rows = discover_raw()
    print(f"[main] discovered {len(rows)} raw clips after harmonization")
    processed = prepare_processed(rows)
    make_splits(processed)


if __name__ == "__main__":
    main()

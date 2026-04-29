"""Train the cry classification model.

Loads the precomputed feature caches under ``features/``, computes balanced
class weights from the train labels, and trains the CNN+attention model with
``ReduceLROnPlateau``, ``EarlyStopping``, ``ModelCheckpoint`` and TensorBoard.

Run as a script::

    python -m cry_classification.train --epochs 60 --batch-size 32
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from sklearn.utils.class_weight import compute_class_weight
from tensorflow import keras

from dataset import LABELS, PROJECT_ROOT
from features import FEATURES_DIR
from model import build_model

MODELS_DIR: Path = PROJECT_ROOT / "models"
LOGS_DIR: Path = PROJECT_ROOT / "logs"
BEST_MODEL_PATH: Path = MODELS_DIR / "best.keras"
HISTORY_PATH: Path = LOGS_DIR / "history.json"


def _load_split(split: str) -> tuple[np.ndarray, np.ndarray]:
    X = np.load(FEATURES_DIR / f"X_{split}.npy")
    y = np.load(FEATURES_DIR / f"y_{split}.npy")
    return X, y


def _class_weights(y_train: np.ndarray) -> dict[int, float]:
    classes = np.arange(len(LABELS))
    weights = compute_class_weight(
        class_weight="balanced",
        classes=classes,
        y=y_train,
    )
    cw = {int(c): float(w) for c, w in zip(classes, weights)}
    print("[train] class weights:")
    for idx, label in enumerate(LABELS):
        print(f"  {label:<12} -> {cw[idx]:.4f}")
    return cw


def _callbacks(run_dir: Path) -> list[keras.callbacks.Callback]:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)

    return [
        keras.callbacks.ModelCheckpoint(
            filepath=str(BEST_MODEL_PATH),
            monitor="val_accuracy",
            mode="max",
            save_best_only=True,
            verbose=1,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=3,
            min_lr=1e-6,
            verbose=1,
        ),
        keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=8,
            restore_best_weights=True,
            verbose=1,
        ),
        keras.callbacks.TensorBoard(log_dir=str(run_dir), histogram_freq=0),
    ]


def train(epochs: int, batch_size: int, learning_rate: float) -> Path:
    X_train, y_train = _load_split("train")
    X_val, y_val = _load_split("val")

    print(
        f"[train] loaded train{X_train.shape} val{X_val.shape} "
        f"classes={len(LABELS)}"
    )

    model = build_model(input_shape=X_train.shape[1:], learning_rate=learning_rate)
    model.summary()

    class_weight = _class_weights(y_train)

    timestamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = LOGS_DIR / timestamp
    callbacks = _callbacks(run_dir)

    history = model.fit(
        X_train,
        y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        class_weight=class_weight,
        callbacks=callbacks,
        verbose=2,
    )

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    serializable = {k: [float(v) for v in vals] for k, vals in history.history.items()}
    with HISTORY_PATH.open("w") as fh:
        json.dump(serializable, fh, indent=2)
    print(f"[train] saved history -> {HISTORY_PATH}")
    print(f"[train] best checkpoint -> {BEST_MODEL_PATH}")
    return BEST_MODEL_PATH


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train cry classification model.")
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tf.keras.utils.set_random_seed(args.seed)
    train(epochs=args.epochs, batch_size=args.batch_size, learning_rate=args.lr)


if __name__ == "__main__":
    main()

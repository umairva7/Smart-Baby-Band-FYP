import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.utils.class_weight import compute_class_weight

from config import (
    DATA_DIR,
    LABELS,
    LABEL_TO_ID,
    LOGS_DIR,
    MODELS_DIR,
    RANDOM_SEED,
)
from model import build_model


def set_seed(seed: int) -> None:
    np.random.seed(seed)
    tf.random.set_seed(seed)


def load_feature_config(config_path: Path) -> tuple[int, int, int]:
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding="utf-8"))
        return tuple(config["feature_shape"])
    raise SystemExit("feature_config.json not found. Run features.py first.")


def make_dataset(df: pd.DataFrame, input_shape: tuple[int, int, int], batch_size: int, shuffle: bool) -> tf.data.Dataset:
    paths = df["feature_path"].tolist()
    labels = df["label"].map(LABEL_TO_ID).astype(np.int32).tolist()

    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    if shuffle:
        ds = ds.shuffle(buffer_size=len(paths), seed=RANDOM_SEED, reshuffle_each_iteration=True)

    def load_npy(path: tf.Tensor, label: tf.Tensor) -> tuple[tf.Tensor, tf.Tensor]:
        def _py_load(p: bytes) -> np.ndarray:
            if isinstance(p, (bytes, bytearray)):
                path_str = p.decode("utf-8")
            else:
                path_str = p.item().decode("utf-8")
            return np.load(path_str).astype(np.float32)

        feature = tf.numpy_function(_py_load, [path], tf.float32)
        feature.set_shape(input_shape)
        return feature, label

    ds = ds.map(load_npy, num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)
    return ds


def main() -> None:
    parser = argparse.ArgumentParser(description="Train cry classification model.")
    parser.add_argument("--splits-path", type=Path, default=DATA_DIR / "splits.csv")
    parser.add_argument("--config-path", type=Path, default=MODELS_DIR / "feature_config.json")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--learning-rate", type=float, default=0.8)
    parser.add_argument("--optimizer", choices=["sgd", "adam"], default="sgd")
    args = parser.parse_args()

    set_seed(RANDOM_SEED)

    df = pd.read_csv(args.splits_path)
    if "feature_path" not in df.columns:
        raise SystemExit("splits.csv is missing feature_path. Run features.py first.")

    train_df = df[df["split"] == "train"].copy()
    val_df = df[df["split"] == "val"].copy()

    if train_df.empty or val_df.empty:
        raise SystemExit("Train/val splits are empty. Run dataset.py first.")

    input_shape = load_feature_config(args.config_path)

    train_ds = make_dataset(train_df, input_shape, args.batch_size, shuffle=True)
    val_ds = make_dataset(val_df, input_shape, args.batch_size, shuffle=False)

    class_weights = compute_class_weight(
        class_weight="balanced",
        classes=np.arange(len(LABELS)),
        y=train_df["label"].map(LABEL_TO_ID).values,
    )
    class_weight = {i: weight for i, weight in enumerate(class_weights)}

    learning_rate = args.learning_rate
    model = build_model(input_shape, num_classes=len(LABELS), learning_rate=learning_rate)
    if args.optimizer == "adam":
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True, monitor="val_loss"),
        tf.keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=5, min_lr=1e-6, monitor="val_loss"),
        tf.keras.callbacks.ModelCheckpoint(MODELS_DIR / "best_model.h5", save_best_only=True),
    ]

    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.epochs,
        class_weight=class_weight,
        callbacks=callbacks,
    )

    history_path = LOGS_DIR / "training_history.json"
    history_path.write_text(json.dumps(history.history, indent=2), encoding="utf-8")
    print(f"Saved training history to {history_path}")


if __name__ == "__main__":
    main()

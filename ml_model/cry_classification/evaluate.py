import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

from config import DATA_DIR, LABELS, LABEL_TO_ID, LOGS_DIR, MODELS_DIR, RANDOM_SEED
from model import build_model


def set_seed(seed: int) -> None:
    np.random.seed(seed)
    tf.random.set_seed(seed)


def load_feature_config(config_path: Path) -> tuple[int, int, int]:
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding="utf-8"))
        return tuple(config["feature_shape"])
    raise SystemExit("feature_config.json not found. Run features.py first.")


def make_dataset(
    df: pd.DataFrame,
    input_shape: tuple[int, int, int],
    batch_size: int,
    label_map: dict[str, int],
) -> tf.data.Dataset:
    paths = df["feature_path"].tolist()
    labels = df["label"].map(label_map).astype(np.int32).tolist()

    ds = tf.data.Dataset.from_tensor_slices((paths, labels))

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


def evaluate_split(
    model: tf.keras.Model,
    df: pd.DataFrame,
    input_shape: tuple[int, int, int],
    batch_size: int,
    label_map: dict[str, int],
    label_names: list[str],
) -> dict:
    ds = make_dataset(df, input_shape, batch_size, label_map)
    y_true = df["label"].map(label_map).values
    y_prob = model.predict(ds, verbose=0)
    y_pred = np.argmax(y_prob, axis=1)

    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "f1_per_class": {
            label_names[i]: float(score)
            for i, score in enumerate(f1_score(y_true, y_pred, average=None, labels=range(len(label_names))))
        },
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=range(len(label_names))).tolist(),
        "classification_report": classification_report(y_true, y_pred, target_names=label_names, output_dict=True),
    }
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate cry classification model.")
    parser.add_argument("--splits-path", type=Path, default=DATA_DIR / "splits.csv")
    parser.add_argument("--config-path", type=Path, default=MODELS_DIR / "feature_config.json")
    parser.add_argument("--model-path", type=Path, default=MODELS_DIR / "best_model.h5")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--skip-cross-dataset", action="store_true")
    parser.add_argument("--epochs", type=int, default=30)
    args = parser.parse_args()

    set_seed(RANDOM_SEED)

    df = pd.read_csv(args.splits_path)
    if "feature_path" not in df.columns:
        raise SystemExit("splits.csv is missing feature_path. Run features.py first.")

    input_shape = load_feature_config(args.config_path)

    model = tf.keras.models.load_model(args.model_path)
    model.compile(
        optimizer=tf.keras.optimizers.SGD(learning_rate=0.8),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    test_df = df[df["split"] == "test"].copy()
    if test_df.empty:
        raise SystemExit("Test split is empty.")

    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    metrics = evaluate_split(model, test_df, input_shape, args.batch_size, LABEL_TO_ID, LABELS)
    metrics_path = LOGS_DIR / "test_metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"Saved test metrics to {metrics_path}")

    if args.skip_cross_dataset:
        return

    dac_df = df[(df["source_dataset"] == "dac") & (df["label"].isin(["hungry", "discomfort", "belly_pain", "burping"]))]
    baby_df = df[(df["source_dataset"] == "baby_crying") & (df["label"].isin(["hungry", "discomfort"]))]

    dac_train = dac_df[dac_df["split"] == "train"].copy()
    dac_val = dac_df[dac_df["split"] == "val"].copy()
    baby_test = baby_df[baby_df["split"] == "test"].copy()

    if dac_train.empty or dac_val.empty or baby_test.empty:
        print("Cross-dataset split is empty. Skipping cross-dataset evaluation.")
        return

    cross_labels = ["hungry", "discomfort", "belly_pain", "burping"]
    cross_label_map = {label: idx for idx, label in enumerate(cross_labels)}

    cross_model = build_model(input_shape, num_classes=len(cross_labels), learning_rate=0.8)
    train_ds = make_dataset(dac_train, input_shape, args.batch_size, cross_label_map)
    val_ds = make_dataset(dac_val, input_shape, args.batch_size, cross_label_map)

    cross_model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.epochs,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True, monitor="val_loss"),
        ],
        verbose=0,
    )

    cross_metrics = evaluate_split(
        cross_model,
        baby_test,
        input_shape,
        args.batch_size,
        cross_label_map,
        cross_labels,
    )
    cross_path = LOGS_DIR / "cross_dataset_metrics.json"
    cross_path.write_text(json.dumps(cross_metrics, indent=2), encoding="utf-8")
    print(f"Saved cross-dataset metrics to {cross_path}")


if __name__ == "__main__":
    main()

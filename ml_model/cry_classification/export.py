"""Export a trained cry classification model.

Produces:
    models/cry_classification.keras   (Keras v3 format)
    models/cry_classification.h5      (legacy HDF5 format)
    models/cry_classification.tflite      (float32 TFLite)
    models/cry_classification_int8.tflite (dynamic-range int8 TFLite)

Run::

    python -m cry_classification.export --model models/best.keras
"""

from __future__ import annotations

import argparse
from pathlib import Path

import tensorflow as tf
from tensorflow import keras

from dataset import PROJECT_ROOT

MODELS_DIR: Path = PROJECT_ROOT / "models"
DEFAULT_MODEL: Path = MODELS_DIR / "best.keras"
EXPORT_BASENAME: str = "cry_classification"


def _save_keras(model: keras.Model, base: Path) -> tuple[Path, Path]:
    keras_path = base.with_suffix(".keras")
    h5_path = base.with_suffix(".h5")
    model.save(keras_path)
    model.save(h5_path)
    print(f"[export] saved {keras_path}")
    print(f"[export] saved {h5_path}")
    return keras_path, h5_path


def _save_tflite(model: keras.Model, base: Path) -> tuple[Path, Path]:
    fp32_path = base.with_suffix(".tflite")
    int8_path = base.parent / f"{base.stem}_int8.tflite"

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    fp32_bytes = converter.convert()
    fp32_path.write_bytes(fp32_bytes)
    print(f"[export] saved {fp32_path} ({len(fp32_bytes) / 1024:.1f} KiB)")

    converter_q = tf.lite.TFLiteConverter.from_keras_model(model)
    converter_q.optimizations = [tf.lite.Optimize.DEFAULT]
    int8_bytes = converter_q.convert()
    int8_path.write_bytes(int8_bytes)
    print(f"[export] saved {int8_path} ({len(int8_bytes) / 1024:.1f} KiB)")
    return fp32_path, int8_path


def export(model_path: Path = DEFAULT_MODEL,
           out_dir: Path = MODELS_DIR,
           basename: str = EXPORT_BASENAME) -> dict[str, Path]:
    if not model_path.exists():
        raise FileNotFoundError(
            f"{model_path} not found. Train the model first (train.py)."
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    base = out_dir / basename

    print(f"[export] loading {model_path}")
    model = keras.models.load_model(model_path)
    model.summary()

    keras_path, h5_path = _save_keras(model, base)
    tflite_path, tflite_int8_path = _save_tflite(model, base)

    return {
        "keras": keras_path,
        "h5": h5_path,
        "tflite": tflite_path,
        "tflite_int8": tflite_int8_path,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export cry classification model.")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--out-dir", type=Path, default=MODELS_DIR)
    parser.add_argument("--basename", type=str, default=EXPORT_BASENAME)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    export(args.model, args.out_dir, args.basename)


if __name__ == "__main__":
    main()

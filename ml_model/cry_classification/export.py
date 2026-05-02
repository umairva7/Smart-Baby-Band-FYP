import argparse
import json
from pathlib import Path

import tensorflow as tf

from config import DURATION_SEC, HOP_LENGTH, ID_TO_LABEL, MODELS_DIR, N_FFT, N_MELS, N_MFCC, SAMPLE_RATE


def main() -> None:
    parser = argparse.ArgumentParser(description="Export cry classification model artifacts.")
    parser.add_argument("--best-model", type=Path, default=MODELS_DIR / "best_model.h5")
    parser.add_argument("--output-model", type=Path, default=MODELS_DIR / "model.h5")
    parser.add_argument("--config-path", type=Path, default=MODELS_DIR / "feature_config.json")
    args = parser.parse_args()

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    model = tf.keras.models.load_model(args.best_model)
    model.save(args.output_model)

    label_map_path = MODELS_DIR / "label_map.json"
    label_map_path.write_text(json.dumps(ID_TO_LABEL, indent=2), encoding="utf-8")

    if not args.config_path.exists():
        feature_config = {
            "sample_rate": SAMPLE_RATE,
            "duration_sec": DURATION_SEC,
            "n_fft": N_FFT,
            "hop_length": HOP_LENGTH,
            "n_mels": N_MELS,
            "n_mfcc": N_MFCC,
        }
        args.config_path.write_text(json.dumps(feature_config, indent=2), encoding="utf-8")

    print(f"Saved model to {args.output_model}")
    print(f"Saved label map to {label_map_path}")


if __name__ == "__main__":
    main()

"""Evaluate a trained cry classification model on the held-out test split.

Outputs:
    - per-class classification report printed to stdout
    - confusion matrix figure -> ``logs/confusion_matrix.png``
    - top-1 accuracy + macro-F1 -> ``logs/test_metrics.json``

Run::

    python -m cry_classification.evaluate
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from tensorflow import keras

from dataset import LABELS, PROJECT_ROOT
from features import FEATURES_DIR

LOGS_DIR: Path = PROJECT_ROOT / "logs"
DEFAULT_MODEL: Path = PROJECT_ROOT / "models" / "best.keras"
CM_PNG: Path = LOGS_DIR / "confusion_matrix.png"
METRICS_JSON: Path = LOGS_DIR / "test_metrics.json"


def _plot_confusion(cm: np.ndarray, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    im = ax.imshow(cm, cmap="Blues")
    fig.colorbar(im, ax=ax)

    ax.set_xticks(range(len(LABELS)))
    ax.set_yticks(range(len(LABELS)))
    ax.set_xticklabels(LABELS, rotation=45, ha="right")
    ax.set_yticklabels(LABELS)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title("Confusion matrix (test split)")

    threshold = cm.max() / 2.0 if cm.max() > 0 else 0.5
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(
                j,
                i,
                str(int(cm[i, j])),
                ha="center",
                va="center",
                color="white" if cm[i, j] > threshold else "black",
                fontsize=10,
            )

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def evaluate(model_path: Path = DEFAULT_MODEL) -> dict:
    if not model_path.exists():
        raise FileNotFoundError(
            f"{model_path} not found. Train the model first (train.py)."
        )

    X_test = np.load(FEATURES_DIR / "X_test.npy")
    y_test = np.load(FEATURES_DIR / "y_test.npy")
    print(f"[evaluate] loaded test{X_test.shape} from {FEATURES_DIR}")

    model = keras.models.load_model(model_path)
    probs = model.predict(X_test, verbose=0)
    y_pred = probs.argmax(axis=1)

    acc = float(accuracy_score(y_test, y_pred))
    macro_f1 = float(f1_score(y_test, y_pred, average="macro"))
    report = classification_report(
        y_test,
        y_pred,
        target_names=LABELS,
        digits=4,
        zero_division=0,
    )
    cm = confusion_matrix(y_test, y_pred, labels=list(range(len(LABELS))))

    print(report)
    print(f"[evaluate] top-1 accuracy = {acc:.4f}")
    print(f"[evaluate] macro F1       = {macro_f1:.4f}")

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    _plot_confusion(cm, CM_PNG)
    print(f"[evaluate] saved confusion matrix -> {CM_PNG}")

    metrics = {
        "model_path": str(model_path),
        "n_test": int(len(y_test)),
        "accuracy": acc,
        "macro_f1": macro_f1,
        "labels": LABELS,
        "confusion_matrix": cm.tolist(),
        "classification_report": report,
    }
    with METRICS_JSON.open("w") as fh:
        json.dump(metrics, fh, indent=2)
    print(f"[evaluate] saved metrics -> {METRICS_JSON}")
    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate cry classification model.")
    parser.add_argument(
        "--model",
        type=Path,
        default=DEFAULT_MODEL,
        help="Path to a saved Keras model (.keras / .h5).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    evaluate(args.model)


if __name__ == "__main__":
    main()

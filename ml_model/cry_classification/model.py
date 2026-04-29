"""CNN + MultiHeadAttention model for the cry classification task.

Architecture (from the project plan):

    Input (128, 128, 2)
      -> Conv2D(32) + BN + ReLU + MaxPool
      -> Conv2D(64) + BN + ReLU + MaxPool
      -> Conv2D(128) + BN + ReLU + MaxPool
      -> Reshape (H*W, C) sequence
      -> MultiHeadAttention(heads=4, key_dim=32) (self-attention)
      -> GlobalAveragePooling1D
      -> Dense(128) + Dropout(0.3)
      -> Dense(n_classes, softmax)

Loss:      sparse_categorical_crossentropy
Optimizer: Adam(lr=1e-3)
"""

from __future__ import annotations

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

from dataset import LABELS

INPUT_SHAPE: tuple[int, int, int] = (128, 128, 2)
NUM_CLASSES: int = len(LABELS)
ATTN_HEADS: int = 4
ATTN_KEY_DIM: int = 32
DENSE_UNITS: int = 128
DROPOUT_RATE: float = 0.3


def _conv_block(x, filters: int, name: str):
    x = layers.Conv2D(filters, kernel_size=3, padding="same", name=f"{name}_conv")(x)
    x = layers.BatchNormalization(name=f"{name}_bn")(x)
    x = layers.ReLU(name=f"{name}_relu")(x)
    x = layers.MaxPool2D(pool_size=2, name=f"{name}_pool")(x)
    return x


def build_model(
    input_shape: tuple[int, int, int] = INPUT_SHAPE,
    n_classes: int = NUM_CLASSES,
    learning_rate: float = 1e-3,
) -> keras.Model:
    """Construct and compile the CNN + attention classifier."""
    inputs = keras.Input(shape=input_shape, name="features")

    x = _conv_block(inputs, 32, "block1")
    x = _conv_block(x, 64, "block2")
    x = _conv_block(x, 128, "block3")

    h, w, c = x.shape[1], x.shape[2], x.shape[3]
    x = layers.Reshape((h * w, c), name="to_sequence")(x)

    x = layers.MultiHeadAttention(
        num_heads=ATTN_HEADS,
        key_dim=ATTN_KEY_DIM,
        name="self_attention",
    )(x, x)

    x = layers.GlobalAveragePooling1D(name="gap")(x)
    x = layers.Dense(DENSE_UNITS, activation="relu", name="dense_1")(x)
    x = layers.Dropout(DROPOUT_RATE, name="dropout")(x)
    outputs = layers.Dense(n_classes, activation="softmax", name="logits")(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name="cry_cnn_attention")
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


if __name__ == "__main__":
    m = build_model()
    m.summary()
    print(f"TF version: {tf.__version__}")

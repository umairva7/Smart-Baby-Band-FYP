"""CNN + MultiHeadAttention model for the cry classification task.

Architecture (from the project plan):

    Input (128, 128, 2)
      -> SpecAugment (freq mask + time mask, training only)
      -> Conv2D(32) + BN + ReLU + MaxPool  [L2=1e-4]
      -> Conv2D(64) + BN + ReLU + MaxPool  [L2=1e-4]
      -> Conv2D(128) + BN + ReLU + MaxPool [L2=1e-4]
      -> Reshape (H*W, C) sequence
      -> MultiHeadAttention(heads=4, key_dim=32) (self-attention)
      -> GlobalAveragePooling1D
      -> Dense(128) + Dropout(0.5)         [L2=1e-4]
      -> Dense(n_classes, softmax)         [L2=1e-4]

Loss:      sparse_categorical_crossentropy
Optimizer: Adam(lr=1e-3)
"""

from __future__ import annotations

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, regularizers

from dataset import LABELS

INPUT_SHAPE: tuple[int, int, int] = (128, 128, 2)
NUM_CLASSES: int = len(LABELS)
ATTN_HEADS: int = 4
ATTN_KEY_DIM: int = 32
DENSE_UNITS: int = 128
DROPOUT_RATE: float = 0.5        # R13: increased from 0.3
L2_LAMBDA: float = 1e-4          # R12: weight decay

# R11: SpecAugment parameters
FREQ_MASK_PARAM: int = 15        # max number of consecutive freq bins to mask
TIME_MASK_PARAM: int = 20        # max number of consecutive time steps to mask
NUM_FREQ_MASKS: int = 2          # how many frequency masks to apply
NUM_TIME_MASKS: int = 2          # how many time masks to apply


# ---------------------------------------------------------------------------
# R11 – SpecAugment layer (training-only)
# ---------------------------------------------------------------------------

class SpecAugment(layers.Layer):
    """Apply frequency and time masking on (H, W, C) spectrogram tensors.

    Masks are random contiguous bands of zeros along the frequency axis
    (height) and time axis (width). Only active during ``training=True``.

    Reference: Park et al., "SpecAugment", Interspeech 2019.
    """

    def __init__(
        self,
        freq_mask_param: int = FREQ_MASK_PARAM,
        time_mask_param: int = TIME_MASK_PARAM,
        num_freq_masks: int = NUM_FREQ_MASKS,
        num_time_masks: int = NUM_TIME_MASKS,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.freq_mask_param = freq_mask_param
        self.time_mask_param = time_mask_param
        self.num_freq_masks = num_freq_masks
        self.num_time_masks = num_time_masks

    def call(self, inputs, training=None):
        if not training:
            return inputs

        x = inputs
        shape = tf.shape(x)
        batch = shape[0]
        freq_bins = shape[1]   # H  (128)
        time_steps = shape[2]  # W  (128)

        # --- Frequency masking ---
        for _ in range(self.num_freq_masks):
            f = tf.random.uniform([], 0, self.freq_mask_param, dtype=tf.int32)
            f0 = tf.random.uniform([], 0, freq_bins - f, dtype=tf.int32)
            # Build a (1, H, 1, 1) mask: 0 in [f0, f0+f), 1 elsewhere
            indices = tf.range(freq_bins)
            mask = tf.cast(
                tf.logical_or(indices < f0, indices >= f0 + f),
                x.dtype,
            )
            mask = tf.reshape(mask, [1, freq_bins, 1, 1])
            x = x * mask

        # --- Time masking ---
        for _ in range(self.num_time_masks):
            t = tf.random.uniform([], 0, self.time_mask_param, dtype=tf.int32)
            t0 = tf.random.uniform([], 0, time_steps - t, dtype=tf.int32)
            indices = tf.range(time_steps)
            mask = tf.cast(
                tf.logical_or(indices < t0, indices >= t0 + t),
                x.dtype,
            )
            mask = tf.reshape(mask, [1, 1, time_steps, 1])
            x = x * mask

        return x

    def get_config(self):
        config = super().get_config()
        config.update(
            {
                "freq_mask_param": self.freq_mask_param,
                "time_mask_param": self.time_mask_param,
                "num_freq_masks": self.num_freq_masks,
                "num_time_masks": self.num_time_masks,
            }
        )
        return config


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

def _conv_block(x, filters: int, name: str):
    x = layers.Conv2D(
        filters,
        kernel_size=3,
        padding="same",
        kernel_regularizer=regularizers.l2(L2_LAMBDA),   # R12
        name=f"{name}_conv",
    )(x)
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

    # R11: SpecAugment (freq + time masking, training only)
    x = SpecAugment(name="spec_augment")(inputs)

    x = _conv_block(x, 32, "block1")
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
    x = layers.Dense(
        DENSE_UNITS,
        activation="relu",
        kernel_regularizer=regularizers.l2(L2_LAMBDA),   # R12
        name="dense_1",
    )(x)
    x = layers.Dropout(DROPOUT_RATE, name="dropout")(x)           # R13: 0.5
    outputs = layers.Dense(
        n_classes,
        activation="softmax",
        kernel_regularizer=regularizers.l2(L2_LAMBDA),   # R12
        name="logits",
    )(x)

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

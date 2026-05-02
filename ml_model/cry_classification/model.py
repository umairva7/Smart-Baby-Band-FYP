from __future__ import annotations

from typing import Tuple

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


def build_model(input_shape: Tuple[int, int, int], num_classes: int = 6, learning_rate: float = 0.8) -> keras.Model:
    inputs = keras.Input(shape=input_shape)
    x = inputs

    for filters in [32, 64, 128, 128]:
        x = layers.Conv2D(filters, (5, 5), strides=(2, 2), padding="same")(x)
        x = layers.BatchNormalization()(x)
        x = layers.ReLU()(x)
        x = layers.MaxPooling2D(pool_size=(2, 2), padding="same")(x)
        x = layers.Dropout(0.3)(x)

    x = layers.Reshape((-1, x.shape[-1]))(x)

    for _ in range(2):
        attn = layers.MultiHeadAttention(num_heads=8, key_dim=16)(x, x)
        x = layers.Add()([x, attn])
        x = layers.LayerNormalization()(x)

    x = layers.LSTM(256, return_sequences=True)(x)
    x = layers.LSTM(128, return_sequences=True)(x)
    x = layers.LSTM(64, return_sequences=True)(x)
    x = layers.LSTM(32, return_sequences=False)(x)
    x = layers.Dropout(0.3)(x)

    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = keras.Model(inputs, outputs)
    optimizer = keras.optimizers.SGD(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model

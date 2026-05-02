import tensorflow as tf
from tensorflow.keras import layers, models, Model

def build_model(input_shape=(305, 128, 1), num_classes=6):
    inputs = layers.Input(shape=input_shape)
    
    x = inputs
    # CNN Local Blocks (x4)
    filters = [32, 64, 128, 128]
    for f in filters:
        x = layers.Conv2D(f, kernel_size=(5, 5), strides=(1, 1), padding='same')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)
        x = layers.MaxPooling2D(pool_size=(2, 2), padding='same')(x)
        x = layers.Dropout(0.3)(x)
        
    # After 4 blocks of pool=2, frequency shape ~ 305 / 16 = 20, time shape ~ 128 / 16 = 8.
    # Output shape: (batch, 20, 8, 128)
    # Flatten spatial (frequency) -> (seq_len, features)
    # We want sequence length to be the time axis (8), so we transpose to (batch, 8, 20, 128)
    # Then reshape to (batch, 8, 20 * 128)
    shape = x.shape
    # shape is (None, H, W, C) where H is freq, W is time.
    x = layers.Permute((2, 1, 3))(x) # Now (None, W, H, C)
    x = layers.Reshape((-1, shape[1] * shape[3]))(x) # Now (None, seq_len, features)
    
    # Attention (x2)
    for _ in range(2):
        attn_out = layers.MultiHeadAttention(num_heads=8, key_dim=16)(x, x)
        x = layers.Add()([x, attn_out])
        x = layers.LayerNormalization()(x)
        
    # LSTM Stack
    x = layers.LSTM(256, return_sequences=True)(x)
    x = layers.LSTM(128, return_sequences=True)(x)
    x = layers.LSTM(64, return_sequences=True)(x)
    x = layers.LSTM(32, return_sequences=False)(x)
    
    x = layers.Dropout(0.3)(x)
    
    # Classifier
    outputs = layers.Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs, outputs)
    
    # Compile with SGD lr=0.8 as paper uses, or fallback to Adam
    optimizer = tf.keras.optimizers.SGD(learning_rate=0.8)
    model.compile(optimizer=optimizer,
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
                  
    return model

if __name__ == "__main__":
    model = build_model()
    model.summary()

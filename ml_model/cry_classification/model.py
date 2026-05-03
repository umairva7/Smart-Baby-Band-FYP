import tensorflow as tf
from tensorflow.keras.layers import Conv2D, BatchNormalization, ReLU, MaxPooling2D, Dropout, Reshape, MultiHeadAttention, LSTM, Dense, Input, Permute, LayerNormalization, Add
from tensorflow.keras.models import Model
from tensorflow.keras.regularizers import l2
from tensorflow.keras.optimizers import Adam

def build_model(input_shape=(128, 128, 1), num_classes=4):
    from tensorflow.keras.layers import Conv2D, BatchNormalization, ReLU, MaxPooling2D, Dropout, Reshape, MultiHeadAttention, LSTM, Dense, Input, Permute, LayerNormalization, Add
    from tensorflow.keras.models import Model
    from tensorflow.keras.regularizers import l2
    
    inputs = Input(shape=input_shape)
    x = inputs
    
    # --- 1. Local Feature Extraction (CNN) ---
    filters = [16, 32, 64, 64] 
    for f in filters:
        x = Conv2D(f, kernel_size=(5, 5), strides=(1, 1), padding='same', kernel_regularizer=l2(1e-4))(x)
        x = BatchNormalization()(x)
        x = ReLU()(x)
        x = MaxPooling2D(pool_size=(2, 2), padding='same')(x)
        x = Dropout(0.3)(x)
        
    # --- 2. The Reshape ---
    shape = x.shape
    # x shape is (None, 8, 8, 64). Sequence length = 8.
    x = Permute((2, 1, 3))(x) 
    x = Reshape((-1, shape[1] * shape[3]))(x) # Flatten freq + channels -> (None, 8, 512)
    
    # --- 3. Global Features (Attention) ---
    attn_out = MultiHeadAttention(num_heads=4, key_dim=16)(x, x)
    x = Add()([x, attn_out])
    x = LayerNormalization()(x)
    
    # --- 4. The LSTM ---
    x = LSTM(128, return_sequences=True)(x)  # First LSTM should return sequences
    x = LSTM(64, return_sequences=False)(x)  # Second LSTM compresses to a final vector
    x = Dropout(0.3)(x)
    
    # --- 5. Classifier ---
    outputs = Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs, outputs)
    
    # Compile here is optional since you compile in train.py, but good practice
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

if __name__ == "__main__":
    model = build_model()
    model.summary()
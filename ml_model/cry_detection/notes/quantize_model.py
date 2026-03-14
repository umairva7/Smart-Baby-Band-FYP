#!/usr/bin/env python3
"""
Convert trained CNN model to TensorFlow Lite (quantized) for ESP32.
Run this after train_cry_detection.py

Install first:
    pip install tensorflow
"""

import os
import numpy as np
import tensorflow as tf
from pathlib import Path

# ============================================================================
# CONFIG
# ============================================================================

MODELS_DIR = Path("./models")
INPUT_MODEL = MODELS_DIR / "cnn_model.h5"
OUTPUT_MODEL = MODELS_DIR / "cnn_model.tflite"

# ============================================================================
# QUANTIZE MODEL
# ============================================================================

def convert_to_tflite_quantized():
    """
    Convert Keras model to TFLite with int8 quantization.
    This reduces model size ~4x and speeds up inference on microcontrollers.
    """
    
    if not INPUT_MODEL.exists():
        print(f"ERROR: Model not found at {INPUT_MODEL}")
        print(f"Did you run train_cry_detection.py first?")
        exit(1)
    
    print(f"Loading model from {INPUT_MODEL}...")
    model = tf.keras.models.load_model(INPUT_MODEL)
    
    print(f"Model architecture:")
    model.summary()
    
    # Create converter
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    
    # Optimization 1: Post-training quantization (int8)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    
    # Optimization 2: Experimental weight-only quantization
    # (Sometimes better for inference, sometimes not. Try if tflite is still slow)
    # converter.target_spec.supported_ops = [
    #     tf.lite.OpsSet.TFLITE_BUILTINS,
    #     tf.lite.OpsSet.SELECT_TF_OPS
    # ]
    
    # Convert
    print("\nConverting to TFLite...")
    tflite_model = converter.convert()
    
    # Save
    with open(OUTPUT_MODEL, 'wb') as f:
        f.write(tflite_model)
    
    # Check size
    input_size = INPUT_MODEL.stat().st_size / (1024 * 1024)  # MB
    output_size = OUTPUT_MODEL.stat().st_size / (1024 * 1024)  # MB
    compression_ratio = input_size / output_size
    
    print(f"\n✅ Conversion complete!")
    print(f"Original model:    {input_size:.2f} MB")
    print(f"Quantized model:   {output_size:.2f} MB")
    print(f"Compression ratio: {compression_ratio:.1f}x")
    print(f"\nSaved to: {OUTPUT_MODEL}")
    
    if output_size > 2.0:
        print(f"\n⚠️  WARNING: Model is {output_size:.2f} MB. ESP32 has limited flash.")
        print(f"   Target: < 2 MB for comfortable fit.")
        print(f"   Solutions:")
        print(f"   - Reduce model layers/filters")
        print(f"   - Reduce MFCC frames (128 → 64)")
        print(f"   - Use weight-only quantization")
    else:
        print(f"\n✅ Model size is good for ESP32!")

# ============================================================================
# TEST INFERENCE (Optional)
# ============================================================================

def test_inference():
    """
    Quick test that the quantized model runs.
    """
    if not OUTPUT_MODEL.exists():
        print(f"ERROR: Quantized model not found at {OUTPUT_MODEL}")
        return
    
    print("\n" + "="*60)
    print("TESTING QUANTIZED MODEL")
    print("="*60)
    
    # Load quantized model
    interpreter = tf.lite.Interpreter(model_path=str(OUTPUT_MODEL))
    interpreter.allocate_tensors()
    
    # Get input/output details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    print(f"\nInput details:  {input_details}")
    print(f"Output details: {output_details}")
    
    # Create dummy input (batch of 1)
    input_shape = input_details[0]['shape']  # Should be (1, 128, 13)
    dummy_input = np.random.randn(*input_shape).astype(np.float32)
    
    # Inference
    import time
    interpreter.set_tensor(input_details[0]['index'], dummy_input)
    
    start = time.time()
    interpreter.invoke()
    elapsed = (time.time() - start) * 1000  # Convert to ms
    
    output = interpreter.get_tensor(output_details[0]['index'])
    
    print(f"\nInference result: {output}")
    print(f"Inference time:   {elapsed:.2f} ms")
    
    if elapsed > 500:
        print(f"\n⚠️  WARNING: Inference is slow ({elapsed:.2f} ms)")
        print(f"   On ESP32 running at 240 MHz, expect ~200-500ms")
        print(f"   If > 1000ms, model is too big for real-time detection")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("Converting CNN model to TensorFlow Lite\n")
    
    convert_to_tflite_quantized()
    test_inference()
    
    print("\n✅ Done!")
    print(f"\nNext steps:")
    print(f"1. Copy {OUTPUT_MODEL} to your ESP32 project")
    print(f"2. Use TensorFlow Lite Micro to run inference on device")
    print(f"3. See esp32_inference.cpp for example C++ code")

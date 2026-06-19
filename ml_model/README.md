# 🧠 Smart Baby Band — Cry Classification ML Model

> Machine Learning model for classifying infant cries based on audio features.

---

## 📌 Overview

This directory contains the machine learning pipelines used to train and export the cry detection and classification models.
The system uses a split-compute architecture where the ESP32 performs a lightweight VAD (Voice Activity Detection), and the cloud backend runs a robust two-stage pipeline on the incoming raw audio bytes.

## 🛠️ Technology Stack

* **Frameworks**: TensorFlow / Keras, Librosa
* **Language**: Python
* **Deployment**: Saved `.keras` / `.h5` models loaded dynamically in our FastAPI backend on Azure.
* **Technique**: Supervised learning using Deep Convolutional Neural Networks (CNN) and LSTMs.
* **Loss Function**: Categorical Focal Loss to heavily penalize majority class bias.

## 🧩 Architecture Fit

1. **Edge (ESP32)**: Captures raw audio via I2S digital microphone, runs a hardware VAD gate (Energy, ZCR, Peak). If triggered, it streams a 3-second raw PCM audio clip over HTTP to the backend.
2. **Stage 1 (Binary Detection)**: The FastAPI backend converts the raw PCM into features and runs a binary `cry_detection` model to verify if the sound is actually a baby crying (filtering out false positives).
3. **Stage 2 (Classification)**: If confirmed as a cry, the backend generates a 128x128x1 Mel Spectrogram and feeds it into the CNN-LSTM `cry_classification` model.
4. **Classes Output**: `hungry`, `tired`, `discomfort`, `diaper`.

## 📂 Directory Structure

* `/cry_detection` — Binary model pipeline (Cry vs. Non-Cry noise)
* `/cry_classification` — 4-Class CNN-LSTM model pipeline

Inside each subdirectory, you will find:
* `dataset.py` — Preprocessing, resampling, and train/val/test splits
* `augment.py` — Time stretching, pitch shifting, and background noise injection
* `features.py` — Extraction of Mel Spectrogram tensors (`.npy`)
* `train.py` — Model definition, compilation, and training loop
* `evaluate.py` — Accuracy, F1 scoring, and confusion matrix generation

## 🚀 Model Deployment

After training in either subdirectory, the final `.keras` model and its `label_map.json` / `feature_config.json` artifacts are generated. To deploy, copy these into the `backend/ml_models/` directory so the FastAPI backend can load them at runtime.

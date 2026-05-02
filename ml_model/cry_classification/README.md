# Smart Baby Band - Cry Classification Pipeline

This folder implements the end-to-end machine learning pipeline for classifying infant cries into 6 distinct categories: `hungry`, `tired`, `discomfort`, `belly_pain`, `diaper`, and `burping`.

## Overview

The pipeline harmonizes two major datasets (`donateacry` and `baby_crying`), extracts advanced "Efficient Graph" features (a combination of STFT, Mel Spectrogram, and MFCC representations), and trains a robust deep learning architecture comprising Convolutional Neural Networks (CNN), Multi-Head Attention, and Long Short-Term Memory (LSTM) layers. 

---

## 1. Data Layout

To use the pipeline, place the raw datasets in the `data/raw/` folder as follows:

```text
smart_baby_band/
├── data/
│   ├── raw/
│   │   ├── donateacry-corpus-master/donateacry_corpus_cleaned_and_updated_data/
│   │   ├── baby-crying/raw/
│   │   └── esc50/ (optional, for background noise augmentation)
```

**Dataset Mapping:**
- **Donate-a-Cry (DaC):** Keeps `belly_pain`, `burping`, `discomfort`, `hungry`, `tired`.
- **Baby Crying:** Maps `sleepy` → `tired`, `uncomfortable` → `discomfort`, keeps `diaper` and `hungry`. Unused labels (`awake`, `hug`) are dropped.

---

## 2. Model Architecture

The deep learning model is built sequentially to process audio as spatial-temporal data:
1. **CNN Local Blocks (4x):** Extracts local spatial-frequency features using 5x5 Conv2D layers with stride/pooling, Batch Normalization, ReLU, and Dropout.
2. **Multi-Head Attention (2x):** Focuses on globally significant features across the frequency and time domains.
3. **Stacked LSTM (4x):** Learns temporal dependencies and sequence structures of the crying audio over time.
4. **Classifier:** Dense layer with Softmax activation outputting probabilities for the 6 target classes.

---

## 3. Feature Extraction (Efficient Graph)

For computational efficiency, audio files are pre-processed offline into an "Efficient Graph" representation:
- **Resampling:** 16kHz mono WAV, fixed to 3.0 seconds padding/truncation.
- **Components:**
  - High-frequency bins from a standard **STFT Spectrogram** (N_FFT=512)
  - Full **Mel Spectrogram** (128 bands)
  - **MFCCs** + Delta + Delta-Delta (40 components each)
- **Final Shape:** Concatenated along the frequency axis to yield a `(305, 128, 1)` tensor shape per 3-second sample.

---

## 4. Execution Order & Usage

Run the following scripts in order to execute the pipeline from start to finish:

### Stage 1: Data Preparation
```bash
python dataset.py
```
- Aggregates raw audio, trims silence, resamples, and normalizes to `[-1, 1]`.
- Creates an 80/10/10 stratified train/val/test split and saves metadata to `data/processed/splits.csv`.

### Stage 2: Data Augmentation
```bash
python augment.py
```
- Performs offline augmentation strictly on the training split to resolve class imbalances (~1500 samples per class).
- Utilizes `TimeStretch`, `PitchShift`, `TimeMask`, and `AddBackgroundNoise` (if ESC-50 is provided).

### Stage 3: Feature Extraction
```bash
python features.py
```
- Processes all augmented and raw audio into the 2D Efficient Graph `.npy` tensors.
- Stores them sequentially inside `features/{split}/`.

### Stage 4: Training
```bash
python train.py
```
- Builds scalable `tf.data.Dataset` pipelines dynamically loading the `.npy` files.
- Applies class weights and uses `EarlyStopping`, `ReduceLROnPlateau`, and `ModelCheckpoint`.
- Training history is saved into the `logs/` directory.

### Stage 5: Evaluation
```bash
python evaluate.py
```
- Loads the best checkpoint and scores accuracy and F1 metrics on the test set.
- Generates a visual `confusion_matrix.png` heatmap in the `logs/` directory.
- Runs the cross-dataset experiment (generalization gap). *Use `--skip-cross-dataset` to bypass.*

### Stage 6: Model Export
```bash
python export.py
```
- Prepares the final compiled `model.h5`, maps indices using `label_map.json`, and validates the `feature_config.json`.

---

## 5. Outputs & Artifacts

Upon successful completion, the directory will be populated with:
- **`data/processed/`**: Cleaned WAV files and `splits.csv` metadata.
- **`data/augmented/`**: Generated augmentation WAVs.
- **`features/{train, val, test}/`**: Pre-computed `.npy` feature tensors.
- **`logs/`**: Training histories (`.json`) and evaluation plots (`.png`).
- **`models/`**: 
  - `best_model.h5`: Trained Keras Checkpoint.
  - `model.h5`: Final exported model.
  - `label_map.json`: String mappings for class indices.
  - `feature_config.json`: Configuration dictionary to mirror audio pipeline in production.

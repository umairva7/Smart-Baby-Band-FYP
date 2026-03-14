# Edge Cry Detection Model - 1 Week Implementation Plan

## Reality Check
- **One week** = ~40 hours of actual work (accounting for sleep, classes, etc.)
- **Goal**: Binary cry detection (cry vs. not-cry) that runs on ESP32-S3
- **Not expected**: Perfect accuracy. Functional accuracy (F1 > 0.65 on real data)
- **Constraint**: Model must be < 2MB when quantized for TFLu

---

## Week Breakdown

### **Day 1-2: Data Prep & Baseline (16 hours)**

**What you're doing:**
1. Download ICSD dataset (4+ hours of audio)
2. Download Environmental50 from Kaggle
3. Create train/val/test split
4. Extract MFCCs (Mel-Frequency Cepstral Coefficients)
5. Train a simple baseline model (SVM or small NN)

**Why this order:**
- You need to see results fast to stay motivated
- MFCC extraction is proven to work (Yao paper used it)
- A baseline now beats a perfect model never

**Deliverable:** 
- Cleaned dataset with 5000+ labeled samples
- Baseline model with F1 >= 0.60 on validation set

---

### **Day 3-4: Model Training & Optimization (16 hours)**

**What you're doing:**
1. Train a tiny CNN (< 50K parameters)
2. Experiment with different architectures quickly
3. Tune hyperparameters (learning rate, batch size, etc.)
4. Handle class imbalance (crying is rare, background is common)

**Why this:**
- CNNs outperform traditional ML for audio (Yao confirmed)
- But they need to stay tiny for edge deployment
- You'll iterate fast—don't get stuck on one architecture

**Deliverable:**
- Trained model with F1 >= 0.70 on validation
- Trained model file (~5-10MB unquantized)

---

### **Day 5: Quantization & Edge Testing (8 hours)**

**What you're doing:**
1. Convert model to TensorFlow Lite format
2. Quantize (int8) to shrink it for ESP32
3. Test accuracy drop after quantization
4. Profile inference time on ESP32 (or emulate it)

**Why now:**
- Quantization always reduces accuracy—you need to plan for it
- Inference speed matters for power budget
- If accuracy drops too much, you loop back to Day 3

**Deliverable:**
- .tflite file < 2MB
- Inference time estimate: < 500ms on ESP32

---

### **Day 6: Integration & Testing (8 hours)**

**What you're doing:**
1. Write C/C++ inference wrapper for ESP32 (use TensorFlow Lite Micro)
2. Test with MFCC extraction on-device
3. Validate end-to-end pipeline (capture audio → extract MFCC → infer → output)
4. Tune confidence threshold (false positive vs. false negative trade-off)

**Why now:**
- Theory means nothing if it doesn't run on the actual hardware
- Threshold tuning is where you control FP rate
- This is where integration bugs surface

**Deliverable:**
- Working C++ code that runs inference on ESP32
- Confidence threshold value tuned for your tolerance

---

### **Day 7: Documentation & Buffer (8 hours)**

**What you're doing:**
1. Document the model (architecture, training data, performance metrics)
2. Write a brief README for your team
3. Buffer time for last-minute fixes
4. Test one more time end-to-end

**Why:**
- Your team needs to understand what you built
- Your future self will forget the details in 2 weeks
- Buffer time is not wasted time—it's insurance

**Deliverable:**
- Model deployed on ESP32
- Documentation of model, threshold, expected performance
- Git commit with working code

---

## Technical Stack (No Surprises)

**Python (offline training):**
```
- librosa (audio processing, MFCC extraction)
- numpy/scipy (signal processing)
- TensorFlow 2.x (model training)
- scikit-learn (optional, for SVM baseline)
```

**Embedded (on ESP32):**
```
- TensorFlow Lite Micro (inference)
- ESP-IDF + FreeRTOS (already in your setup)
- INMP441 driver (audio capture, you likely have this)
```

**No PyTorch, no fancy stuff.** TensorFlow is standard for embedded, you can quantize it, and TFLu is battle-tested.

---

## Model Architecture (Specific Recommendation)

**Don't overthink this.** Use this exact architecture to start:

```python
Input: (1, 128, 13)  # 128 MFCC frames, 13 coefficients
├── Conv1D(32 filters, kernel=3, padding='same') + BatchNorm + ReLU
├── MaxPool1D(pool_size=2)
├── Conv1D(64 filters, kernel=3, padding='same') + BatchNorm + ReLU
├── GlobalAveragePooling1D()
├── Dense(32, activation='relu') + Dropout(0.3)
├── Dense(1, activation='sigmoid')  # Binary classification
Output: probability (0-1)
```

**Why this:**
- ~40K parameters (easily fits on ESP32)
- Conv layers learn audio patterns
- GlobalAveragePooling + Dense = fast inference
- Dropout prevents overfitting on limited data

---

## Data Strategy (Critical)

### **Class Balance Problem**
Real-world data is 90% non-crying, 10% crying. Your model will cheat and predict "not crying" for everything.

**Solution:**
1. **Oversample** crying samples during training
2. **Undersample** non-crying samples (randomly remove some)
3. Use `class_weight` in loss function: `{0: 1.0, 1: 9.0}` (weight crying 9x more)

### **Train/Val/Test Split**
```
Train: 70% (balanced with oversampling)
Val:   15% (original distribution, for real-world evaluation)
Test:  15% (original distribution, for final metrics)
```

Why separate original dist for Val/Test? Because that's what you'll see in production.

### **Data Augmentation** (Optional but helps)
```python
- Time stretching (slow down/speed up audio 0.9x - 1.1x)
- Pitch shifting (+/- 2 semitones)
- Background noise mixing (add quiet background from Environmental50)
```

Only do this if you have time. Not mandatory for a 1-week sprint.

---

## Metrics That Matter

**Don't just report accuracy.** Report:

| Metric | What It Means | Target |
|--------|---------------|--------|
| **Precision** | Of detected cries, how many are real cries? | > 0.70 |
| **Recall** | Of all real cries, how many did we catch? | > 0.65 |
| **F1** | Harmonic mean of precision & recall | > 0.67 |
| **Inference Time** | How long does one prediction take? | < 500ms |
| **Model Size** | .tflite file size | < 2MB |

**Precision vs. Recall trade-off:**
- High precision = fewer false alarms (parents won't ignore you)
- High recall = fewer missed cries (safety)
- You probably want precision > recall (annoying alerts destroy trust)

---

## Failure Modes & What to Do

### **Problem: Model is too slow on ESP32**
- **Solution**: Reduce MFCC frame length (use 64 frames instead of 128)
- **Or**: Reduce Conv filters (16 instead of 32)
- **Last resort**: Use SVM with MFCC features (faster inference, slightly lower accuracy)

### **Problem: Accuracy drops after quantization**
- **Solution**: Use dynamic range quantization instead of int8
- **Or**: Retrain with quantization-aware training (QAT) - takes extra day
- **If stuck**: Accept ~5-10% accuracy loss, adjust threshold to compensate

### **Problem: Too many false positives in testing**
- **Solution**: Increase confidence threshold (0.5 → 0.6 → 0.7)
- Trade-off: You'll miss some real cries, but fewer false alarms
- **Document this trade-off** in your report

### **Problem: You're behind schedule**
- **Priority 1**: Get baseline working (MFCC + SVM) by Day 2
- **Priority 2**: Deploy to ESP32 and confirm it runs
- **Priority 3**: Fine-tune accuracy
- **Skip**: Fancy augmentation, complex architectures, extensive hyperparameter search

---

## Deliverables (What Your Team Expects)

1. **Model file** (.tflite, < 2MB)
2. **C++ inference code** (compiles on ESP32)
3. **Training script** (Python, reproducible)
4. **README.md** with:
   - Model architecture (diagram or text)
   - Training data (sources, size, split)
   - Performance metrics (F1, precision, recall, inference time)
   - Confidence threshold used & why
   - Known limitations
5. **Dataset info**:
   - Which datasets used (ICSD, Environmental50)
   - Data preprocessing steps
   - Class balance approach

---

## Code Structure (Start With This)

```
cry-detection/
├── data/
│   ├── raw/                 # Downloaded datasets
│   ├── processed/           # After preprocessing
│   └── splits/              # train.csv, val.csv, test.csv
├── models/
│   ├── baseline_svm.pkl     # Quick baseline
│   ├── cnn_model.h5         # Trained model
│   └── cnn_model.tflite     # Quantized for ESP32
├── scripts/
│   ├── download_data.py     # Get ICSD + Environmental50
│   ├── preprocess.py        # Extract MFCCs, balance data
│   ├── train.py             # Train the CNN
│   ├── evaluate.py          # Compute F1, precision, recall
│   └── quantize.py          # Convert to TFLite
├── esp32/
│   └── cry_detection.cpp    # Inference wrapper
├── README.md                # Documentation
└── requirements.txt         # Python dependencies
```

---

## Don't Do This (Common Mistakes)

❌ Spend 2 days trying to implement from-scratch audio processing  
❌ Download 50+ GB of data (subset is fine for 1 week)  
❌ Try to get 95% accuracy (0.70 F1 is respectable with limited time)  
❌ Build your own quantization (TensorFlow does this for you)  
❌ Ignore false positives until the end (tune threshold early)  
❌ Skip documentation (your team won't understand your model)  
❌ Wait for the Yao dataset (use ICSD + Environmental50 now)  

---

## If You Get Stuck (Hour-by-Hour Triage)

**Hour 1 of being stuck:**
- Google the exact error + "TensorFlow" or "librosa"
- Check StackOverflow

**Hour 2:**
- Ask ChatGPT (for debugging, not architecture decisions)
- Check GitHub issues on TensorFlow repo

**Hour 3:**
- Simplify the problem (reduce model size, fewer samples, etc.)
- Switch to the SVM baseline—it's simpler and works

**Hour 4:**
- Message your team lead
- Accept the limitation, document it, move on

**Don't waste a full day on one bug.**

---

## Success Criteria (Realistic)

✅ **By end of Day 2:** Baseline model trained, F1 > 0.60  
✅ **By end of Day 4:** CNN model trained, F1 > 0.70  
✅ **By end of Day 5:** Model quantized, runs on ESP32, inference < 500ms  
✅ **By end of Day 6:** End-to-end pipeline tested on hardware  
✅ **By end of Day 7:** Documented, deployed, no fires  

This is achievable. Start now.

---

## Key Insight (Why This Plan Works)

You're not building a production model. You're building a **proof-of-concept** that:
1. Works (runs without crashing)
2. Performs (F1 > 0.65, good enough for edge detection)
3. Fits (< 2MB on ESP32)
4. Integrates (talks to cloud when cry detected)

Once this works, your team can iterate, add more data, fine-tune. You're laying the foundation in one week. That's ambitious but doable.

**Start with MFCC extraction tomorrow morning. No more planning.**

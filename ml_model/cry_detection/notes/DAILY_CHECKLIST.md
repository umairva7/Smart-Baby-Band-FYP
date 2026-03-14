# Cry Detection - Daily Checklist

## DAY 1 (Monday) - Data Setup & Baseline

- [ ] **Morning (2 hours)**
  - [ ] Set up Python environment
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install librosa numpy scipy scikit-learn tensorflow pandas soundfile
    ```
  - [ ] Create directory structure
    ```
    cry-detection/
    ├── data/raw/
    ├── data/processed/
    ├── models/
    └── scripts/
    ```
  - [ ] Download ICSD dataset (~2 GB, start downloading now)
  - [ ] Download Environmental50 dataset from Kaggle

- [ ] **Afternoon (4 hours)**
  - [ ] Run `train_cry_detection.py` on a subset (first 100 files)
  - [ ] Debug MFCC extraction (test on 1 file first)
  - [ ] Train SVM baseline on subset
  - [ ] Record baseline F1 score
  - [ ] Commit: "Initial data loading and SVM baseline"

- [ ] **Evening (2 hours)**
  - [ ] Load full ICSD dataset
  - [ ] Check data distribution (how many cry vs. non-cry samples?)
  - [ ] Start CNN training (let it run overnight if needed)

**End of Day 1 target:** SVM baseline F1 > 0.55, full dataset loaded

---

## DAY 2 (Tuesday) - CNN Training & Hyperparameter Tuning

- [ ] **Morning (2 hours)**
  - [ ] Check CNN training results from overnight
  - [ ] Evaluate validation F1 score
  - [ ] If F1 < 0.65: adjust model (add more data augmentation, change architecture)
  - [ ] If F1 > 0.70: move on to testing

- [ ] **Midday (3 hours)**
  - [ ] Experiment with 2-3 different architectures (vary filter sizes, layers)
  - [ ] Try different learning rates (0.0001, 0.001, 0.01)
  - [ ] Test different class weights (1:1, 1:2, 1:5, 1:10)
  - [ ] Log results in a table (architecture, LR, class_weight, F1)

- [ ] **Afternoon (3 hours)**
  - [ ] Pick the best model so far
  - [ ] Run on full validation set
  - [ ] Save model: `cnn_model.h5`
  - [ ] Commit: "CNN baseline F1 >= 0.70"

- [ ] **Evening (2 hours)**
  - [ ] Evaluate on test set (unbiased)
  - [ ] Calculate precision, recall, confusion matrix
  - [ ] Document results

**End of Day 2 target:** CNN F1 > 0.70 on validation, > 0.68 on test

---

## DAY 3 (Wednesday) - Quantization & Size Optimization

- [ ] **Morning (2 hours)**
  - [ ] Run `quantize_model.py`
  - [ ] Check output file size
  - [ ] If > 2.5 MB: reduce model size
    - [ ] Reduce Conv filters (32→16, 64→32)
    - [ ] Reduce MFCC frames (128→64)
    - [ ] Reduce dense layers

- [ ] **Midday (3 hours)**
  - [ ] Test quantized model inference on laptop
  - [ ] Measure inference time
  - [ ] If > 500ms: further optimization needed
  - [ ] Create `model_info.txt` with specs

- [ ] **Afternoon (3 hours)**
  - [ ] If quantization reduced accuracy too much:
    - [ ] Retrain with quantization-aware training (QAT) - optional, takes 4 hours
    - [ ] Or accept 5-10% accuracy loss and adjust threshold
  - [ ] Document accuracy drop

**End of Day 3 target:** .tflite file < 2 MB, inference time < 500ms

---

## DAY 4 (Thursday) - ESP32 Integration Prep

- [ ] **Morning (2 hours)**
  - [ ] Generate C++ byte array from .tflite
    ```bash
    xxd -i cnn_model.tflite > cnn_model_data.cc
    ```
  - [ ] Copy to ESP32 project
  - [ ] Review `esp32_inference.cpp` skeleton

- [ ] **Midday (3 hours)**
  - [ ] Check existing INMP441 audio driver in your codebase
  - [ ] Extract MFCC computation code (or simplify for now)
  - [ ] Create test harness: feed dummy MFCC data to model
  - [ ] Verify inference runs without crashing

- [ ] **Afternoon (3 hours)**
  - [ ] Integrate with audio input (connect INMP441 if available)
  - [ ] Test real-time MFCC extraction
  - [ ] Monitor memory usage
  - [ ] Check inference speed on device

**End of Day 4 target:** Model loads on ESP32, inference produces output

---

## DAY 5 (Friday) - End-to-End Testing & Threshold Tuning

- [ ] **Morning (3 hours)**
  - [ ] Record 10 cry samples + 10 non-cry samples on device
  - [ ] Run inference on each
  - [ ] Create confusion matrix
  - [ ] Calculate precision & recall

- [ ] **Midday (2 hours)**
  - [ ] Tune confidence threshold based on real data
  - [ ] Goal: Minimize false positives while catching most cries
  - [ ] Test threshold on full test set
  - [ ] Document final threshold value

- [ ] **Afternoon (3 hours)**
  - [ ] Simulate MQTT publishing when cry detected
  - [ ] Test with FastAPI backend (mock version)
  - [ ] Measure latency: cry→detection→MQTT→cloud
  - [ ] Document latency

**End of Day 5 target:** End-to-end pipeline working, false positive rate acceptable

---

## DAY 6 (Saturday) - Final Integration & Testing

- [ ] **Morning (4 hours)**
  - [ ] Test with real-world scenarios
    - [ ] Baby crying with background noise
    - [ ] False positives (dog barking, vacuum, speech)
    - [ ] Edge cases (quiet cry, loud cry)
  - [ ] Log results

- [ ] **Afternoon (4 hours)**
  - [ ] Power profiling (if time)
    - [ ] Measure current draw during inference
    - [ ] Verify battery budget
  - [ ] Final bug fixes
  - [ ] Clean up code

**End of Day 6 target:** System passes real-world tests

---

## DAY 7 (Sunday) - Documentation & Buffer

- [ ] **Morning (3 hours)**
  - [ ] Write `README.md`
    - [ ] Model architecture (text or diagram)
    - [ ] Training data sources
    - [ ] Performance metrics (F1, precision, recall)
    - [ ] Inference time and model size
    - [ ] Known limitations

  - [ ] Write `MODEL_CARD.md`
    - [ ] Model name & version
    - [ ] Training procedure
    - [ ] Evaluation results
    - [ ] Confidence threshold rationale

- [ ] **Midday (3 hours)**
  - [ ] Code review (clean up, comments)
  - [ ] Commit to Git with meaningful messages
  - [ ] Create GitHub release/tag

- [ ] **Afternoon (2 hours)**
  - [ ] Buffer for last-minute fixes
  - [ ] Test one more time end-to-end
  - [ ] Prepare presentation/demo

**End of Day 7 target:** Documented, deployed, ready to hand off

---

## Success Metrics (Checklist)

- [ ] **Performance**
  - [ ] F1 score on test set >= 0.65
  - [ ] Precision >= 0.70 (minimize false alarms)
  - [ ] Recall >= 0.60 (catch most cries)

- [ ] **Deployment**
  - [ ] Model size < 2 MB
  - [ ] Inference time < 500 ms
  - [ ] Runs on ESP32 without crashes

- [ ] **Documentation**
  - [ ] README.md complete
  - [ ] Model architecture explained
  - [ ] Training procedure reproducible
  - [ ] Threshold value documented

- [ ] **Code Quality**
  - [ ] Git history is clean
  - [ ] Code is commented
  - [ ] No hardcoded magic numbers (except threshold)

---

## If You're Behind (Triage)

**If behind on Day 2:**
- Skip CNN experiments, stick with best baseline
- Train a simpler model (fewer layers)

**If behind on Day 4:**
- Use a pre-trained model (transfer learning from pre-trained audio model)
- Or use SVM instead of CNN (simpler to deploy)

**If behind on Day 6:**
- Skip real-world testing
- Use test set evaluation only
- Document as "tested on offline data"

**If behind on Day 7:**
- Minimum docs: README.md + inline code comments
- Skip fancy formatting
- Just ship it working

---

## Quick Debug Commands

```bash
# Check data
python -c "
import numpy as np
from pathlib import Path
mfcc_dir = Path('data/processed')
files = list(mfcc_dir.glob('*.npy'))
print(f'Total samples: {len(files)}')
"

# Test model inference locally
python -c "
import tensorflow as tf
model = tf.keras.models.load_model('models/cnn_model.h5')
print(model.summary())
"

# Check quantized model size
ls -lh models/cnn_model.tflite

# Monitor training
# In train_cry_detection.py, add: 
# tensorboard --logdir ./logs
```

---

## Commit Messages (Git)

```bash
Day 1: "feat: ICSD data loading and SVM baseline"
Day 2: "feat: CNN model training (F1=0.70)"
Day 3: "feat: TFLite quantization (size 1.2MB)"
Day 4: "feat: ESP32 integration and MFCC extraction"
Day 5: "feat: threshold tuning and MQTT integration"
Day 6: "test: end-to-end validation with real data"
Day 7: "docs: README and model card"
```

---

## Contact Points (When stuck)

1. **Data loading error**: Check file paths, audio format
2. **Model accuracy too low**: Add more data, longer training, adjust class weights
3. **Quantization issues**: Reduce model size, use dynamic range quantization
4. **ESP32 memory error**: Reduce tensor arena, use int8 quantization
5. **False positive rate high**: Increase confidence threshold, retrain with more negatives

**General: Simplify the problem. Get something working first, then optimize.**

# Learning Path: From Audio Basics to Edge Cry Detection

**Goal:** Understand the concepts deeply enough that you can modify and debug the code, not just run it.

**Time Required:** 4-6 hours of focused learning before writing code.

---

## Phase 1: Audio Fundamentals (2-3 hours)

### What You'll Learn
- How sound becomes numbers (sampling)
- Why Fourier Transform reveals frequencies
- Why MFCC is the right feature for this problem
- Common mistakes that sink projects

### Materials

**1. Read: AUDIO_FUNDAMENTALS.md (Sections 1-5)**
   - Skip the math proofs, focus on the intuition
   - Key sections:
     - Section 1: Sampling (why 16 kHz?)
     - Section 2: Fourier/STFT (why frequencies matter?)
     - Section 3: Spectrogram (time + frequency together)
     - Section 4: Mel-scale (human hearing)
     - Section 5: MFCC (what we actually feed to ML)

   **Time:** 45 minutes
   **Key takeaway:** Audio pipeline is: Raw → STFT → Mel-scale → MFCC

**2. Run: audio_walkthrough.py**
   - Execute this Python script
   - It generates synthetic cry + background
   - Shows plots at each step of the pipeline
   - You'll see VISUALLY what MFCC actually looks like
   
   **Time:** 45 minutes
   **How to run:**
   ```bash
   python audio_walkthrough.py
   # Displays plots (matplotlib)
   # Uncomment plt.show() to view
   ```
   
   **What to do:**
   - Look at the time-domain raw audio (messy)
   - Look at the FFT (shows frequencies)
   - Look at the spectrogram (frequencies over time)
   - Look at the mel-spectrogram (more detail at low freq)
   - Look at the MFCC (compressed, clean features)
   - Notice: Cry has distinct pattern, background is random
   
   **Key takeaway:** MFCC makes the difference obvious to ML

**3. Read: AUDIO_FUNDAMENTALS.md (Sections 6-12)**
   - Why deep learning works here
   - Common mistakes
   - Quick reference math
   - Practice exercises
   
   **Time:** 45 minutes
   **Key takeaway:** Use MFCC + CNN, balance dataset, use real-world training data

---

## Phase 2: Understand the Training Pipeline (1.5 hours)

### What You'll Learn
- How to load and preprocess data
- How to build a small neural network
- How to train and evaluate models
- What metrics actually matter

### Materials

**1. Read: CRY_DETECTION_ROADMAP.md**
   - Sections "Model Architecture" and "Data Strategy"
   - Why the specific CNN architecture is recommended
   - Why class balancing is critical
   - Why you need separate train/val/test sets
   
   **Time:** 30 minutes
   **Key takeaway:** Simple CNN + balanced data + real test set

**2. Review: train_cry_detection.py (Don't run yet, just read)**
   - Read comments carefully
   - Focus on these functions:
     - `extract_mfcc()` - implements MFCC extraction (calls librosa)
     - `balance_dataset()` - why oversampling matters
     - `build_cnn_model()` - the actual architecture
     - `train_cnn()` - training loop
   
   **Time:** 45 minutes
   **What to understand:**
   ```python
   # This is the MFCC extraction (you now understand this)
   mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, ...)
   
   # This is the class balancing (why it matters)
   oversample_indices = np.random.choice(cry_indices, size=n_majority, replace=True)
   
   # This is the CNN architecture (simple, not fancy)
   Conv2D(32, kernel=(3, 3)) → Conv2D(64, kernel=(3, 3)) → Dense(32) → Dense(1)
   
   # This is training
   model.fit(X_train, y_train, validation_data=(X_val, y_val), ...)
   ```
   
   **Key takeaway:** Training loop is standard Keras, data handling is critical

---

## Phase 3: Understand Edge Deployment (1 hour)

### What You'll Learn
- Why model size matters for microcontrollers
- What quantization does (and doesn't)
- How inference runs on ESP32

### Materials

**1. Read: quantize_model.py**
   - What does `convert()` do?
   - Why is model size checked?
   - What happens if model is > 2 MB?
   
   **Time:** 20 minutes
   **Key takeaway:** Quantization shrinks model 4x, costs ~5% accuracy

**2. Review: esp32_inference.cpp (Just skim, don't memorize)**
   - You won't write this from scratch
   - But understand the flow:
     1. Load .tflite model (byte array in C++)
     2. Create TensorFlow Lite interpreter
     3. Feed MFCC data to input tensor
     4. Call `interpreter->Invoke()` (this is the inference)
     5. Get output (probability 0-1)
     6. Check if > threshold
   
   **Time:** 15 minutes
   **Key takeaway:** TensorFlow Lite Micro handles the heavy lifting

**3. Read: CRY_DETECTION_ROADMAP.md (Section "Failure Modes")**
   - What goes wrong during quantization?
   - How to fix it?
   - Acceptable trade-offs?
   
   **Time:** 15 minutes
   **Key takeaway:** If accuracy drops > 10%, retrain or simplify architecture

---

## Phase 4: Put It Together (30 minutes)

### What You'll Do

**Read this in order:**
1. CRY_DETECTION_ROADMAP.md (sections 1-3)
2. DAILY_CHECKLIST.md (Day 1 tasks)
3. Look at audio_walkthrough.py output in your head (don't re-run)

### Mental Model You Should Have

```
You have a baby crying at home (real audio):

1. MFCC Extraction (On ESP32):
   Raw audio (16 kHz) → 128 frames of 13 MFCC values
   (This is MFCC extraction in esp32_inference.cpp, compute_mfcc())
   
2. Edge Inference (On ESP32):
   128×13 MFCC → TensorFlow Lite CNN → probability (0-1)
   If prob > 0.6: "CRY DETECTED!"
   
3. Cloud Classification (On FastAPI):
   Raw audio window + MFCC → Full CNN → Label (Hunger/Pain/Discomfort)
   Return detailed classification to parent's phone

Your job: Build the edge model (steps 1-2)
Your cloud team: Builds the classification model (step 3)
```

---

## Common Pitfalls (Learn These Now)

### Pitfall 1: "What's the magic MFCC parameter?"
**Wrong:** "Should I use 13 or 40 MFCCs?"
**Right:** "13 MFCCs capture 90% of information, use 13. If accuracy is bad, it's not the MFCC count."

### Pitfall 2: "Why doesn't my model work?"
**Wrong:** "I'll try 10 different architectures"
**Right:** "Is my training data representative? Did I balance classes? Did I normalize MFCC?"

### Pitfall 3: "The quantized model lost accuracy"
**Wrong:** "Quantization doesn't work, I need a bigger model"
**Right:** "Expected 5-10% accuracy drop. Retrain with QAT or lower threshold."

### Pitfall 4: "I trained on clean lab data"
**Wrong:** "My model should work on real homes"
**Right:** Yao paper proves this fails. Use ICSD (real home recordings).

### Pitfall 5: "False positives are killing us"
**Wrong:** "I need higher recall"
**Right:** "Increase confidence threshold (0.6 → 0.7). Precision matters more."

---

## Questions You Should Be Able to Answer

**If you can't answer these, re-read the materials.**

1. **Sampling:**
   - Why 16 kHz and not 8 kHz or 44.1 kHz?
   - What's Nyquist theorem and why does it matter?

2. **MFCC:**
   - What are the 5 steps to compute MFCC? (Load → STFT → Mel → Log → DCT)
   - Why is mel-scale better than linear frequency?
   - Why do we use 13 coefficients?

3. **Dataset:**
   - Why is class balancing critical?
   - Why separate train/val/test sets?
   - Why does in-lab training data fail on real homes? (Yao paper)

4. **Model:**
   - Why CNN instead of SVM?
   - What does the first Conv layer learn? (Frequency patterns)
   - What does the Dense layer learn? (Combinations of patterns)

5. **Deployment:**
   - What's the purpose of quantization?
   - Is 5-10% accuracy loss acceptable?
   - What's the worst-case inference time on ESP32?

---

## Daily Schedule (4-6 hours)

### Day 0 (Before Writing Code)

**Hour 1:**
- Read AUDIO_FUNDAMENTALS.md sections 1-5
- Take notes on: sampling, FFT, spectrogram, MFCC

**Hour 2:**
- Run audio_walkthrough.py
- Look at plots, understand what you're seeing
- Skim AUDIO_FUNDAMENTALS.md sections 6-12

**Hour 3:**
- Review train_cry_detection.py (just read, don't run)
- Understand: extract_mfcc(), balance_dataset(), build_cnn_model()

**Hour 4:**
- Review quantize_model.py and esp32_inference.cpp (quick skim)
- Read DAILY_CHECKLIST.md Day 1-2

**Hour 5:**
- Read CRY_DETECTION_ROADMAP.md completely
- Understand the 7-day timeline

**Hour 6:**
- Mental model: Draw a diagram (on paper or in your head) of:
  - Raw audio → MFCC extraction → CNN → threshold → MQTT
  - Label each box with what it does
- If you can't explain it, re-read that section

---

## Red Flags (If This Happens, You Missed Something)

❌ **"I don't know what 13 means in n_mfcc=13"**
   → Re-read AUDIO_FUNDAMENTALS.md section 5

❌ **"Why can't I just use raw audio instead of MFCC?"**
   → Re-read AUDIO_FUNDAMENTALS.md section 6 (Common Mistakes)

❌ **"How do I know if my model is good?"**
   → Re-read CRY_DETECTION_ROADMAP.md section on "Metrics That Matter"

❌ **"Should I use SVM or CNN?"**
   → Yao paper shows CNN is slightly better, but SVM works too
   → Read AUDIO_FUNDAMENTALS.md section 9

❌ **"My training accuracy is 95% but test is 50%"**
   → You have class imbalance or overfitting
   → Read CRY_DETECTION_ROADMAP.md section "Data Strategy"

---

## After This Learning, You Can:

✅ Understand why MFCC is used (not magic, it's justified)
✅ Read train_cry_detection.py and modify it intelligently
✅ Debug audio preprocessing issues
✅ Explain to your team why you balanced the dataset
✅ Make informed decisions about model size/accuracy trade-offs
✅ Fix problems instead of copy-pasting solutions

---

## Final Checklist Before Coding

- [ ] I understand sampling and Nyquist theorem
- [ ] I understand FFT shows frequencies
- [ ] I understand spectrogram is FFT over time
- [ ] I understand mel-scale matches human hearing
- [ ] I understand MFCC compresses mel-spectrogram
- [ ] I understand why class balancing matters
- [ ] I understand why real-world training data matters
- [ ] I understand the CNN architecture choices
- [ ] I understand quantization trade-offs
- [ ] I can draw the full pipeline from audio to inference

---

## Next Steps

Once you've done all this:

1. **Run audio_walkthrough.py** and stare at the plots for 30 minutes
2. **Read train_cry_detection.py** line by line, pausing at comments
3. **Run train_cry_detection.py** on ICSD dataset
4. **Study the results** (confusion matrix, F1 score)
5. **Run quantize_model.py** and verify model size
6. **Review esp32_inference.cpp** and understand the flow
7. **Follow DAILY_CHECKLIST.md** for Day 1-2

By then, you'll understand the code deeply. You won't be copy-pasting. You'll be building.

---

## Resources to Have Open

**During learning:**
- AUDIO_FUNDAMENTALS.md
- audio_walkthrough.py output
- https://librosa.org/ (for MFCC parameter reference)

**During coding:**
- train_cry_detection.py (template)
- CRY_DETECTION_ROADMAP.md (timeline)
- Yao et al. 2022 paper (if stuck on concepts)

**During debugging:**
- DAILY_CHECKLIST.md (what should be done by now?)
- Section "Common Mistakes" (AUDIO_FUNDAMENTALS.md)
- Section "Failure Modes" (CRY_DETECTION_ROADMAP.md)

---

## Time Estimate

- **Learning phase:** 4-6 hours
- **Data prep + baseline training:** 16 hours (Days 1-2)
- **Model optimization:** 16 hours (Days 3-4)
- **Edge integration:** 8 hours (Days 5-6)
- **Documentation:** 8 hours (Day 7)

**Total: ~50 hours of focused work to get a working system**

That's achievable in 1 week if you work 7-8 hours a day with no distractions.

---

## One Final Thing

**Don't watch tutorial videos.** Read code and papers instead.
- Videos are slow
- Papers and code are fast and exact
- Audio concepts are 30 years old, any written resource is fine

**Don't overthink the math.** The intuition is enough.
- You don't need to implement DCT from scratch
- Librosa does it for you
- Understanding "what it does" matters, not "why it works mathematically"

**Do understand the trade-offs.** That's where expertise comes from.
- Why MFCC over raw audio?
- Why 16 kHz and not 44.1 kHz?
- Why balance the dataset?
- Why quantize the model?

Answer these, and you're no longer following a tutorial. You're engineering.

---

**Start with AUDIO_FUNDAMENTALS.md. Take notes. Then run audio_walkthrough.py. Then you're ready to code.**

# Cry Detection: Quick Start Guide
## Everything You Need, Organized

You have **8 files** in `/mnt/user-data/outputs/`. Here's what each does and when to use it.

---

## The Files (In Order of Use)

### 1. **LEARNING_PATH.md** ⭐ START HERE
**What:** Roadmap for learning without copy-pasting
**When:** Read this FIRST (30 min)
**Why:** Tells you exactly what to learn and in what order
**Key section:** "Daily Schedule (4-6 hours)"

### 2. **AUDIO_FUNDAMENTALS.md** 
**What:** Deep explanation of sampling, Fourier, MFCC, why they work
**When:** Read Sections 1-5 (45 min), then skim 6-12 (45 min)
**Why:** Understand *why* the code does what it does
**Key section:** Section 5 "MFCC: The Feature That Actually Works"

### 3. **audio_walkthrough.py**
**What:** Python script that shows you MFCC at each step visually
**When:** Run after reading AUDIO_FUNDAMENTALS.md (45 min)
**Why:** Seeing plots makes the concepts stick
**How to run:**
```bash
python audio_walkthrough.py
# Uncomment plt.show() lines to view plots
```
**Key section:** The matplotlib plots (compare cry vs background at each step)

### 4. **CRY_DETECTION_ROADMAP.md**
**What:** 1-week timeline, model architecture, data strategy
**When:** Read after LEARNING_PATH.md (but before coding) (60 min)
**Why:** Know the full picture before writing code
**Key sections:** 
- "Week Breakdown" (realistic timeline)
- "Model Architecture" (why this specific CNN)
- "Data Strategy" (why balance classes)
- "Metrics That Matter" (what you're optimizing for)

### 5. **DAILY_CHECKLIST.md**
**What:** Hour-by-hour todo list for Day 1-7
**When:** Use during coding (print this out!)
**Why:** Keeps you on track, prevents spiraling
**How to use:** Check off items as you complete them

### 6. **train_cry_detection.py**
**What:** Complete Python script to train SVM + CNN
**When:** Run on Day 1-2 (after learning phase) (16 hours)
**Why:** Baseline working code, heavily commented
**Before running:**
- Set DATA_DIR to where you downloaded ICSD
- Review the comments, understand each function
- Don't just run it blindly

### 7. **quantize_model.py**
**What:** Convert trained Keras model to TensorFlow Lite for ESP32
**When:** Run on Day 3 (after train_cry_detection.py finishes)
**Why:** Makes model small enough to fit on ESP32
**Input:** `models/cnn_model.h5` (from train_cry_detection.py)
**Output:** `models/cnn_model.tflite` (< 2 MB)

### 8. **esp32_inference.cpp**
**What:** C++ skeleton for running inference on ESP32
**When:** Reference on Day 4-6 (don't write from scratch)
**Why:** Shows the flow of MFCC extraction → inference
**How to use:** Copy parts into your actual ESP32 project, fill in MFCC computation

---

## The Actual Workflow

### Before You Code (4-6 hours)
```
1. Read LEARNING_PATH.md (30 min)
2. Read AUDIO_FUNDAMENTALS.md sections 1-5 (45 min)
3. Run audio_walkthrough.py (45 min)
4. Skim AUDIO_FUNDAMENTALS.md sections 6-12 (45 min)
5. Review train_cry_detection.py (don't run, just read) (45 min)
6. Read CRY_DETECTION_ROADMAP.md (60 min)
7. Mental check: Can you explain MFCC to someone? If yes, proceed.
```

### Day 1-2: Data + Training (16 hours)
```
Use: train_cry_detection.py
     DAILY_CHECKLIST.md (Day 1-2 section)
     AUDIO_FUNDAMENTALS.md (for reference if stuck)

1. Set up Python environment
2. Download ICSD + Environmental50 datasets
3. Run train_cry_detection.py on small subset (test)
4. Debug any issues
5. Run on full dataset (let it train overnight)
6. Check results (F1 score, confusion matrix)
7. Commit to Git
```

### Day 3: Quantization (8 hours)
```
Use: quantize_model.py
     CRY_DETECTION_ROADMAP.md (section "Failure Modes")

1. Run quantize_model.py
2. Check model size (should be < 2 MB)
3. If too big: Reduce model architecture, re-train
4. Test inference time (should be < 500 ms)
5. Commit .tflite file
```

### Day 4-7: Edge Integration + Documentation (24 hours)
```
Use: esp32_inference.cpp (reference)
     DAILY_CHECKLIST.md (Day 4-7 sections)
     CRY_DETECTION_ROADMAP.md (section "Success Criteria")

1. Integrate model into ESP32 project
2. Test MFCC extraction on device
3. Test inference pipeline
4. Tune confidence threshold
5. Test with real audio
6. Write documentation (README.md)
7. Commit everything
```

---

## Quick Answers (Before You Ask)

**Q: Should I read all of AUDIO_FUNDAMENTALS.md?**
A: Sections 1-5 are mandatory (it's the fundamentals). Sections 6-12 are optional but helpful.

**Q: Do I need to understand the math behind DCT?**
A: No. Understand "it decorrelates MFCC values." That's enough.

**Q: What if MFCC extraction is too hard?**
A: Use librosa. It handles everything. Focus on the concepts, not implementation.

**Q: What if my model accuracy is low?**
A: Not a model problem, it's a data problem. Check:
  - Are you using real-world training data (ICSD)?
  - Did you balance classes?
  - Did you normalize MFCC?
If all yes, then try a bigger model.

**Q: How long should each phase take?**
A: See LEARNING_PATH.md "Daily Schedule"

**Q: What if I fall behind?**
A: See CRY_DETECTION_ROADMAP.md "If You Get Stuck (Hour-by-Hour Triage)"

**Q: Can I skip the learning phase and just run code?**
A: Technically yes. You'll get a working system but won't understand it. Then you can't debug or modify it. Bad idea.

---

## Files You'll Create (Your Work)

```
cry-detection/
├── data/
│   ├── raw/
│   │   └── ICSD/
│   │       ├── infant_cry/ (your downloaded files)
│   │       └── snoring/
│   └── processed/
│       └── (MFCC features, auto-generated)
├── models/
│   ├── cnn_model.h5 (from train_cry_detection.py)
│   ├── cnn_model.tflite (from quantize_model.py)
│   └── svm_model.pkl (from train_cry_detection.py)
├── train_cry_detection.py (copy from outputs)
├── quantize_model.py (copy from outputs)
├── README.md (you write this)
└── esp32/ (your ESP32 project)
    └── cry_detection.cpp (modified from esp32_inference.cpp)
```

---

## How to Use These Files

### Copy Them to Your Project
```bash
# Download all 8 files to your repo
cp /mnt/user-data/outputs/* your_project/

# Or use them as reference while you code
# You don't have to copy, just read and understand
```

### Don't Copy-Paste Blindly
```
❌ Bad: Copy train_cry_detection.py, run it, done
✅ Good: Read train_cry_detection.py, understand it, modify as needed
```

### Take Notes
```
AUDIO_FUNDAMENTALS.md is long. While reading, write a summary:

"Key Points:"
- Sampling at 16 kHz captures frequencies up to 8 kHz (Nyquist)
- FFT converts time-domain signal to frequency-domain
- Spectrogram applies FFT to sliding windows (shows frequencies over time)
- Mel-scale matches human perception (more detail at low frequencies)
- MFCC compresses mel-spectrogram from 128 → 13 features
- Normalization (mean=0, std=1) stabilizes ML training
- Class balancing (oversample minority class) is critical
- Train on real-world data (ICSD), not lab recordings

You don't need perfect notes. Just enough to remember concepts.
```

---

## One-Sentence Summary of Each File

| File | One-Liner |
|------|-----------|
| LEARNING_PATH.md | Do this first: tells you what to learn and when |
| AUDIO_FUNDAMENTALS.md | Why MFCC works: read before any code |
| audio_walkthrough.py | Visualize MFCC extraction at each step |
| CRY_DETECTION_ROADMAP.md | 1-week timeline and realistic expectations |
| DAILY_CHECKLIST.md | Hour-by-hour tasks, print and check off |
| train_cry_detection.py | Working code: load data, train SVM + CNN |
| quantize_model.py | Convert trained model to TFLite for ESP32 |
| esp32_inference.cpp | C++ skeleton for edge inference |

---

## The Hardest Part

**Understanding the concepts is harder than writing code.**

- Code is straightforward: load data → train → save
- Concepts are subtle: why these parameters? why this architecture?

**Spend time on AUDIO_FUNDAMENTALS.md.** Don't skim.
- Take notes
- Run audio_walkthrough.py and stare at plots
- Answer the questions in LEARNING_PATH.md
- If you can't, re-read that section

Once concepts click, coding is fast.

---

## Success Checklist

Before you consider yourself "ready to code":

- [ ] I read LEARNING_PATH.md
- [ ] I read AUDIO_FUNDAMENTALS.md sections 1-5 and took notes
- [ ] I ran audio_walkthrough.py and looked at all plots
- [ ] I understand what MFCC is and why we use it
- [ ] I understand why we balance classes
- [ ] I understand the CNN architecture choices
- [ ] I read CRY_DETECTION_ROADMAP.md
- [ ] I can answer the questions in AUDIO_FUNDAMENTALS.md section 12

If any are unchecked, keep reading.

---

## Final Words

You came here saying "I'm not a professional, just a student." 

**That's actually an advantage.**

Professionals often copy-paste code they don't understand. You're taking the time to learn concepts. In 1 week, you'll know more than most people who've built audio ML systems.

The code isn't the hard part. The concepts are. And you're doing them first.

**This is how you build something that actually works.**

---

## Next Step

1. Print out this file
2. Open LEARNING_PATH.md
3. Follow the "Daily Schedule (4-6 hours)" section
4. Don't skip the learning phase
5. Report back when you've read AUDIO_FUNDAMENTALS.md + run audio_walkthrough.py

You've got a solid 1-week roadmap now. Use it.

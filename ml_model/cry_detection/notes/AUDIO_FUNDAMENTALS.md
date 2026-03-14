# Audio Fundamentals for Cry Detection
## Concepts Before Code

You need to understand **5 core ideas**. Master these, and the code makes sense. Skip them, and you're just copy-pasting magic numbers.

---

## 1. SAMPLING: Converting Sound Waves to Numbers

### The Problem
Sound is a continuous wave in the air. Computers store discrete numbers. How do we convert one to the other?

### The Solution: Sampling
You grab the amplitude (height) of the sound wave at regular time intervals.

```
Continuous sound wave:
    ╱╲      ╱╲
   ╱  ╲    ╱  ╲    ← Smooth curve
  ╱    ╲  ╱    ╲

Sampled at 16 kHz (16,000 times per second):
    •      •
       •      •     ← We only know the height at these points
    •      •
```

### Key Parameters

**Sampling Rate (fs):** How many samples per second?
- **8 kHz:** Phone quality (audio only up to 4 kHz) - too low for cry detection
- **16 kHz:** Speech quality (audio up to 8 kHz) - GOOD for babies crying
- **44.1 kHz:** CD quality (audio up to 22 kHz) - overkill, uses more CPU/memory
- **48 kHz:** Professional audio - overkill

**For cry detection: Use 16 kHz.** Baby cries are mostly < 8 kHz anyway.

### Nyquist Theorem (Why 16 kHz?)
You can only capture frequencies up to half your sampling rate.
- 16 kHz sampling → capture up to 8 kHz frequencies
- Baby cry fundamental frequency: 400-600 Hz ✓ (well below 8 kHz)
- If you use 8 kHz, you lose high-frequency details → worse accuracy

### In Code
```python
import librosa

# Load audio at 16 kHz
y, sr = librosa.load('baby_cry.wav', sr=16000)
# y = array of 16000 * duration samples
# sr = 16000 (sampling rate)
```

---

## 2. TIME vs. FREQUENCY: Understanding What Frequencies Are

### The Problem
Cry detection isn't just about *when* a sound occurs. It's about *what frequencies* are in that sound.

A vacuum cleaner has different frequencies than a baby cry. How do we separate frequencies?

### Fourier Transform (DFT)
Any complex sound can be broken down into simple sine waves at different frequencies.

```
Baby cry (complex):
     ╱╲╱╲╱╲╱╲╱╲╱╲╱  (looks messy)

Can be decomposed into:
  Frequency 1:  ~~~~ ~~~~ ~~~~ (slow wave)
  Frequency 2:  ╱╲╱╲╱╲╱╲╱╲╱╲╱ (fast wave)
  Frequency 3:  ╱╱╱╱╱╱╱╱╱╱╱╱╱ (very fast wave)
  + etc.
```

**Fourier Transform = Tool that decomposes complex signals into simple frequencies**

### Practical Example: Why It Matters
```
Cry audio:     [mostly 400-600 Hz] + [some 100-200 Hz] + [some 2-4 kHz]
Vacuum audio:  [mostly 60 Hz (hum)] + [wide noise across all frequencies]
Dog bark:      [mostly 800-2000 Hz] + [sudden onset]

Machine learns: "If I see high energy at 400-600 Hz + gradual onset = cry"
```

### In Code
```python
import numpy as np

# Time-domain signal (raw audio)
signal = np.array([0.1, 0.2, 0.15, -0.1, -0.2, ...])  # 16000 values

# Convert to frequency domain
from scipy.fft import fft
frequencies = fft(signal)
# frequencies = [complex numbers representing each frequency's strength]
```

---

## 3. SPECTROGRAMS: Time + Frequency Together

### The Problem
Fourier Transform tells us "what frequencies exist" but **when they exist doesn't matter**.

A cry that starts softly and gets loud looks the same as a cry that stays loud → Bad for detection.

### Solution: Spectrogram
**Divide audio into short chunks → Apply Fourier to each chunk → Stack results**

```
Audio signal (over 2 seconds):
[CHUNK 1: 0-0.025s] [CHUNK 2: 0.025-0.05s] [CHUNK 3: 0.05-0.075s] ... (80 chunks)

Chunk 1:              Chunk 2:              Chunk 3:
Freq analysis   →     Freq analysis   →     Freq analysis   →  ...
├─ 100 Hz: 0.05      ├─ 100 Hz: 0.07      ├─ 100 Hz: 0.1
├─ 200 Hz: 0.1       ├─ 200 Hz: 0.15      ├─ 200 Hz: 0.2
├─ 400 Hz: 0.8  ✓    ├─ 400 Hz: 0.9   ✓   ├─ 400 Hz: 0.95  ✓
└─ 800 Hz: 0.2       └─ 800 Hz: 0.15      └─ 800 Hz: 0.1

Stack them (time on x-axis, frequency on y-axis):

   Freq
   |
2000|░░░░░░░░
1000|░░░░▓▓▓░
 500|░░▓▓▓▓▓░  ← Cry shows up as dark band at 400-600 Hz
 200|░░░░░░░░
 100|░░░░░░░░
   └─────────  Time (2 seconds)

Dark = high energy at that frequency/time
Light = low energy
```

### Key Spectrogram Parameters

**Frame Length (window size):**
- How long is each chunk? (e.g., 25 milliseconds)
- **Tradeoff:**
  - Longer frame → better frequency resolution (know exact frequency) but worse time resolution (can't pinpoint when)
  - Shorter frame → worse frequency resolution but better time resolution
- **For cry detection: 25 ms is standard** (good balance)

**Hop Length (overlap):**
- How much do frames overlap? (e.g., 10 milliseconds)
- **Smaller overlap → more frames → more data → slower but slightly better**
- **For cry detection: 10 ms is standard** (75% overlap = good temporal coverage)

### In Code
```python
import librosa

# Load audio
y, sr = librosa.load('baby_cry.wav', sr=16000)

# Compute spectrogram
# Parameters:
#   n_fft: 400 (≈ 25 ms at 16 kHz, captures up to ~8 kHz frequency)
#   hop_length: 160 (≈ 10 ms, 75% overlap)
spectrogram = librosa.stft(y, n_fft=400, hop_length=160)
spectrogram = np.abs(spectrogram)  # Get magnitude (ignore phase)

# Result shape: (201, ~3141)
# 201 = frequency bins (0 to 8 kHz in steps of ~40 Hz)
# 3141 = time frames (2 seconds at 16 kHz with 10 ms hop)
```

---

## 4. MEL-SCALE FREQUENCY: Matching Human Hearing

### The Problem
Human ears don't perceive frequency linearly.

```
We hear the difference between:
  - 100 Hz and 200 Hz as HUGE (octave difference)
  
But barely hear the difference between:
  - 8100 Hz and 8200 Hz (same pitch difference, imperceptible)
```

A spectrogram uses linear frequencies (100, 200, 300, 400, ...). That wastes bins on high frequencies we can't perceive.

### Solution: Mel-Scale
Map frequencies to a **perceptual scale** that matches human hearing.

```
Linear scale (regular spectrogram):
Freq|████|████|████|████|████|████|████|████|████|
    0  1kHz 2kHz 3kHz 4kHz 5kHz 6kHz 7kHz 8kHz

Mel scale (human-like):
Freq|████████|████████|████|████|████|███|██|██|
    0  500Hz  1kHz   2kHz 3kHz 4kHz 5kHz 6kHz 8kHz
    
More resolution at low frequencies (where cries are)
```

### Mel-Spectrogram in Code
```python
# Spectrogram with mel-scale
mel_spectrogram = librosa.feature.melspectrogram(
    y=y, 
    sr=sr,
    n_fft=400,
    hop_length=160,
    n_mels=128  # Number of mel-frequency bins (128 is common)
)

# Result: (128, ~3141)
# 128 = mel-frequency bins (better for human perception)
# ~3141 = time frames (same as before)
```

### Why This Matters for Cry Detection
Cries have energy at **low frequencies (400-600 Hz)**, which is where mel-scale gives us the most detail. Perfect for babies.

---

## 5. MFCC: The Feature That Actually Works

### The Problem
A mel-spectrogram is still 128 × 3141 = 401,408 numbers for 2 seconds of audio.

Your ESP32 can't process that in real-time. You need **compression**.

### Solution: MFCC (Mel-Frequency Cepstral Coefficients)
**Take a mel-spectrogram → Compress it to 13-39 numbers per time frame**

#### Step-by-Step

**Step 1: Mel-spectrogram**
```
Input: Audio → Mel-spectrogram (128 frequency bins, ~3141 time frames)
```

**Step 2: Log the energy**
```
Why log? 
- Human hearing responds logarithmically (louder sounds need exponentially more energy to perceive)
- Log compresses the dynamic range (loud and soft sounds get similar representation)
- ML models train faster on log-compressed data
```

**Step 3: Discrete Cosine Transform (DCT)**
```
What: Mathematical transform (like FFT but for real numbers)
Why: Decorrelates the mel-frequency bins (removes redundancy)
     Keeps most important information in first 13 coefficients

Think of it like:
  Mel-spectrogram = [128 correlated numbers]
  DCT = [13 important numbers] + [115 redundant numbers]
  
We keep the first 13 = MFCC
```

**Step 4: Result**
```
One 2-second cry audio → 128 time frames × 13 MFCC coefficients
Compression ratio: 401,408 → 1,664 numbers (240x smaller!)
```

### Why MFCC Works So Well
1. **Human hearing inspired** (mel-scale)
2. **Logarithmic compression** (realistic dynamic range)
3. **Decorrelated features** (DCT removes redundancy)
4. **Proven track record** (used in speech recognition since 1980s)

The Yao et al. paper used MFCC + acoustic features and got F1 = 0.613 on real-world data. Not because MFCC is magic, but because it captures what matters: frequency content over time.

### In Code
```python
# Extract MFCC
mfcc = librosa.feature.mfcc(
    y=y,
    sr=16000,
    n_mfcc=13,           # Extract first 13 coefficients
    n_fft=400,           # Frame length
    hop_length=160       # Frame overlap
)

# Result: (13, ~3141)
# 13 = MFCC coefficients
# ~3141 = time frames
```

---

## 6. Why These Features Detect Cries (Intuition)

### What Makes a Cry Sound Like a Cry?

**1. Frequency Content**
```
Baby cry:      High energy at 400-600 Hz (fundamental frequency)
               Some harmonics at 800-1200 Hz
               Not much above 2 kHz

Vacuum:        Broad noise across 0-8 kHz (no single frequency dominates)

Dog bark:      High energy at 800-2000 Hz (higher than cry)
               Sharp onset/offset

Speech:        Formants (peaks) at 700, 1200, 2500 Hz
               Varies a lot over time
```

**2. Time Pattern**
```
Cry:           Gradual onset (builds up)
               Sustained (holds for 1+ seconds)
               Gradual offset (fades out)

Cough:         Sharp onset
               Brief duration (< 0.5 second)
               Sharp offset

White noise:   Flat over time
               No structure
```

**3. Modulation (Frequency variation)**
```
Cry:           Pitch wobbles (vibrato-like)
               Not perfectly steady

Machine hum:   Dead flat (60 Hz constant)
```

### How ML Uses These
```
CNN + MFCC:
  Input: 128 time frames × 13 MFCC coefficients
         (captures frequency content over 2 seconds)
  
  First conv layer learns: "Pattern that looks like low frequencies with high energy"
  Second conv layer learns: "Pattern that looks like time modulation"
  Dense layer combines: "If both patterns present → likely a cry"
```

---

## 7. Practical Audio Parameters for Your Project

### Your Setup
```
Sampling rate:        16 kHz (baby cry is < 8 kHz)
Frame length:         25 ms = 400 samples
Hop length:           10 ms = 160 samples
MFCC coefficients:    13 (+ energy sometimes = 14)
Audio window:         2 seconds = 128 frames
```

### Why These Values?
```
16 kHz:       Captures up to 8 kHz → covers baby cry (400-600 Hz primary)
              Uses less memory than 44.1 kHz
              Still high quality for audio ML

25 ms frame:  Standard for speech/cry (good balance)
              At 16 kHz: 400 samples = 25 ms

10 ms hop:    75% overlap between frames
              More temporal detail without huge overhead
              At 16 kHz: 160 samples = 10 ms

13 MFCC:      Sweet spot between compression and information
              More MFCCs = more memory (bad for edge)
              Fewer MFCCs = lose information (bad for accuracy)
              13 works in practice

2 sec window: Long enough to capture cry structure
              Short enough to fit on ESP32 PSRAM (8 MB)
              2 sec × 16k samples/sec = 32k samples = ~128 KB
```

---

## 8. From Raw Audio to Input for ML

### The Pipeline
```
Step 1: Load audio at 16 kHz
        Input: baby_cry.wav
        Output: numpy array of 16,000 samples (for 1 second)

Step 2: Divide into 25 ms frames with 10 ms hop
        Input: 16,000 samples (1 second)
        Output: 101 frames of 400 samples each
                (with 75% overlap)

Step 3: Compute STFT (Fourier on each frame)
        Input: 101 frames × 400 samples
        Output: 101 frames × 201 frequency bins
                (complex numbers)

Step 4: Convert to Mel-scale
        Input: 101 frames × 201 frequency bins
        Output: 101 frames × 128 mel-frequency bins
                (human-like frequency perception)

Step 5: Log amplitude
        Input: 101 frames × 128 mel bins
        Output: 101 frames × 128 log-magnitudes
                (human-like loudness perception)

Step 6: Apply DCT (Discrete Cosine Transform)
        Input: 101 frames × 128 mel bins
        Output: 101 frames × 13 MFCC coefficients
                (decorrelated, compressed)

Step 7: Pad/truncate to standard size
        Input: variable-length MFCC (e.g., 101 frames for 1 sec)
        Output: 128 frames × 13 MFCC (always 2 seconds)
                (or 64 frames for 1 second, depending on your choice)

Step 8: Normalize
        Input: raw MFCC (can be any range)
        Output: MFCC with mean=0, std=1
                (helps ML training)

ML Input: (128, 13) array
          Ready for CNN
```

### Code (One Complete Pipeline)
```python
import librosa
import numpy as np

def audio_to_mfcc(audio_path, sr=16000, n_mfcc=13, frames=128):
    # Step 1: Load
    y, sr = librosa.load(audio_path, sr=sr)
    
    # Steps 2-6: Extract MFCC (librosa does all this internally)
    mfcc = librosa.feature.mfcc(
        y=y, 
        sr=sr,
        n_mfcc=n_mfcc,
        n_fft=int(0.025 * sr),      # 25 ms
        hop_length=int(0.010 * sr)  # 10 ms
    )  # Shape: (13, variable)
    
    # Step 7: Pad/truncate
    if mfcc.shape[1] < frames:
        pad_width = ((0, 0), (0, frames - mfcc.shape[1]))
        mfcc = np.pad(mfcc, pad_width, mode='constant')
    else:
        mfcc = mfcc[:, :frames]
    
    # Step 8: Normalize
    mfcc = (mfcc - mfcc.mean(axis=1, keepdims=True)) / (mfcc.std(axis=1, keepdims=True) + 1e-5)
    
    # Transpose to (frames, n_mfcc) for CNN
    return mfcc.T  # Shape: (128, 13)
```

---

## 9. Why Deep Learning Works Here

### The Pattern Recognition Problem
```
Human (rule-based approach):
  IF frequency_peak ∈ [400, 600] Hz
     AND energy_ratio > 0.8
     AND onset_time < 0.5 seconds
  THEN cry
  ELSE not cry

Problem: Too many edge cases, exceptions, hand-tuned thresholds

CNN (pattern-based approach):
  Layer 1: Learn low-level patterns
           "Vertical band at 400 Hz"
           "Temporal rise pattern"
           "High amplitude region"
  
  Layer 2: Combine patterns
           "Vertical band + temporal rise" = cry signal
           "Broad noise + no structure" = background
  
  Layer 3: Final classification
           "This is 93% likely a cry"

Advantage: Learns from data, adapts to variations
```

### Why Small Networks Work (TinyML)
```
You don't need 100M parameters to detect cries.

Cry vs. non-cry is a simpler problem than:
  - Image classification (billions of possible variations)
  - Natural language (infinite sentence combinations)

A 40K parameter CNN works because:
  1. MFCC is already highly compressed (13 features, not 1000s)
  2. Cry vs. non-cry is binary (not 1000 classes)
  3. The pattern is consistent across babies (universal acoustic feature)
```

---

## 10. Common Mistakes (Don't Make These)

### Mistake 1: Using Raw Audio as Input
```
❌ WRONG: Feed raw [0.1, 0.05, -0.1, ...] samples to CNN
         Why: Too many features (16,000 per second)
              CNN learns nothing useful

✅ RIGHT: Use MFCC (13 features per 10 ms)
         Why: Compressed, human-relevant, proven to work
```

### Mistake 2: Not Normalizing MFCC
```
❌ WRONG: MFCC ranges from -100 to +100 (raw values)
         Why: ML optimization is slower, unstable

✅ RIGHT: Normalize to mean=0, std=1
         Why: Faster convergence, more stable training
```

### Mistake 3: Training Only on Lab Audio
```
❌ WRONG: Train on clean cries recorded in quiet room
         Why: Yao paper proves this fails in real homes
              Model learns to detect "clean cry sound" not actual cries

✅ RIGHT: Train on ICSD (real home recordings)
         Why: Model learns to separate cry from background clutter
```

### Mistake 4: Using Too Many MFCC Coefficients
```
❌ WRONG: Use 40 MFCCs for edge device
         Why: 40 × 128 frames = 5,120 features
              ESP32 struggles, quantization hurts

✅ RIGHT: Use 13 MFCCs
         Why: Enough to capture cry, small enough for edge
```

### Mistake 5: Ignoring Class Imbalance
```
❌ WRONG: Train on 90% non-cry, 10% cry (real distribution)
         Why: Model learns to predict "not cry" for everything
              Trivial 90% accuracy, useless in practice

✅ RIGHT: Balance during training (50% cry, 50% non-cry)
         Why: Model forced to learn discriminative features
```

---

## 11. Quick Reference: Audio Math You Need

### Sampling
```
Duration (seconds) = Num_samples / Sampling_rate
Example: 16,000 samples at 16 kHz = 1 second
```

### Frequency Resolution
```
Freq_resolution = Sampling_rate / FFT_size
Example: 16 kHz / 400 = 40 Hz per bin
         (You can distinguish 40 Hz increments)
```

### Time Resolution
```
Frame_duration = FFT_size / Sampling_rate
Example: 400 / 16,000 = 0.025 seconds = 25 ms

Frame_shift = Hop_length / Sampling_rate
Example: 160 / 16,000 = 0.010 seconds = 10 ms
```

### Number of Frames
```
Num_frames = (Signal_length - FFT_size) / Hop_length + 1
Example: (16,000 - 400) / 160 + 1 ≈ 100 frames (for 1 second)
         or ≈ 200 frames (for 2 seconds)
```

---

## 12. Recommended Reading (Optional)

If you want deeper understanding:

1. **"An Introduction to Signal Processing"** - Oppenheim & Schafer
   - Rigorous but standard reference
   - Read chapters on Fourier, windowing, sampling

2. **"Speech and Language Processing"** - Jurafsky & Martin
   - Chapter 3 on acoustic features
   - MFCCs explained clearly

3. **Yao et al. 2022 paper** (you have it)
   - Section 4 on cry detection models
   - Real-world performance metrics

4. **Librosa documentation**
   - Practical examples for all audio processing
   - https://librosa.org/

---

## Summary: What You Need to Know

| Concept | Why It Matters | Key Takeaway |
|---------|---|---|
| **Sampling (16 kHz)** | Convert sound to numbers | Choose rate ≥ 2× highest frequency |
| **Fourier/STFT** | Extract frequencies over time | Use librosa, don't implement yourself |
| **Spectrogram** | See frequencies evolving | Visualize before feeding to ML |
| **Mel-scale** | Match human hearing | Use 128 mel bins (standard) |
| **MFCC** | Compress spectrogram | Use 13 coefficients (works in practice) |
| **Normalization** | Stabilize ML training | mean=0, std=1 before feeding to CNN |
| **Real-world data** | Generalization | Yao paper: clean data fails in real homes |

---

## Practice Exercises (Do These)

### Exercise 1: Load and visualize
```python
import librosa
import matplotlib.pyplot as plt

# Load
y, sr = librosa.load('baby_cry.wav', sr=16000)

# Plot raw audio (time domain)
plt.figure(figsize=(12, 4))
plt.plot(y[:sr])  # First 1 second
plt.title("Raw Audio (Time Domain)")
plt.show()

# Plot spectrogram (frequency domain)
spec = librosa.feature.melspectrogram(y=y, sr=sr)
librosa.display.specshow(spec, sr=sr, x_axis='time', y_axis='mel')
plt.title("Mel-Spectrogram")
plt.colorbar()
plt.show()
```

### Exercise 2: Extract MFCC
```python
# Extract MFCC
mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

# Visualize
plt.figure(figsize=(12, 4))
librosa.display.specshow(mfcc, sr=sr, x_axis='time')
plt.ylabel('MFCC')
plt.title('MFCC Features')
plt.colorbar()
plt.show()

# Check shape
print(f"MFCC shape: {mfcc.shape}")
# Should be (13, ~3141) for 2 seconds at 16 kHz with 10 ms hop
```

### Exercise 3: Compare cry vs. non-cry MFCC
```python
# Load both
cry, sr = librosa.load('baby_cry.wav', sr=16000)
non_cry, sr = librosa.load('vacuum.wav', sr=16000)

# Extract MFCC
mfcc_cry = librosa.feature.mfcc(y=cry, sr=sr, n_mfcc=13)
mfcc_non = librosa.feature.mfcc(y=non_cry, sr=sr, n_mfcc=13)

# Plot side-by-side
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

librosa.display.specshow(mfcc_cry, sr=sr, x_axis='time', ax=ax1)
ax1.set_title("Cry MFCC")

librosa.display.specshow(mfcc_non, sr=sr, x_axis='time', ax=ax2)
ax2.set_title("Non-Cry MFCC")

plt.tight_layout()
plt.show()

# Observation: Cry should have darker band at low MFCCs
# Non-cry (vacuum) should be more uniform
```

---

## Final Takeaway

You don't need to understand the math deeply. You need to understand the **intuition**:

1. **Audio is a wave** → Sample it to get numbers
2. **Waves have frequencies** → Use Fourier to extract them
3. **Humans hear non-linearly** → Use mel-scale
4. **Compress for speed** → Use MFCC
5. **ML finds patterns** → CNN learns cry patterns from MFCC

Everything else is implementation detail. Librosa handles steps 2-4. You just need to pick reasonable parameters and feed data to a CNN.

**Now stop reading and do Exercise 1-3. Seeing MFCCs for cry vs. vacuum will teach you more than reading this.**

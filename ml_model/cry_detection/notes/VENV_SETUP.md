# Python Environment Setup for Smart Baby Band Monorepo

## Quick Answer

**One `.venv` per language stack, shared by team:**
- **Python projects:** One `.venv` at repo root (for all Python)
- **Node.js projects:** Use npm/yarn (separate from Python)
- **Flutter projects:** Flutter SDK (separate from Python)

Your structure:
```
Smart-Baby-Band-FYP/
├── .venv/               ← Single Python venv (shared)
├── .gitignore           ← Ignore .venv and node_modules
├── requirements.txt     ← All Python dependencies (from all projects)
├── package.json         ← Node.js dependencies
│
├── hardware/
│   └── (C/C++, no venv needed)
│
├── ml_model/
│   ├── datasets/
│   ├── train.py
│   ├── quantize.py
│   └── inference.py
│
├── app/
│   └── (Flutter, no Python venv)
│
└── backend/
    ├── server.js
    ├── models/
    └── (Node.js, uses package.json)
```

---

## Why One Venv?

### ✅ GOOD: One shared venv
```bash
# Anyone on the team does this once:
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or: .venv\Scripts\activate  (Windows)
pip install -r requirements.txt

# Everyone uses the same dependencies
# Easy to track what versions work together
# One source of truth
```

### ❌ BAD: Separate venv per project
```bash
ml_model/.venv/
backend/.venv/
app/.venv/  # doesn't make sense, app is Flutter
hardware/.venv/  # doesn't make sense, hardware is C++

# Problems:
# - Confusing for team
# - Duplicate packages (storage waste)
# - Hard to sync versions
# - "Works on my machine" problems
```

---

## Exact Setup Instructions

### Step 1: Create Single Python Venv at Repo Root

```bash
cd Smart-Baby-Band-FYP/

# Create venv
python3 -m venv .venv

# Activate it
# On Linux/Mac:
source .venv/bin/activate

# On Windows PowerShell:
.venv\Scripts\Activate.ps1

# On Windows Command Prompt:
.venv\Scripts\activate.bat

# You should see (.venv) in your terminal prompt
```

### Step 2: Create requirements.txt at Repo Root

```bash
# At: Smart-Baby-Band-FYP/requirements.txt

# For cry detection model (ml_model/)
librosa==0.10.0
numpy==1.24.3
scipy==1.11.0
scikit-learn==1.3.0
tensorflow==2.13.0
pandas==2.0.3
soundfile==0.12.1
matplotlib==3.7.2

# For Flask/Django backend if you use Python
# (but your backend is Node.js, so skip this)

# For data exploration/analysis
jupyter==1.0.0
ipython==8.12.2

# Pinned versions (if team has different OS):
# Linux/Mac: tensorflow==2.13.0
# Windows: tensorflow==2.13.0 (same)
```

### Step 3: Install Dependencies

```bash
# Make sure you're in the venv (you see (.venv) in prompt)
pip install -r requirements.txt

# Verify installation
python -c "import tensorflow; print(tensorflow.__version__)"
# Should print: 2.13.0
```

### Step 4: Add .gitignore to Repo Root

Copy the `.gitignore` file to your repo root. This prevents:
- `.venv/` folder from being committed (1GB+)
- `ml_model/data/raw/` datasets (gigabytes)
- `ml_model/models/*.h5` trained models (megabytes)
- `node_modules/` (Node.js, heavy)

**Without .gitignore, your repo will be 5+ GB. With it, <100 MB.**

---

## How Your Team Works With This Setup

### Team Member 1 (You - ML Model)

```bash
# Day 1: Clone and setup
git clone <repo>
cd Smart-Baby-Band-FYP
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Now you can:
python ml_model/train.py      # Training
python ml_model/quantize.py   # Quantization
jupyter notebook               # Explore data

# All dependencies are in one place, shared with team
```

### Team Member 2 (Backend - Node.js)

```bash
# Same setup (one venv, but they don't use Python)
git clone <repo>
cd Smart-Baby-Band-FYP
python3 -m venv .venv
source .venv/bin/activate  # Don't actually need this, but doesn't hurt
pip install -r requirements.txt  # Same, not needed for Node.js

# But they use Node.js tools:
npm install          # Install Node.js dependencies
npm start            # Run backend server

# The .venv exists but they ignore it
# No confusion, no redundancy
```

### Team Member 3 (Flutter App)

```bash
# Same setup
git clone <repo>
cd Smart-Baby-Band-FYP
python3 -m venv .venv
source .venv/bin/activate  # Doesn't affect Flutter

# Flutter works independently:
flutter pub get
flutter run

# The .venv exists, they ignore it
```

---

## Common Mistakes (Don't Make These)

### ❌ Mistake 1: Separate venv per project
```bash
# DON'T do this:
ml_model/.venv/
backend/.venv/
app/.venv/

# Problems:
# - Team members confused about which venv to activate
# - 3x disk space for duplicate packages
# - Hard to sync Python version (2 or 3.8 or 3.11?)
```

### ✅ Correct: One venv at root
```bash
.venv/  # Single source of truth
```

### ❌ Mistake 2: Not committing requirements.txt
```bash
# DON'T do this:
git add .venv/
# (This commits 1GB of files!)

# DO this:
pip freeze > requirements.txt
git add requirements.txt
# (This commits 5 KB of text)
```

### ✅ Correct: Commit requirements.txt, ignore .venv
```bash
git add requirements.txt
# In .gitignore:
.venv/
```

### ❌ Mistake 3: Using hardcoded paths
```python
# DON'T do this:
data_path = "/home/umair/cry-detection/data"  # Only works for you!

# DO this:
from pathlib import Path
data_path = Path(__file__).parent.parent / "ml_model" / "data"
# Works for everyone
```

### ❌ Mistake 4: Updating requirements.txt manually
```bash
# DON'T do this:
# Edit requirements.txt by hand, typos everywhere

# DO this:
pip freeze > requirements.txt
# Generates exact versions you're using
```

---

## Updating Dependencies (As Team)

### When You Add a New Package

```bash
# You install something new
pip install ultralytics  # New library for your ML model

# Update requirements.txt
pip freeze > requirements.txt

# Commit it
git add requirements.txt
git commit -m "feat: add ultralytics for inference"
git push

# Your team members pull and update:
git pull
pip install -r requirements.txt  # Gets new package
```

### When There's a Version Conflict

Example: You use TensorFlow 2.13, but another team member uses 2.12, causing bugs.

```bash
# Solution: Be explicit in requirements.txt
# Instead of:
tensorflow

# Use:
tensorflow==2.13.0  # Exact version, everyone gets same

# Then all team members:
pip install -r requirements.txt --upgrade
```

---

## IDE Configuration (VS Code Example)

### Step 1: Open .venv Python Interpreter

In VS Code:
1. `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "Python: Select Interpreter"
3. Choose `.venv` (should show path like `./Smart-Baby-Band-FYP/.venv/bin/python`)

### Step 2: Verify It's Working

```bash
# In VS Code terminal, type:
which python
# Should show: /path/to/Smart-Baby-Band-FYP/.venv/bin/python

# Not:
# /usr/bin/python (system Python, wrong!)
```

### Step 3: Configure Jupyter (For Notebooks)

In VS Code, when you open a `.ipynb` file:
1. Top right: "Select Kernel"
2. Choose `.venv Python` (not system Python)

---

## Your Project Structure (Updated)

```
Smart-Baby-Band-FYP/
│
├── .venv/                    ← Single Python environment (DO NOT commit)
├── .gitignore                ← Tells Git what to ignore
├── requirements.txt          ← All Python dependencies (DO commit)
├── README.md
│
├── docs/                      # Reports, diagrams
│
├── hardware/                  # C/C++ (no venv needed)
│   ├── firmware/
│   │   ├── esp32_cry_detection.cpp
│   │   └── esp32_quantized_inference.c
│   └── README.md
│
├── ml_model/                  # Python ML code
│   ├── datasets/
│   │   ├── raw/               # ICSD + Environmental50 (large, don't commit)
│   │   ├── processed/         # Generated MFCC features (don't commit)
│   │   └── splits/            # train/val/test split info
│   ├── models/
│   │   ├── cnn_model.h5       # Trained model (don't commit, store on Drive)
│   │   ├── cnn_model.tflite   # Quantized (don't commit, upload to repo releases)
│   │   └── model_info.txt     # Model specs (DO commit)
│   ├── notebooks/
│   │   └── eda.ipynb          # Data exploration
│   ├── train.py               # Training script (your train_cry_detection.py)
│   ├── quantize.py            # Quantization script (your quantize_model.py)
│   ├── evaluate.py            # Evaluation metrics
│   └── README.md
│
├── app/                        # Flutter (no venv)
│   ├── lib/
│   ├── pubspec.yaml
│   └── README.md
│
├── backend/                    # Node.js (separate npm packages)
│   ├── src/
│   ├── package.json
│   ├── package-lock.json
│   └── README.md
│
└── CONTRIBUTING.md            # Team guidelines (include venv setup!)
```

---

## Instructions for Each Team Member (Copy This)

### Setup (Everyone Does This Once)

```bash
# 1. Clone repo
git clone <your-repo-url>
cd Smart-Baby-Band-FYP

# 2. Create Python environment (ONCE)
python3 -m venv .venv

# 3. Activate it (Every time you work)
# Linux/Mac:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify
python -c "import tensorflow; print('TensorFlow OK')"
```

### Before You Commit Code

```bash
# Add your code
git add ml_model/train.py

# If you installed new packages, update requirements.txt
pip freeze > requirements.txt
git add requirements.txt

# Commit
git commit -m "feat: add new training script"

# Push
git push
```

### If You Pull New Code and Get Import Errors

```bash
# Pull latest
git pull

# Reinstall dependencies (in case requirements.txt changed)
pip install -r requirements.txt --upgrade

# Run your code
python ml_model/train.py
```

---

## Large Files (Models, Datasets)

### Where They Go

❌ **NOT in Git:**
- `ml_model/data/raw/` (ICSD is 2+ GB)
- `ml_model/models/*.h5` (trained weights)
- `ml_model/models/*.tflite` (quantized model)

✅ **In Git (just references):**
- `requirements.txt` (lists pip packages)
- `model_info.txt` (documents model specs)
- `DATA_DOWNLOAD.md` (instructions to download datasets)

### How to Share Large Files

**Option 1: Google Drive**
```
Create a shared folder:
Smart-Baby-Band-FYP/datasets/

Share link with team
Instructions in ml_model/README.md:
  "Download from: [link to Google Drive]"
```

**Option 2: GitHub Releases**
```
For trained models:
1. Train model locally
2. Create GitHub Release
3. Upload .tflite file as attachment
4. Share release link with team

Team downloads from release, saves to ml_model/models/
```

**Option 3: .gitignore + Local Copy**
```
.gitignore ignores ml_model/data/raw/
Each team member downloads ICSD separately
Same .gitignore means no accidental commits
```

---

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'tensorflow'"

```bash
# Solution: Activate venv first!
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Then check:
which python
# Should show: /path/to/.venv/bin/python

# If it doesn't, reinstall:
pip install -r requirements.txt
```

### Problem: "Different Python versions between team members"

```bash
# Specify in requirements.txt:
# At top of file:

# python_requires >= 3.8
tensorflow==2.13.0  # Works on Python 3.8-3.11
numpy==1.24.3
librosa==0.10.0

# All team members now use compatible versions
```

### Problem: "requirements.txt has conflicts"

```bash
# Example: tensorflow wants numpy 1.24 but librosa wants 1.23

# Solution 1: Let pip resolve
pip install -r requirements.txt
# (pip is smart enough to find compatible versions)

# Solution 2: Fix manually
# Edit requirements.txt with compatible versions:
tensorflow==2.13.0  # Uses numpy 1.24
librosa==0.10.0     # Also compatible with 1.24
numpy==1.24.3       # Explicit version everyone agrees on

# Solution 3: Use pip-tools
pip install pip-tools
pip-compile requirements.in > requirements.txt
# (advanced, skip for now)
```

### Problem: ".venv folder is 1 GB, slowing down Git"

```bash
# You didn't add .gitignore! Fix it:
echo ".venv/" >> .gitignore
git add .gitignore
git rm -r --cached .venv/  # Remove from Git history
git commit -m "chore: remove .venv from git"
git push

# Now .venv stays local, never committed
```

---

## Final Checklist

Before your team starts working:

- [ ] One `.venv` at repo root (not in subfolders)
- [ ] `.gitignore` includes `.venv/`
- [ ] `requirements.txt` at repo root with all Python packages
- [ ] Each team member can:
  - [ ] `source .venv/bin/activate` (or Windows equivalent)
  - [ ] `pip install -r requirements.txt` without errors
  - [ ] `python -c "import tensorflow"` works
- [ ] `.gitignore` prevents large files:
  - [ ] `ml_model/data/raw/` not committed
  - [ ] `ml_model/models/*.h5` not committed
  - [ ] `ml_model/models/*.tflite` not committed
- [ ] Team knows where to get large files (Google Drive, Release, etc.)
- [ ] All team members can activate venv in their IDE

---

## One More Thing: requirements.txt Strategy

### Option 1: Minimal (Simple, Fast)
```
librosa
numpy
scipy
scikit-learn
tensorflow
pandas
soundfile
```

**Pros:** Small, simple
**Cons:** Versions might change, inconsistent across team

### Option 2: Pinned Versions (Recommended for Teams)
```
librosa==0.10.0
numpy==1.24.3
scipy==1.11.0
scikit-learn==1.3.0
tensorflow==2.13.0
pandas==2.0.3
soundfile==0.12.1
```

**Pros:** Everyone gets exact same versions, reproducible
**Cons:** Slightly outdated as packages update

### Option 3: Compatible Versions (Flexible)
```
librosa>=0.10.0,<0.11.0
numpy>=1.24.0,<2.0.0
tensorflow>=2.13.0,<2.14.0
```

**Pros:** Balance between reproducibility and flexibility
**Cons:** More complex syntax

**For your 1-week sprint: Use Option 2 (pinned versions).**
Easy, works, team gets same thing.

---

## Summary

| Question | Answer |
|----------|--------|
| One venv or multiple? | **One at repo root** |
| Who activates it? | **Everyone, once** |
| What gets committed? | **requirements.txt, not .venv/** |
| Where do models go? | **Google Drive or GitHub Releases** |
| What if someone adds a package? | **Update requirements.txt, commit, push** |
| How does team stay in sync? | **pip install -r requirements.txt** after pull |

**That's it. One venv, one requirements.txt, one team.**

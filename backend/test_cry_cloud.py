"""
Cloud Cry Classification Tester
Sends processed audio files from your local dataset to the Azure /predict endpoint
and compares predictions against ground-truth labels from splits.csv.

Usage:
    python test_cry_cloud.py               # Test 5 samples per class (20 total)
    python test_cry_cloud.py --count 10    # Test 10 samples per class (40 total)
    python test_cry_cloud.py --all         # Test ALL samples (takes a while)
"""

import requests
import csv
import os
import sys
import time
from collections import defaultdict

# ─── Configuration ───────────────────────────────────────────
AZURE_URL = "http://20.195.40.177:8000/predict"
DATASET_DIR = "../ml_model/cry_classification/data/processed"
SPLITS_CSV = os.path.join(DATASET_DIR, "splits.csv")
SAMPLES_PER_CLASS = 5  # default samples per class

# ─── Parse Args ──────────────────────────────────────────────
test_all = "--all" in sys.argv
for i, arg in enumerate(sys.argv):
    if arg == "--count" and i + 1 < len(sys.argv):
        SAMPLES_PER_CLASS = int(sys.argv[i + 1])

# ─── Load Ground Truth Labels ───────────────────────────────
print(f"Loading labels from {SPLITS_CSV}...")
samples_by_class = defaultdict(list)

with open(SPLITS_CSV, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        label = row["label"]
        filepath = os.path.join(DATASET_DIR, os.path.basename(row["filepath"]))
        if os.path.exists(filepath):
            samples_by_class[label].append(filepath)

print(f"Found classes: {dict({k: len(v) for k, v in samples_by_class.items()})}")

# ─── Select Samples ─────────────────────────────────────────
test_samples = []
for label, files in sorted(samples_by_class.items()):
    selected = files if test_all else files[:SAMPLES_PER_CLASS]
    for f in selected:
        test_samples.append((f, label))

print(f"\nTesting {len(test_samples)} samples against {AZURE_URL}\n")
print("=" * 70)

# ─── Run Tests ───────────────────────────────────────────────
results = {"correct": 0, "wrong": 0, "error": 0, "non_cry": 0}
class_results = defaultdict(lambda: {"correct": 0, "total": 0})
confusion = defaultdict(lambda: defaultdict(int))

for i, (filepath, true_label) in enumerate(test_samples):
    filename = os.path.basename(filepath)
    
    # Read PCM data (skip 44-byte WAV header)
    with open(filepath, "rb") as f:
        f.read(44)
        pcm_data = f.read()

    try:
        start = time.time()
        res = requests.post(AZURE_URL, data=pcm_data, 
                          headers={"Content-Type": "application/octet-stream"},
                          timeout=30)
        elapsed = time.time() - start
        
        if res.status_code != 200:
            print(f"  [{i+1:3d}] {filename:30s} | TRUE: {true_label:10s} | ERROR: HTTP {res.status_code}")
            results["error"] += 1
            continue

        data = res.json()
        
        # Check if cry was detected
        if data.get("cry_detected") == False:
            print(f"  [{i+1:3d}] {filename:30s} | TRUE: {true_label:10s} | NON-CRY (det_conf={data.get('confidence', '?')})")
            results["non_cry"] += 1
            class_results[true_label]["total"] += 1
            continue
        
        pred_label = data.get("data", {}).get("cry_label", data.get("cry_label", "?"))
        confidence = data.get("data", {}).get("confidence", data.get("confidence", 0))
        
        is_correct = pred_label == true_label
        status = "✅" if is_correct else "❌"
        
        print(f"  [{i+1:3d}] {filename:30s} | TRUE: {true_label:10s} | PRED: {pred_label:10s} | CONF: {confidence:.2f} | {elapsed:.1f}s {status}")
        
        if is_correct:
            results["correct"] += 1
        else:
            results["wrong"] += 1
            
        class_results[true_label]["total"] += 1
        class_results[pred_label if is_correct else true_label]["total"] += 0  # ensure key exists
        if is_correct:
            class_results[true_label]["correct"] += 1
            
        confusion[true_label][pred_label] += 1

    except requests.exceptions.Timeout:
        print(f"  [{i+1:3d}] {filename:30s} | TRUE: {true_label:10s} | TIMEOUT")
        results["error"] += 1
    except Exception as e:
        print(f"  [{i+1:3d}] {filename:30s} | TRUE: {true_label:10s} | ERROR: {e}")
        results["error"] += 1

# ─── Print Summary ───────────────────────────────────────────
print("\n" + "=" * 70)
print("CLOUD INFERENCE RESULTS")
print("=" * 70)

total_classified = results["correct"] + results["wrong"]
accuracy = (results["correct"] / total_classified * 100) if total_classified > 0 else 0

print(f"  Correct:      {results['correct']}")
print(f"  Wrong:        {results['wrong']}")
print(f"  Non-cry:      {results['non_cry']}  (detection gate filtered)")
print(f"  Errors:       {results['error']}")
print(f"  ACCURACY:     {accuracy:.1f}%  ({results['correct']}/{total_classified})")

print("\nPer-Class Accuracy:")
for label in sorted(class_results.keys()):
    c = class_results[label]
    acc = (c["correct"] / c["total"] * 100) if c["total"] > 0 else 0
    print(f"  {label:12s}  {c['correct']:3d}/{c['total']:3d}  ({acc:.0f}%)")

if confusion:
    print("\nConfusion Matrix (rows=true, cols=predicted):")
    all_labels = sorted(set(list(confusion.keys()) + [l for d in confusion.values() for l in d.keys()]))
    header = f"  {'':12s} " + " ".join(f"{l:>10s}" for l in all_labels)
    print(header)
    for true in all_labels:
        row = f"  {true:12s} " + " ".join(f"{confusion[true].get(pred, 0):10d}" for pred in all_labels)
        print(row)

print("\nDone!")

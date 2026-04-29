# Cry Classification

CNN + MultiHeadAttention classifier that predicts the reason behind an
infant cry from a 3-second audio clip.

## Classes (5)

After harmonizing the two source datasets and dropping behaviorally
ambiguous / extremely small classes:

| Label        | DonateACry sources | baby-crying sources |
| ------------ | ------------------ | ------------------- |
| `hungry`     | `hungry`           | `hungry`            |
| `tired`      | `tired`            | `sleepy`            |
| `discomfort` | `discomfort`       | `uncomfortable`     |
| `diaper`     |  -                 | `diaper`            |
| `hug`        |  -                 | `hug`               |

Dropped: `awake` (behaviorally ambiguous), `burping` and `belly_pain`
(too few samples to learn reliably even after augmentation).

## Pipeline

```
data/raw/
   v
dataset.py           ->  data/processed/<label>/*.wav   +  data/processed/splits.csv (80/10/10 stratified)
   v
augment.py           ->  4x expansion of TRAIN split only (time-stretch / pitch-shift / both)
   v
features.py          ->  features/X_{train,val,test}.npy  (128, 128, 2 float32)
                          features/norm_stats.npz         (per-channel mean/std from train)
   v
train.py             ->  models/best.keras                (best by val_accuracy)
                          logs/<timestamp>/                (TensorBoard)
                          logs/history.json
   v
evaluate.py          ->  logs/test_metrics.json
                          logs/confusion_matrix.png
   v
export.py            ->  models/cry_classification.{keras,h5,tflite}
                          models/cry_classification_int8.tflite
```

## Run order

All commands assume the working directory is `ml_model/cry_classification/`
and the workspace virtualenv (`.venv` at the repo root) is active.

```bash
cd ml_model/cry_classification

python dataset.py     # harmonize labels, resample/trim to data/processed, write splits.csv
python augment.py     # default fixed mode: 4x expand train split (idempotent)
# optional for imbalance:
# python augment.py --mode balanced              # upsample each class to max original class count
# python augment.py --mode balanced --target-count 600
python features.py    # build feature caches under features/

python train.py --epochs 60 --batch-size 32     # train, save models/best.keras
python evaluate.py                              # classification report + confusion matrix
python export.py                                # .keras / .h5 / .tflite / int8 .tflite
```

## Model

```
Input (128, 128, 2)
 -> Conv2D(32) + BN + ReLU + MaxPool
 -> Conv2D(64) + BN + ReLU + MaxPool
 -> Conv2D(128) + BN + ReLU + MaxPool
 -> Reshape to (256, 128) sequence
 -> MultiHeadAttention(heads=4, key_dim=32)
 -> GlobalAveragePooling1D
 -> Dense(128) + Dropout(0.3)
 -> Dense(5, softmax)
```

Loss `sparse_categorical_crossentropy`, optimizer `Adam(lr=1e-3)`,
`ReduceLROnPlateau(factor=0.5, patience=3)`,
`EarlyStopping(patience=8, restore_best_weights=True)`, balanced class
weights computed from the train labels.

## Features

Each WAV is converted into a `(128, 128, 2)` float32 tensor:

- **Channel 0** - mel spectrogram (128 mel bins, n_fft=2048, hop=375),
  converted to dB via `librosa.power_to_db`, resized to 128x128.
- **Channel 1** - 40 MFCC + delta + delta2 stacked vertically (120 rows),
  resized to 128x128.

Both channels are z-score normalized using per-channel mean/std computed
on the train split only. Stats are saved to `features/norm_stats.npz` so
inference paths can apply the same normalization.

## Notes

- `data/`, `features/`, `models/` and `logs/` are gitignored.
- `baby-crying/test/` clips are unlabeled (`test_*.wav`) and are not used;
  the test set comes from the stratified 80/10/10 split.
- The pipeline is reproducible: every random seed defaults to 42.
- `dataset.py` rewrites `data/processed/splits.csv` from originals only. If you
  run it again, rerun `augment.py` afterward.

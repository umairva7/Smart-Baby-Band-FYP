
# Cry Classification Pipeline

This folder implements the end-to-end cry classification plan: dataset prep, augmentation, feature extraction, model training, evaluation, and export.

## Data Layout

Place raw datasets under:

- data/raw/donate_a_cry/
- data/raw/baby_crying/
- data/raw/esc50/ (optional, for background noise)

## Run Order

Run each stage from this folder so local imports resolve:

1. Prepare data
	- python dataset.py
2. Offline augmentation
	- python augment.py
3. Feature extraction
	- python features.py
4. Train model
	- python train.py
5. Evaluate
	- python evaluate.py
	- python evaluate.py --skip-cross-dataset
6. Export artifacts
	- python export.py

Each script supports --help for optional arguments.

## Outputs

- data/processed/ cleaned WAV files
- data/augmented/ augmented WAV files
- data/splits.csv train/val/test metadata
- features/{train,val,test}/ .npy feature tensors
- models/best_model.h5 trained checkpoint
- models/model.h5 exported model
- models/label_map.json class labels
- models/feature_config.json feature parameters
- logs/ training and evaluation metrics

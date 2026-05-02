import os
import json
import shutil

MODELS_DIR = "models/"
LABEL_MAP = {
    0: "hungry", 
    1: "tired", 
    2: "discomfort",
    3: "belly_pain", 
    4: "diaper", 
    5: "burping"
}

def main():
    if not os.path.exists(MODELS_DIR):
        print(f"Error: {MODELS_DIR} not found.")
        return
        
    best_model_path = os.path.join(MODELS_DIR, "best_model.h5")
    export_model_path = os.path.join(MODELS_DIR, "model.h5")
    
    if os.path.exists(best_model_path):
        shutil.copy(best_model_path, export_model_path)
        print(f"Exported model to {export_model_path}")
    else:
        print(f"Warning: {best_model_path} not found. Ensure train.py has completed.")
        
    label_map_path = os.path.join(MODELS_DIR, "label_map.json")
    with open(label_map_path, "w") as f:
        json.dump(LABEL_MAP, f, indent=4)
    print(f"Saved label map to {label_map_path}")
    
    config_path = os.path.join(MODELS_DIR, "feature_config.json")
    if os.path.exists(config_path):
        print(f"Feature config already exists at {config_path}")
    else:
        print(f"Warning: {config_path} not found. Ensure features.py has completed.")
        
    print("Export process complete. Artifacts are ready in the models/ directory.")

if __name__ == "__main__":
    main()

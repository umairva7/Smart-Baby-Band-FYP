"""
🍼 Smart Baby Band - Hardware & ML Simulation Suite

This interactive suite acts as your physical Smart Baby Band wearable and ML pipeline.
It generates realistic vitals, environment logs, cry detections, and threshold-based
emergency notifications to Firestore/RTDB, allowing you to fully test the Flutter app
without any hardware!
"""

import sys
import os
import random
import wave
import json
from datetime import datetime, timedelta

# Adjust path so we can import from backend app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import firebase_admin
from firebase_admin import credentials, firestore, db

# --- Config ---
SERVICE_ACCOUNT_PATH = "firebase-service-account.json"
RTDB_URL = "https://smart-baby-band-default-rtdb.firebaseio.com"
TEST_AUDIO_DIR = "../ml_model/cry_classification/data/raw/baby-crying/test"

# --- Colors for Terminal ---
CLR_HEADER = '\033[95m'
CLR_BLUE = '\033[94m'
CLR_GREEN = '\033[92m'
CLR_WARNING = '\033[93m'
CLR_FAIL = '\033[91m'
CLR_END = '\033[0m'
CLR_BOLD = '\033[1m'

def print_banner():
    print(f"{CLR_HEADER}{CLR_BOLD}")
    print(" 🍼  SMART BABY BAND - HARDWARE & ML PIPELINE SIMULATOR  🍼 ")
    print("=" * 60)
    print(f"{CLR_END}")
    print("Welcome! Use this tool to test cry classification and trigger alerts.")
    print("Make sure your Flutter app is running on your device or emulator.")
    print("-" * 60)

def init_firebase():
    """Initializes Firebase Admin SDK."""
    if not firebase_admin._apps:
        print(f"🔄 Connecting to Firebase using {SERVICE_ACCOUNT_PATH}...")
        try:
            cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
            firebase_admin.initialize_app(cred, {
                'databaseURL': RTDB_URL
            })
            print(f"{CLR_GREEN}✅ Successfully connected to Firebase!{CLR_END}\n")
        except Exception as e:
            print(f"{CLR_FAIL}❌ Failed to connect to Firebase: {e}{CLR_END}")
            print("Please ensure your firebase-service-account.json is in this folder.")
            sys.exit(1)

def get_linked_user_and_baby():
    """Finds the link between user and baby_profiles."""
    db_fs = firestore.client()
    profiles = db_fs.collection("baby_profiles").limit(1).get()
    
    if not profiles:
        print(f"{CLR_WARNING}⚠️ No baby profiles found in Firestore!{CLR_END}")
        print("Please register a baby profile in the app first.")
        return None, None
        
    profile = profiles[0].to_dict()
    device_id = profile.get("device_id", "babyband_01")
    user_id = profile.get("user_id", "")
    baby_name = profile.get("name", "Baby")
    
    print(f"👶 Mapped Baby Profile: {CLR_BOLD}{baby_name}{CLR_END} (Device ID: {device_id})")
    print(f"👤 Linked Parent UID: {user_id}\n")
    return user_id, device_id

def simulate_cry_event(user_id, device_id):
    """Simulates the Cry Detection and Classification ML pipeline."""
    db_fs = firestore.client()
    
    print(f"\n{CLR_BLUE}=== ML Cry Classification Simulator ==={CLR_END}")
    print("Select a cry reason to classify:")
    print("1) Hungry Cry")
    print("2) Tired Cry (Sleepy)")
    print("3) Discomfort Cry")
    print("4) Diaper Change needed")
    print("5) High Pain Cry (Will trigger critical notification!)")
    
    choice = input("Select option (1-5): ").strip()
    
    cry_types = {
        "1": ("hungry", 0.94, "Hunger"),
        "2": ("tired", 0.88, "Tiredness"),
        "3": ("discomfort", 0.82, "Discomfort"),
        "4": ("diaper", 0.91, "Wet Diaper"),
        "5": ("pain", 0.97, "Severe Pain")
    }
    
    if choice not in cry_types:
        print(f"{CLR_FAIL}Invalid choice. Cancelled.{CLR_END}")
        return
        
    cry_label, confidence, displayName = cry_types[choice]
    now = datetime.now(timezone_aware_utc())
    
    # 1. Update Firebase RTDB (Live Cry classification)
    print("⚡ Pushing live cry detection to Realtime Database...")
    rtdb_ref = db.reference("cry_classifications")
    rtdb_ref.push({
        "timestamp": now.isoformat(),
        "device_id": device_id,
        "cry_label": cry_label,
        "confidence": confidence,
        "cry_detected": True
    })
    
    # 2. Add to Firestore Cry Events collection
    print("💾 Saving Cry Event to Firestore History...")
    db_fs.collection("cry_events").add({
        "baby_id": device_id,
        "cry_type": cry_label,
        "confidence": confidence,
        "timestamp": now
    })
    
    # 3. Trigger heads-up notification in real-time
    if cry_label == "pain":
        print("🚨 Critical Pain Cry detected! Triggering notification...")
        db_fs.collection("notifications").add({
            "user_id": user_id,
            "baby_id": device_id,
            "type": "critical",
            "title": "🚨 Sudden Pain Cry Detected",
            "message": f"Your baby is crying intensely (Severe Pain, confidence {confidence*100:.0f}%). Please check immediately!",
            "is_read": False,
            "created_at": now
        })
    else:
        db_fs.collection("notifications").add({
            "user_id": user_id,
            "baby_id": device_id,
            "type": "warning",
            "title": "🍼 Cry Detected",
            "message": f"Cry reason classified as: {displayName} ({confidence*100:.0f}% confidence)",
            "is_read": False,
            "created_at": now
        })
        
    print(f"{CLR_GREEN}🎉 Success! Cry simulated. Look at your Mobile App's Dashboard & Alerts screen!{CLR_END}\n")

def simulate_realtime_vitals(user_id, device_id):
    """Simulates real-time sensor telemetry and evaluates alerts against parent thresholds."""
    db_fs = firestore.client()
    
    print(f"\n{CLR_BLUE}=== Vitals & Environmental Telemetry Simulator ==={CLR_END}")
    print("Choose vitals status:")
    print("1) Safe & Healthy (HR: 120 BPM, Temp: 36.5°C)")
    print("2) High Heart Rate Alert (HR: 185 BPM - Danger!)")
    print("3) High Temperature Alert (Temp: 39.1°C - Fever warning!)")
    
    choice = input("Select option (1-3): ").strip()
    
    # Load parent settings to read their dynamic alert thresholds
    print("🔍 Reading customized parent alert thresholds from Firestore...")
    user_doc = db_fs.collection("users").document(user_id).get()
    settings = {}
    if user_doc.exists:
        settings = user_doc.to_dict().get("settings", {})
        
    hr_thresh = settings.get("hr_alert_threshold", 150)
    temp_thresh = settings.get("temp_alert_threshold", 37.5)
    
    print(f"   ↳ Custom Heart Rate Threshold: {hr_thresh} BPM")
    print(f"   ↳ Custom Temperature Threshold: {temp_thresh}°C")
    
    if choice == "1":
        bpm = 120
        temp = 36.5
        humidity = 55.0
    elif choice == "2":
        bpm = 185
        temp = 36.7
        humidity = 52.0
    elif choice == "3":
        bpm = 128
        temp = 39.1
        humidity = 48.0
    else:
        print(f"{CLR_FAIL}Invalid choice. Cancelled.{CLR_END}")
        return
        
    now = datetime.now(timezone_aware_utc())
    
    # 1. Pushing Vitals to Firestore
    print("💾 Pushing sensor telemetry to Firestore...")
    db_fs.collection("sensor_data").add({
        "device_id": device_id,
        "heart_rate": bpm,
        "timestamp": now
    })
    
    db_fs.collection("environment_logs").add({
        "device_id": device_id,
        "temperature": temp,
        "humidity": humidity,
        "overall": "danger" if (bpm > hr_thresh or temp > temp_thresh) else "normal",
        "timestamp": now
    })
    
    # 2. Check and trigger Notifications
    if bpm > hr_thresh:
        print(f"🚨 Heart Rate {bpm} BPM exceeds threshold of {hr_thresh}! Pushing alert...")
        db_fs.collection("notifications").add({
            "user_id": user_id,
            "baby_id": device_id,
            "type": "critical",
            "title": "⚠️ High Heart Rate Alert",
            "message": f"Heart rate reached {bpm} BPM, which is above your safe limit of {hr_thresh} BPM.",
            "is_read": False,
            "created_at": now
        })
        
    if temp > temp_thresh:
        print(f"🌡️ Temperature {temp}°C exceeds threshold of {temp_thresh}! Pushing alert...")
        db_fs.collection("notifications").add({
            "user_id": user_id,
            "baby_id": device_id,
            "type": "warning",
            "title": "🌡️ High Temperature Alert",
            "message": f"Baby's temperature is {temp}°C, exceeding your configured threshold of {temp_thresh}°C.",
            "is_read": False,
            "created_at": now
        })
        
    print(f"{CLR_GREEN}🎉 Success! Vitals telemetry pushed. Check your App's Dashboard, Charts & Alerts!{CLR_END}\n")

def generate_24h_history(user_id, device_id):
    """Generates 24-hours of realistic, fluctuating history records for premium chart views."""
    db_fs = firestore.client()
    
    print(f"\n{CLR_BLUE}=== 24-Hour Premium Trend Data Generator ==={CLR_END}")
    print("This will populate 24 hours of chronologically historical data.")
    print("This is perfect to show off the gorgeous time-based history area charts!")
    confirm = input("Generate 24h history? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled.")
        return
        
    print("🧹 Cleaning up old historical data for a clean slate...")
    batch = db_fs.batch()
    old_sensors = db_fs.collection("sensor_data").where("device_id", "==", device_id).get()
    for doc in old_sensors:
        batch.delete(doc.reference)
    old_env = db_fs.collection("environment_logs").where("device_id", "==", device_id).get()
    for doc in old_env:
        batch.delete(doc.reference)
    batch.commit()
    
    print("✍️ Generating 144 fluctuating data points for the past 24 hours...")
    
    batch = db_fs.batch()
    now = datetime.now(timezone_aware_utc())
    
    base_hr = 120
    base_temp = 36.6
    
    for i in range(144):
        time_offset = timedelta(minutes=10 * (144 - i))
        entry_time = now - time_offset
        
        hr_variation = random.choice([-5, -3, -1, 0, 1, 3, 5, 8])
        temp_variation = random.choice([-0.2, -0.1, 0.0, 0.1, 0.2, 0.3])
        
        bpm = base_hr + hr_variation
        temp = base_temp + temp_variation
        humidity = 52.0 + random.uniform(-3, 3)
        
        sensor_ref = db_fs.collection("sensor_data").document()
        batch.set(sensor_ref, {
            "device_id": device_id,
            "heart_rate": bpm,
            "timestamp": entry_time
        })
        
        env_ref = db_fs.collection("environment_logs").document()
        batch.set(env_ref, {
            "device_id": device_id,
            "temperature": round(temp, 2),
            "humidity": round(humidity, 1),
            "overall": "normal",
            "timestamp": entry_time
        })
        
        if (i + 1) % 20 == 0:
            batch.commit()
            batch = db_fs.batch()
            
    batch.commit()
    print(f"{CLR_GREEN}✅ Success! 144 data points populated. Reopen the History page in the app to view the gorgeous area trend charts!{CLR_END}\n")

def test_real_wav_dataset(user_id, device_id):
    """Loads a real WAV file from your dataset, processes it, and tests the backend pipeline."""
    print(f"\n{CLR_BLUE}=== Real WAV Audio Pipeline Tester ==={CLR_END}")
    
    # 1. Find WAV files
    wav_files = []
    if os.path.exists(TEST_AUDIO_DIR):
        wav_files = [f for f in os.listdir(TEST_AUDIO_DIR) if f.endswith('.wav')]
        
    if not wav_files:
        print(f"{CLR_WARNING}⚠️ No WAV files found in dataset path: {TEST_AUDIO_DIR}{CLR_END}")
        print("Checking alternative folders in the workspace...")
        # Walk and search
        for root, dirs, files in os.walk("../ml_model"):
            for f in files:
                if f.endswith('.wav') and len(wav_files) < 10:
                    wav_files.append(os.path.join(root, f))
                    
    if not wav_files:
        print(f"{CLR_FAIL}❌ Could not locate any .wav audio files in dataset folders!{CLR_END}")
        return

    # Select samples to show
    selected_samples = wav_files[:5]
    print("Located test WAV files. Choose a file to test the ML pipeline:")
    for idx, f in enumerate(selected_samples):
        print(f"{idx + 1}) {os.path.basename(f)}")
    print(f"6) [Random selection]")

    choice = input("Select option (1-6): ").strip()
    if choice == "6":
        selected_file_name = random.choice(wav_files)
    else:
        try:
            val = int(choice) - 1
            if 0 <= val < len(selected_samples):
                selected_file_name = selected_samples[val]
            else:
                print(f"{CLR_FAIL}Invalid choice. Cancelled.{CLR_END}")
                return
        except ValueError:
            print(f"{CLR_FAIL}Invalid choice. Cancelled.{CLR_END}")
            return

    file_path = os.path.join(TEST_AUDIO_DIR, selected_file_name) if not os.path.isabs(selected_file_name) else selected_file_name
    print(f"📖 Loaded Audio file: {CLR_BOLD}{os.path.basename(file_path)}{CLR_END}")

    # 2. Extract PCM bytes: 3 seconds at 16kHz = 48000 samples × 2 bytes/sample = 96000 bytes
    print("🎚️ Reading WAV file and parsing into 16-bit PCM bytes (16kHz)...")
    try:
        with wave.open(file_path, 'rb') as w:
            params = w.getparams()
            n_frames = w.getnframes()
            raw_frames = w.readframes(n_frames)
            
            # Slice or pad to exactly 96000 bytes (3 seconds)
            if len(raw_frames) >= 96000:
                pcm_bytes = raw_frames[:96000]
            else:
                pcm_bytes = raw_frames + b'\x00' * (96000 - len(raw_frames))
    except Exception as e:
        print(f"{CLR_FAIL}❌ Failed to read WAV file: {e}{CLR_END}")
        return

    print(f"🔋 PCM Bytes generated: {len(pcm_bytes)} bytes successfully parsed.")
    print("How would you like to run this prediction?")
    print("1) Send HTTP POST to FastAPI server (running at http://127.0.0.1:8000/predict)")
    print("2) Execute Keras/TFLite models directly in this script (in-process)")
    
    run_choice = input("Select option (1-2): ").strip()

    if run_choice == "1":
        # Make HTTP POST request to local server
        import urllib.request
        import urllib.error
        
        print("🔌 Sending audio payload to http://127.0.0.1:8000/predict...")
        req = urllib.request.Request(
            url="http://127.0.0.1:8000/predict",
            data=pcm_bytes,
            headers={"Content-Type": "application/octet-stream"}
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                print(f"{CLR_GREEN}✅ Success! FastAPI response received:{CLR_END}")
                print(json.dumps(res_data, indent=2))
        except urllib.error.URLError as ue:
            print(f"{CLR_FAIL}❌ Connection Failed: Is your uvicorn server running? (Exception: {ue}){CLR_END}")
            print("To run the server, type in a terminal:")
            print("  uvicorn app.main:app --reload")
            print("Falling back to direct ML Pipeline execution inside this script...\n")
            _execute_direct_ml(pcm_bytes, user_id, device_id)
    else:
        _execute_direct_ml(pcm_bytes, user_id, device_id)

def _execute_direct_ml(pcm_bytes, user_id, device_id):
    """Runs the real ML models directly in the script process."""
    print("🧠 Loading models directly inside this process...")
    try:
        from app.services.cry_service import CryService
        from app.routes.cry_events import cry_detector
    except ImportError as ie:
        print(f"{CLR_FAIL}❌ Cannot run in-process: Could not import backend services ({ie}){CLR_END}")
        return

    # 1. Run Cry Detection
    print("📡 Passing audio to Cry Detection Gate (Binary Classification)...")
    try:
        is_cry, confidence = cry_detector.is_cry(pcm_bytes)
        print(f"   ↳ Detection Result: is_cry={is_cry}, confidence={confidence:.4f}")
    except Exception as e:
        print(f"{CLR_FAIL}❌ Cry Detector failure: {e}{CLR_END}")
        return

    if not is_cry:
        print(f"{CLR_WARNING}⚠️ Ambient Noise / Non-Cry Detected. Skipping diaper/hunger classification.{CLR_END}")
        return

    # 2. Run Cry Classification
    print("🩺 Cry Detected! Passing audio to CNN-LSTM Cry Classification Pipeline...")
    service = CryService()
    try:
        result = service.db.collection("baby_profiles").limit(1).get() # Verify firebase client
        res = sys.modules.get('tensorflow')
        if not res:
            import tensorflow as tf
        
        # Call predict_audio
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run predict_audio to compute Mel spectrograms, predict CNN-LSTM, and write to RTDB/Firestore
        print("⚙️ Running MFCC feature extraction and Keras model inference...")
        pred_res = loop.run_until_complete(service.predict_audio(pcm_bytes, device_id=device_id))
        
        print(f"{CLR_GREEN}✅ Success! Pipeline computed successfully!{CLR_END}")
        print(json.dumps(pred_res, indent=2))
        
        # Fetch displayName and label
        label = pred_res.get("cry_label", "hungry")
        conf = pred_res.get("confidence", 0.90)
        display_names = {"hungry": "Hunger", "tired": "Tiredness", "discomfort": "Discomfort", "diaper": "Wet Diaper"}
        displayName = display_names.get(label, label.capitalize())

        # Trigger notification
        now = datetime.now(timezone_aware_utc())
        db_fs = firestore.client()
        db_fs.collection("notifications").add({
            "user_id": user_id,
            "baby_id": device_id,
            "type": "warning",
            "title": "🍼 Cry Detected via ML Model",
            "message": f"Real WAV classification: {displayName} ({conf*100:.0f}% confidence)",
            "is_read": False,
            "created_at": now
        })
        print(f"{CLR_GREEN}🎉 ML Result Pushed to Firebase! Watch the app light up in real-time!{CLR_END}\n")
    except Exception as e:
        print(f"{CLR_FAIL}❌ Pipeline Execution failed: {e}{CLR_END}")

def timezone_aware_utc():
    try:
        from datetime import UTC
        return UTC
    except ImportError:
        # Fallback for Python < 3.11
        from datetime import timezone
        return timezone.utc

def main():
    print_banner()
    init_firebase()
    user_id, device_id = get_linked_user_and_baby()
    
    if not user_id or not device_id:
        return
        
    while True:
        print("✨ MAIN MENU - SELECT SIMULATION ACTION ✨")
        print("=" * 55)
        print("1) Simulate Cry ML Inference (Quick Trigger)")
        print("2) Simulate Vitals Telemetry (Heart Rate & Temp)")
        print("3) Populate 24-Hour Vitals History Charts (Premium Graph)")
        print("4) Test ML Pipeline with Real WAV Audio Dataset (Advanced)")
        print("5) Exit")
        print("=" * 55)
        
        choice = input("Enter choice (1-5): ").strip()
        
        if choice == "1":
            simulate_cry_event(user_id, device_id)
        elif choice == "2":
            simulate_realtime_vitals(user_id, device_id)
        elif choice == "3":
            generate_24h_history(user_id, device_id)
        elif choice == "4":
            test_real_wav_dataset(user_id, device_id)
        elif choice == "5":
            print("\n👋 Happy testing! See you soon!")
            break
        else:
            print(f"{CLR_FAIL}Invalid choice. Try again.{CLR_END}\n")

if __name__ == "__main__":
    main()

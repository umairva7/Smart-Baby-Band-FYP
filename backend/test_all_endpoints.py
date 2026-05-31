import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing /api/health ...")
    try:
        res = requests.get(f"{BASE_URL}/api/health")
        print(f"[{res.status_code}] {res.json()}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 40)

def test_sleep():
    print("Testing POST /api/sleep/ ...")
    payload = {
        "device_id": "babyband_01",
        "timestamp": int(time.time() * 1000),
        "heart": {"bpm": 120.5, "varianceBpm": 5.2, "fingerDetected": True, "valid": True},
        "motion": {"meanMag": 0.05, "varianceMag": 0.002, "spikeCount": 1, "detected": True},
        "environment": {"temperature": 25.0, "humidity": 50.0, "valid": True}
    }
    try:
        res = requests.post(f"{BASE_URL}/api/sleep/", json=payload)
        print(f"[{res.status_code}] {res.text}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 40)

def test_sensor():
    print("Testing POST /api/sensor/ ...")
    payload = {
        "device_id": "babyband_01",
        "timestamp": int(time.time() * 1000),
        "environment": {
            "temperature": 26.5,
            "humidity": 45.2,
            "valid": True
        }
    }
    try:
        res = requests.post(f"{BASE_URL}/api/sensor/", json=payload)
        print(f"[{res.status_code}] {res.text}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 40)

def test_alerts():
    print("Testing GET /api/alerts/?device_id=babyband_01 ...")
    try:
        res = requests.get(f"{BASE_URL}/api/alerts/?device_id=babyband_01")
        print(f"[{res.status_code}] {res.text}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 40)

def test_predict():
    print("Testing POST /predict ...")
    filename = "../ml_model/cry_classification/data/processed/processed_0.wav"
    try:
        with open(filename, "rb") as f:
            f.read(44)  # skip header
            pcm_data = f.read()
        res = requests.post(f"{BASE_URL}/predict", data=pcm_data, headers={"Content-Type": "application/octet-stream"})
        print(f"[{res.status_code}] {res.text[:200]}...")
    except FileNotFoundError:
        print(f"Skipping /predict: Audio file {filename} not found.")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 40)

if __name__ == "__main__":
    print(f"Starting endpoint tests against {BASE_URL}\\n")
    test_health()
    test_sleep()
    test_sensor()
    test_alerts()
    test_predict()
    print("Tests finished.")

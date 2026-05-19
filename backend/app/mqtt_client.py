# ssl import removed
import json
import paho.mqtt.client as mqtt
from firebase_admin import db
import os
from app.config import get_settings

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to Local Mosquitto Broker")
        # Subscribe to the telemetry topic matching the ESP32
        client.subscribe("babyband/01/data")
    else:
        print(f"❌ Failed to connect to MQTT broker, return code {rc}")

def on_message(client, userdata, msg):
    """
    Called when a message is received from AWS IoT Core.
    We parse it and push to Firebase RTDB.
    """
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        
        # We process 10-second telemetry. (Cry events bypass this via HTTP /predict)
        if payload.get("event") == "sensor_status" or "heart" in payload:
            ref = db.reference("sensor_telemetry")
            ref.push(payload)
            print("📡 Forwarded MQTT Telemetry to Firebase RTDB.")
            
            try:
                from firebase_admin import firestore
                from app.routes.sensor_data import classify_environment
                db_fs = firestore.client()
                
                device_id = payload.get("device_id", "babyband_01")
                timestamp = payload.get("timestamp")
                
                env = payload.get("environment", {})
                heart = payload.get("heart", {})
                motion = payload.get("motion", {})
                
                # 1. Environment Logs
                if env.get("valid"):
                    temp = env.get("temperature", 0)
                    hum = env.get("humidity", 0)
                    t_stat, h_stat, overall = classify_environment(temp, hum)
                    env_doc = {
                        "device_id": device_id,
                        "timestamp": timestamp,
                        "temperature": temp,
                        "humidity": hum,
                        "temperature_status": t_stat,
                        "humidity_status": h_stat,
                        "overall": overall
                    }
                    db_fs.collection("environment_logs").add(env_doc)
                
                # 2. Sensor Data History
                baby_docs = db_fs.collection("baby_profiles").where("device_id", "==", device_id).limit(1).stream()
                baby_id = ""
                for doc in baby_docs:
                    baby_id = doc.id
                    
                if baby_id:
                    sensor_doc = {
                        "baby_id": baby_id,
                        "device_id": device_id,
                        "heart_rate": heart.get("bpm"),
                        "variance_bpm": heart.get("varianceBpm"),
                        "temperature": env.get("temperature"),
                        "humidity": env.get("humidity"),
                        "motion": motion, # includes meanMag, varianceMag, spikeCount
                        "timestamp": firestore.SERVER_TIMESTAMP
                    }
                    db_fs.collection("sensor_data").add(sensor_doc)
                    print(f"💾 Saved windowed sensor aggregates to Firestore for baby: {baby_id}")
            except Exception as inner_e:
                print(f"❌ Error saving MQTT data to Firestore: {inner_e}")
            
    except Exception as e:
        print(f"Error processing MQTT message: {e}")

def start_mqtt_client():
    """
    Initializes and starts the MQTT client in a background thread.
    """
    settings = get_settings()
    
    ENDPOINT = "127.0.0.1"
    PORT = 1883
    CLIENT_ID = "fastapi-backend-listener"

    client = mqtt.Client(client_id=CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(ENDPOINT, PORT, 60)
        # loop_start runs a background thread to handle network traffic automatically
        client.loop_start()
        return client
    except Exception as e:
        print(f"❌ Could not connect to Local Mosquitto: {e}")
        return None

def stop_mqtt_client(client):
    if client:
        client.loop_stop()
        client.disconnect()
        print("👋 MQTT Client disconnected")

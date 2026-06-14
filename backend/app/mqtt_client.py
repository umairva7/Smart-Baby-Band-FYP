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
            print(f"\n📊 [MQTT] Received Telemetry:")
            print(json.dumps(payload, indent=2))
            
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
                        "timestamp": firestore.SERVER_TIMESTAMP,
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
                    
                    # 3. Check Alert Thresholds
                    _check_alert_thresholds(db_fs, baby_id, device_id, heart, env)
                    
            except Exception as inner_e:
                print(f"❌ Error saving MQTT data to Firestore: {inner_e}")
            
    except Exception as e:
        print(f"Error processing MQTT message: {e}")

def _check_alert_thresholds(db_fs, baby_id, device_id, heart, env):
    """Check vitals against user-configured thresholds and create Firestore notifications."""
    from datetime import datetime
    try:
        # Find user_id from baby_profiles
        baby_doc = db_fs.collection("baby_profiles").document(baby_id).get()
        if not baby_doc.exists:
            return
        user_id = baby_doc.to_dict().get("user_id", "")
        if not user_id:
            return

        # Read user's alert settings
        user_doc = db_fs.collection("users").document(user_id).get()
        settings = {}
        if user_doc.exists:
            settings = user_doc.to_dict().get("settings", {})
        
        hr_threshold = settings.get("hr_alert_threshold", 150)
        temp_threshold = settings.get("temp_alert_threshold", 37.5)

        bpm = heart.get("bpm", 0)
        temp = env.get("temperature", 0)
        finger = heart.get("fingerDetected", False)
        valid = heart.get("valid", False)
        
        fcm_token = user_doc.to_dict().get("fcm_token") if user_doc.exists else None

        # Helper to send FCM
        def send_fcm(title, body):
            if fcm_token:
                try:
                    from firebase_admin import messaging
                    message = messaging.Message(
                        notification=messaging.Notification(title=title, body=body),
                        token=fcm_token,
                    )
                    messaging.send(message)
                except Exception as e:
                    print(f"⚠️ FCM send failed: {e}")

        # Heart Rate Alert
        if valid and finger and bpm > hr_threshold:
            title = "⚠️ High Heart Rate Alert"
            body = f"Heart rate reached {bpm:.0f} BPM (threshold: {hr_threshold:.0f} BPM)"
            db_fs.collection("notifications").add({
                "user_id": user_id,
                "baby_id": baby_id,
                "type": "critical",
                "title": title,
                "message": body,
                "is_read": False,
                "created_at": datetime.utcnow(),
            })
            send_fcm(title, body)
            print(f"🔔 Heart rate alert: {bpm:.0f} BPM > {hr_threshold:.0f}")

        # Temperature Alert
        if env.get("valid", False) and temp > temp_threshold:
            title = "🌡️ High Temperature Alert"
            body = f"Temperature reached {temp:.1f}°C (threshold: {temp_threshold:.1f}°C)"
            db_fs.collection("notifications").add({
                "user_id": user_id,
                "baby_id": baby_id,
                "type": "warning",
                "title": title,
                "message": body,
                "is_read": False,
                "created_at": datetime.utcnow(),
            })
            send_fcm(title, body)
            print(f"🔔 Temperature alert: {temp:.1f}°C > {temp_threshold:.1f}")

    except Exception as e:
        print(f"⚠️ Error checking alert thresholds: {e}")

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

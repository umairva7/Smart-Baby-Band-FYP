import ssl
import json
import paho.mqtt.client as mqtt
from firebase_admin import db
import os
from app.config import get_settings

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to AWS IoT Core MQTT Broker")
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
        
        # We process 30-second telemetry. (Cry events bypass this via HTTP /predict)
        if payload.get("event") == "sensor_status" or "heart" in payload:
            ref = db.reference("sensor_telemetry")
            ref.push(payload)
            print("📡 Forwarded MQTT Telemetry to Firebase RTDB.")
            
    except Exception as e:
        print(f"Error processing MQTT message: {e}")

def start_mqtt_client():
    """
    Initializes and starts the MQTT client in a background thread.
    """
    settings = get_settings()
    
    # We will assume the certs are moved to backend/certs/
    CERTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../certs"))
    
    CA_PATH = os.path.join(CERTS_DIR, "root-ca.pem.txt")
    CERT_PATH = os.path.join(CERTS_DIR, "737beb19c7bd8c628d88f72ad94750769d419e781adc56352dd0a82c58a1fb6d-certificate.pem.crt")
    KEY_PATH = os.path.join(CERTS_DIR, "737beb19c7bd8c628d88f72ad94750769d419e781adc56352dd0a82c58a1fb6d-private.pem.key")
    
    # Found in Endpoint.txt
    ENDPOINT = "a36ya5skrm71sd-ats.iot.ap-southeast-2.amazonaws.com"
    PORT = 8883
    CLIENT_ID = "fastapi-backend-listener"

    if not all(os.path.exists(p) for p in [CA_PATH, CERT_PATH, KEY_PATH]):
        print("⚠️  MQTT Certificates missing. MQTT listener will not start.")
        print(f"Expected them in: {CERTS_DIR}")
        return None

    client = mqtt.Client(client_id=CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message

    # Configure TLS for AWS IoT Core
    client.tls_set(
        ca_certs=CA_PATH,
        certfile=CERT_PATH,
        keyfile=KEY_PATH,
        cert_reqs=ssl.CERT_REQUIRED,
        tls_version=ssl.PROTOCOL_TLSv1_2,
        ciphers=None
    )

    try:
        client.connect(ENDPOINT, PORT, 60)
        # loop_start runs a background thread to handle network traffic automatically
        client.loop_start()
        return client
    except Exception as e:
        print(f"❌ Could not connect to AWS IoT Core: {e}")
        return None

def stop_mqtt_client(client):
    if client:
        client.loop_stop()
        client.disconnect()
        print("👋 MQTT Client disconnected")

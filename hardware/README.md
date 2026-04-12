# 🍼 Smart Baby Band – Hardware System Documentation

> Embedded IoT Wearable Hardware Design
> Final Year Project – University of Central Punjab (Fall 2025)

---

## 📌 Hardware Overview

The **Smart Baby Band** is a low-power IoT wearable device designed to continuously monitor an infant’s physiological signals and environmental conditions in real time.

The system integrates multiple biomedical sensors with an **ESP32 microcontroller**, enabling:

* Real-time data acquisition
* Edge-level preprocessing
* Secure cloud communication (AWS IoT)
* Intelligent monitoring for cry detection and sleep analysis

---

## 🎯 Hardware Objectives

* Capture baby cry audio using a digital microphone
* Monitor heart rate and pulse signals (real-time + averaged)
* Track motion patterns for sleep detection
* Measure temperature and humidity for comfort monitoring
* Transmit processed data securely to cloud via WiFi (MQTT)
* Maintain low power consumption suitable for wearable usage

---

## 🧩 Hardware Architecture

### 🔹 Core Microcontroller

**ESP32 Development Board**

* Dual-core processor
* Built-in WiFi & BLE
* I2S support for digital audio
* I2C communication for sensors
* Deep sleep & power optimization features

### Responsibilities:

* Sensor data acquisition
* Signal preprocessing (filtering + averaging)
* JSON data formatting
* MQTT communication with AWS IoT
* Power management

---

## 🔧 Sensor Modules

### 🎤 INMP441 – Digital Microphone (I2S)

* Captures baby cry audio
* High-quality digital output via I2S
* Used for MFCC feature extraction
* Input for ML-based cry classification

---

### 💓 MAX30102 – Heart Rate Sensor

* Optical pulse sensor
* Measures heart rate (BPM) and SpO2
* I2C communication
* **Implemented Fix:**

  * Handles zero-reading issue
  * Uses **10-second averaging** for stable output

---

### 💤 MPU6050 – Motion Sensor

* 3-axis accelerometer + gyroscope
* Detects movement, posture, and activity
* Used for sleep stage estimation
* I2C communication

---

### 🌡️ BME280 / DHT11 – Environmental Sensor

* Measures temperature and humidity
* Used for baby comfort monitoring
* **Improvement:**

  * 10-second averaged readings for stability

---

## 🔌 Communication Interfaces

| Interface | Purpose                            |
| --------- | ---------------------------------- |
| I2S       | Digital audio input (INMP441)      |
| I2C       | MAX30102, MPU6050, BME280          |
| WiFi      | Cloud communication (AWS IoT Core) |
| BLE       | Optional mobile pairing            |

---

## ⚡ Power System

* Rechargeable battery-powered wearable
* 3.3V regulated supply
* Optimized for low power consumption

### Power Optimization Techniques

* ESP32 Deep Sleep mode
* Controlled WiFi transmission intervals
* Sensor sampling optimization
* Batch data transmission instead of continuous streaming

---

## 📡 Data Handling Pipeline (Hardware Level)

1. Sensors capture raw signals
2. ESP32 reads data via I2C/I2S
3. Preprocessing applied:

   * Noise filtering
   * Sampling control
   * **10-second averaging (HR, Temp, Humidity)**
4. Data structured into JSON format
5. MQTT publish to AWS IoT Core

---

## 📦 Example JSON Payload

```json
{
  "temperature_avg": 36.5,
  "humidity_avg": 60,
  "heart_rate_avg": 78,
  "motion": "active",
  "cry_detected": true,
  "timestamp": "2026-04-10T12:00:00Z"
}
```

---

## 🔐 Security Implementation

* Secure WiFi communication
* TLS-based MQTT protocol
* AWS IoT certificate-based authentication
* Private key & certificate stored in firmware

---

## 🛠️ Firmware Responsibilities

* Sensor initialization & calibration
* Error handling (sensor failure, reconnection)
* Real-time buffering of sensor data
* Watchdog timer implementation
* Auto-restart on system failure
* Stable data output using averaging techniques

---

## 📊 Engineering Challenges & Solutions

| Challenge             | Solution                                    |
| --------------------- | ------------------------------------------- |
| Noisy cry audio       | Digital filtering + ML preprocessing (MFCC) |
| Heart rate showing 0  | Fixed sensor reading logic + averaging      |
| Sensor instability    | 10-second averaging for reliable output     |
| Multiple I2C devices  | Managed shared bus efficiently              |
| Real-time constraints | Optimized sampling & processing             |
| High power usage      | Deep sleep + controlled transmissions       |

---

## 🚀 Technical Skills Demonstrated

* Embedded C/C++ (ESP32)
* I2C & I2S Protocols
* Sensor Integration & Calibration
* Real-Time Data Processing
* MQTT & AWS IoT Integration
* Low-Power Embedded System Design
* Secure IoT Communication (TLS, Certificates)
* Hardware-Software Co-Design

---

## 🔄 Current Status

✅ Cry detection working
✅ Motion detection working
✅ Sensor integration completed
✅ Cloud communication (MQTT) working
✅ Averaging implemented for stable readings

🔄 In Progress:

* ML model integration for cry classification
* Sleep stage prediction logic
* Mobile app real-time sync optimization

---

## 🏆 Summary

The Smart Baby Band hardware system represents a **production-ready IoT wearable architecture**, combining:

* Biomedical sensing
* Digital audio processing
* Secure cloud connectivity
* Real-time embedded intelligence

This project demonstrates strong capabilities in **embedded systems, IoT, and edge-AI engineering**, making it suitable for real-world healthcare and smart monitoring applications.

---

📜 Academic Project – University of Central Punjab (2025)

---

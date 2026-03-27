# 🍼 Smart Baby Band – Hardware System Documentation

> Embedded IoT Wearable Hardware Design
> Final Year Project – University of Central Punjab (Fall 2025)

---

## 📌 Hardware Overview

The Smart Baby Band hardware system is a low-power IoT wearable device designed to collect physiological and environmental data from infants in real time.

The hardware architecture integrates multiple biomedical and environmental sensors with an ESP32 microcontroller to enable real-time monitoring, edge processing, and secure wireless communication.

---

## 🎯 Hardware Objectives

* Capture baby cry audio using digital microphone
* Monitor heart rate and pulse signals
* Track motion patterns for sleep detection
* Measure temperature and humidity levels
* Transmit processed data securely to cloud via WiFi
* Maintain low power consumption for wearable use

---

## 🧩 Hardware Architecture

### Core Microcontroller

#### ESP32 Development Board

* Dual-core processor
* Built-in WiFi & BLE
* I2S support for digital microphone
* I2C communication for sensors
* Low-power operating modes

The ESP32 acts as the central controller handling:

* Sensor data acquisition
* Signal preprocessing
* MQTT communication
* Power management

---

## 🔧 Sensor Modules

### 🎤 INMP441 – Digital Microphone (I2S)

* Captures baby cry audio
* Connected via I2S interface
* Provides digital audio stream to ESP32
* Used for MFCC feature extraction

### 💓 MAX30102 – Heart Rate Sensor

* Optical pulse oximeter module
* Measures heart rate and blood oxygen levels
* Communicates via I2C
* Used for sleep analysis and health monitoring

### 💤 MPU6050 – Motion Sensor

* 3-axis accelerometer + gyroscope
* Detects body movement and posture changes
* Used for sleep stage estimation
* Communicates via I2C

### 🌡️ BME280 / DHT11 – Environmental Sensor

* Measures temperature
* Measures humidity
* Used for comfort monitoring

---

## 🔌 Communication Interfaces

| Interface | Used For                       |
| --------- | ------------------------------ |
| I2S       | Digital audio (INMP441)        |
| I2C       | MAX30102, MPU6050, BME280      |
| WiFi      | Cloud communication            |
| BLE       | Mobile pairing (optional mode) |

---

## ⚡ Power System

* Rechargeable battery-powered wearable
* Voltage regulation for stable 3.3V operation
* Optimized sleep modes in ESP32
* Low-power sensor polling strategy

Power optimization strategies implemented:

* Deep sleep when idle
* Controlled WiFi transmission intervals
* Efficient sampling rates

---

## 📡 Data Handling Pipeline (Hardware Level)

1. Sensors capture raw signals
2. ESP32 reads sensor data via I2C/I2S
3. Basic preprocessing performed (noise filtering, sampling control)
4. Data formatted into structured JSON packets
5. MQTT publish over WiFi to AWS IoT Core endpoint

---

## 🔐 Security at Hardware Level

* Secure WiFi connection
* TLS-based MQTT communication
* AWS IoT certificate-based device authentication
* Secure key storage within device firmware

---

## 🛠️ Firmware Responsibilities

* Sensor initialization & calibration
* Error handling & reconnection logic
* Real-time data buffering
* Watchdog timer integration
* Fault tolerance & auto-restart handling

---

## 📊 Engineering Challenges Solved

* Handling noisy audio input from infant environment
* Managing multiple I2C devices on shared bus
* Synchronizing I2S audio with sensor readings
* Reducing latency in MQTT transmission
* Maintaining battery efficiency in wearable form

---

## 🚀 Technical Skills Demonstrated

* Embedded C/C++ Programming (ESP32)
* I2C & I2S Protocol Implementation
* Sensor Fusion Techniques
* Real-Time Data Processing
* MQTT Protocol Integration
* Low-Power IoT Design
* Secure IoT Device Authentication
* Hardware-Software System Integration

---

## 🏆 Summary

The Smart Baby Band hardware system demonstrates a production-level embedded IoT architecture integrating biomedical sensors, digital audio processing, and secure wireless communication.

It reflects strong expertise in embedded systems engineering, IoT device design, and real-time hardware integration suitable for IoT, embedded, and edge-AI engineering roles.

---

📜 Academic Project – University of Central Punjab (2025)

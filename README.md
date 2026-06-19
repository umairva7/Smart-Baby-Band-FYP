# 🍼 Smart Baby Band – Cry & Sleep Monitoring System

> AI-Powered IoT Wearable for Infant Cry Classification & Sleep Tracking
> Final Year Project – University of Central Punjab (Fall 2025)

---

## 🎯 Project Status

| Component | Status |
|-----------|--------|
| Hardware (ESP32-S3 + Sensors) | ✅ Complete |
| Mosquitto MQTT Pipeline | ✅ Complete |
| FastAPI Backend | ✅ Complete |
| Firebase (Firestore + FCM) | ✅ Complete |
| Binary Cry Model (Stage 1) | ✅ Complete |
| Cry Classification Model (Stage 2) | ✅ Complete |
| Sleep Tracking Logic | ✅ Complete |
| Flutter Mobile App | ✅ Complete |
| 3D Printed Enclosure | 🔄 In Progress |

---

## 📌 Project Overview

The **Smart Baby Band** is an AI-enabled IoT wearable device designed to monitor infant health and behavior in real time. The system integrates embedded hardware, cloud computing, machine learning, and a mobile application into one complete end-to-end solution.

The objective is to assist parents in understanding baby needs through intelligent cry detection, sleep tracking, and environmental monitoring.

### Core Capabilities

* 🎤 AI-Based Cry Classification (Hungry, Tired, Discomfort, Diaper)
* 💤 Sleep Stage Detection (Awake, Light, Deep)
* 💓 Heart Rate Monitoring (MAX30102)
* 🌡️ Temperature & Humidity Monitoring (BME280 / DHT11)
* 📡 Real-Time Cloud Communication (MQTT / Firebase)
* 📱 Mobile Dashboard with Alerts & Reports (Flutter)

---

## 🏗️ System Architecture

### End-to-End Data Flow

1. Sensors collect physiological and environmental data.
2. ESP32 processes signals and formats data packets. It runs a local Voice Activity Detection (VAD) gate to filter out silence.
3. Data is transmitted securely via **MQTT** over WiFi to a local **Mosquitto Broker** hosted on an Azure VM.
4. Raw audio (when VAD triggers) is sent via HTTP POST to the FastAPI backend `/predict` endpoint.
5. **FastAPI backend** (Azure VM) bridges sensor data to Firebase Firestore/RTDB for storage. It runs sliding-window statistical analysis for sleep and executes a two-stage ML pipeline (Binary Cry Detection + CNN-LSTM 4-Class Classification) for audio.
6. **Mobile application** streams insights via Firestore/RTDB and receives real-time FCM Push Notifications for alerts.

This architecture ensures low latency, secure communication, and scalability, utilizing a split edge-cloud compute model.

---

## 🔧 Hardware Stack

| Component      | Purpose                                  |
| -------------- | ---------------------------------------- |
| ESP32-S3       | Main microcontroller with WiFi           |
| INMP441        | Digital microphone (I2S) for cry capture |
| MPU6050        | Motion tracking for sleep detection      |
| MAX30102       | Heart rate & pulse monitoring            |
| BME280         | Temperature & humidity monitoring        |
| Battery Module | Portable wearable power system           |

### Embedded System Responsibilities

* Sensor data acquisition
* Signal preprocessing and local VAD (Energy + ZCR + Peak)
* MQTT publishing
* HTTP Raw PCM Upload
* Local ring-buffering & fault handling

---

## 🧠 Artificial Intelligence & Machine Learning

### 🎤 Cry Classification (Two-Stage Pipeline)

1. **Stage 1 (Binary Detection):** A lightweight cloud model filters out non-cry audio triggers from the hardware.
2. **Stage 2 (Classification):** A CNN-LSTM deep learning model categorizes the cry.
   - Audio is converted into a 128x128x1 Mel Spectrogram.
   - Classification categories: **Hungry, Tired, Discomfort, Diaper**.
   - Model optimized with Categorical Focal Loss to handle dataset imbalance.

### 💤 Sleep Stage Detection

* Motion analysis using MPU6050
* Heart rate variability analysis
* Sleep state estimation: Awake, Light Sleep, Deep Sleep

### ML Technology Stack

* **Python** (TensorFlow / Keras / Librosa)
* **TensorFlow** (Model deployment in FastAPI)

---

## ☁️ Cloud Infrastructure

### Communication Protocol

* MQTT over WiFi (ESP32 to Azure Mosquitto Broker)
* HTTP POST for audio uploads
* REST APIs & Real-time Listeners (FastAPI & Flutter to Firebase)

### Cloud Platforms & Backend Setup

* **Azure VM (Ubuntu)**: Hosts the Mosquitto MQTT broker and FastAPI backend.
* **Firebase (Firestore + RTDB + FCM)**: Real-time database for streams, and Cloud Messaging for emergency push notifications.
* **FastAPI (Python)**: Core backend server handling MQTT ingestion, sliding-window telemetry buffers, ML inference, safety classification, and alerting.

---

## 📱 Mobile Application (Flutter)

### Key Features

* Live sensor readings via Firebase Real-Time Database (RTDB) and Firestore streams.
* Real-time FCM Push Notifications for cry detection and environment danger.
* Dynamic Sleep tracking and Environment dashboards using `StreamBuilder`.
* Secure authentication system with dynamic `device_id` resolution for multi-user mapping.

The mobile application acts as the primary user interface for parents.

---

## 👨‍💻 Team Members & Roles

* **Umair Imran** → AI/ML Engineer
* **Arslan Shafique** → Hardware Developer
* **Uzair Ghaffar** → Mobile App Developer

---

## 📂 Repository Structure

```text
Smart-Baby-Band-FYP/
├── app/               # Flutter mobile app
├── backend/           # FastAPI backend (Python + Firebase + Azure VM)
├── docs/              # Reports, diagrams, presentations
├── hardware/          # Hardware code (ESP32-S3 + sensors)
├── ml_model/          # Cry detection & classification models (datasets, training)
├── .gitignore         # Root git ignore patterns
└── requirements.txt   # Python dependencies
```

---

## 📜 License

Academic Research Project – University of Central Punjab (2025)

For demonstration and educational purposes.

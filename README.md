# 🍼 Smart Baby Band – Cry & Sleep Monitoring System

> AI-Powered IoT Wearable for Infant Cry Classification & Sleep Tracking
> Final Year Project – University of Central Punjab (Fall 2025)

---

## 📌 Project Overview

The **Smart Baby Band** is an AI-enabled IoT wearable device designed to monitor infant health and behavior in real time. The system integrates embedded hardware, cloud computing, machine learning, and a mobile application into one complete end-to-end solution.

The objective is to assist parents in understanding baby needs through intelligent cry detection, sleep tracking, and environmental monitoring.

### Core Capabilities

* 🎤 AI-Based Cry Classification
* 💤 Sleep Stage Detection
* 💓 Heart Rate Monitoring
* 🌡️ Temperature & Humidity Monitoring
* 📡 Real-Time Cloud Communication
* 📱 Mobile Dashboard with Alerts & Reports

---

## 🏗️ System Architecture

### End-to-End Data Flow

1. Sensors collect physiological and environmental data.
2. ESP32 processes signals and formats data packets.
3. Data is transmitted securely via MQTT over WiFi.
4. Cloud services (AWS IoT / Firebase) receive and store data.
5. AI models classify cry type and estimate sleep stage.
6. Mobile application displays insights, alerts, and reports.

This architecture ensures low latency, secure communication, and scalability.

---

## 👥 Team & Roles

### 🔹 Arslan Shafique – Hardware & IoT Lead

* Sensor integration (INMP441, MPU6050, MAX30102, BME280/DHT11)
* ESP32 firmware development
* BLE & WiFi communication setup
* MQTT publish/subscribe implementation
* AWS IoT / Firebase cloud integration
* Secure device authentication & TLS configuration
* Edge & cloud AI model deployment

### 🔹 Muhammad Uzair – Mobile App Developer

* Flutter-based mobile application
* Real-time dashboard development
* BLE integration
* Notifications & reporting features

### 🔹 Umair Imran – Backend Integration Lead

* API development
* Cloud data routing
* AI inference endpoints
* Secure backend services

---

## 🔧 Hardware Stack

| Component      | Purpose                                  |
| -------------- | ---------------------------------------- |
| ESP32          | Main microcontroller with WiFi & BLE     |
| INMP441        | Digital microphone (I2S) for cry capture |
| MPU6050        | Motion tracking for sleep detection      |
| MAX30102       | Heart rate & pulse monitoring            |
| BME280 / DHT11 | Temperature & humidity monitoring        |
| Battery Module | Portable wearable power system           |

### Embedded System Responsibilities

* Sensor data acquisition
* Signal preprocessing
* Secure MQTT publishing
* Local buffering & fault handling
* Power optimization for wearable usage

---

## 🧠 Artificial Intelligence & Machine Learning

### 🎤 Cry Classification

* Audio preprocessing using MFCC (Mel-Frequency Cepstral Coefficients)
* Neural network model trained on labeled cry dataset
* Classification categories:

  * Hunger
  * Pain
  * Discomfort
  * Normal

### 💤 Sleep Stage Detection

* Motion analysis using MPU6050
* Heart rate variability analysis
* Sleep state estimation:

  * Awake
  * Light Sleep
  * Deep Sleep

### ML Technology Stack

* Python
* TensorFlow / PyTorch
* Librosa (Audio Feature Extraction)
* Scikit-learn

---

## ☁️ Cloud Infrastructure

### Communication Protocol

* MQTT (Publish/Subscribe Model)
* Secure TLS-based communication

### Cloud Platforms

* AWS IoT Core
* Firebase Realtime Database

### Cloud Capabilities

* Real-time device data ingestion
* Secure device authentication (certificates)
* Data storage & analytics
* Alert triggering system
* Weekly health reports generation

---

## 📱 Mobile Application (Flutter)

### Key Features

* Live sensor readings
* Cry type notifications
* Sleep tracking graphs
* Temperature alerts
* Weekly health summaries
* Secure authentication system

The mobile application acts as the primary user interface for parents.

---

## 🔐 Security Implementation

* MQTT over TLS encryption
* AWS IoT certificate-based device authentication
* Secure REST APIs
* Encrypted mobile login
* Role-based access control

---

## 📊 Key Features Summary

✔ Real-time cry classification
✔ AI-powered sleep prediction
✔ Environmental comfort monitoring
✔ Mobile push notifications
✔ Cloud-based analytics dashboard
✔ Cost-effective IoT architecture

---

## 📂 Repository Structure

```
/hardware
   ├── esp32_firmware
   ├── sensor_drivers

/cloud
   ├── mqtt_config
   ├── aws_iot
   ├── firebase_config

/ai
   ├── cry_classification_model
   ├── sleep_detection_model

/mobile_app
   ├── flutter_app

/docs
   ├── architecture_diagrams
   ├── proposal
   ├── final_presentation
```

---

## 🚀 Technical Skills Demonstrated

* Embedded Systems Engineering (ESP32)
* IoT Architecture Design
* MQTT Protocol Implementation
* Cloud Computing (AWS IoT / Firebase)
* AI Model Development & Deployment
* Edge Processing
* Real-Time Data Streaming
* Sensor Fusion Techniques
* Secure Communication Architecture
* Cross-Platform Mobile Development (Flutter)

---

## 🎯 Project Impact

The Smart Baby Band improves upon existing baby monitoring solutions by combining:

* Real-time AI classification
* Multi-sensor health monitoring
* Integrated cloud analytics
* Affordable and scalable hardware design

It demonstrates the ability to design and deploy a full-stack IoT + AI system from hardware to cloud to user interface.

---

## 🏆 Recruiter Summary

This project showcases:

* Complete IoT product development lifecycle
* Hardware + AI + Cloud integration
* Production-level architecture thinking
* Secure real-time data engineering
* Strong cross-team collaboration

It reflects practical industry-ready skills in IoT, AI systems, and cloud integration.

---

## 📜 License

Academic Research Project – University of Central Punjab (2025)

For demonstration and educational purposes.

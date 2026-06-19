# 📱 Smart Baby Band – Mobile Application

> Cross-platform mobile dashboard for the Smart Baby Band IoT system, built with Flutter.

---

## 📌 Overview

The mobile application acts as the primary user interface for parents, providing real-time insights into their baby's health and environment.

It connects directly to **Firebase (Firestore & RTDB)** to fetch real-time sensor updates and interfaces with our **FastAPI Backend (Azure VM)** for complex aggregate analytics and Machine Learning-based cry classification results.

## ✨ Key Features

* **Real-Time Dashboard**: See live heart rate, temperature, humidity, and sleep status.
* **Cry History & Alerts**: View history of detected cries classified by the ML model (Hungry, Tired, Discomfort, Diaper).
* **Sleep Tracking**: Track baby's sleep patterns (Deep, Light, Awake) with graphical history.
* **Environment Monitoring**: Check room temperature and humidity with instant alerts for anomalies.
* **Push Notifications**: Receive immediate FCM alerts for high heart rate, abnormal temperature, or crying events.
* **Authentication**: Secure login via Firebase Auth.

## 🛠️ Technology Stack

* **Framework**: Flutter (Dart)
* **Real-time Database**: Firebase Firestore & Firebase Realtime Database
* **Authentication**: Firebase Authentication
* **Backend API**: FastAPI (Python) for ML predictions and hardware MQTT data ingestion

## 🚀 Getting Started

Ensure you have [Flutter](https://docs.flutter.dev/get-started/install) installed on your system.

```bash
# Get dependencies
flutter pub get

# Run the app
flutter run
```

## 📂 Architecture Note

The app uses an **API-First** and **Real-time Listener** approach:

* **Direct from Firebase**: Sensor data, baby profiles, and settings are streamed directly from Firestore and RTDB using real-time listeners.
* **via FastAPI**: The ESP32 hardware publishes MQTT data and audio to the Python backend on Azure. The backend processes this data, runs the Two-Stage ML models, and pushes the results to Firebase, which instantly syncs to the Flutter app.

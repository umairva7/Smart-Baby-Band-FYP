# 🍼 Smart Baby Band — Backend API

> FastAPI + Firebase backend for the Smart Baby Band IoT wearable.

---

## 🏗️ Architecture

```
ESP32 → MQTT → Mosquitto Broker (Azure VM) → FastAPI (Azure VM) → Firestore ← Flutter (real-time)
```

| Component | Role |
|-----------|------|
| **FastAPI** | ML inference, MQTT ingestion, reports, complex queries |
| **Firebase Auth** | User authentication (login/register from Flutter) |
| **Firestore / RTDB** | Real-time database for all sensor/event data |
| **Mosquitto** | MQTT broker running locally on the Azure VM for ESP32 communication |
| **Azure VM** | Ubuntu Server hosting the complete backend infrastructure |

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- Firebase project with Firestore enabled
- Firebase service account key (JSON)

### 2. Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Place your Firebase service account key
# Download from: Firebase Console → Project Settings → Service Accounts
# Save as: backend/firebase_key.json
```

### 3. Run the Server

```bash
# From the backend/ directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. View API Documentation

Open in browser: **http://localhost:8000/docs** (Swagger UI)

---

## 📂 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── mqtt_client.py       # Paho MQTT subscriber & Firestore writer
│   ├── firebase_client.py   # Firebase Admin SDK setup
│   ├── routes/              # API endpoint definitions
│   ├── services/            # Business logic (Cry & Sleep Services)
│   └── utils/               # Helper functions
├── ml_models/               # Trained .keras models for inference
├── tests/                   # Test scripts
├── .env                     # Environment config
├── firebase_key.json        # Firebase Admin credentials
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/api/health` | Health check + Firebase status |
| `POST`| `/predict` | Raw PCM audio upload for Two-Stage ML cry classification |
| `GET` | `/api/auth/profile` | Get user profile |
| `PUT` | `/api/auth/settings` | Update user settings |
| `GET/POST` | `/api/baby/profile` | Baby profile CRUD |
| `GET` | `/api/sensor/latest/{baby_id}` | Latest sensor reading |
| `GET` | `/api/sensor/history/{baby_id}` | Sensor history |
| `GET` | `/api/cry/history/{baby_id}` | Cry event history |
| `GET` | `/api/sleep/history/{baby_id}` | Sleep session history |
| `GET` | `/api/notifications/` | User notifications |
| `GET` | `/api/reports/dashboard/{baby_id}` | Dashboard summary |

---

## 🔒 Authentication

Most endpoints require a Firebase Auth ID token:

```
Authorization: Bearer <firebase_id_token>
```

The Flutter app gets this token from Firebase Auth after login.

---

## 👨‍💻 Team

- **Umair Imran** — AI/ML Engineer & Backend Developer
- **Arslan Shafique** — Hardware Developer (ESP32 + Sensors)
- **Uzair Ghaffar** — Mobile App Developer (Flutter)

# 👶 Smart Baby Band FYP  

Final Year Project – **Smart Baby Band for Infants**  
This project aims to design and develop a wearable smart band for infants that helps parents monitor their baby’s health and well-being in real-time. The system uses **sensors, AI-based cry recognition, and a mobile app** to provide instant alerts and insights.  

---

## 📌 Project Overview
The Smart Baby Band will:  
- Monitor **vital signs** (temperature, heartbeat, motion).  
- Detect and classify **infant cries** (hunger, pain, discomfort, etc.) using ML.  
- Send **real-time notifications** to parents via a mobile app.  
- Store and display historical data for better monitoring.  

---

## 👨‍👩‍👦 Team Members & Roles
- **Umair Imran** → AI/ML Engineer   
- **Arslan Shafique** → Hardware Developer  
- **Uzair Ghaffar** → Mobile App Developer 

---

## 🛠️ Tech Stack
### Hardware  
- ESP32 Microcontroller  
- Temperature Sensor (DHT11/DS18B20)  
- Heartbeat/SpO2 Sensor (MAX30102)  
- Accelerometer (MPU6050)  

### Software & ML  
- **Python** (TensorFlow / PyTorch for model training)  
- **TensorFlow Lite / ONNX** (model deployment on mobile)  

### Mobile App  
- **Flutter** (cross-platform app)  
- **Firebase** (authentication + notifications)  

### Backend & Database  
- **Node.js + Express.js** (REST API)  
- **MongoDB Atlas** (cloud database)  

---

## 📂 Repository Structure
```bash
Smart-Baby-Band-FYP/
│── README.md
│── docs/              # Reports, diagrams, presentations
│
├── hardware/          # Hardware code (ESP32 + sensors)
├── ml_model/          # Cry detection model (datasets, training, inference)
├── app/               # Flutter mobile app
└── backend/           # Node.js backend (API + MongoDB)

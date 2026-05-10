# Smart Baby Band — Hardware System Documentation

> Embedded IoT Wearable — ESP32-S3 Firmware & Sensor Integration  
> Final Year Project — University of Central Punjab (Fall 2025)  
> Group ID: F25CS085 | Advisor: Muhammad Ammar Hassan

---

## Hardware Overview

The Smart Baby Band is a low-power IoT wearable device that continuously monitors an infant's physiological signals and environmental conditions in real time. The system integrates multiple biomedical sensors with an ESP32-S3 microcontroller, enabling real-time data acquisition, on-device edge AI inference, and secure cloud communication via AWS IoT Core.

The device operates on a split-computing architecture: a lightweight TensorFlow Lite Micro model runs binary cry detection directly on the ESP32-S3, while multi-class cry classification is offloaded to a FastAPI backend on AWS EC2. This design minimizes power consumption and bandwidth usage by transmitting only confirmed cry events rather than continuous audio streams.

---

## Hardware Objectives

- Capture infant cry audio using a digital I2S microphone
- Run on-device binary cry detection using TFLite Micro (V3 model, F1: 0.753)
- Monitor heart rate using optical PPG sensing with 10-second rolling average
- Track motion patterns via accelerometer/gyroscope for sleep session detection
- Measure room temperature and humidity for comfort zone monitoring
- Transmit processed MFCC features and vitals to AWS IoT Core via MQTT over TLS
- Maintain low power consumption suitable for wearable usage through deep sleep and edge-gating

---

## Core Microcontroller

### ESP32-S3

The ESP32-S3 is a hard requirement for this system. Its Xtensa LX7 processor includes vector instructions that accelerate the matrix multiplications in the TFLite Micro convolutional layers. The base ESP32 does not have this capability and cannot run the model within the required latency budget.

**Key specifications used:**

| Feature | Detail |
|---|---|
| Processor | Dual-core Xtensa LX7 @ 240MHz |
| SRAM | 512KB internal |
| PSRAM | 8MB external (tensor arena: 300KB) |
| Wi-Fi | 802.11 b/g/n 2.4GHz |
| Audio interface | I2S (INMP441 microphone) |
| Sensor interface | I2C (MAX30102, MPU6050, BME280) |
| Framework | ESP-IDF 5.x with FreeRTOS |
| Language | C++ |

**Firmware responsibilities:**

- Sensor initialization and calibration on boot
- FreeRTOS task scheduling for concurrent sensor acquisition
- Audio buffering and DSP preprocessing (bandpass filter, pre-emphasis)
- MFCC feature extraction (26 coefficients, ESP32-matched pipeline)
- Z-score normalization using `mfcc_norm_stats.h`
- TFLite Micro inference with 3-window temporal smoothing
- JSON payload packaging and MQTT publish via AWS IoT Core
- Error handling, watchdog timer, auto-restart on failure
- Deep sleep and power management between transmission cycles

---

## Sensor Modules

### INMP441 — Digital Microphone (I2S)

- Captures infant cry audio at 16kHz, 16-bit PCM
- Digital I2S output eliminates analog noise
- Audio pipeline: bandpass filter (300Hz–8kHz) → pre-emphasis (0.97) → 512-sample FFT windows → 26 Mel filter banks → natural log → raw DCT-II → 26 MFCC coefficients
- MFCC pipeline exactly mirrors the ESP32 C++ `computeMFCC()` function to prevent training-inference mismatch (the V1 model failure root cause)
- On-device TFLite Micro model (255.3KB Float32) classifies each window as cry vs. noise
- 3-window temporal smoothing required before triggering MQTT publish (~3.8 seconds of sustained crying)

**Key parameters:**

| Parameter | Value |
|---|---|
| Sample rate | 16kHz |
| MFCC coefficients | 26 |
| FFT size | 512 |
| Frame length | 400 samples (25ms) |
| Hop length | 160 samples (10ms) |
| Frames per inference | 128 (~2 seconds) |
| Detection threshold | 0.40 |
| Energy gate | 0.10 (skip inference if below) |
| Temporal smoothing | 3 consecutive windows |

---

### MAX30102 — Heart Rate Sensor (I2C)

- Optical PPG sensor measuring heart rate (BPM) and SpO2
- I2C address: 0x57
- **Implemented fix:** zero-reading issue resolved via corrected sensor initialization sequence and register configuration
- 10-second rolling average applied before packaging into MQTT payload for stable output
- Output used by FastAPI AlertEngine: BPM > 160 triggers critical alert

---

### MPU6050 — Motion Sensor (I2C)

- 3-axis accelerometer + 3-axis gyroscope
- I2C address: 0x68
- Motion index computed from accelerometer magnitude: `sqrt(ax² + ay² + az²)`
- Moving average filter applied to suppress instantaneous spikes
- Used by FastAPI backend for sleep session detection: sustained low motion index triggers session start, significant motion resumes triggers session end
- Sleep quality labeled as Restful / Disturbed / Insufficient based on session duration and interruption count

---

### BME280 — Environmental Sensor (I2C)

- Measures room temperature (°C) and relative humidity (%)
- I2C address: 0x76
- 10-second rolling average for stable readings
- Used by AlertEngine: room temperature > 28°C and humidity > 70% trigger informational alerts

> **Note:** DHT11 was evaluated as an alternative but BME280 was selected for higher accuracy and I2C compatibility with the shared sensor bus.

---

## Communication Interfaces

| Interface | Sensors / Purpose |
|---|---|
| I2S | INMP441 microphone — digital audio |
| I2C | MAX30102 · MPU6050 · BME280 — shared bus, mutex-protected |
| Wi-Fi (802.11) | AWS IoT Core — MQTT over TLS 8883 |
| BLE | Reserved — not used in current prototype |

**I2C bus management:** Three sensors share the I2C bus. The SensorManager singleton serializes all read requests via a FreeRTOS mutex to prevent bus collisions. Each sensor runs in its own FreeRTOS task at a defined priority level:

| Task | Priority | Interval |
|---|---|---|
| Audio acquisition | Highest | Continuous |
| Heart rate sampling | Medium | 30 seconds |
| Motion sampling | Medium | 30 seconds |
| Environmental sampling | Low | 30 seconds |

---

## MQTT Payload Schema

When a cry is confirmed by temporal smoothing, the firmware packages the following JSON payload and publishes to AWS IoT Core on topic `device/{device_id}/data` with QoS 1:

```json
{
  "meta": {
    "device_id": "esp32_84A2",
    "timestamp": 1715420000
  },
  "triggers": {
    "cry_detected": true,
    "motion_active": false
  },
  "features": {
    "mfcc": [
      -12.45, 8.32, -4.11, 2.05, 0.99,
      -1.23, 0.45, -0.67, 1.12, -0.88,
      0.33, -0.21, 0.05, 1.44, -2.11,
      0.78, -0.34, 1.02, -0.56, 0.23,
      -0.89, 0.67, -0.12, 0.45, -0.78, 0.34
    ],
    "vitals": {
      "bpm": 125,
      "temp_skin": 36.8,
      "env_temp": 24.5,
      "humidity": 58.0
    }
  }
}
```

**Note:** The `mfcc` array contains 26 coefficients (not 13 as in earlier versions). This was corrected in V2 to match the ESP32's `MEL_FILTERS=26` configuration.

Periodic vitals-only payloads (no cry event) omit the `mfcc` array to reduce payload size.

---

## Security Implementation

- Mutual TLS authentication on MQTT connection (port 8883)
- X.509 device certificate provisioned via AWS IoT device registry
- Each device has a unique certificate, private key, and AWS root CA embedded in firmware at flash time
- IoT policy restricts each device to publish only on its own `device/{device_id}/data` topic
- No username/password authentication — certificate-based only

**Files required in firmware:**

- `device_cert.pem` — device certificate
- `private_key.pem` — device private key
- `aws_root_ca.pem` — AWS root certificate authority

---

## TFLite Micro Deployment

| Property | Value |
|---|---|
| Model file | `cnn_model_fixed.tflite` |
| Format | TensorFlow Lite Float32 |
| Size | 255.3KB |
| Tensor arena | 300KB (PSRAM) |
| Input shape | (1, 128, 26, 1) |
| Output shape | (1, 1, 1, 1) — single float probability |
| Supported ops | CONV_2D (×6), MAX_POOL_2D (×3), LOGISTIC (×1) |

Dense layers were converted to equivalent Conv2D operations during export to eliminate `STRIDED_SLICE` and `MEAN` ops unsupported by TFLite Micro on ESP32.

**Files embedded in firmware:**

| File | Purpose |
|---|---|
| `model_data.h` | TFLite model binary (xxd -i cnn_model_fixed.tflite) |
| `mfcc_norm_stats.h` | Z-score normalization — 26 means + 26 stds |

---

## Power System

- Rechargeable LiPo battery — 3.7V nominal
- 3.3V regulated supply via onboard LDO
- Target: low-power wearable with multi-hour operation

**Power optimization techniques:**

| Technique | Implementation |
|---|---|
| Edge-gating | MQTT publish only on confirmed cry — no continuous streaming |
| Energy gate | Skip TFLite inference if audio energy < 0.10 |
| Deep sleep | ESP32 deep sleep between sensor polling intervals |
| Sensor averaging | 10-second rolling average reduces polling frequency |
| Batch transmission | Single JSON payload per event, not per sensor reading |
| Wi-Fi control | Wi-Fi powered down between MQTT publish cycles |

---

## Engineering Challenges and Solutions

| Challenge | Solution |
|---|---|
| TFLite model outputting near-zero on hardware | Rewrote Python MFCC pipeline to exactly match ESP32 C++ math (magnitude spectrum, natural log, raw DCT-II) — resolved V1 numerical mismatch |
| Heart rate showing 0 | Fixed sensor initialization sequence and register config, added 10-second rolling average |
| Three sensors sharing I2C bus | SensorManager singleton with FreeRTOS mutex serializes all bus access |
| Transient false positives in cry detection | 3-window temporal smoothing — alarm only after ~3.8 seconds of sustained detection |
| Model too large for ESP32 SRAM | Tensor arena allocated in 300KB PSRAM — model never loaded into SRAM |
| Dense layer ops unsupported by TFLite Micro | Converted Dense layers to Conv2D equivalents via fix_model.py post-processing |
| Continuous audio streaming too power-hungry | On-device binary detection gates cloud transmission — only confirmed cries trigger MQTT |
| Noisy environmental sensor readings | 10-second rolling average on BME280 and MAX30102 outputs |

---

## Current Status

**Completed:**

- ESP32-S3 firmware — sensor initialization, I2C/I2S drivers, FreeRTOS task structure
- INMP441 audio pipeline — bandpass filter, pre-emphasis, MFCC extraction
- TFLite Micro V3 model — deployed, verified on hardware, F1: 0.753
- Z-score normalization — `mfcc_norm_stats.h` generated and validated
- Temporal smoothing — 3-window voting confirmed functional
- MAX30102 — heart rate fix implemented, 10-second averaging working
- MPU6050 — motion index and moving average working
- BME280 — temperature and humidity with averaging working
- AWS IoT Core — X.509 certificate provisioned, MQTT TLS connection established
- JSON payload packaging — schema validated

**In Progress:**

- Full end-to-end MQTT integration with FastAPI backend
- Hardware-software integration testing with cloud inference pipeline
- Band form factor and wearable enclosure

---

## Model Performance Summary (V3)

| Metric | Single Inference | With 3-Window Smoothing |
|---|---|---|
| Precision | 50.0% | 62.5% |
| Recall | 87.5% | 94.7% |
| F1 Score | 0.636 | 0.753 |
| False positives | 482 | 312 |
| False negatives | 69 | 29 |

Exceeds ICASSP 2022 state-of-the-art benchmark (F1: 0.613) for real-world unconstrained cry detection.

---

## References

1. Espressif Systems. ESP32-S3 Technical Reference Manual v1.1. 2023.
2. Warden, P. and Situnayake, D. TinyML: Machine Learning with TensorFlow Lite. O'Reilly, 2019.
3. Yao, X. et al. "Infant Crying Detection in Real-World Environments." ICASSP 2022.
4. Infineon Technologies. DEEPCRAFT Ready Model for Baby Cry Detection. V2.0, Dec 2025.
5. Google Developers. TensorFlow Lite for Microcontrollers. 2024.
6. OASIS Standard. MQTT Version 3.1.1 Specification. 2014.

---

*Academic Project — University of Central Punjab, Faculty of Information Technology & Computer Science, 2025*

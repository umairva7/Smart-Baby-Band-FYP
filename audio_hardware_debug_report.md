# ESP32 Audio Capture & Buffer Diagnostic Report
**For:** Hardware Engineering Team
**Component:** I2S MEMS Microphone (e.g., INMP441) Audio Pipeline

This report outlines the exact format, units, and expected behavior of the audio data being captured by the ESP32-S3 and printed to the Serial Monitor. This information is critical for diagnosing potential endianness, DC offset, or I2S configuration issues.

---

## 1. Data Format & Specifications

*   **Data Type:** Signed 16-bit integer (`int16_t`).
*   **Buffer Size:** `audioClipBuffer` holds exactly 48,000 samples.
*   **Time Duration:** 3.0 seconds per full capture.
*   **Sampling Rate:** 16,000 Hz (16 kHz).
*   **Endianness:** Little-Endian (ESP32 native architecture).
*   **Units:** Raw PCM (Pulse-Code Modulation) amplitude. These are dimensionless integers representing the instantaneous sound pressure wave (voltage output from the mic).

## 2. Expected Values & Ranges

Because the data is `int16_t`, the absolute physical limits of the values are:
*   **Absolute Maximum:** `+32,767`
*   **Absolute Minimum:** `-32,768`
*   **Silence/Baseline:** `0`

### How to interpret the Serial Monitor output:

#### A. The First 10 Samples Dump
```text
=== START RAW AUDIO DUMP ===
45
52
-12
-30
...
```
*   **Expected in a quiet room:** Values should hover very close to `0` (e.g., between `-100` and `+100`). This represents the inherent electrical noise floor of the microphone.
*   **If you see massive numbers (e.g., `32700`, `-32500`) during silence:** The I2S byte-alignment is wrong, the left/right channel selection is shifted, or the microphone is outputting a massive DC offset. 
*   **If you see exactly `0` repeating forever:** The I2S bus is locked up, the microphone is unplugged, or the clock (BCLK/LRCLK) is not running.

#### B. The Min/Max Stats Dump
```text
[AUDIO DEBUG] Min: -14502, Max: 15320
```
*   **Expected during a Loud Cry:** The difference between Min and Max should be massive. A healthy loud sound should yield a `Max` around `15,000` to `30,000` and a `Min` around `-15,000` to `-30,000`.
*   **Expected during Silence:** The Min and Max should both be very small (e.g., Min: `-200`, Max: `150`).
*   **Warning Sign (Clipping):** If Min is *exactly* `-32768` and Max is *exactly* `32767`, the microphone is clipping. The sound is too loud or the gain is too high, resulting in distorted, squared-off audio that the ML model cannot classify.

## 3. Backend Conversion (Python)
When this raw `int16_t` buffer is received by the cloud backend via HTTP POST, it is parsed and normalized to float32 using this exact math:
```python
# Converts the raw 16-bit integers into floating point numbers between -1.0 and 1.0
audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
```

## 4. Hardware Debugging Checklist
If the backend is rejecting the audio or the ML model is failing, the hardware team should verify:
1.  **I2S Configuration:** Ensure `I2S_COMM_FORMAT_STAND_I2S` is used. If the mic uses MSB (Left-Justified), the bits will be shifted, drastically altering the integer values.
2.  **Channel Selection:** Ensure the microphone's L/R pin is tied securely to GND or VDD, and the ESP32 is reading only from that specific active channel (otherwise it might interleave audio with static/zeros).
3.  **DC Offset:** If the baseline is resting at something like `8000` instead of `0` during silence, a software high-pass filter (DC removal) needs to be added before the HTTP upload.

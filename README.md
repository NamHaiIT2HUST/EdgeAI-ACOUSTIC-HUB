# 🚀 EDGE AI ACOUSTIC HUB
**Hệ thống Giám sát & Cảnh báo Âm thanh thông minh ứng dụng TinyML**

Dự án này tập trung vào việc triển khai một hệ thống IoT Full-stack, sử dụng vi điều khiển **ESP32-S3** để thực hiện phân tích âm thanh tại biên (Edge Computing) và đồng bộ dữ liệu về hệ thống quản lý trung tâm (Local Server).

---

## 📌 Lộ trình thực hiện (Project Roadmap)

Dự án được chia làm 4 giai đoạn thực thi (Phases). Trạng thái hiện tại: **🔴 Phase 1**.

### 🟢 Phase 1: Firmware & Data Acquisition (In Progress)
* **Mục tiêu:** Xây dựng nền tảng phần cứng, đọc dữ liệu ADC và quản lý bộ nhớ.
* **Trọng tâm kỹ thuật:** * Lập trình **ESP-IDF (C/C++)** quản lý thanh ghi ADC.
    * Kỹ thuật **Ring Buffer** & **Pointer Management** để xử lý luồng dữ liệu liên tục.
    * Thu thập Dataset âm thanh thô qua giao thức Serial.

### 🟡 Phase 2: TinyML & AI Inference
* **Mục tiêu:** Huấn luyện và triển khai mô hình AI offline.
* **Trọng tâm kỹ thuật:**
    * Trích xuất đặc trưng phổ âm (MFCC) trên **Edge Impulse**.
    * Nhúng mô hình Neural Network (C++ library) vào ESP32-S3.
    * Thực thi điều khiển Relay dựa trên kết quả suy luận AI với độ trễ < 500ms.

### 🟠 Phase 3: Communication & IoT Infrastructure
* **Mục tiêu:** Thiết lập hạ tầng mạng và giao thức truyền tin.
* **Trọng tâm kỹ thuật:**
    * Triển khai **MQTT Broker (Mosquitto)** trên môi trường **Docker/Linux**.
    * Viết mã nguồn Wi-Fi/MQTT Client cho ESP32-S3 sử dụng JSON payload.

### 🔵 Phase 4: Backend & GUI Dashboard
* **Mục tiêu:** Xây dựng phần mềm quản lý và giám sát.
* **Trọng tâm kỹ thuật:**
    * Phát triển Backend Python tích hợp **SQLAlchemy ORM**.
    * Thiết kế giao diện Desktop bằng **PyQt6** (Event Logging & Remote Override).

---

## 📂 Cấu trúc thư mục (Project Structure)

```text
EdgeAI_Acoustic_Hub/
├── firmware/         # Mã nguồn ESP-IDF (C/C++)
├── server/           # Docker, Python Backend & PyQt GUI
├── ai_model/         # Dataset & Exported AI libraries
├── docs/             # Architecture diagrams & Documentation
└── README.md         # Tài liệu dự án
```

## 🛠 Công nghệ sử dụng (Tech Stack)

**Hardware**: ESP32-S3 (Xtensa® Dual-core 32-bit), KY-038 Sound Sensor, DHT11, Relay 5V.

**Embedded**: ESP-IDF (FreeRTOS), C/C++, ADC/DMA.

**AI/ML**: Edge Impulse, TinyML, Signal Processing (DSP).

**Software**: Python, SQLAlchemy (ORM), PyQt6, MQTT (Mosquitto).

**DevOps**: Linux, Docker & Docker Compose.


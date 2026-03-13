# Phase 3: IoT Infrastructure & Message Brokerage

## 1. Giới thiệu tổng quan

Phase này tập trung vào việc xây dựng "Hệ thần kinh trung tâm" cho dự án. Thay vì kết nối trực tiếp thiết bị đầu cuối (Edge Device) với ứng dụng (Frontend), hệ thống sử dụng kiến trúc Pub/Sub (Publisher/Subscriber) thông qua giao thức MQTT.

## 2. Tại sao lại dùng Docker & Mosquitto?

Thay vì cài đặt phần mềm thủ công, chúng ta sử dụng Containerization (Docker) vì 3 lý do chiến lược:

### Isolation (Cô lập): 

Đảm bảo môi trường chạy Broker không bị xung đột với các phần mềm khác trên máy tính.

### Scalability (Khả năng mở rộng): 

Dễ dàng nâng cấp lên cụm Broker (Cluster) nếu số lượng thiết bị tăng lên hàng ngàn con.

### Portability (Tính di động): C

hỉ cần 1 file cấu hình, hệ thống có thể chạy y hệt trên Windows, Linux, Mac hoặc thậm chí là Cloud (AWS/Azure).

## 3. Phân tích kỹ thuật cấu hình

mosquitto.conf

listener 1883 0.0.0.0: Mở cổng giao tiếp tiêu chuẩn. Việc set 0.0.0.0 cho phép thiết bị từ bên ngoài mạng (Wokwi, ESP32 thật) truy cập vào thay vì chỉ bó hẹp trong localhost.

allow_anonymous true: Tối ưu hóa tốc độ kết nối trong giai đoạn phát triển (Development Phase).

docker-compose.yml

Port Mapping: Map cổng 1883 (MQTT) và 9001 (WebSockets). Việc mở cổng 9001 là bước chuẩn bị cực kỳ quan trọng để Web Dashboard (Phase 4) có thể nhận dữ liệu real-time trực tiếp từ trình duyệt.


# Phase 4:
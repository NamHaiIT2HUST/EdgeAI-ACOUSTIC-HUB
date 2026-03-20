//dùng để mô phỏng lấy lấy dữ liệu và kiểm tra giao thức trên wokwi
#include <WiFi.h>
#include <PubSubClient.h>
#include "DHTesp.h"

// --- CẤU HÌNH CHÂN CẮM ---
const int DHT_PIN = 15;
const int LED_PIN = 2; // Pin 2 kết nối với đèn LED

DHTesp dhtSensor;

// --- CẤU HÌNH WIFI & MQTT ---
const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "broker.emqx.io";

// Topic gửi và nhận
const char* topic_pub = "namhai/iot/data";
const char* topic_sub = "namhai/iot/command";

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastMsg = 0;
bool relayState = false; // Trạng thái mặc định của Đèn (Tắt)

// Hàm kết nối WiFi
void setup_wifi() {
  delay(10);
  Serial.println("\nĐang kết nối WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi connected!");
}

// Hàm nhận lệnh từ Dashboard (BẮT SÓNG)
void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  Serial.print("📥 Nhận lệnh từ Dashboard: ");
  Serial.println(message);

  // Nếu đúng topic và đúng lệnh TOGGLE
  if (String(topic) == topic_sub && message == "TOGGLE") {
    relayState = !relayState; // Đảo trạng thái biến
    digitalWrite(LED_PIN, relayState ? HIGH : LOW); // Bật/Tắt đèn thật
    
    Serial.print("🚨 -> Đã đổi trạng thái LED thành: ");
    Serial.println(relayState ? "ON" : "OFF");
  }
}

// Hàm giữ kết nối MQTT
void reconnect() {
  while (!client.connected()) {
    Serial.print("Đang kết nối MQTT Broker...");
    String clientId = "ESP32-AcousticHub-";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println("✅ OK!");
      // QUAN TRỌNG: Đăng ký nghe lén topic command
      client.subscribe(topic_sub); 
    } else {
      Serial.print("Lỗi, mã = ");
      Serial.print(client.state());
      Serial.println(" Thử lại sau 5 giây...");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  
  // Khởi tạo chân LED và cảm biến
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  dhtSensor.setup(DHT_PIN, DHTesp::DHT22);
  
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback); // Gắn hàm lắng nghe
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop(); // Lệnh này giúp ESP32 liên tục kiểm tra tin nhắn đến

  // Gửi dữ liệu mỗi 2 giây
  unsigned long now = millis();
  if (now - lastMsg > 2000) {
    lastMsg = now;

    // Đọc cảm biến
    TempAndHumidity data = dhtSensor.getTempAndHumidity();
    float temp = data.temperature;
    float humid = data.humidity;
    String relay_str = relayState ? "ON" : "OFF"; // Cập nhật trạng thái đèn hiện tại

    // Tạo chuỗi JSON thủ công
    String payload = "{\"temp\":" + String(temp, 1) + 
                     ",\"humid\":" + String(humid, 1) + 
                     ",\"relay\":\"" + relay_str + "\"}";

    Serial.print("📤 Sent: ");
    Serial.println(payload);
    
    // Bắn lên Broker
    client.publish(topic_pub, payload.c_str());
  }
}
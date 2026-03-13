import paho.mqtt.client as mqtt
import json
from .database import SessionLocal, engine
from .models import Base, Telemetry

#Tự động tạo bảng nếu chưa có
Base.metadata.create_all(bind=engine)

MQTT_BROKER = "broker.emqx.io"
MQTT_TOPIC = "namhai/iot/data"

def on_connect(client, userdata, flags, rc):
    print(f"✅ Connected to Broker (Code {rc})")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    db = SessionLocal()
    try:
        data = json.loads(msg.payload.decode())
        print(f"📥 New Data: {data}")
        
        entry = Telemetry(
            temperature=data.get('temp'),
            humidity=data.get('humid'),
            relay_status=data.get('relay')
        )
        
        db.add(entry)
        db.commit()
        print("💾 Logged to SQLite!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_forever()
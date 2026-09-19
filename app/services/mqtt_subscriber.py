import asyncio
import json
import uuid
import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.cycle_log import IncineratorStatus

BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPIC_PATTERN = "cycleai/incinerator/+/status"


def save_reading(data: dict):
    """Save an incoming MQTT message to PostgreSQL."""
    db: Session = SessionLocal()
    try:
        status = IncineratorStatus(
            id=str(uuid.uuid4()),
            device_id=data.get("device_id", "UNKNOWN"),
            temperature_celsius=data.get("temperature_celsius"),
            is_burning=data.get("is_burning", False),
            fill_percentage=data.get("fill_percentage"),
            usage_count=data.get("usage_count", 0),
            battery_level=data.get("battery_level"),
            is_online=data.get("is_online", True),
        )
        db.add(status)
        db.commit()
    except Exception as e:
        print(f"DB error saving incinerator reading: {e}")
        db.rollback()
    finally:
        db.close()


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        save_reading(data)
        print(f"Saved reading from {data.get('device_id')} | "
              f"Temp: {data.get('temperature_celsius')}°C | "
              f"Burning: {data.get('is_burning')}")
    except Exception as e:
        print(f"Error processing MQTT message: {e}")


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        client.subscribe(TOPIC_PATTERN, qos=1)
        print(f"MQTT subscriber connected and listening on: {TOPIC_PATTERN}")
    else:
        print(f"MQTT connection failed: {rc}")


def start_mqtt_subscriber():
    """
    Starts the MQTT subscriber in a separate thread.
    Called from FastAPI startup event.
    """
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER_HOST, BROKER_PORT, 60)
        client.loop_start()
        print("MQTT subscriber started")
    except Exception as e:
        print(f"MQTT broker not available: {e}. IoT features disabled.")

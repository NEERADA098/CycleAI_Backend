#!/usr/bin/env python3
"""
ESP32 Smart Incinerator Simulator

This script simulates what the ESP32 microcontroller firmware
does in a real deployed smart incinerator. It publishes sensor
readings via MQTT every 10 seconds.

In a real deployment, this Python script is replaced by C++ 
firmware running on an actual ESP32 board with physical sensors:
- DS18B20 temperature sensor
- HX711 load cell (weight/fill sensor)  
- Battery voltage divider circuit

To run: python3 esp32_simulator.py
"""

import paho.mqtt.client as mqtt
import json
import time
import random
import math

BROKER_HOST = "localhost"
BROKER_PORT = 1883
PUBLISH_INTERVAL = 10  # seconds

INCINERATORS = [
    {
        "device_id": "INC001",
        "location": "Kottayam District Hospital",
        "base_temp": 45.0,
    },
    {
        "device_id": "INC002", 
        "location": "Ettumanoor PHC",
        "base_temp": 38.0,
    },
    {
        "device_id": "INC003",
        "location": "Vaikom PHC",
        "base_temp": 22.0,
    },
]

def simulate_reading(device: dict, cycle: int) -> dict:
    """
    Generates realistic sensor readings.
    
    Temperature varies based on whether burning is happening.
    Fill percentage increases slowly over time.
    Battery drains slowly.
    """
    # Simulate burning cycle: burns for 3 minutes every 30 minutes
    burning_phase = (cycle % 18) < 3
    
    if burning_phase:
        temperature = device["base_temp"] + random.uniform(180, 220)
    else:
        temperature = device["base_temp"] + random.uniform(0, 15)
    
    fill = min(100.0, (cycle * 0.5) + random.uniform(0, 2))
    battery = max(20.0, 98.0 - (cycle * 0.1))
    
    return {
        "device_id": device["device_id"],
        "temperature_celsius": round(temperature, 1),
        "is_burning": burning_phase,
        "fill_percentage": round(fill, 1),
        "usage_count": cycle // 18,
        "battery_level": round(battery, 1),
        "is_online": True,
    }

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"Connected to MQTT broker at {BROKER_HOST}:{BROKER_PORT}")
    else:
        print(f"Connection failed with code {rc}")

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    
    for device in INCINERATORS:
        will_topic = f"cycleai/incinerator/{device['device_id']}/status"
        will_payload = json.dumps({
            "device_id": device["device_id"],
            "is_online": False,
            "temperature_celsius": None,
            "is_burning": False,
            "fill_percentage": None,
            "usage_count": 0,
            "battery_level": None,
        })
        client.will_set(will_topic, will_payload, qos=1, retain=True)
    
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    client.loop_start()
    
    cycle = 0
    print(f"Publishing readings every {PUBLISH_INTERVAL}s. Press Ctrl+C to stop.")
    print("-" * 60)
    
    while True:
        for device in INCINERATORS:
            reading = simulate_reading(device, cycle)
            topic = f"cycleai/incinerator/{device['device_id']}/status"
            payload = json.dumps(reading)
            client.publish(topic, payload, qos=1, retain=True)
            
            status = "🔥 BURNING" if reading["is_burning"] else "💤 Idle"
            print(f"{device['device_id']} | {status} | "
                  f"Temp: {reading['temperature_celsius']}°C | "
                  f"Fill: {reading['fill_percentage']}% | "
                  f"Battery: {reading['battery_level']}%")
        
        print("-" * 60)
        cycle += 1
        time.sleep(PUBLISH_INTERVAL)

if __name__ == "__main__":
    main()

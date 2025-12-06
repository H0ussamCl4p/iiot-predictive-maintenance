import paho.mqtt.client as mqtt
import time
import json
import random
import math
import os

BROKER = os.getenv("MQTT_BROKER", "localhost")
TOPIC = "factory/plc/data"
client = mqtt.Client()
client.connect(BROKER, 1883, 60)

print("📉 Simulating GRADUAL WEAR (Drift)... Watch your AI Score drop!")

tick = 0
wear_factor = 0 # Starts at 0, increases slowly

try:
    while True:
        # 1. Base Vibration starts at 10, but increases by 0.2 every second
        wear_factor += 0.2 
        vibration = 10 + wear_factor + random.uniform(-0.5, 0.5)
        
        # Temp also rises slowly
        temp = 45 + (wear_factor * 0.5) + random.uniform(-0.2, 0.2)
        
        payload = {
            "timestamp": time.time(),
            "machine_id": "Press_01",
            "vibration": round(vibration, 2),
            "temperature": round(temp, 2)
        }

        client.publish(TOPIC, json.dumps(payload))
        print(f"Time: {tick}s | Vib: {vibration:.2f} | Temp: {temp:.2f} | Wear Level: {wear_factor:.1f}")
        
        tick += 1
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopped.")

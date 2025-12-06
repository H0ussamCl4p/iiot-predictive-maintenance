import paho.mqtt.client as mqtt
import time
import json
import random
import math

# Configuration
BROKER = "localhost" 
TOPIC = "factory/plc/data"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

try:
    client.connect(BROKER, 1883, 60)
    print(f"✅ Virtual PLC connected to {BROKER}")
except:
    print(f"❌ Could not connect to Mosquitto at {BROKER}. Is it running?")
    exit()

print("   Sending data... Press Ctrl+C to stop.")

tick = 0

try:
    while True:
        # 1. Simulate "Normal" Behavior (Sine wave + small noise)
        # Vibration moves in a wave between 9 and 11
        vibration = 10 + (2 * math.sin(tick * 0.1)) + random.uniform(-0.5, 0.5)
        
        # Temperature moves in a wave between 43 and 47
        temp = 45 + (2 * math.sin(tick * 0.05)) + random.uniform(-0.2, 0.2)
        
        # 2. Randomly inject an ANOMALY (2% chance)
        is_anomaly = False
        if random.random() < 0.5: 
            print("\n⚠️  GENERATING SIMULATED FAILURE! (Bearing seizure)")
            vibration = vibration + random.randint(15, 30) # Massive vibration spike
            temp = temp + random.randint(10, 20)           # Overheating
            is_anomaly = True

        # 3. Create JSON Payload
        # NOTE: Keys must match what main.py expects ('vibration', 'temperature')
        payload = {
            "timestamp": time.time(),
            "machine_id": "Press_01",
            "vibration": round(vibration, 2),
            "temperature": round(temp, 2)
        }

        # 4. Send to MQTT
        client.publish(TOPIC, json.dumps(payload))
        
        # Log to console so you see what's happening
        if is_anomaly:
             print(f"   [SENT] 🔥 ANOMALY: Vib={payload['vibration']} Temp={payload['temperature']}")
        else:
             print(f"   [SENT] Normal:  Vib={payload['vibration']} Temp={payload['temperature']}")

        tick += 1
        time.sleep(0.5) # Send data every 0.5 seconds

except KeyboardInterrupt:
    print("\n🛑 Simulation stopped.")

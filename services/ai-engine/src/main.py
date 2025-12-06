import paho.mqtt.client as mqtt
import joblib
import json
import numpy as np
import os
import pandas as pd # Added for timestamp handling
from influxdb import InfluxDBClient

# --- CONFIGURATION ---
BROKER = os.getenv("MQTT_BROKER", "localhost")
TOPIC = "factory/plc/data"
MODEL_FILE = "model_brain.pkl"
SCALER_FILE = "scaler.pkl"
LOG_FILE = "live_data.csv" # The file where we save history for the dashboard

# InfluxDB Configuration
INFLUX_HOST = os.getenv("INFLUX_HOST", "localhost")
INFLUX_PORT = int(os.getenv("INFLUX_PORT", "8086"))
INFLUX_DB = os.getenv("INFLUX_DB", "factory_data")

# --- INITIALIZATION ---
# 1. Load the AI (if available)
model = None
scaler = None

if os.path.exists(MODEL_FILE) and os.path.exists(SCALER_FILE):
    print("🧠 Loading AI Model...")
    try:
        model = joblib.load(MODEL_FILE)
        scaler = joblib.load(SCALER_FILE)
        print("✅ AI Model loaded successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not load model: {e}")
        model = None
        scaler = None
else:
    print("ℹ️  No AI model found. Data will be collected without predictions.")
    print("   Train a model via the AI Admin dashboard first.")

# 2. Connect to InfluxDB
print("📊 Connecting to InfluxDB...")
try:
    influx_client = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT)
    influx_client.switch_database(INFLUX_DB)
    print(f"✅ Connected to InfluxDB: {INFLUX_DB}")
except Exception as e:
    print(f"⚠️  Warning: Could not connect to InfluxDB: {e}")
    influx_client = None

# 2. Setup the Log File (Create headers if file doesn't exist)
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        f.write("timestamp,vibration,temperature,score,status\n")

print(f"✅ AI Ready. Logging data to {LOG_FILE}...")

# --- CORE LOGIC ---
def on_message(client, userdata, msg):
    try:
        # 1. Parse Data
        payload = json.loads(msg.payload.decode())
        vib = payload['vibration']
        temp = payload['temperature']
        
        # 2. Pre-process and Predict (if model available)
        status = "NORMAL"
        score = 0.0
        
        if model is not None and scaler is not None:
            features = np.array([[vib, temp]])
            features_scaled = scaler.transform(features)
            
            # 3. Predict
            prediction = model.predict(features_scaled)
            score = model.decision_function(features_scaled)[0]
            
            # 4. Determine Status
            if prediction[0] == -1: 
                status = "ANOMALY"
            elif score < 0.10: 
                status = "WARNING"
        
        # 5. Output to Terminal (Color Coded)
        # Green for Normal, Yellow for Warning, Red for Anomaly
        color = "\033[92m" if status == "NORMAL" else "\033[93m" if status == "WARNING" else "\033[91m"
        print(f"{color}[{status}] Vib: {vib:.2f} | Temp: {temp:.2f} | Score: {score:.4f}\033[0m")

        # 6. SAVE TO CSV (Critical for Dashboard)
        # We append the new row to the file
        with open(LOG_FILE, "a") as f:
            timestamp = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"{timestamp},{vib},{temp},{score},{status}\n")
        
        # 7. SAVE TO INFLUXDB (For Grafana)
        if influx_client:
            try:
                json_body = [
                    {
                        "measurement": "machine_telemetry",
                        "tags": {
                            "machine_id": "Press_01",
                            "status": status
                        },
                        "fields": {
                            "vibration": float(vib),
                            "temperature": float(temp),
                            "ai_score": float(score)
                        }
                    }
                ]
                influx_client.write_points(json_body)
            except Exception as influx_error:
                print(f"⚠️  InfluxDB write error: {influx_error}")
            
    except Exception as e:
        print(f"Error processing message: {e}")

# --- MQTT CONNECTION ---
# Using legacy API for paho-mqtt 1.6.1 compatibility
client = mqtt.Client()
client.on_message = on_message

try:
    print(f"🔌 Connecting to MQTT broker: {BROKER}...")
    client.connect(BROKER, 1883, 60)
    client.subscribe(TOPIC)
    print(f"✅ Subscribed to topic: {TOPIC}")
    print("🎧 Listening for sensor data...")
    client.loop_forever()
except ConnectionRefusedError:
    print(f"❌ Error: Could not connect to MQTT broker at {BROKER}")
except Exception as e:
    print(f"❌ MQTT Error: {e}")
except KeyboardInterrupt:
    print("\n🛑 Stopping Detector.")

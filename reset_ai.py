import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# --- SETTINGS ---
DATA_FILE = "data/training_data.csv"
MODEL_FILE = "model_brain.pkl"
SCALER_FILE = "scaler.pkl"

print("🔥 STARTING SYSTEM RESET...")

# 1. CLEANUP (Delete old files)
if os.path.exists(MODEL_FILE): os.remove(MODEL_FILE)
if os.path.exists(SCALER_FILE): os.remove(SCALER_FILE)
if not os.path.exists('data'): os.makedirs('data')

# 2. GENERATE HEALTHY DATA
print("⚙️  Generating healthy data (Golden Batch)...")
points = 3000
# Vibration: Sine wave centered at 10, moves between 8 and 12
vib = 10 + 2 * np.sin(np.linspace(0, 50, points)) + np.random.normal(0, 0.2, points)
# Temperature: Centered at 45
temp = 45 + np.random.normal(0, 0.5, points)

df = pd.DataFrame({"vibration": vib, "temperature": temp})
df.to_csv(DATA_FILE, index=False)
print(f"   - Data saved. Range: Vib [{min(vib):.1f} to {max(vib):.1f}]")

# 3. TRAIN MODEL
print("🧠 Training AI...")
# Load data
X_train = df[['vibration', 'temperature']].values

# SCALE (Crucial!)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)

# TRAIN
# contamination=0.001 -> We are strict! Only 0.1% of training data is noise.
model = IsolationForest(contamination=0.01, random_state=42)
model.fit(X_scaled)

# SAVE
joblib.dump(model, MODEL_FILE)
joblib.dump(scaler, SCALER_FILE)
print("✅ Brain saved.")

# 4. INSTANT VERIFICATION (The Proof)
print("\n--- 🧪 VERIFICATION TEST ---")

def test_value(v, t):
    # Scale input exactly like training
    val_scaled = scaler.transform([[v, t]])
    # Predict
    pred = model.predict(val_scaled)[0]
    score = model.decision_function(val_scaled)[0]
    status = "✅ NORMAL" if pred == 1 else "❌ ANOMALY"
    print(f"Input [Vib:{v}, Temp:{t}] -> Score: {score:.4f} -> {status}")

test_value(10.0, 45.0)  # Should be Normal
test_value(11.5, 46.0)  # Should be Normal
test_value(40.0, 60.0)  # SHOULD BE ANOMALY

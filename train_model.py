import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

# Configuration
INPUT_FILE = "data/training_data.csv"
MODEL_FILE = "model_brain.pkl"
SCALER_FILE = "scaler.pkl"

print("🧠 Loading training data...")
# 1. Load Data
df = pd.read_csv(INPUT_FILE)
print(f"   - Loaded {len(df)} rows.")

# 2. Select Features (The columns the AI should look at)
# We ignore 'timestamp' because time doesn't cause failure, vibration/temp does.
features = ['vibration', 'temperature']
X = df[features].values

# 3. Scale the Data (CRITICAL STEP)
# Vibration is ~10, Temp is ~45. We squash them to the same range so the AI plays fair.
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 4. Train the Model (Isolation Forest)
# contamination=0.01 means "Assume 1% of this training data might be noise/glitches"
print("🏋️  Training Isolation Forest...")
model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
model.fit(X_scaled)

# 5. Save the Brain and the Scaler
# We need BOTH files to run this on another computer.
joblib.dump(model, MODEL_FILE)
joblib.dump(scaler, SCALER_FILE)

print("✅ Training Complete!")
print(f"   - Model saved to: {MODEL_FILE}")
print(f"   - Scaler saved to: {SCALER_FILE}")

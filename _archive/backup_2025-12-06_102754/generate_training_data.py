import pandas as pd
import numpy as np
import os

# Ensure the data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

FILENAME = "data/training_data.csv"
DATA_POINTS = 3000  # 50 minutes of data

print(f"⚙️ Generating {DATA_POINTS} points of HEALTHY data...")

# 1. Simulate Time
timestamps = pd.date_range(start="2025-01-01", periods=DATA_POINTS, freq="S")

# 2. Simulate Healthy Vibration 
# Sine wave around 10 + small random noise
vibration = 10 + 2 * np.sin(np.linspace(0, 50, DATA_POINTS)) + np.random.normal(0, 0.2, DATA_POINTS)

# 3. Simulate Healthy Temperature
# Warms up to 45 degrees and stays there
temperature = 40 + 5 * (1 - np.exp(-np.linspace(0, 5, DATA_POINTS))) + np.random.normal(0, 0.1, DATA_POINTS)
# Adjust to match the Virtual PLC (which hovers around 45-47)
temperature = temperature + 2 

# 4. Save to CSV
df = pd.DataFrame({
    "timestamp": timestamps,
    "vibration": vibration,
    "temperature": temperature
})

df.to_csv(FILENAME, index=False)
print(f"✅ Success! Data saved to '{FILENAME}'.")
print(f"   - Min Vib: {min(vibration):.2f} | Max Vib: {max(vibration):.2f}")

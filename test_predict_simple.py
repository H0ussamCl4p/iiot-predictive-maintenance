import requests
import json

# Simple test of the /predict endpoint
url = "http://localhost:8000/predict"

test_data = {
    "data": {
        "Humidity": 65.0,
        "Temperature": 45.0,
        "Age": 12.0,
        "Quantity": 42000.0
    }
}

print("Testing /predict endpoint...")
print(f"Input: {json.dumps(test_data, indent=2)}\n")

response = requests.post(url, json=test_data)

print(f"Status: {response.status_code}")
print(f"\nResponse:")
print(json.dumps(response.json(), indent=2))

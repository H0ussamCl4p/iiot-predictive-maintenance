"""Test upload to verify the endpoint works"""
import requests
import sys
import os

# Create a test CSV
csv_content = """UID,ProductType,Humidity,Temperature,Age,Quantity,MTTF
1,A,60,25,100,50,1000
2,B,65,28,120,45,950
3,A,58,26,110,52,1020"""

with open("test_data.csv", "w") as f:
    f.write(csv_content)

print("📤 Testing upload to http://localhost:8000/upload-dataset")
print(f"📁 File: test_data.csv ({len(csv_content)} bytes)")

try:
    with open("test_data.csv", "rb") as f:
        files = {"file": ("test_data.csv", f, "text/csv")}
        response = requests.post(
            "http://localhost:8000/upload-dataset",
            files=files,
            timeout=60
        )
        
    print(f"\n✅ Status Code: {response.status_code}")
    print(f"📋 Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n🎉 Success!")
        print(f"   Rows: {result.get('total_rows')}")
        print(f"   Columns: {result.get('numeric_columns')}")
        print(f"   Features: {result.get('feature_count')}")
    else:
        print(f"\n❌ Failed with status {response.status_code}")
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"\n💥 Exception: {e}")
    import traceback
    traceback.print_exc()
finally:
    if os.path.exists("test_data.csv"):
        os.remove("test_data.csv")
        print("\n🗑️  Cleaned up test file")

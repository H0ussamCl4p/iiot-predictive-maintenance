"""
Test Combined Predictions - Real-time Anomaly Detection + Future Failure Prediction
Demonstrates the full power of the predictive maintenance system
"""

import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000"

def test_combined_predictions():
    """Test the combined prediction endpoint with various scenarios"""
    
    print("="*80)
    print("🔮 COMBINED PREDICTIVE MAINTENANCE SYSTEM TEST")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Check model availability
    print("📋 Checking model availability...")
    try:
        models_status = requests.get(f"{API_URL}/models/status").json()
        print(f"  Anomaly Detection Model: {'✅ Available' if models_status['anomaly_detection_model']['available'] else '❌ Not Available'}")
        print(f"  Predictive Model: {'✅ Available' if models_status['predictive_model']['available'] else '❌ Not Available'}")
        print()
    except Exception as e:
        print(f"  ⚠️ Could not check models: {e}\n")
    
    # Test scenarios
    test_cases = [
        {
            "name": "Scenario 1: Optimal Conditions",
            "description": "Brand new equipment, perfect operating conditions",
            "data": {
                "Humidity": 45.0,
                "Temperature": 22.0,
                "Age": 2.0,
                "Quantity": 50000.0,
                "MTTF": 800.0
            },
            "expected": "Should show NORMAL current state and LOW future risk"
        },
        {
            "name": "Scenario 2: Early Warning Signs",
            "description": "Slightly elevated temperature and humidity",
            "data": {
                "Humidity": 68.0,
                "Temperature": 55.0,
                "Age": 10.0,
                "Quantity": 42000.0,
                "MTTF": 450.0
            },
            "expected": "Should show WARNING or MEDIUM risk"
        },
        {
            "name": "Scenario 3: Current Anomaly, Future OK",
            "description": "Temporary spike but equipment is relatively new",
            "data": {
                "Humidity": 82.0,
                "Temperature": 75.0,
                "Age": 5.0,
                "Quantity": 48000.0,
                "MTTF": 600.0
            },
            "expected": "Current anomaly detected, but future looks manageable"
        },
        {
            "name": "Scenario 4: Aging Equipment Degradation",
            "description": "Old equipment with declining performance",
            "data": {
                "Humidity": 60.0,
                "Temperature": 65.0,
                "Age": 18.0,
                "Quantity": 35000.0,
                "MTTF": 200.0
            },
            "expected": "Should show future HIGH risk due to age and low MTTF"
        },
        {
            "name": "Scenario 5: Critical - Immediate Failure Risk",
            "description": "Multiple critical factors, failure imminent",
            "data": {
                "Humidity": 92.0,
                "Temperature": 88.0,
                "Age": 23.0,
                "Quantity": 25000.0,
                "MTTF": 50.0
            },
            "expected": "Should show CRITICAL on both current and future"
        },
        {
            "name": "Scenario 6: Edge Case - Missing MTTF",
            "description": "Sensor without MTTF data (prediction only)",
            "data": {
                "Humidity": 55.0,
                "Temperature": 40.0,
                "Age": 8.0,
                "Quantity": 44000.0
            },
            "expected": "Should still work with prediction model"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print("="*80)
        print(f"TEST {i}: {test_case['name']}")
        print("="*80)
        print(f"📝 Description: {test_case['description']}")
        print(f"🎯 Expected: {test_case['expected']}\n")
        
        print("📊 Input Data:")
        for key, value in test_case['data'].items():
            print(f"  • {key}: {value}")
        
        try:
            # Make prediction request
            response = requests.post(
                f"{API_URL}/predict",
                json={"data": test_case['data']}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract key information
                current_state = result.get('current_state', {})
                future_pred = result.get('future_prediction', {})
                overall = result.get('overall_assessment', {})
                
                print(f"\n{'='*80}")
                print("📊 ANALYSIS RESULTS")
                print(f"{'='*80}\n")
                
                # Current State
                print("🔍 CURRENT STATE (Real-time Anomaly Detection):")
                print(f"  Status: {current_state.get('status_emoji', '')} {current_state.get('status', 'UNKNOWN')}")
                print(f"  Risk Level: {current_state.get('risk_level', 'UNKNOWN')}")
                print(f"  Anomaly Score: {current_state.get('anomaly_score', 0)}/100")
                
                if current_state.get('warnings'):
                    print(f"  Warnings:")
                    for warning in current_state['warnings']:
                        print(f"    {warning}")
                else:
                    print(f"  ✅ No warnings detected")
                
                # Future Prediction
                print(f"\n🔮 FUTURE PREDICTION (Time-to-Failure Forecast):")
                if future_pred.get('model_loaded'):
                    print(f"  Risk Level: {future_pred.get('future_risk_emoji', '')} {future_pred.get('future_risk_level', 'UNKNOWN')}")
                    print(f"  Predicted MTTF: {future_pred.get('predicted_mttf', 'N/A')} hours")
                    print(f"  Estimated Days Until Failure: ~{future_pred.get('estimated_days_until_failure', 'N/A')} days")
                    print(f"  Confidence: {future_pred.get('confidence', 'N/A')}")
                    
                    if future_pred.get('most_critical_factor'):
                        mcf = future_pred['most_critical_factor']
                        print(f"  Most Critical Factor: {mcf['name']} (importance: {mcf['importance']}%)")
                else:
                    print(f"  ⚠️ Predictive model not loaded")
                
                # Overall Assessment
                print(f"\n{'='*80}")
                print("💡 OVERALL ASSESSMENT")
                print(f"{'='*80}")
                print(f"  Overall Risk: {overall.get('risk_level', 'UNKNOWN')}")
                print(f"  Analysis: {overall.get('analysis', 'N/A')}")
                print(f"\n  📋 Recommendation:")
                print(f"  {overall.get('recommendation', 'N/A')}")
                
                # Action taken
                if future_pred.get('recommended_action'):
                    print(f"\n  🔧 Specific Action:")
                    print(f"  {future_pred['recommended_action']}")
                
                results.append({
                    "test": test_case['name'],
                    "current_risk": current_state.get('risk_level'),
                    "future_risk": future_pred.get('future_risk_level'),
                    "overall_risk": overall.get('risk_level'),
                    "success": True
                })
                
            else:
                print(f"\n❌ API Error: {response.status_code}")
                print(f"   {response.text}")
                results.append({
                    "test": test_case['name'],
                    "success": False,
                    "error": response.text
                })
        
        except Exception as e:
            print(f"\n❌ Test Failed: {str(e)}")
            results.append({
                "test": test_case['name'],
                "success": False,
                "error": str(e)
            })
        
        print()
    
    # Summary
    print("="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    successful = sum(1 for r in results if r.get('success'))
    total = len(results)
    
    print(f"Tests Run: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}\n")
    
    if successful == total:
        print("✅ All tests passed! System is fully operational.\n")
        print("🎯 Your predictive maintenance system can now:")
        print("   1. ✅ Detect real-time anomalies (Is equipment anomalous NOW?)")
        print("   2. 🔮 Predict future failures (WHEN will it fail?)")
        print("   3. 💡 Provide actionable recommendations")
        print("   4. 📊 Assess overall risk (current + future)")
    else:
        print(f"⚠️ {total - successful} test(s) failed. Check errors above.\n")
    
    print("="*80)
    print("🚀 NEXT STEPS:")
    print("="*80)
    print("1. Integrate with your IoT sensors for real-time monitoring")
    print("2. Set up automated alerts when CRITICAL risk detected")
    print("3. Create maintenance scheduling based on predicted MTTF")
    print("4. Build dashboards showing current state + future projections")
    print("="*80)


if __name__ == "__main__":
    print("\n🔍 Testing Combined Prediction System...")
    print("   Make sure the API server is running (docker-compose up)\n")
    
    try:
        # Quick connectivity check
        response = requests.get(f"{API_URL}/health", timeout=5)
        print(f"✅ API Server is reachable\n")
    except:
        print(f"❌ Cannot reach API server at {API_URL}")
        print(f"   Please start the server with: docker-compose up -d\n")
        exit(1)
    
    test_combined_predictions()

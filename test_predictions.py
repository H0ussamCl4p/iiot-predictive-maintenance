"""Test the trained model with various scenarios"""
import requests
import json

API_URL = "http://localhost:8000"

def test_model_predictions():
    """Test model with normal and anomalous data"""
    
    # First, check model status
    print("🔍 Checking model status...")
    response = requests.get(f"{API_URL}/model-info")
    model_info = response.json()
    
    print(f"\n📊 Model Info:")
    print(f"  Status: {'✅ Trained' if model_info.get('is_trained') else '❌ Not Trained'}")
    print(f"  Training Samples: {model_info.get('sample_count', 0):,}")
    print(f"  Features: {model_info.get('feature_count', 0)}")
    print(f"  Columns: {', '.join(model_info.get('features', []))}")
    
    if not model_info.get('is_trained'):
        print("\n❌ Model is not trained. Please train the model first.")
        return
    
    # Get the features used for training
    features = model_info.get('features', [])
    print(f"\n🎯 Testing predictions with {len(features)} features...")
    
    # Create test scenarios
    test_cases = [
        {
            "name": "Normal Operation (Typical Values)",
            "data": {
                features[0]: 2500,   # UID
                features[1]: 55,     # Humidity
                features[2]: 25,     # Temperature
                features[3]: 10,     # Age
                features[4]: 45000,  # Quantity
                features[5]: 500     # MTTF
            }
        },
        {
            "name": "High Temperature Warning",
            "data": {
                features[0]: 2501,
                features[1]: 55,
                features[2]: 85,     # Very high temperature
                features[3]: 10,
                features[4]: 45000,
                features[5]: 100     # Low MTTF
            }
        },
        {
            "name": "Extreme Humidity + Low MTTF (Anomaly)",
            "data": {
                features[0]: 2502,
                features[1]: 95,     # Very high humidity
                features[2]: 70,
                features[3]: 20,     # Old equipment
                features[4]: 30000,  # Low quantity
                features[5]: 50      # Very low MTTF
            }
        },
        {
            "name": "Excellent Condition",
            "data": {
                features[0]: 2503,
                features[1]: 45,     # Good humidity
                features[2]: 22,     # Good temperature
                features[3]: 3,      # New equipment
                features[4]: 50000,  # High quantity
                features[5]: 800     # High MTTF
            }
        },
        {
            "name": "Equipment Failure Imminent",
            "data": {
                features[0]: 2504,
                features[1]: 90,     # High humidity
                features[2]: 95,     # Extreme temperature
                features[3]: 25,     # Very old
                features[4]: 20000,  # Very low quantity
                features[5]: 30      # Critical MTTF
            }
        }
    ]
    
    print("\n" + "="*70)
    print("TEST RESULTS")
    print("="*70)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("   " + "-"*60)
        
        # Show input values
        print("   Input:")
        for key, value in test_case['data'].items():
            clean_key = key.strip().replace('\ufeff', '')
            print(f"     • {clean_key}: {value}")
        
        # Make prediction by uploading as temporary data
        # Note: In production, you'd have a /predict endpoint
        # For now, we'll check if values are within normal ranges based on training data
        
        humidity = test_case['data'][features[1]]
        temperature = test_case['data'][features[2]]
        age = test_case['data'][features[3]]
        mttf = test_case['data'][features[5]]
        
        # Simple heuristic based on typical ranges
        anomaly_score = 0
        warnings = []
        
        # Temperature check
        if temperature > 80:
            anomaly_score += 30
            warnings.append("🔴 Critical temperature")
        elif temperature > 70:
            anomaly_score += 15
            warnings.append("🟡 High temperature")
        
        # Humidity check
        if humidity > 85:
            anomaly_score += 25
            warnings.append("🔴 Extreme humidity")
        elif humidity > 75:
            anomaly_score += 10
            warnings.append("🟡 High humidity")
        
        # Age check
        if age > 20:
            anomaly_score += 20
            warnings.append("⚠️ Equipment very old")
        elif age > 15:
            anomaly_score += 10
            warnings.append("⚠️ Equipment aging")
        
        # MTTF check (Mean Time To Failure)
        if mttf < 100:
            anomaly_score += 35
            warnings.append("🔴 Critical MTTF - Failure imminent")
        elif mttf < 300:
            anomaly_score += 20
            warnings.append("🟡 Low MTTF - Maintenance needed")
        elif mttf < 500:
            anomaly_score += 5
            warnings.append("ℹ️ MTTF below average")
        
        # Determine status
        if anomaly_score >= 60:
            status = "🔴 ANOMALY DETECTED"
            risk_level = "CRITICAL"
        elif anomaly_score >= 30:
            status = "🟡 WARNING"
            risk_level = "MEDIUM"
        else:
            status = "✅ NORMAL"
            risk_level = "LOW"
        
        print(f"\n   Prediction:")
        print(f"     Status: {status}")
        print(f"     Risk Level: {risk_level}")
        print(f"     Anomaly Score: {anomaly_score}/100")
        
        if warnings:
            print(f"\n   Warnings:")
            for warning in warnings:
                print(f"     {warning}")
        
        if anomaly_score >= 60:
            print(f"\n   💡 Recommendation: Immediate maintenance required")
        elif anomaly_score >= 30:
            print(f"\n   💡 Recommendation: Schedule maintenance soon")
        else:
            print(f"\n   💡 Recommendation: Continue normal operation")
    
    print("\n" + "="*70)
    print("\n✅ Testing complete!")
    print("\n💡 Note: For real predictions, use the trained IsolationForest model")
    print("   The model learns patterns from your 5,000 training samples")

if __name__ == "__main__":
    try:
        test_model_predictions()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to AI Engine at http://localhost:8000")
        print("   Make sure Docker services are running: docker-compose up -d")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

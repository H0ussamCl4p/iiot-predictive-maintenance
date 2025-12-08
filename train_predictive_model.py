"""
Predictive Maintenance Model - Future Failure Prediction
Combines time-series analysis with anomaly detection to predict future failures
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pickle
import os

def train_predictive_model(data_path: str, model_output_path: str):
    """
    Train a model that predicts future MTTF (Mean Time To Failure)
    Lower predicted MTTF = higher risk of failure soon
    """
    print("🔄 Loading training data...")
    df = pd.read_csv(data_path)
    
    # Features that influence failure (excluding UID and MTTF itself)
    feature_cols = [col for col in df.columns if col not in ['UID', 'MTTF', 'MTTF ']]
    
    # Target: MTTF (time until failure)
    target_col = 'MTTF' if 'MTTF' in df.columns else 'MTTF '
    
    X = df[feature_cols]
    y = df[target_col]
    
    print(f"📊 Training with {len(X)} samples")
    print(f"📈 Features: {', '.join(feature_cols)}")
    print(f"🎯 Target: {target_col} (Mean Time To Failure)")
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train Random Forest Regressor (predicts continuous values)
    print("\n🤖 Training Random Forest Regressor...")
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_scaled, y)
    
    # Feature importance
    feature_importance = sorted(
        zip(feature_cols, model.feature_importances_),
        key=lambda x: x[1],
        reverse=True
    )
    
    print("\n📊 Feature Importance (What drives failures?):")
    for feat, importance in feature_importance:
        print(f"  • {feat}: {importance:.4f}")
    
    # Save model
    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    model_data = {
        'model': model,
        'scaler': scaler,
        'features': feature_cols,
        'target': target_col
    }
    
    with open(model_output_path, 'wb') as f:
        pickle.dump(model_data, f)
    
    print(f"\n✅ Predictive model saved to {model_output_path}")
    
    # Model performance
    train_score = model.score(X_scaled, y)
    print(f"📈 Training R² Score: {train_score:.4f}")
    
    return model_data


def predict_future_failure(input_data: dict, model_path: str):
    """
    Predict when equipment will fail based on current conditions
    Returns: predicted MTTF and risk assessment
    """
    # Load model
    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)
    
    model = model_data['model']
    scaler = model_data['scaler']
    features = model_data['features']
    
    # Prepare input
    input_df = pd.DataFrame([input_data])
    input_df = input_df[features]  # Ensure correct order
    
    # Scale
    input_scaled = scaler.transform(input_df)
    
    # Predict MTTF
    predicted_mttf = model.predict(input_scaled)[0]
    
    # Risk assessment based on predicted MTTF
    if predicted_mttf < 100:
        risk_level = "CRITICAL"
        risk_color = "🔴"
        action = "IMMEDIATE MAINTENANCE REQUIRED"
        days_estimate = predicted_mttf / 24  # Rough conversion to days
    elif predicted_mttf < 300:
        risk_level = "HIGH"
        risk_color = "🟠"
        action = "Schedule maintenance within 1-2 weeks"
        days_estimate = predicted_mttf / 24
    elif predicted_mttf < 500:
        risk_level = "MEDIUM"
        risk_color = "🟡"
        action = "Monitor closely, plan maintenance"
        days_estimate = predicted_mttf / 24
    else:
        risk_level = "LOW"
        risk_color = "🟢"
        action = "Continue normal operation"
        days_estimate = predicted_mttf / 24
    
    return {
        'predicted_mttf': round(predicted_mttf, 2),
        'estimated_days_until_failure': round(days_estimate, 1),
        'risk_level': risk_level,
        'risk_color': risk_color,
        'recommended_action': action,
        'confidence': 'High' if predicted_mttf < 200 or predicted_mttf > 600 else 'Medium'
    }


if __name__ == "__main__":
    import sys
    
    # Paths
    data_path = "services/ai-engine/data/training_data.csv"
    model_path = "services/ai-engine/models/predictive_model.pkl"
    
    if not os.path.exists(data_path):
        print(f"❌ Training data not found at {data_path}")
        print("   Please upload a dataset first using the AI Admin app")
        sys.exit(1)
    
    print("="*70)
    print("🔮 PREDICTIVE MAINTENANCE MODEL - FUTURE FAILURE PREDICTION")
    print("="*70)
    
    # Train model
    model_data = train_predictive_model(data_path, model_path)
    
    print("\n" + "="*70)
    print("🧪 TESTING PREDICTIONS")
    print("="*70)
    
    # Test scenarios
    test_cases = [
        {
            "name": "New Equipment - Optimal Conditions",
            "data": {
                "Humidity": 45,
                "Temperature": 22,
                "Age": 2,
                "Quantity": 50000
            }
        },
        {
            "name": "Aging Equipment - Normal Conditions",
            "data": {
                "Humidity": 55,
                "Temperature": 30,
                "Age": 12,
                "Quantity": 42000
            }
        },
        {
            "name": "High Risk - Multiple Warning Signs",
            "data": {
                "Humidity": 80,
                "Temperature": 70,
                "Age": 18,
                "Quantity": 35000
            }
        },
        {
            "name": "Critical - Failure Imminent",
            "data": {
                "Humidity": 92,
                "Temperature": 88,
                "Age": 23,
                "Quantity": 25000
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("   " + "-"*60)
        
        # Show inputs
        print("   Current Conditions:")
        for key, value in test_case['data'].items():
            print(f"     • {key}: {value}")
        
        # Predict
        prediction = predict_future_failure(test_case['data'], model_path)
        
        print(f"\n   {prediction['risk_color']} Prediction:")
        print(f"     Risk Level: {prediction['risk_level']}")
        print(f"     Predicted MTTF: {prediction['predicted_mttf']} hours")
        print(f"     Est. Days Until Failure: ~{prediction['estimated_days_until_failure']} days")
        print(f"     Confidence: {prediction['confidence']}")
        print(f"\n   💡 Action: {prediction['recommended_action']}")
    
    print("\n" + "="*70)
    print("✅ Predictive model training complete!")
    print(f"📦 Model saved: {model_path}")
    print("\n🎯 This model can now predict FUTURE failures based on current conditions")

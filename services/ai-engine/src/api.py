"""
FastAPI Backend Server for IIoT Predictive Maintenance
Provides REST API endpoints for Next.js frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from influxdb import InfluxDBClient
from typing import List, Dict, Any, Optional
from datetime import datetime
import uvicorn
import os
import json
import pickle

# Configuration
INFLUX_HOST = os.getenv("INFLUX_HOST", "localhost")
INFLUX_PORT = int(os.getenv("INFLUX_PORT", "8086"))
INFLUX_DB = os.getenv("INFLUX_DB", "factory_data")
MEASUREMENT = "machine_telemetry"
MODEL_PATH = "/app/models/anomaly_model.pkl"

# Initialize FastAPI
app = FastAPI(
    title="IIoT Predictive Maintenance API",
    description="Real-time machine monitoring and anomaly detection API",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server (default)
        "http://localhost:3001",  # Next.js dev server (alternate port)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize InfluxDB client
try:
    influx_client = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT)
    influx_client.switch_database(INFLUX_DB)
    print(f"✓ Connected to InfluxDB: {INFLUX_DB}")
except Exception as e:
    print(f"⚠️  Warning: Could not connect to InfluxDB: {e}")
    influx_client = None


# Pydantic models for request bodies
class TrainRequest(BaseModel):
    n_estimators: Optional[int] = 100
    contamination: Optional[float] = 0.1
    random_state: Optional[int] = 42


def map_status_code(status_code: str) -> str:
    """Map numeric status codes to human-readable strings"""
    status_mapping = {
        "0": "NORMAL",
        "1": "WARNING",
        "2": "ANOMALY",
        "NORMAL": "NORMAL",
        "WARNING": "WARNING",
        "ANOMALY": "ANOMALY"
    }
    return status_mapping.get(str(status_code), "UNKNOWN")


def calculate_health_score(vibration: float, temperature: float, ai_score: float) -> dict:
    """
    Calculate machine health score (0-100%) based on multiple factors
    Returns: health score, status, and next maintenance estimate
    """
    # Base score starts at 100
    health_score = 100.0
    
    # Vibration impact (0-85 = good, 85-95 = warning, >95 = critical)
    if vibration > 95:
        health_score -= 40
    elif vibration > 85:
        health_score -= 20
    elif vibration > 75:
        health_score -= 10
    
    # Temperature impact (0-70 = good, 70-80 = warning, >80 = critical)
    if temperature > 80:
        health_score -= 30
    elif temperature > 70:
        health_score -= 15
    elif temperature > 65:
        health_score -= 5
    
    # AI score impact (most important factor)
    if ai_score < -0.5:  # Anomaly
        health_score -= 35
    elif ai_score < 0.0:  # Warning
        health_score -= 15
    elif ai_score < 0.1:
        health_score -= 5
    
    # Ensure score is between 0-100
    health_score = max(0, min(100, health_score))
    
    # Determine health status
    if health_score >= 80:
        status = "EXCELLENT"
        color = "green"
    elif health_score >= 60:
        status = "GOOD"
        color = "green"
    elif health_score >= 40:
        status = "FAIR"
        color = "yellow"
    elif health_score >= 20:
        status = "POOR"
        color = "orange"
    else:
        status = "CRITICAL"
        color = "red"
    
    # Estimate days until maintenance (based on health score)
    # Higher score = more days until maintenance needed
    if health_score >= 80:
        days_until_maintenance = 14 + (health_score - 80) * 0.5
    elif health_score >= 60:
        days_until_maintenance = 7 + (health_score - 60) * 0.35
    elif health_score >= 40:
        days_until_maintenance = 3 + (health_score - 40) * 0.2
    elif health_score >= 20:
        days_until_maintenance = 1 + (health_score - 20) * 0.1
    else:
        days_until_maintenance = 0  # Immediate maintenance required
    
    return {
        "score": round(health_score, 1),
        "status": status,
        "color": color,
        "days_until_maintenance": round(days_until_maintenance, 1),
        "maintenance_urgency": "immediate" if days_until_maintenance < 1 else "soon" if days_until_maintenance < 3 else "scheduled"
    }


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "IIoT Predictive Maintenance API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": [
            "/api/live",
            "/api/history",
            "/docs"
        ]
    }


@app.get("/api/live")
async def get_live_data():
    """
    Get the latest sensor reading and AI prediction
    Returns: Current vibration, temperature, AI score, and status
    """
    if not influx_client:
        raise HTTPException(
            status_code=503,
            detail="InfluxDB connection not available"
        )
    
    try:
        # Query for the most recent record
        query = f'''
            SELECT last("vibration") as vibration,
                   last("temperature") as temperature,
                   last("ai_score") as score
            FROM "{MEASUREMENT}"
            WHERE time > now() - 1h
        '''
        
        result = influx_client.query(query)
        points = list(result.get_points())
        
        if not points:
            raise HTTPException(
                status_code=404,
                detail="No data available. Ensure the data ingestion pipeline is running."
            )
        
        data = points[0]
        
        # Get the latest status from tags (if available)
        status_query = f'''
            SELECT last("ai_score") as score
            FROM "{MEASUREMENT}"
            WHERE time > now() - 1h
        '''
        status_result = influx_client.query(status_query)
        
        # Determine status based on AI score
        score = float(data.get('score', 0))
        vibration = float(data.get('vibration', 0))
        temperature = float(data.get('temperature', 0))
        
        if score < -0.5:
            status = "ANOMALY"
        elif score < 0.1:
            status = "WARNING"
        else:
            status = "NORMAL"
        
        # Calculate health score
        health_data = calculate_health_score(vibration, temperature, score)
        
        return {
            "vibration": round(vibration, 2),
            "temperature": round(temperature, 2),
            "score": round(score, 4),
            "status": status,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "health": health_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error querying InfluxDB: {str(e)}"
        )


@app.get("/api/history")
async def get_history(limit: int = 50):
    """
    Get historical sensor readings for charting
    
    Args:
        limit: Number of records to return (default: 50, max: 500)
    
    Returns: List of timestamped readings
    """
    if not influx_client:
        raise HTTPException(
            status_code=503,
            detail="InfluxDB connection not available"
        )
    
    # Limit to reasonable range
    limit = min(limit, 500)
    
    try:
        # Query for historical data
        query = f'''
            SELECT "vibration", "temperature", "ai_score"
            FROM "{MEASUREMENT}"
            WHERE time > now() - 1h
            ORDER BY time DESC
            LIMIT {limit}
        '''
        
        result = influx_client.query(query)
        points = list(result.get_points())
        
        if not points:
            return []
        
        # Reverse to get chronological order
        points.reverse()
        
        # Format data for frontend
        history = []
        for point in points:
            score = float(point.get('ai_score', 0))
            
            # Determine status
            if score < -0.5:
                status = "ANOMALY"
            elif score < 0.1:
                status = "WARNING"
            else:
                status = "NORMAL"
            
            history.append({
                "timestamp": point.get('time'),
                "vibration": round(float(point.get('vibration', 0)), 2),
                "temperature": round(float(point.get('temperature', 0)), 2),
                "score": round(score, 4),
                "status": status
            })
        
        return history
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error querying InfluxDB: {str(e)}"
        )


@app.get("/api/stats")
async def get_statistics():
    """
    Get aggregated statistics for the dashboard
    Returns: Summary statistics over the last 24 hours
    """
    if not influx_client:
        raise HTTPException(
            status_code=503,
            detail="InfluxDB connection not available"
        )
    
    try:
        # Get statistics for last 24h
        query = f'''
            SELECT mean("vibration") as avg_vibration,
                   max("vibration") as max_vibration,
                   mean("temperature") as avg_temperature,
                   max("temperature") as max_temperature,
                   mean("ai_score") as avg_score,
                   min("ai_score") as min_score,
                   count("ai_score") as total_readings
            FROM "{MEASUREMENT}"
            WHERE time > now() - 24h
        '''
        
        result = influx_client.query(query)
        points = list(result.get_points())
        
        if not points or not points[0].get('total_readings'):
            return {
                "vibration": {"average": 0, "max": 0},
                "temperature": {"average": 0, "max": 0},
                "ai_score": {"average": 0, "min": 0},
                "uptime_percentage": 0,
                "total_readings": 0,
                "anomalies_today": 0,
                "warnings_today": 0
            }
        
        data = points[0]
        total_readings = int(data.get('total_readings', 0))
        
        # Count anomalies and warnings in last 24h
        anomaly_query = f'''
            SELECT count("ai_score") as count
            FROM "{MEASUREMENT}"
            WHERE time > now() - 24h AND "ai_score" < -0.5
        '''
        anomaly_result = influx_client.query(anomaly_query)
        anomaly_points = list(anomaly_result.get_points())
        anomalies = int(anomaly_points[0].get('count', 0)) if anomaly_points else 0
        
        warning_query = f'''
            SELECT count("ai_score") as count
            FROM "{MEASUREMENT}"
            WHERE time > now() - 24h AND "ai_score" >= -0.5 AND "ai_score" < 0.1
        '''
        warning_result = influx_client.query(warning_query)
        warning_points = list(warning_result.get_points())
        warnings = int(warning_points[0].get('count', 0)) if warning_points else 0
        
        # Calculate uptime (percentage of normal readings)
        normal_readings = total_readings - anomalies - warnings
        uptime_percentage = (normal_readings / total_readings * 100) if total_readings > 0 else 100
        
        return {
            "vibration": {
                "average": round(float(data.get('avg_vibration', 0)), 2),
                "max": round(float(data.get('max_vibration', 0)), 2)
            },
            "temperature": {
                "average": round(float(data.get('avg_temperature', 0)), 2),
                "max": round(float(data.get('max_temperature', 0)), 2)
            },
            "ai_score": {
                "average": round(float(data.get('avg_score', 0)), 4),
                "min": round(float(data.get('min_score', 0)), 4)
            },
            "uptime_percentage": round(uptime_percentage, 1),
            "total_readings": total_readings,
            "anomalies_today": anomalies,
            "warnings_today": warnings
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error querying statistics: {str(e)}"
        )


@app.get("/api/alerts")
async def get_alerts(limit: int = 20):
    """
    Get recent alerts (anomalies and warnings) with timestamps
    Returns: List of alerts in reverse chronological order
    """
    if not influx_client:
        raise HTTPException(
            status_code=503,
            detail="InfluxDB connection not available"
        )
    
    # Limit to reasonable range
    limit = min(limit, 100)
    
    try:
        # Query for alerts (warnings and anomalies) in last 24h
        query = f'''
            SELECT "vibration", "temperature", "ai_score"
            FROM "{MEASUREMENT}"
            WHERE time > now() - 24h AND "ai_score" < 0.1
            ORDER BY time DESC
            LIMIT {limit}
        '''
        
        result = influx_client.query(query)
        points = list(result.get_points())
        
        if not points:
            return []
        
        # Format alerts for frontend
        alerts = []
        for point in points:
            score = float(point.get('ai_score', 0))
            vibration = float(point.get('vibration', 0))
            temperature = float(point.get('temperature', 0))
            
            # Determine severity
            if score < -0.5:
                severity = "ANOMALY"
                color = "red"
            else:
                severity = "WARNING"
                color = "yellow"
            
            # Create descriptive message
            reasons = []
            if vibration > 75:
                reasons.append(f"High vibration: {vibration:.1f}")
            if temperature > 70:
                reasons.append(f"High temperature: {temperature:.1f}°C")
            if score < -0.5:
                reasons.append(f"Low AI score: {score:.3f}")
            
            message = ", ".join(reasons) if reasons else f"AI score: {score:.3f}"
            
            alerts.append({
                "timestamp": point.get('time'),
                "severity": severity,
                "color": color,
                "message": message,
                "vibration": round(vibration, 2),
                "temperature": round(temperature, 2),
                "score": round(score, 4)
            })
        
        return alerts
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error querying alerts: {str(e)}"
        )


@app.get("/api/work-orders")
async def get_work_orders():
    """
    Get all maintenance work orders with status
    Returns: List of work orders sorted by priority and due date
    """
    # Mock work orders (in production, this would query a database)
    work_orders = [
        {
            "id": "WO-1245",
            "machine_id": "Press_001",
            "title": "High Vibration Alert",
            "description": "Investigate and resolve abnormal vibration levels detected at 10:45 AM",
            "priority": "HIGH",
            "status": "OPEN",
            "assigned_to": "John Smith",
            "created_at": "2025-12-06T10:47:00Z",
            "due_date": "2025-12-08T17:00:00Z",
            "estimated_hours": 4,
            "category": "Emergency Repair"
        },
        {
            "id": "WO-1246",
            "machine_id": "Press_001",
            "title": "Scheduled Preventive Maintenance",
            "description": "Routine inspection and lubrication based on health score prediction",
            "priority": "MEDIUM",
            "status": "IN_PROGRESS",
            "assigned_to": "Mike Johnson",
            "created_at": "2025-12-05T08:00:00Z",
            "due_date": "2025-12-10T12:00:00Z",
            "estimated_hours": 8,
            "category": "Preventive Maintenance"
        },
        {
            "id": "WO-1243",
            "machine_id": "Press_001",
            "title": "Temperature Sensor Calibration",
            "description": "Calibrate temperature sensors as part of quarterly maintenance",
            "priority": "LOW",
            "status": "SCHEDULED",
            "assigned_to": "Sarah Williams",
            "created_at": "2025-12-04T14:30:00Z",
            "due_date": "2025-12-15T16:00:00Z",
            "estimated_hours": 2,
            "category": "Calibration"
        },
        {
            "id": "WO-1240",
            "machine_id": "Press_001",
            "title": "Bearing Replacement",
            "description": "Replaced worn bearings causing vibration anomaly",
            "priority": "HIGH",
            "status": "COMPLETED",
            "assigned_to": "John Smith",
            "created_at": "2025-12-03T09:15:00Z",
            "due_date": "2025-12-03T18:00:00Z",
            "completed_at": "2025-12-03T16:30:00Z",
            "estimated_hours": 6,
            "actual_hours": 5.5,
            "category": "Repair"
        }
    ]
    
    # Sort: HIGH priority first, then by due date
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    work_orders.sort(key=lambda x: (priority_order.get(x["priority"], 3), x.get("due_date", "")))
    
    return work_orders


@app.get("/api/patterns")
async def get_anomaly_patterns():
    """
    Analyze historical data to detect recurring patterns and correlations
    Returns: List of detected patterns with confidence scores
    """
    if not influx_client:
        raise HTTPException(
            status_code=503,
            detail="InfluxDB connection not available"
        )
    
    try:
        # Check if InfluxDB has data
        check_query = f'''
            SELECT COUNT("vibration")
            FROM "{MEASUREMENT}"
            WHERE time > now() - 7d
        '''
        check_result = influx_client.query(check_query)
        check_points = list(check_result.get_points())
        
        if not check_points or check_points[0].get('count', 0) < 10:
            # Not enough data yet, return info pattern
            return [{
                "id": "PATTERN-000",
                "type": "NO_PATTERN",
                "title": "Insufficient Data for Analysis",
                "description": "System is still collecting data. Pattern analysis requires at least 7 days of continuous monitoring.",
                "confidence": 100,
                "occurrences": 0,
                "severity": "INFO",
                "recommendation": "Continue running the system. Check back in a few days for pattern detection results.",
                "detected_at": datetime.utcnow().isoformat() + "Z"
            }]
        
        # Analyze vibration patterns by hour of day
        hour_query = f'''
            SELECT mean("vibration") as avg_vibration, 
                   mean("temperature") as avg_temperature,
                   count("vibration") as count
            FROM "{MEASUREMENT}"
            WHERE time > now() - 7d
            GROUP BY time(1h)
        '''
        
        result = influx_client.query(hour_query)
        points = list(result.get_points())
        
        patterns = []
        
        # Pattern 1: Time-based vibration analysis
        if points and len(points) > 24:
            vibration_values = [float(p.get('avg_vibration', 0)) for p in points if p.get('avg_vibration')]
            avg_vibration = sum(vibration_values) / len(vibration_values) if vibration_values else 0
            
            # Find peaks (hours with significantly higher vibration)
            high_vibration_hours = []
            for i, point in enumerate(points[-24:]):  # Last 24 hours
                vib = float(point.get('avg_vibration', 0))
                if vib > avg_vibration * 1.2:  # 20% above average
                    hour = i % 24
                    high_vibration_hours.append(hour)
            
            if high_vibration_hours:
                most_common_hour = max(set(high_vibration_hours), key=high_vibration_hours.count)
                pattern_frequency = high_vibration_hours.count(most_common_hour) / len(points[-24:]) * 100
                
                patterns.append({
                    "id": "PATTERN-001",
                    "type": "TIME_BASED",
                    "title": f"Vibration Spikes During Hour {most_common_hour}:00-{most_common_hour+1}:00",
                    "description": f"Elevated vibration levels detected consistently around {most_common_hour}:00. This may correlate with shift changes, operator behavior, or scheduled production activities.",
                    "confidence": min(85 + pattern_frequency * 0.5, 95),
                    "occurrences": high_vibration_hours.count(most_common_hour),
                    "severity": "MEDIUM",
                    "recommendation": "Review production schedule and operator procedures during this time window. Consider adjusting maintenance windows to avoid peak production hours.",
                    "detected_at": datetime.utcnow().isoformat() + "Z"
                })
        
        # Pattern 2: Temperature correlation with vibration
        if points:
            temp_vib_correlation = []
            for point in points[-50:]:  # Last 50 readings
                temp = float(point.get('avg_temperature', 0))
                vib = float(point.get('avg_vibration', 0))
                if temp > 70 and vib > 75:
                    temp_vib_correlation.append((temp, vib))
            
            if len(temp_vib_correlation) > 5:
                correlation_strength = len(temp_vib_correlation) / min(50, len(points)) * 100
                
                patterns.append({
                    "id": "PATTERN-002",
                    "type": "CORRELATION",
                    "title": "Temperature-Vibration Correlation Detected",
                    "description": f"High temperature (>70°C) frequently occurs alongside high vibration (>75 units). Found {len(temp_vib_correlation)} co-occurrences in recent data.",
                    "confidence": min(70 + correlation_strength, 92),
                    "occurrences": len(temp_vib_correlation),
                    "severity": "HIGH",
                    "recommendation": "Investigate cooling system efficiency. Consider installing additional cooling or adjusting operating parameters to reduce thermal stress.",
                    "detected_at": datetime.utcnow().isoformat() + "Z"
                })
        
        # Pattern 3: Day-of-week analysis
        weekday_query = f'''
            SELECT mean("vibration") as avg_vibration,
                   count("vibration") as count
            FROM "{MEASUREMENT}"
            WHERE time > now() - 7d
            GROUP BY time(1d)
        '''
        
        weekday_result = influx_client.query(weekday_query)
        weekday_points = list(weekday_result.get_points())
        
        if len(weekday_points) >= 7:
            day_vibrations = [(i % 7, float(p.get('avg_vibration', 0))) for i, p in enumerate(weekday_points)]
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            # Find day with highest average vibration
            if day_vibrations:
                max_day_idx = max(day_vibrations, key=lambda x: x[1])[0]
                max_day_value = max(day_vibrations, key=lambda x: x[1])[1]
                avg_all_days = sum(v for _, v in day_vibrations) / len(day_vibrations)
                
                if max_day_value > avg_all_days * 1.15:  # 15% above average
                    patterns.append({
                        "id": "PATTERN-003",
                        "type": "WEEKLY_CYCLE",
                        "title": f"Elevated Activity on {day_names[max_day_idx]}s",
                        "description": f"Vibration levels on {day_names[max_day_idx]}s average {max_day_value:.1f} units, which is {((max_day_value/avg_all_days - 1) * 100):.1f}% higher than other days.",
                        "confidence": 78,
                        "occurrences": len([d for d, _ in day_vibrations if d == max_day_idx]),
                        "severity": "LOW",
                        "recommendation": f"Review {day_names[max_day_idx]} production schedules. This pattern may indicate higher workload or different operational procedures on this day.",
                        "detected_at": datetime.utcnow().isoformat() + "Z"
                    })
        
        # If no patterns detected, return helpful message
        if not patterns:
            patterns.append({
                "id": "PATTERN-000",
                "type": "NO_PATTERN",
                "title": "No Significant Patterns Detected",
                "description": "Analysis of the last 7 days shows consistent operation without recurring anomaly patterns. This indicates stable machine performance.",
                "confidence": 95,
                "occurrences": 0,
                "severity": "INFO",
                "recommendation": "Continue monitoring. Patterns typically emerge over longer time periods (2-4 weeks).",
                "detected_at": datetime.utcnow().isoformat() + "Z"
            })
        
        return patterns
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing patterns: {str(e)}"
        )


# ==========================================
# HEALTH & AI ADMIN ENDPOINTS
# ==========================================

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker"""
    return {"status": "healthy", "service": "ai-engine"}


@app.get("/model-info")
async def get_model_info():
    """Get information about the trained model"""
    try:
        model_exists = os.path.exists(MODEL_PATH)
        
        if not model_exists:
            return {
                "exists": False,
                "type": None,
                "n_estimators": None,
                "contamination": None,
                "last_trained": None,
                "sample_count": 0
            }
        
        # Load model to get parameters
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        
        # Get training data count
        sample_count = 0
        if influx_client:
            try:
                query = f'SELECT COUNT(*) FROM {MEASUREMENT}'
                result = influx_client.query(query)
                points = list(result.get_points())
                if points:
                    sample_count = points[0].get('count_vibration', 0)
            except:
                pass
        
        # Get model parameters
        params = {
            "exists": True,
            "type": type(model).__name__,
            "n_estimators": getattr(model, 'n_estimators', None),
            "contamination": getattr(model, 'contamination', None),
            "last_trained": datetime.fromtimestamp(os.path.getmtime(MODEL_PATH)).isoformat(),
            "sample_count": sample_count
        }
        
        return params
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading model info: {str(e)}")


@app.post("/train")
async def train_model(request: TrainRequest):
    """Train or retrain the anomaly detection model"""
    try:
        from sklearn.ensemble import IsolationForest
        import numpy as np
        
        if not influx_client:
            raise HTTPException(status_code=503, detail="InfluxDB not available")
        
        # Fetch training data
        query = f'SELECT * FROM {MEASUREMENT} LIMIT 10000'
        result = influx_client.query(query)
        points = list(result.get_points())
        
        if len(points) < 100:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient training data. Need at least 100 samples, got {len(points)}"
            )
        
        # Prepare features
        features = []
        for point in points:
            features.append([
                point.get('vibration', 0),
                point.get('temperature', 0),
                point.get('pressure', 0)
            ])
        
        X = np.array(features)
        
        # Train model
        model = IsolationForest(
            n_estimators=request.n_estimators,
            contamination=request.contamination,
            random_state=request.random_state,
            n_jobs=-1
        )
        
        model.fit(X)
        
        # Save model
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model, f)
        
        return {
            "message": "Model trained successfully",
            "samples_used": len(points),
            "n_estimators": request.n_estimators,
            "contamination": request.contamination,
            "model_path": MODEL_PATH
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@app.post("/reset-model")
async def reset_model():
    """Delete the trained model"""
    try:
        if os.path.exists(MODEL_PATH):
            os.remove(MODEL_PATH)
            return {"message": "Model deleted successfully"}
        else:
            return {"message": "No model found to delete"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting model: {str(e)}")


if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Starting FastAPI Server")
    print("=" * 70)
    print(f"API Documentation: http://localhost:8000/docs")
    print(f"Alternative Docs: http://localhost:8000/redoc")
    print(f"CORS Enabled for: http://localhost:3000")
    print("=" * 70)
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

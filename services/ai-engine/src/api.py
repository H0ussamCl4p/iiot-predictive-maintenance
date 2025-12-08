"""
FastAPI Backend Server for IIoT Predictive Maintenance
Provides REST API endpoints for Next.js frontend
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from influxdb import InfluxDBClient
from typing import List, Dict, Any, Optional
from datetime import datetime
import uvicorn
import os
import json
import pickle
import csv
import io
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

# Configuration
INFLUX_HOST = os.getenv("INFLUX_HOST", "localhost")
INFLUX_PORT = int(os.getenv("INFLUX_PORT", "8086"))
INFLUX_DB = os.getenv("INFLUX_DB", "factory_data")
MEASUREMENT = "machine_telemetry"
MODEL_PATH = "/app/models/anomaly_model.pkl"
PREDICTIVE_MODEL_PATH = "/app/models/predictive_model.pkl"

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
            vibration_values = [float(p['avg_vibration']) for p in points if p.get('avg_vibration') is not None]
            avg_vibration = sum(vibration_values) / len(vibration_values) if vibration_values else 0
            
            # Find peaks (hours with significantly higher vibration)
            high_vibration_hours = []
            for i, point in enumerate(points[-24:]):  # Last 24 hours
                vib_val = point.get('avg_vibration')
                if vib_val is not None:
                    vib = float(vib_val)
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
                temp_val = point.get('avg_temperature')
                vib_val = point.get('avg_vibration')
                if temp_val is not None and vib_val is not None:
                    temp = float(temp_val)
                    vib = float(vib_val)
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
            day_vibrations = [(i % 7, float(p['avg_vibration'])) for i, p in enumerate(weekday_points) if p.get('avg_vibration') is not None]
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            # Find day with highest average vibration
            if day_vibrations and len(day_vibrations) > 0:
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
    """Get information about the trained model and uploaded data"""
    try:
        model_exists = os.path.exists(MODEL_PATH)
        data_path = "/app/data/training_data.csv"
        column_mapping_path = "/app/data/column_mapping.json"
        
        # Get uploaded data info
        data_info = {}
        if os.path.exists(column_mapping_path):
            with open(column_mapping_path, 'r') as f:
                data_info = json.load(f)
        
        if not model_exists:
            return {
                "exists": False,
                "is_trained": False,
                "type": None,
                "n_estimators": None,
                "contamination": None,
                "last_trained": None,
                "sample_count": data_info.get('total_rows', 0),
                "features": data_info.get('original_columns', []),
                "feature_count": data_info.get('feature_count', 0),
                "uploaded_file": data_info.get('filename', None)
            }
        
        # Load model to get parameters
        with open(MODEL_PATH, 'rb') as f:
            model_data = pickle.load(f)
        
        # Handle both old and new model formats
        if isinstance(model_data, dict):
            model = model_data.get('model')
            columns = model_data.get('columns', [])
            trained_at = model_data.get('trained_at')
        else:
            # Old format (just the model)
            model = model_data
            columns = []
            trained_at = datetime.fromtimestamp(os.path.getmtime(MODEL_PATH)).isoformat()
        
        # Get model parameters
        params = {
            "exists": True,
            "is_trained": True,
            "type": type(model).__name__,
            "n_estimators": getattr(model, 'n_estimators', None),
            "contamination": getattr(model, 'contamination', None),
            "last_trained": trained_at,
            "sample_count": data_info.get('total_rows', 0),
            "features": columns or data_info.get('original_columns', []),
            "feature_count": len(columns) or data_info.get('feature_count', 0),
            "uploaded_file": data_info.get('filename', None)
        }
        
        return params
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading model info: {str(e)}")


@app.post("/train")
async def train_model(request: TrainRequest):
    """Train or retrain the anomaly detection model with uploaded data"""
    try:
        from sklearn.ensemble import IsolationForest
        from sklearn.preprocessing import StandardScaler
        import pandas as pd
        import numpy as np
        
        # Check for uploaded training data
        data_path = "/app/data/training_data.csv"
        column_mapping_path = "/app/data/column_mapping.json"
        
        if not os.path.exists(data_path):
            raise HTTPException(
                status_code=400,
                detail="No training data found. Please upload a dataset first using the Dataset Upload feature."
            )
        
        # Load uploaded data
        df = pd.read_csv(data_path)
        
        if len(df) < 100:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient training data. Need at least 100 samples, got {len(df)}"
            )
        
        # Load column info
        column_info = {}
        if os.path.exists(column_mapping_path):
            with open(column_mapping_path, 'r') as f:
                column_info = json.load(f)
        
        # Prepare features (all numeric columns)
        X = df.values
        
        # Normalize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train model
        model = IsolationForest(
            n_estimators=request.n_estimators,
            contamination=request.contamination,
            random_state=request.random_state,
            n_jobs=-1
        )
        
        model.fit(X_scaled)
        
        # Save model and scaler
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        
        model_data = {
            'model': model,
            'scaler': scaler,
            'columns': df.columns.tolist(),
            'feature_count': len(df.columns),
            'trained_at': datetime.utcnow().isoformat()
        }
        
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model_data, f)
        
        return {
            "message": "Model trained successfully",
            "samples_used": len(df),
            "features": df.columns.tolist(),
            "feature_count": len(df.columns),
            "n_estimators": request.n_estimators,
            "contamination": request.contamination,
            "model_path": MODEL_PATH,
            "source_file": column_info.get('filename', 'unknown')
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


@app.post("/upload-dataset")
async def upload_dataset(file: UploadFile = File(...)):
    """Upload CSV/Excel dataset - auto-detects columns and file format"""
    try:
        import pandas as pd
        
        print(f"📥 Upload request received: {file.filename}, content_type: {file.content_type}")
        
        # Validate file type
        allowed_extensions = ['.csv', '.xls', '.xlsx']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        print(f"🔍 Detected file extension: {file_ext}")
        
        if file_ext not in allowed_extensions:
            error_msg = f"File type not supported. Allowed: {', '.join(allowed_extensions)}"
            print(f"❌ {error_msg}")
            raise HTTPException(
                status_code=400, 
                detail=error_msg
            )
        
        # Read file content
        contents = await file.read()
        print(f"📦 File size: {len(contents)} bytes")
        
        # Load data based on file type
        try:
            if file_ext == '.csv':
                # Try to auto-detect delimiter (comma or semicolon)
                df = pd.read_csv(io.BytesIO(contents), sep=None, engine='python')
            elif file_ext in ['.xls', '.xlsx']:
                df = pd.read_excel(io.BytesIO(contents))
            print(f"✅ Parsed {len(df)} rows, {len(df.columns)} columns: {df.columns.tolist()}")
        except Exception as e:
            error_msg = f"Failed to parse file: {str(e)}"
            print(f"❌ {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        if df.empty:
            raise HTTPException(status_code=400, detail="File contains no data")
        
        # Auto-detect numeric columns (features)
        numeric_cols = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
        
        if not numeric_cols:
            raise HTTPException(
                status_code=400, 
                detail="No numeric columns found. File must contain at least one numeric column."
            )
        
        # Handle missing values
        df_clean = df[numeric_cols].fillna(df[numeric_cols].mean())
        
        # Store column mapping for later use
        column_mapping_path = "/app/data/column_mapping.json"
        os.makedirs(os.path.dirname(column_mapping_path), exist_ok=True)
        
        column_info = {
            "original_columns": numeric_cols,
            "feature_count": len(numeric_cols),
            "uploaded_at": datetime.utcnow().isoformat(),
            "filename": file.filename,
            "total_rows": len(df_clean)
        }
        
        with open(column_mapping_path, 'w') as f:
            json.dump(column_info, f, indent=2)
        
        # Save processed data for training
        data_path = "/app/data/training_data.csv"
        df_clean.to_csv(data_path, index=False)
        
        # Also insert into InfluxDB for visualization
        points = []
        for idx, row in df_clean.iterrows():
            fields = {col: float(row[col]) for col in numeric_cols}
            
            point = {
                "measurement": MEASUREMENT,
                "tags": {
                    "source": "uploaded_dataset",
                    "filename": file.filename
                },
                "time": datetime.utcnow().isoformat(),
                "fields": fields
            }
            points.append(point)
        
        if influx_client and points:
            try:
                influx_client.write_points(points[:1000])  # Limit to first 1000 points for visualization
            except Exception as e:
                print(f"Warning: Could not write to InfluxDB: {e}")
        
        return {
            "message": "Dataset uploaded and processed successfully",
            "filename": file.filename,
            "total_rows": len(df_clean),
            "numeric_columns": numeric_cols,
            "feature_count": len(numeric_cols),
            "ready_for_training": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


# ============================================================================
# COMBINED PREDICTION ENDPOINT - Real-time Anomaly + Future Failure
# ============================================================================

class PredictionRequest(BaseModel):
    """Request model for combined prediction"""
    data: Dict[str, float]  # Current sensor readings
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": {
                    "Humidity": 65.0,
                    "Temperature": 45.0,
                    "Age": 12.0,
                    "Quantity": 42000.0
                }
            }
        }


@app.post("/predict")
async def predict_combined(request: PredictionRequest):
    """
    Combined prediction endpoint that provides:
    1. Real-time anomaly detection (Is it anomalous NOW?)
    2. Future failure prediction (WHEN will it fail?)
    
    Returns comprehensive analysis with risk assessment
    """
    try:
        input_data = request.data
        
        # =====================================================================
        # Part 1: Real-time Anomaly Detection (Isolation Forest)
        # =====================================================================
        anomaly_result = {
            "is_anomaly": False,
            "anomaly_score": 0,
            "status": "UNKNOWN",
            "model_loaded": False
        }
        
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, 'rb') as f:
                    model_data = pickle.load(f)
                
                # Handle both old and new model formats
                if isinstance(model_data, dict):
                    model = model_data.get('model')
                    scaler = model_data.get('scaler')
                    expected_features = model_data.get('columns', [])
                else:
                    model = model_data
                    scaler = None
                    expected_features = list(input_data.keys())
                
                # Prepare input for anomaly detection
                input_df = np.array([[input_data.get(feat, 0) for feat in expected_features]])
                
                if scaler:
                    input_scaled = scaler.transform(input_df)
                else:
                    input_scaled = input_df
                
                # Predict anomaly (-1 = anomaly, 1 = normal)
                prediction = model.predict(input_scaled)[0]
                anomaly_score_raw = model.score_samples(input_scaled)[0]
                
                # Convert to 0-100 scale (lower = more anomalous)
                anomaly_score = max(0, min(100, int((anomaly_score_raw + 0.5) * 100)))
                
                # Calculate heuristic score for better interpretation
                heuristic_score = 0
                warnings = []
                
                # Temperature checks
                temp = input_data.get('Temperature', 0)
                if temp > 80:
                    heuristic_score += 30
                    warnings.append("🔴 Critical temperature detected")
                elif temp > 70:
                    heuristic_score += 15
                    warnings.append("🟡 High temperature warning")
                
                # Humidity checks
                humidity = input_data.get('Humidity', 0)
                if humidity > 85:
                    heuristic_score += 25
                    warnings.append("🔴 Extreme humidity levels")
                elif humidity > 75:
                    heuristic_score += 10
                    warnings.append("🟡 High humidity detected")
                
                # Age checks
                age = input_data.get('Age', 0)
                if age > 20:
                    heuristic_score += 20
                    warnings.append("⚠️ Equipment very old")
                elif age > 15:
                    heuristic_score += 10
                    warnings.append("⚠️ Equipment aging")
                
                # MTTF checks (if available)
                mttf = input_data.get('MTTF', input_data.get('MTTF ', 0))
                if mttf > 0:
                    if mttf < 100:
                        heuristic_score += 35
                        warnings.append("🔴 Critical MTTF - Failure imminent")
                    elif mttf < 300:
                        heuristic_score += 20
                        warnings.append("🟡 Low MTTF - Maintenance needed")
                    elif mttf < 500:
                        heuristic_score += 5
                        warnings.append("ℹ️ MTTF below average")
                
                # Determine status
                if heuristic_score >= 60 or prediction == -1:
                    status = "ANOMALY"
                    risk_level = "CRITICAL"
                    status_emoji = "🔴"
                elif heuristic_score >= 30:
                    status = "WARNING"
                    risk_level = "MEDIUM"
                    status_emoji = "🟡"
                else:
                    status = "NORMAL"
                    risk_level = "LOW"
                    status_emoji = "✅"
                
                anomaly_result = {
                    "is_anomaly": (status == "ANOMALY"),
                    "status": status,
                    "status_emoji": status_emoji,
                    "risk_level": risk_level,
                    "anomaly_score": heuristic_score,
                    "model_score": anomaly_score,
                    "warnings": warnings,
                    "model_loaded": True
                }
                
            except Exception as e:
                print(f"Anomaly detection error: {e}")
                anomaly_result["error"] = str(e)
        
        # =====================================================================
        # Part 2: Future Failure Prediction (Random Forest Regressor)
        # =====================================================================
        prediction_result = {
            "predicted_mttf": None,
            "estimated_days_until_failure": None,
            "future_risk_level": "UNKNOWN",
            "recommended_action": "Model not available",
            "model_loaded": False
        }
        
        if os.path.exists(PREDICTIVE_MODEL_PATH):
            try:
                with open(PREDICTIVE_MODEL_PATH, 'rb') as f:
                    pred_model_data = pickle.load(f)
                
                pred_model = pred_model_data['model']
                pred_scaler = pred_model_data['scaler']
                pred_features = pred_model_data['features']
                
                # Prepare input for prediction
                pred_input = np.array([[input_data.get(feat, 0) for feat in pred_features]])
                pred_input_scaled = pred_scaler.transform(pred_input)
                
                # Predict MTTF
                predicted_mttf = pred_model.predict(pred_input_scaled)[0]
                days_estimate = predicted_mttf / 24  # Convert hours to days
                
                # Risk assessment based on predicted MTTF
                if predicted_mttf < 100:
                    future_risk = "CRITICAL"
                    future_emoji = "🔴"
                    action = "IMMEDIATE MAINTENANCE REQUIRED - Equipment likely to fail within days"
                    confidence = "High"
                elif predicted_mttf < 300:
                    future_risk = "HIGH"
                    future_emoji = "🟠"
                    action = "Schedule maintenance within 1-2 weeks"
                    confidence = "High"
                elif predicted_mttf < 500:
                    future_risk = "MEDIUM"
                    future_emoji = "🟡"
                    action = "Monitor closely, plan maintenance within next month"
                    confidence = "Medium"
                else:
                    future_risk = "LOW"
                    future_emoji = "🟢"
                    action = "Continue normal operation, routine maintenance sufficient"
                    confidence = "Medium"
                
                # Get feature importance for explanation
                feature_importance = {
                    feat: float(imp) 
                    for feat, imp in zip(pred_features, pred_model.feature_importances_)
                }
                
                # Find most critical factor
                most_critical_factor = max(
                    [(feat, input_data.get(feat, 0), imp) for feat, imp in feature_importance.items()],
                    key=lambda x: x[2]
                )
                
                prediction_result = {
                    "predicted_mttf": round(predicted_mttf, 2),
                    "estimated_days_until_failure": round(days_estimate, 1),
                    "future_risk_level": future_risk,
                    "future_risk_emoji": future_emoji,
                    "recommended_action": action,
                    "confidence": confidence,
                    "feature_importance": feature_importance,
                    "most_critical_factor": {
                        "name": most_critical_factor[0],
                        "value": most_critical_factor[1],
                        "importance": round(most_critical_factor[2] * 100, 1)
                    },
                    "model_loaded": True
                }
                
            except Exception as e:
                print(f"Predictive model error: {e}")
                prediction_result["error"] = str(e)
        
        # =====================================================================
        # Part 3: Combined Risk Assessment
        # =====================================================================
        
        # Overall risk is highest of current + future
        risk_levels = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3, "UNKNOWN": -1}
        current_risk_val = risk_levels.get(anomaly_result.get("risk_level", "UNKNOWN"), -1)
        future_risk_val = risk_levels.get(prediction_result.get("future_risk_level", "UNKNOWN"), -1)
        
        overall_risk_val = max(current_risk_val, future_risk_val)
        overall_risk = [k for k, v in risk_levels.items() if v == overall_risk_val][0] if overall_risk_val >= 0 else "UNKNOWN"
        
        # Generate comprehensive recommendation
        if overall_risk == "CRITICAL":
            overall_action = "⚠️ URGENT: Both current conditions and future predictions indicate critical risk. Shut down equipment and perform immediate inspection."
        elif overall_risk == "HIGH":
            overall_action = "⚠️ HIGH PRIORITY: Schedule maintenance within 24-48 hours to prevent potential failure."
        elif overall_risk == "MEDIUM":
            overall_action = "⚠️ ATTENTION: Monitor closely and schedule maintenance within 1-2 weeks."
        else:
            overall_action = "✅ Equipment operating normally. Continue routine monitoring and maintenance schedule."
        
        # Return combined results
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "input_data": input_data,
            
            # Current state analysis
            "current_state": {
                **anomaly_result,
                "description": "Real-time anomaly detection using Isolation Forest"
            },
            
            # Future prediction
            "future_prediction": {
                **prediction_result,
                "description": "Time-to-failure prediction using Random Forest Regressor"
            },
            
            # Overall assessment
            "overall_assessment": {
                "risk_level": overall_risk,
                "recommendation": overall_action,
                "analysis": f"Current: {anomaly_result.get('status', 'UNKNOWN')}, Future: {prediction_result.get('future_risk_level', 'UNKNOWN')}"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.get("/models/status")
async def get_models_status():
    """Check which models are available"""
    return {
        "anomaly_detection_model": {
            "available": os.path.exists(MODEL_PATH),
            "path": MODEL_PATH,
            "type": "Isolation Forest",
            "purpose": "Real-time anomaly detection"
        },
        "predictive_model": {
            "available": os.path.exists(PREDICTIVE_MODEL_PATH),
            "path": PREDICTIVE_MODEL_PATH,
            "type": "Random Forest Regressor",
            "purpose": "Future failure prediction"
        }
    }


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

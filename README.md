# Predictive Maintenance

## Overview
This project provides an IIoT predictive maintenance stack with:
- FastAPI backend serving live data, history, stats, alerts, and pattern analysis
- Next.js dashboard with AI Health Score trend and prediction panel
- MQTT simulator feeding vibration and temperature into InfluxDB
- Optional desktop Tkinter admin

## Backend API
- `GET /api/live`: Latest telemetry and AI assessment.
	- `vibration` (number)
	- `temperature` (number)
	- `score` (number, AI Health Score)
	- `status` (NORMAL|WARNING|ANOMALY)
	- `timestamp` (ISO string)
	- `health` (score/status/color/days_until_maintenance/maintenance_urgency)
- `GET /api/history?limit=50`: Last readings for charts.
	- Array of `{ timestamp, vibration, temperature, score, status }`
- `GET /api/stats`, `GET /api/alerts`, `GET /api/patterns`: Aggregates and insights.

## AI Score: Definition and Meaning
The `score` is the AI Health Score per reading, expressing confidence that the machine is healthy.

- Range: `0.0` to `1.0` (higher is healthier) for visualization consistency.
- Source:
	- With a trained anomaly model (IsolationForest), we derive a per-sample score and normalize it. Lower model scores indicate anomaly; higher indicate normal.
	- If no model score is available, a fallback heuristic estimates the score from vibration and temperature. It auto-calibrates expected maxima from recent data in InfluxDB (last ~2h) so the scale adapts to your environment.
- Status mapping (used across `/api/live` and `/api/history`):
	- `ANOMALY`: score < 0.1
	- `WARNING`: 0.1 ≤ score < 0.3
	- `NORMAL`: score ≥ 0.3

The separate `health` object provides an aggregated 0–100 score and a days-until-maintenance estimate for planning.

## Environment Variables
- `INFLUX_HOST`, `INFLUX_PORT`, `INFLUX_DB`: InfluxDB connection.
- `MQTT_BROKER`: MQTT broker host for simulator data.
- `EXPECTED_MAX_VIBRATION`: Max expected vibration for fallback normalization.
- `EXPECTED_MAX_TEMPERATURE`: Max expected temperature for fallback normalization.

## Quick Start (Windows PowerShell)
```powershell
docker-compose up -d
Start-Sleep -Seconds 3
Start-Process http://localhost:3001/dashboard
```

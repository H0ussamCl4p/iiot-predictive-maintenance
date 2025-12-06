# 🚀 IIoT Microservices Refactoring - Complete Guide

## ✅ Files Created

### 1. **refactor_structure.ps1**
PowerShell script that automates the entire refactoring process:
- Creates microservices directory structure
- Moves Python files to `services/ai-engine/src/`
- Moves simulator to `services/simulator/`
- Moves frontend to `services/web-frontend/`
- Cleans up venv, __pycache__, and temp files
- Generates requirements.txt for each service
- Creates infrastructure configs (Mosquitto, InfluxDB, Grafana)

### 2. **docker-compose-new.yml**
Master orchestrator defining all services:
- **Infrastructure:** Mosquitto, InfluxDB, Grafana
- **AI Engine:** Multi-process container (FastAPI + Streamlit + AI Consumer)
- **Simulator:** Wear data generation
- **Frontend:** Next.js application
- **Network:** `iiot_net` connecting all services
- **Health checks** for all critical services

### 3. **Dockerfile.ai-engine**
AI Engine multi-process container:
- Base: Python 3.10-slim
- Runs Supervisord to manage 3 processes:
  - **FastAPI** (port 8000) - REST API
  - **Streamlit** (port 8501) - Admin Dashboard
  - **AI Consumer** (main.py) - MQTT subscriber
- Includes health check endpoint
- Auto-restart on failure

### 4. **Dockerfile.simulator**
Simulator container:
- Base: Python 3.10-slim
- Runs `simulate_wear.py` continuously
- Publishes MQTT messages

### 5. **Dockerfile.frontend**
Next.js production container:
- Multi-stage build (deps → builder → runner)
- Optimized for production
- Node 18 Alpine base
- Runs standalone server

### 6. **streamlit_admin.py**
AI Admin Dashboard (Streamlit):
- **Model Management:**
  - Train new models
  - Retrain existing models
  - Reset models
  - View model metrics
- **Configuration:**
  - Adjust training parameters (estimators, contamination)
- **Monitoring:**
  - View service logs
  - Check model status
  - System info

### 7. **README_MICROSERVICES.md**
Comprehensive documentation:
- Architecture diagram
- Service descriptions
- Quick start guide
- Configuration examples
- Troubleshooting tips
- Production deployment checklist

### 8. **.env.example**
Environment variable template with all required keys

## 📋 Execution Steps

### Step 1: Run Refactoring Script

```powershell
cd C:\Users\HoussamClap\Documents\Projects-app\iiot-predictive-maintenance

# Execute refactoring
.\refactor_structure.ps1
```

**This will:**
1. ✅ Create `infrastructure/` and `services/` directories
2. ✅ Move all Python files to `services/ai-engine/src/`
3. ✅ Move frontend to `services/web-frontend/`
4. ✅ Move simulator to `services/simulator/`
5. ✅ Delete `venv/` and `__pycache__/`
6. ✅ Create `requirements.txt` files
7. ✅ Generate config files for infrastructure

### Step 2: Prepare Docker Files

```powershell
# Rename docker-compose file
Rename-Item -Path "docker-compose-new.yml" -NewName "docker-compose.yml"

# Copy Dockerfiles to service directories
Copy-Item "Dockerfile.ai-engine" "services/ai-engine/Dockerfile"
Copy-Item "Dockerfile.simulator" "services/simulator/Dockerfile"
Copy-Item "Dockerfile.frontend" "services/web-frontend/Dockerfile"

# Copy Streamlit dashboard
Copy-Item "streamlit_admin.py" "services/ai-engine/dashboard/admin.py"
```

### Step 3: Configure Environment

```powershell
# Copy environment template
Copy-Item ".env.example" ".env"

# Edit .env file with your values
notepad .env
```

Add your credentials:
```env
NEXTAUTH_SECRET=your_32_character_random_string
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

### Step 4: Update Next.js Config

Add to `services/web-frontend/next.config.js`:

```javascript
module.exports = {
  output: 'standalone',
  // ... rest of config
}
```

### Step 5: Build & Deploy

```bash
# Build all containers
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

## 🌐 Access Services

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend Dashboard** | http://localhost:3001 | Main monitoring UI |
| **AI Admin Panel** | http://localhost:8501 | Train/manage AI models |
| **FastAPI Docs** | http://localhost:8000/docs | API documentation |
| **Grafana** | http://localhost:3000 | Metrics visualization |
| **InfluxDB** | http://localhost:8086 | Database UI |

## 🎯 Key Features

### AI Engine (Supervisord Multi-Process)

Three concurrent processes in one container:

1. **FastAPI Backend** (Port 8000)
   - `/api/live` - Real-time machine data
   - `/api/history` - Historical trends
   - `/api/stats` - 24h statistics
   - `/api/alerts` - Anomaly alerts
   - `/api/work-orders` - Maintenance tasks
   - `/api/patterns` - AI-detected patterns
   - `/health` - Health check

2. **Streamlit Dashboard** (Port 8501)
   - 🎯 Train AI models with custom parameters
   - 🔄 Retrain models on new data
   - 🗑️ Reset models
   - 📊 View model accuracy & metrics
   - 📜 Monitor service logs
   - ⚙️ Configure training settings

3. **MQTT Consumer** (Background Process)
   - Subscribes to sensor data
   - Runs real-time anomaly detection
   - Stores predictions in InfluxDB
   - Publishes results to MQTT

### Benefits of This Architecture

✅ **Isolated Services** - Each service in its own container
✅ **No Local Dependencies** - No more venv issues
✅ **Easy Scaling** - Scale individual services independently
✅ **Production Ready** - Health checks, auto-restart, logging
✅ **Multi-Process AI** - Three processes managed by Supervisord
✅ **Admin Interface** - Dedicated Streamlit dashboard for AI management
✅ **Network Isolation** - Services communicate via `iiot_net`
✅ **Volume Persistence** - Models and data persist across restarts

## 🔧 Common Commands

```bash
# View all services
docker-compose ps

# View logs for specific service
docker-compose logs -f ai-engine

# Restart a service
docker-compose restart simulator

# Rebuild and restart
docker-compose up -d --build ai-engine

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Access container shell
docker exec -it iiot_ai_engine bash

# Check Supervisord status
docker exec -it iiot_ai_engine supervisorctl status

# Restart a Supervisord process
docker exec -it iiot_ai_engine supervisorctl restart fastapi
```

## 🐛 Troubleshooting

### Service Won't Start

```bash
docker-compose logs [service-name]
```

### AI Engine Issues

```bash
# Check Supervisord
docker exec -it iiot_ai_engine supervisorctl status

# View process logs
docker exec -it iiot_ai_engine tail -f /app/logs/fastapi.out.log
docker exec -it iiot_ai_engine tail -f /app/logs/streamlit.out.log
docker exec -it iiot_ai_engine tail -f /app/logs/ai_consumer.out.log
```

### Network Issues

```bash
# Inspect network
docker network inspect iiot_network

# Test connectivity
docker exec -it iiot_ai_engine ping influxdb
docker exec -it iiot_ai_engine ping mosquitto
```

## 📊 Directory Structure After Refactoring

```
iiot-predictive-maintenance/
├── docker-compose.yml           ← Master orchestrator
├── refactor_structure.ps1       ← Automation script
├── .env                         ← Environment variables
├── .env.example                 ← Template
│
├── infrastructure/              ← Infrastructure configs
│   ├── mosquitto/
│   │   └── mosquitto.conf
│   ├── influxdb/
│   │   ├── data/
│   │   └── config/
│   └── grafana/
│       └── provisioning/
│
└── services/                    ← All microservices
    ├── ai-engine/               ← AI Brain
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   ├── src/
    │   │   ├── main.py          ← MQTT consumer
    │   │   ├── api.py           ← FastAPI
    │   │   ├── train_model.py   ← Training logic
    │   │   └── ...
    │   ├── dashboard/
    │   │   └── admin.py         ← Streamlit admin
    │   ├── models/              ← Model files (.pkl)
    │   └── data/                ← Training data
    │
    ├── simulator/               ← Data generator
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── simulate_wear.py
    │
    └── web-frontend/            ← Next.js UI
        ├── Dockerfile
        ├── package.json
        ├── app/
        ├── components/
        └── ...
```

## ✨ What's New

1. **Multi-Process AI Engine** - One container, three processes
2. **Streamlit Admin Dashboard** - Dedicated AI management UI
3. **Supervisord** - Process manager for AI engine
4. **Health Checks** - All services have health monitoring
5. **Network Isolation** - Dedicated Docker network
6. **Volume Mounts** - Persistent model and data storage
7. **Auto-Restart** - Services restart on failure
8. **Comprehensive Logging** - Logs for all processes

## 🎓 Next Steps

1. ✅ Run `refactor_structure.ps1`
2. ✅ Copy Dockerfiles to service directories
3. ✅ Rename `docker-compose-new.yml` → `docker-compose.yml`
4. ✅ Create `.env` from `.env.example`
5. ✅ Add `output: 'standalone'` to Next.js config
6. ✅ Run `docker-compose build`
7. ✅ Run `docker-compose up -d`
8. ✅ Access http://localhost:8501 to train AI
9. ✅ Access http://localhost:3001 for main dashboard

## 📞 Support

Check logs if issues occur:
```bash
docker-compose logs -f
```

Happy containerizing! 🐳

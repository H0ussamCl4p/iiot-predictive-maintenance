# 🏭 IIoT Predictive Maintenance - Microservices Architecture

## 📋 Overview

This is a fully Dockerized, production-ready IIoT (Industrial Internet of Things) system for predictive maintenance using AI/ML anomaly detection.

### 🎯 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Network                    │
│                         (iiot_net)                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Mosquitto   │  │   InfluxDB   │  │   Grafana    │      │
│  │  (MQTT)      │  │  (Time-Series│  │  (Monitoring)│      │
│  │  Port: 1883  │  │   Database)  │  │  Port: 3000  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘      │
│         │                  │                                  │
│  ┌──────▼──────────────────▼───────────────────┐            │
│  │          AI Engine (Supervisord)            │            │
│  │  ┌─────────────┐  ┌──────────────────────┐ │            │
│  │  │   FastAPI   │  │  Streamlit Dashboard │ │            │
│  │  │  Port: 8000 │  │     Port: 8501       │ │            │
│  │  │             │  │  (AI Admin Panel)    │ │            │
│  │  └─────────────┘  └──────────────────────┘ │            │
│  │  ┌──────────────────────────────────────┐  │            │
│  │  │    MQTT Consumer (main.py)           │  │            │
│  │  │    Real-time AI Processing           │  │            │
│  │  └──────────────────────────────────────┘  │            │
│  └─────────────────────────────────────────────┘            │
│                                                               │
│  ┌──────────────┐                ┌──────────────┐           │
│  │  Simulator   │                │   Next.js    │           │
│  │  (Wear Data) │                │   Frontend   │           │
│  │              │                │  Port: 3001  │           │
│  └──────────────┘                └──────────────┘           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- PowerShell (Windows) or Bash (Linux/Mac)
- Git

### Step 1: Refactor Project Structure

Run the refactoring script:

```powershell
# PowerShell
.\refactor_structure.ps1
```

This will:
- ✅ Create microservices directory structure
- ✅ Move files to their correct locations
- ✅ Clean up venv and __pycache__
- ✅ Generate requirements.txt for each service
- ✅ Create infrastructure configs

### Step 2: Rename docker-compose file

```powershell
mv docker-compose-new.yml docker-compose.yml
```

### Step 3: Create Environment File

Create a `.env` file in the project root:

```env
# NextAuth Configuration
NEXTAUTH_SECRET=your_secret_here
NEXTAUTH_URL=http://localhost:3001

# Google OAuth
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
```

### Step 4: Build & Run

```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## 📦 Services

### 1. **Infrastructure Layer**

#### Mosquitto (MQTT Broker)
- **Port:** 1883 (MQTT), 9001 (WebSocket)
- **Purpose:** Message broker for real-time sensor data
- **Config:** `infrastructure/mosquitto/mosquitto.conf`

#### InfluxDB (Time-Series Database)
- **Port:** 8086
- **Purpose:** Store sensor readings and predictions
- **Database:** `factory_data`
- **Credentials:** admin/admin123

#### Grafana (Monitoring)
- **Port:** 3000
- **Purpose:** Visualize metrics and create dashboards
- **Credentials:** admin/admin
- **Datasource:** Pre-configured InfluxDB connection

### 2. **AI Engine** (Core Service)

Multi-process container running **3 concurrent processes** via Supervisord:

#### Process A: FastAPI Backend
- **Port:** 8000
- **API Docs:** http://localhost:8000/docs
- **Endpoints:**
  - `GET /api/live` - Current machine state
  - `GET /api/history` - Historical data
  - `GET /api/stats` - 24h statistics
  - `GET /api/alerts` - Recent anomalies
  - `GET /api/work-orders` - Maintenance tasks
  - `GET /api/patterns` - AI pattern detection
  - `GET /health` - Health check

#### Process B: Streamlit Admin Dashboard
- **Port:** 8501
- **URL:** http://localhost:8501
- **Features:**
  - 🎯 Train/Retrain AI models
  - 📊 View model accuracy & metrics
  - 🔄 Reset models
  - 📜 View service logs
  - ⚙️ Configure training parameters

#### Process C: MQTT Consumer (main.py)
- Subscribes to sensor data from MQTT
- Runs anomaly detection in real-time
- Publishes predictions back to MQTT
- Stores results in InfluxDB

**File Structure:**
```
services/ai-engine/
├── Dockerfile
├── requirements.txt
├── src/
│   ├── main.py          # MQTT consumer & AI processing
│   ├── api.py           # FastAPI REST API
│   ├── train_model.py   # Model training logic
│   ├── reset_ai.py      # Model reset utility
│   └── virtual_plc.py   # PLC simulation
├── dashboard/
│   └── admin.py         # Streamlit admin interface
├── models/
│   └── anomaly_model.pkl
└── data/
    └── training_data.csv
```

### 3. **Simulator**

- **Purpose:** Generate synthetic machine wear data
- **Output:** MQTT messages simulating sensor readings
- **File:** `services/simulator/simulate_wear.py`

### 4. **Web Frontend** (Next.js)

- **Port:** 3001
- **URL:** http://localhost:3001
- **Features:**
  - 🔐 Google OAuth authentication
  - 📊 Real-time monitoring dashboard
  - 📈 Live charts & metrics
  - 🔔 Alert timeline
  - 💚 Machine health score
  - 🔧 Work order management
  - 🧠 AI pattern recognition
  - 📱 Fully responsive design

## 🔧 Configuration

### Mosquitto MQTT Broker

```conf
# infrastructure/mosquitto/mosquitto.conf
listener 1883
allow_anonymous true
```

### InfluxDB Datasource (Grafana)

```yaml
# infrastructure/grafana/provisioning/datasources/influxdb.yml
apiVersion: 1
datasources:
  - name: InfluxDB
    type: influxdb
    url: http://influxdb:8086
    database: factory_data
```

### AI Engine Environment Variables

```yaml
INFLUX_HOST: influxdb
INFLUX_PORT: 8086
INFLUX_DB: factory_data
MQTT_BROKER: mosquitto
MQTT_PORT: 1883
```

## 🛠️ Development

### View Service Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ai-engine
docker-compose logs -f web-frontend
docker-compose logs -f simulator
```

### Restart a Service

```bash
docker-compose restart ai-engine
```

### Rebuild a Service

```bash
docker-compose up -d --build ai-engine
```

### Access Container Shell

```bash
docker exec -it iiot_ai_engine /bin/bash
docker exec -it iiot_frontend /bin/sh
```

### View Supervisord Status (AI Engine)

```bash
docker exec -it iiot_ai_engine supervisorctl status
```

## 📊 Accessing Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend Dashboard | http://localhost:3001 | Google OAuth |
| AI Admin Panel | http://localhost:8501 | No auth |
| FastAPI Docs | http://localhost:8000/docs | No auth |
| Grafana | http://localhost:3000 | admin/admin |
| InfluxDB | http://localhost:8086 | admin/admin123 |

## 🔍 Monitoring

### Health Checks

All services have health checks configured:

```bash
# Check all services
docker-compose ps

# Manual health check
curl http://localhost:8000/health
curl http://localhost:8086/ping
```

### Metrics

View metrics in:
1. **Grafana** - http://localhost:3000
2. **InfluxDB** - Query directly
3. **AI Admin Dashboard** - http://localhost:8501

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs [service-name]

# Restart service
docker-compose restart [service-name]

# Full reset
docker-compose down
docker-compose up -d
```

### AI Engine Issues

```bash
# Check Supervisord status
docker exec -it iiot_ai_engine supervisorctl status

# View individual process logs
docker exec -it iiot_ai_engine tail -f /app/logs/fastapi.out.log
docker exec -it iiot_ai_engine tail -f /app/logs/streamlit.out.log
docker exec -it iiot_ai_engine tail -f /app/logs/ai_consumer.out.log
```

### Database Connection Issues

```bash
# Check InfluxDB
docker exec -it iiot_influxdb influx -execute 'SHOW DATABASES'

# Check network
docker network inspect iiot_network
```

## 📝 Project Structure

```
iiot-predictive-maintenance/
├── docker-compose.yml           # Master orchestrator
├── refactor_structure.ps1       # Refactoring script
├── Dockerfile.ai-engine         # AI engine template
├── Dockerfile.simulator         # Simulator template
├── Dockerfile.frontend          # Frontend template
├── .env                         # Environment variables
├── infrastructure/
│   ├── mosquitto/
│   │   └── mosquitto.conf
│   ├── influxdb/
│   │   ├── data/
│   │   └── config/
│   └── grafana/
│       └── provisioning/
└── services/
    ├── ai-engine/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   ├── src/
    │   ├── dashboard/
    │   ├── models/
    │   └── data/
    ├── simulator/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── simulate_wear.py
    └── web-frontend/
        ├── Dockerfile
        ├── package.json
        └── [Next.js files]
```

## 🎓 Training AI Models

### Via Streamlit Admin Dashboard (Recommended)

1. Go to http://localhost:8501
2. Click "🎯 Train Model"
3. Adjust parameters if needed
4. Monitor training progress
5. View accuracy metrics

### Via API

```bash
# Trigger training via API (if endpoint exists)
curl -X POST http://localhost:8000/api/train
```

### Manual Training

```bash
docker exec -it iiot_ai_engine python src/train_model.py
```

## 🚢 Production Deployment

### Security Checklist

- [ ] Change default passwords (InfluxDB, Grafana)
- [ ] Enable authentication on Mosquitto
- [ ] Use secrets management for API keys
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up backup strategy

### Scaling

```yaml
# Scale simulator instances
docker-compose up -d --scale simulator=3
```

## 📄 License

MIT License

## 👥 Contributors

IIoT Predictive Maintenance Team

## 🔗 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Docker Documentation](https://docs.docker.com/)
- [InfluxDB 1.8 Documentation](https://docs.influxdata.com/influxdb/v1.8/)

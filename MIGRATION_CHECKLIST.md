# 📋 IIoT Microservices Migration Checklist

## ✅ Phase 1: Refactoring (Automated)

Run `refactor_structure.ps1`:

- [ ] Infrastructure directories created
  - [ ] `infrastructure/mosquitto/`
  - [ ] `infrastructure/influxdb/`
  - [ ] `infrastructure/grafana/`
- [ ] Services directories created
  - [ ] `services/ai-engine/src/`
  - [ ] `services/ai-engine/dashboard/`
  - [ ] `services/ai-engine/models/`
  - [ ] `services/simulator/`
  - [ ] `services/web-frontend/`
- [ ] Python files moved to `services/ai-engine/src/`
  - [ ] `main.py`
  - [ ] `api_server.py` → `api.py`
  - [ ] `train_model.py`
  - [ ] `reset_ai.py`
  - [ ] `virtual_plc.py`
- [ ] Simulator files moved
  - [ ] `simulate_wear.py`
  - [ ] `generate_training_data.py`
- [ ] Frontend files moved to `services/web-frontend/`
- [ ] Old files cleaned up
  - [ ] `venv/` deleted
  - [ ] `__pycache__/` deleted
  - [ ] Loose root files removed
- [ ] Requirements files generated
  - [ ] `services/ai-engine/requirements.txt`
  - [ ] `services/simulator/requirements.txt`
- [ ] Config files created
  - [ ] `infrastructure/mosquitto/mosquitto.conf`
  - [ ] `infrastructure/influxdb/config/init.iql`
  - [ ] `infrastructure/grafana/provisioning/datasources/influxdb.yml`

## ✅ Phase 2: Docker Setup (Semi-Automated)

Run `setup_docker.ps1`:

- [ ] Dockerfiles copied to services
  - [ ] `services/ai-engine/Dockerfile`
  - [ ] `services/simulator/Dockerfile`
  - [ ] `services/web-frontend/Dockerfile`
- [ ] Streamlit dashboard set up
  - [ ] `services/ai-engine/dashboard/admin.py`
- [ ] Docker Compose renamed
  - [ ] `docker-compose-new.yml` → `docker-compose.yml`
  - [ ] Old `docker-compose.yml` backed up as `docker-compose.old.yml`
- [ ] Environment file created
  - [ ] `.env` created from `.env.example`

## ✅ Phase 3: Manual Configuration

### 1. Environment Variables

Edit `.env` file:

```bash
notepad .env
```

- [ ] Set `NEXTAUTH_SECRET` (generate with: `openssl rand -base64 32`)
- [ ] Add `GOOGLE_CLIENT_ID`
- [ ] Add `GOOGLE_CLIENT_SECRET`
- [ ] Verify `NEXTAUTH_URL=http://localhost:3001`

### 2. Next.js Configuration

Edit `services/web-frontend/next.config.ts`:

```typescript
const nextConfig = {
  output: 'standalone',  // ← Add this line
  // ... rest of config
}
```

- [ ] Added `output: 'standalone'` to Next.js config

### 3. Verify File Structure

```
services/
├── ai-engine/
│   ├── Dockerfile ✓
│   ├── requirements.txt ✓
│   ├── src/
│   │   ├── main.py ✓
│   │   ├── api.py ✓
│   │   ├── train_model.py ✓
│   │   ├── reset_ai.py ✓
│   │   └── virtual_plc.py ✓
│   ├── dashboard/
│   │   └── admin.py ✓
│   ├── models/ ✓
│   └── data/ ✓
├── simulator/
│   ├── Dockerfile ✓
│   ├── requirements.txt ✓
│   ├── simulate_wear.py ✓
│   └── generate_training_data.py ✓
└── web-frontend/
    ├── Dockerfile ✓
    ├── package.json ✓
    ├── next.config.ts ✓ (with output: 'standalone')
    └── ... (Next.js files)
```

## ✅ Phase 4: Build & Deploy

### 1. Build Docker Images

```bash
docker-compose build
```

- [ ] Mosquitto image pulled
- [ ] InfluxDB image pulled
- [ ] Grafana image pulled
- [ ] AI Engine image built successfully
- [ ] Simulator image built successfully
- [ ] Web Frontend image built successfully

### 2. Start Services

```bash
docker-compose up -d
```

- [ ] All containers started
- [ ] No error messages in logs

### 3. Verify Health Checks

```bash
docker-compose ps
```

- [ ] `iiot_mosquitto` - healthy
- [ ] `iiot_influxdb` - healthy
- [ ] `iiot_grafana` - running
- [ ] `iiot_ai_engine` - healthy
- [ ] `iiot_simulator` - running
- [ ] `iiot_frontend` - running

### 4. Check Logs

```bash
docker-compose logs -f
```

- [ ] No error messages
- [ ] Services connecting successfully
- [ ] AI engine processes running (FastAPI, Streamlit, AI Consumer)

## ✅ Phase 5: Verification

### 1. Access Services

- [ ] Frontend: http://localhost:3001 (loads successfully)
- [ ] AI Admin: http://localhost:8501 (Streamlit dashboard visible)
- [ ] API Docs: http://localhost:8000/docs (Swagger UI accessible)
- [ ] Grafana: http://localhost:3000 (login works: admin/admin)
- [ ] InfluxDB: http://localhost:8086/ping (returns "pong")

### 2. Test Functionality

#### Frontend (http://localhost:3001)
- [ ] Google OAuth login works
- [ ] Dashboard loads with metrics
- [ ] Real-time data updates
- [ ] Charts render correctly
- [ ] Work orders display
- [ ] Pattern analysis shows

#### AI Admin Dashboard (http://localhost:8501)
- [ ] Dashboard loads
- [ ] Model status visible
- [ ] "Train Model" button works
- [ ] Logs display correctly
- [ ] System info accurate

#### FastAPI (http://localhost:8000/docs)
- [ ] `/api/live` returns data
- [ ] `/api/history` returns historical data
- [ ] `/api/stats` returns statistics
- [ ] `/api/alerts` returns alerts
- [ ] `/api/work-orders` returns work orders
- [ ] `/api/patterns` returns patterns
- [ ] `/health` returns healthy status

### 3. Test AI Pipeline

- [ ] Simulator publishes to MQTT
- [ ] AI consumer receives MQTT messages
- [ ] Anomaly detection runs
- [ ] Results stored in InfluxDB
- [ ] Predictions visible in frontend

### 4. Test Multi-Process Container

Check AI Engine processes:

```bash
docker exec -it iiot_ai_engine supervisorctl status
```

- [ ] `fastapi` - RUNNING
- [ ] `streamlit` - RUNNING
- [ ] `ai_consumer` - RUNNING

## ✅ Phase 6: Production Readiness (Optional)

### Security

- [ ] Change default Grafana password (admin/admin)
- [ ] Change default InfluxDB password
- [ ] Enable MQTT authentication
- [ ] Use Docker secrets for sensitive data
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules

### Monitoring

- [ ] Set up Grafana dashboards
- [ ] Configure alerts in Grafana
- [ ] Set up log aggregation
- [ ] Configure backup strategy for InfluxDB

### Scaling

- [ ] Test scaling simulator: `docker-compose up -d --scale simulator=3`
- [ ] Monitor resource usage
- [ ] Configure resource limits in docker-compose.yml

### Documentation

- [ ] Update README with production deployment steps
- [ ] Document environment variables
- [ ] Create troubleshooting guide
- [ ] Add architecture diagrams

## 🐛 Troubleshooting

If any step fails, check:

```bash
# View logs
docker-compose logs [service-name]

# Restart service
docker-compose restart [service-name]

# Rebuild service
docker-compose up -d --build [service-name]

# Check network
docker network inspect iiot_network

# Access container shell
docker exec -it [container-name] bash
```

## 📊 Success Criteria

✅ All services running and healthy
✅ Frontend accessible and functional
✅ AI Admin dashboard operational
✅ API endpoints responding correctly
✅ Data flowing: Simulator → MQTT → AI → InfluxDB → Frontend
✅ Real-time anomaly detection working
✅ Work orders and patterns displaying
✅ Logs show no critical errors

## 🎉 Completion

Once all checkboxes are ticked, your IIoT system is successfully migrated to a Dockerized microservices architecture!

**Final Command:**

```bash
docker-compose ps
```

You should see all 6 containers running:
- iiot_mosquitto
- iiot_influxdb
- iiot_grafana
- iiot_ai_engine
- iiot_simulator
- iiot_frontend

🚀 **Congratulations! Your IIoT platform is now production-ready!**

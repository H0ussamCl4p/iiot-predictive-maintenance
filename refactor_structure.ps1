# IIoT Project Refactoring Script
# Transforms the project into a Dockerized Microservices Architecture

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  IIoT Microservices Refactoring" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create New Directory Structure
Write-Host "[1/7] Creating new directory structure..." -ForegroundColor Yellow

$directories = @(
    "infrastructure/mosquitto",
    "infrastructure/influxdb/data",
    "infrastructure/influxdb/config",
    "infrastructure/grafana/provisioning/dashboards",
    "infrastructure/grafana/provisioning/datasources",
    "services/ai-engine/src",
    "services/ai-engine/models",
    "services/ai-engine/dashboard",
    "services/ai-engine/data",
    "services/simulator",
    "services/web-frontend"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    Write-Host "  Created: $dir" -ForegroundColor Green
}

# Step 2: Move AI Engine Files
Write-Host "`n[2/7] Moving AI Engine files..." -ForegroundColor Yellow

$aiFiles = @{
    "main.py" = "services/ai-engine/src/main.py"
    "train_model.py" = "services/ai-engine/src/train_model.py"
    "api_server.py" = "services/ai-engine/src/api.py"
    "reset_ai.py" = "services/ai-engine/src/reset_ai.py"
    "virtual_plc.py" = "services/ai-engine/src/virtual_plc.py"
}

foreach ($source in $aiFiles.Keys) {
    if (Test-Path $source) {
        Move-Item -Path $source -Destination $aiFiles[$source] -Force
        Write-Host "  Moved: $source -> $($aiFiles[$source])" -ForegroundColor Green
    }
}

# Move model files if they exist
if (Test-Path "*.pkl") {
    Get-ChildItem -Path "*.pkl" | ForEach-Object {
        Move-Item -Path $_.FullName -Destination "services/ai-engine/models/" -Force
    }
    Write-Host "  Moved: *.pkl -> services/ai-engine/models/" -ForegroundColor Green
}

# Move data folder if exists
if (Test-Path "data") {
    Get-ChildItem -Path "data" | ForEach-Object {
        Move-Item -Path $_.FullName -Destination "services/ai-engine/data/" -Force
    }
    Remove-Item -Path "data" -Force -Recurse -ErrorAction SilentlyContinue
    Write-Host "  Moved: data/ -> services/ai-engine/data/" -ForegroundColor Green
}

# Step 3: Move Simulator Files
Write-Host "`n[3/7] Moving Simulator files..." -ForegroundColor Yellow

if (Test-Path "simulate_wear.py") {
    Move-Item -Path "simulate_wear.py" -Destination "services/simulator/simulate_wear.py" -Force
    Write-Host "  Moved: simulate_wear.py -> services/simulator/" -ForegroundColor Green
}

if (Test-Path "generate_training_data.py") {
    Move-Item -Path "generate_training_data.py" -Destination "services/simulator/generate_training_data.py" -Force
    Write-Host "  Moved: generate_training_data.py -> services/simulator/" -ForegroundColor Green
}

# Step 4: Move Frontend Files
Write-Host "`n[4/7] Moving Frontend files..." -ForegroundColor Yellow

if (Test-Path "frontend") {
    $frontendItems = Get-ChildItem -Path "frontend" -Force
    foreach ($item in $frontendItems) {
        Move-Item -Path $item.FullName -Destination "services/web-frontend/" -Force
    }
    Remove-Item -Path "frontend" -Force -Recurse -ErrorAction SilentlyContinue
    Write-Host "  Moved: frontend/* -> services/web-frontend/" -ForegroundColor Green
}

# Step 5: Cleanup Old Files
Write-Host "`n[5/7] Cleaning up old files and directories..." -ForegroundColor Yellow

$cleanupItems = @(
    "venv",
    "__pycache__",
    ".pytest_cache"
)

foreach ($item in $cleanupItems) {
    if (Test-Path $item) {
        Remove-Item -Path $item -Force -Recurse -ErrorAction SilentlyContinue
        Write-Host "  Removed: $item" -ForegroundColor Red
    }
}

# Clean up any remaining .pyc and __pycache__
Get-ChildItem -Path . -Include __pycache__,*.pyc -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue

# Step 6: Create requirements.txt files
Write-Host "`n[6/7] Creating requirements.txt files..." -ForegroundColor Yellow

# AI Engine requirements
$aiRequirements = "fastapi==0.104.1
uvicorn[standard]==0.24.0
influxdb==5.3.1
paho-mqtt==1.6.1
scikit-learn==1.3.2
numpy==1.24.3
pandas==2.0.3
python-multipart==0.0.6
streamlit==1.29.0
supervisor==4.2.5"

Set-Content -Path "services/ai-engine/requirements.txt" -Value $aiRequirements
Write-Host "  Created: services/ai-engine/requirements.txt" -ForegroundColor Green

# Simulator requirements
$simRequirements = "paho-mqtt==1.6.1
numpy==1.24.3
influxdb==5.3.1"

Set-Content -Path "services/simulator/requirements.txt" -Value $simRequirements
Write-Host "  Created: services/simulator/requirements.txt" -ForegroundColor Green

# Step 7: Create configuration files
Write-Host "`n[7/7] Creating configuration files..." -ForegroundColor Yellow

# Mosquitto config
$mosquittoConfig = "listener 1883
allow_anonymous true"

Set-Content -Path "infrastructure/mosquitto/mosquitto.conf" -Value $mosquittoConfig
Write-Host "  Created: infrastructure/mosquitto/mosquitto.conf" -ForegroundColor Green

# InfluxDB init script
$influxInit = "CREATE DATABASE factory_data"

Set-Content -Path "infrastructure/influxdb/config/init.iql" -Value $influxInit
Write-Host "  Created: infrastructure/influxdb/config/init.iql" -ForegroundColor Green

# Grafana datasource
$grafanaDatasource = "apiVersion: 1

datasources:
  - name: InfluxDB
    type: influxdb
    access: proxy
    url: http://influxdb:8086
    database: factory_data
    isDefault: true
    editable: true"

Set-Content -Path "infrastructure/grafana/provisioning/datasources/influxdb.yml" -Value $grafanaDatasource
Write-Host "  Created: infrastructure/grafana/provisioning/datasources/influxdb.yml" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Refactoring Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Run: .\setup_docker.ps1" -ForegroundColor White
Write-Host "  2. Edit .env file with your credentials" -ForegroundColor White
Write-Host "  3. Run: docker-compose build" -ForegroundColor White
Write-Host "  4. Run: docker-compose up -d" -ForegroundColor White
Write-Host ""
Write-Host "Access services at:" -ForegroundColor Yellow
Write-Host "  - Frontend: http://localhost:3001" -ForegroundColor Cyan
Write-Host "  - API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  - AI Dashboard: http://localhost:8501" -ForegroundColor Cyan
Write-Host "  - Grafana: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""

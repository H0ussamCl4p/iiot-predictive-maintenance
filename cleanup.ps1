# ============================================================
# IIoT Predictive Maintenance - Project Cleanup Script
# Migrating from Old Stack (Streamlit/CSV) to New Stack (Docker/InfluxDB/Grafana)
# ============================================================

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "[IIoT Project Cleanup - Archiving Old Stack]" -ForegroundColor Yellow
Write-Host ("=" * 61) -ForegroundColor Cyan

# Define the archive folder
$archiveFolder = "_archive"
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$archivePath = Join-Path $PSScriptRoot "$archiveFolder\backup_$timestamp"

# Create archive directory
Write-Host "`n[*] Creating backup archive..." -ForegroundColor Green
New-Item -ItemType Directory -Path $archivePath -Force | Out-Null
Write-Host "   [OK] Archive created: $archivePath" -ForegroundColor Gray

# Files to archive (OLD STACK)
$filesToArchive = @(
    "dashboard.py",           # Streamlit dashboard - replaced by Grafana
    "virtual_plc.py",         # Old simulator - replaced by simulate_wear.py
    "live_data.csv",          # CSV logs - replaced by InfluxDB
    "reset_ai.py",            # Temp script - no longer needed
    "generate_training_data.py"  # Only needed once - can archive
)

# Move files to archive
Write-Host "`n[*] Archiving old files..." -ForegroundColor Green
$archivedCount = 0
foreach ($file in $filesToArchive) {
    $sourcePath = Join-Path $PSScriptRoot $file
    if (Test-Path $sourcePath) {
        $destPath = Join-Path $archivePath $file
        Move-Item -Path $sourcePath -Destination $destPath -Force
        Write-Host "   [OK] Archived: $file" -ForegroundColor Gray
        $archivedCount++
    }
    else {
        Write-Host "   [SKIP] Not found: $file" -ForegroundColor DarkGray
    }
}

# Generate new requirements.txt based on active files
Write-Host "`n[*] Generating fresh requirements.txt..." -ForegroundColor Green

$requirements = @"
# IIoT Predictive Maintenance - Production Stack
# Docker + InfluxDB + Grafana Architecture
# Generated on $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

# Core ML & Data Processing
pandas==2.2.0
numpy==1.26.3
scikit-learn==1.4.0
joblib==1.3.2

# MQTT Communication
paho-mqtt==2.1.0

# InfluxDB Time-Series Database
influxdb==5.3.2

# Grafana API Configuration
requests==2.32.3

# Additional Dependencies
python-dateutil>=2.6.0
pytz>=2024.1
"@

$requirementsPath = Join-Path $PSScriptRoot "requirements.txt"
$requirements | Out-File -FilePath $requirementsPath -Encoding UTF8 -Force
Write-Host "   [OK] requirements.txt regenerated" -ForegroundColor Gray

# Display final project structure
Write-Host "`n[*] Clean Project Structure:" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

# Get remaining Python files
$remainingFiles = Get-ChildItem -Path $PSScriptRoot -Filter "*.py" | Select-Object -ExpandProperty Name
$remainingFiles = $remainingFiles | Sort-Object

Write-Host "`n[Python Scripts - Active]" -ForegroundColor Yellow
foreach ($file in $remainingFiles) {
    $description = switch ($file) {
        "main.py"           { "- Core AI Engine (MQTT to InfluxDB)" }
        "simulate_wear.py"  { "- Machine Degradation Simulator" }
        "train_model.py"    { "- ML Model Training Script" }
        "setup_grafana.py"  { "- Grafana Auto-Configuration" }
        default             { "- Active script" }
    }
    Write-Host "   $file" -NoNewline -ForegroundColor White
    Write-Host " $description" -ForegroundColor Gray
}

Write-Host "`n[Data & Models]" -ForegroundColor Yellow
Write-Host "   data/" -NoNewline -ForegroundColor White
Write-Host " - Training datasets" -ForegroundColor Gray
Write-Host "   model_brain.pkl" -NoNewline -ForegroundColor White
Write-Host " - Trained Isolation Forest" -ForegroundColor Gray
Write-Host "   scaler.pkl" -NoNewline -ForegroundColor White
Write-Host " - Feature scaler" -ForegroundColor Gray

Write-Host "`n[Infrastructure]" -ForegroundColor Yellow
Write-Host "   docker-compose.yml" -NoNewline -ForegroundColor White
Write-Host " - InfluxDB + Grafana containers" -ForegroundColor Gray

Write-Host "`n[Archived Files]" -ForegroundColor Yellow
Write-Host "   $archiveFolder\backup_$timestamp\" -NoNewline -ForegroundColor White
Write-Host " - $archivedCount files backed up" -ForegroundColor Gray

# Summary
Write-Host "`n" + ("=" * 61) -ForegroundColor Cyan
Write-Host "[SUCCESS] Cleanup Complete!" -ForegroundColor Green
Write-Host ("=" * 61) -ForegroundColor Cyan

Write-Host "`n[Summary]" -ForegroundColor Yellow
Write-Host "   - Archived: $archivedCount old files" -ForegroundColor Gray
Write-Host "   - Remaining: $($remainingFiles.Count) active Python scripts" -ForegroundColor Gray
Write-Host "   - Architecture: Docker > InfluxDB > Grafana" -ForegroundColor Gray
Write-Host "   - Backup location: $archivePath" -ForegroundColor Gray

Write-Host "`n[Next Steps]" -ForegroundColor Yellow
Write-Host "   1. Review the archive if needed: cd $archiveFolder" -ForegroundColor Gray
Write-Host "   2. Start services: docker-compose up -d" -ForegroundColor Gray
Write-Host "   3. Run simulator: python simulate_wear.py" -ForegroundColor Gray
Write-Host "   4. Run AI engine: python main.py" -ForegroundColor Gray
Write-Host "   5. View dashboard: http://localhost:3000" -ForegroundColor Gray

Write-Host "`n[DONE] Your project is now production-ready!" -ForegroundColor Green
Write-Host ""

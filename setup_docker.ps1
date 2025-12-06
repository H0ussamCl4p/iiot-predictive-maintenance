# Docker Setup Script
# Prepares Docker files and configuration for microservices deployment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Docker Setup for IIoT Project" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Copy Dockerfiles to service directories
Write-Host "[1/5] Copying Dockerfiles to service directories..." -ForegroundColor Yellow

if (Test-Path "Dockerfile.ai-engine") {
    Copy-Item -Path "Dockerfile.ai-engine" -Destination "services/ai-engine/Dockerfile" -Force
    Write-Host "  Copied: Dockerfile.ai-engine -> services/ai-engine/Dockerfile" -ForegroundColor Green
}

if (Test-Path "Dockerfile.simulator") {
    Copy-Item -Path "Dockerfile.simulator" -Destination "services/simulator/Dockerfile" -Force
    Write-Host "  Copied: Dockerfile.simulator -> services/simulator/Dockerfile" -ForegroundColor Green
}

if (Test-Path "Dockerfile.frontend") {
    Copy-Item -Path "Dockerfile.frontend" -Destination "services/web-frontend/Dockerfile" -Force
    Write-Host "  Copied: Dockerfile.frontend -> services/web-frontend/Dockerfile" -ForegroundColor Green
}

# Step 2: Setup Streamlit dashboard
Write-Host "`n[2/5] Setting up Streamlit admin dashboard..." -ForegroundColor Yellow

if (Test-Path "streamlit_admin.py") {
    Copy-Item -Path "streamlit_admin.py" -Destination "services/ai-engine/dashboard/admin.py" -Force
    Write-Host "  Copied: streamlit_admin.py -> services/ai-engine/dashboard/admin.py" -ForegroundColor Green
}

# Step 3: Prepare docker-compose.yml
Write-Host "`n[3/5] Preparing docker-compose.yml..." -ForegroundColor Yellow

if (Test-Path "docker-compose.yml") {
    Move-Item -Path "docker-compose.yml" -Destination "docker-compose.old.yml" -Force
    Write-Host "  Backed up: docker-compose.yml -> docker-compose.old.yml" -ForegroundColor Yellow
}

if (Test-Path "docker-compose-new.yml") {
    Rename-Item -Path "docker-compose-new.yml" -NewName "docker-compose.yml" -Force
    Write-Host "  Renamed: docker-compose-new.yml -> docker-compose.yml" -ForegroundColor Green
}

# Step 4: Create environment file
Write-Host "`n[4/5] Creating environment file..." -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item -Path ".env.example" -Destination ".env" -Force
        Write-Host "  Created: .env from .env.example" -ForegroundColor Green
        Write-Host "  WARNING: Edit .env file and add your Google OAuth credentials!" -ForegroundColor Red
    }
} else {
    Write-Host "  .env file already exists (skipped)" -ForegroundColor Yellow
}

# Step 5: Check Next.js configuration
Write-Host "`n[5/5] Checking Next.js configuration..." -ForegroundColor Yellow

$nextConfigPath = "services/web-frontend/next.config.ts"
if (Test-Path $nextConfigPath) {
    $configContent = Get-Content -Path $nextConfigPath -Raw
    if ($configContent -match "output.*standalone") {
        Write-Host "  Next.js standalone output already configured" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: Add this to next.config.ts:" -ForegroundColor Red
        Write-Host "    output: 'standalone'," -ForegroundColor Yellow
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Docker Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Edit .env file with your credentials:" -ForegroundColor White
Write-Host "     notepad .env" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Add to services/web-frontend/next.config.ts:" -ForegroundColor White
Write-Host "     output: 'standalone'," -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. Build all containers:" -ForegroundColor White
Write-Host "     docker-compose build" -ForegroundColor Cyan
Write-Host ""
Write-Host "  4. Start all services:" -ForegroundColor White
Write-Host "     docker-compose up -d" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access Services:" -ForegroundColor Yellow
Write-Host "  - Frontend:    http://localhost:3001" -ForegroundColor Cyan
Write-Host "  - AI Admin:    http://localhost:8501" -ForegroundColor Cyan
Write-Host "  - API Docs:    http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  - Grafana:     http://localhost:3000" -ForegroundColor Cyan
Write-Host ""

# Quick Docker Build Script
# Optimized for fast rebuilds with layer caching

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Fast Docker Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Building optimized Docker images..." -ForegroundColor Yellow
Write-Host "  - Split requirements for better caching" -ForegroundColor White
Write-Host "  - Volume mounts for instant code updates" -ForegroundColor White
Write-Host "  - Minimal .dockerignore for faster context" -ForegroundColor White
Write-Host ""

# Build all services
docker-compose build

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  Build Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To start all services:" -ForegroundColor Yellow
    Write-Host "  docker-compose up -d" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "After first build, code changes are instant (no rebuild needed):" -ForegroundColor Yellow
    Write-Host "  - AI Engine: Edit src/ or dashboard/ files" -ForegroundColor White
    Write-Host "  - Simulator: Edit simulate_wear.py" -ForegroundColor White
    Write-Host "  - Frontend: Use 'npm run dev' in services/web-frontend/" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "`nBuild failed. Check errors above." -ForegroundColor Red
}

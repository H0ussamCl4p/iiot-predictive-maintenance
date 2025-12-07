# ==========================================
# Docker Build Performance Benchmark
# ==========================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Docker Build Performance Test" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Enable BuildKit
$env:DOCKER_BUILDKIT = "1"
$env:COMPOSE_DOCKER_CLI_BUILD = "1"

Write-Host "BuildKit Status: ENABLED`n" -ForegroundColor Green

# Test 1: Clean Build (no cache)
Write-Host "`n[TEST 1] Clean Build (no cache)" -ForegroundColor Yellow
Write-Host "Removing all build cache..." -ForegroundColor Gray
docker builder prune -af | Out-Null

Write-Host "Starting clean build..." -ForegroundColor Gray
$cleanStart = Get-Date
docker-compose build --parallel --no-cache 2>&1 | Out-Null
$cleanEnd = Get-Date
$cleanDuration = ($cleanEnd - $cleanStart).TotalSeconds

Write-Host "Clean Build Time: $([math]::Round($cleanDuration, 2))s" -ForegroundColor $(if ($cleanDuration -lt 60) { "Green" } else { "Red" })

# Test 2: Incremental Build (with cache)
Write-Host "`n[TEST 2] Incremental Build (with cache)" -ForegroundColor Yellow
Write-Host "Rebuilding with cache..." -ForegroundColor Gray
$cacheStart = Get-Date
docker-compose build --parallel 2>&1 | Out-Null
$cacheEnd = Get-Date
$cacheDuration = ($cacheEnd - $cacheStart).TotalSeconds

Write-Host "Cached Build Time: $([math]::Round($cacheDuration, 2))s" -ForegroundColor $(if ($cacheDuration -lt 10) { "Green" } elseif ($cacheDuration -lt 30) { "Yellow" } else { "Red" })

# Test 3: Startup Time
Write-Host "`n[TEST 3] Container Startup" -ForegroundColor Yellow
Write-Host "Starting all services..." -ForegroundColor Gray

# Stop any running containers first
docker-compose down 2>&1 | Out-Null

$startupStart = Get-Date
docker-compose up -d 2>&1 | Out-Null
Start-Sleep -Seconds 5

# Wait for health checks
$timeout = 60
$elapsed = 0
$healthy = $false

while ($elapsed -lt $timeout -and -not $healthy) {
    $containers = docker-compose ps --format json | ConvertFrom-Json
    $allHealthy = $true
    
    foreach ($container in $containers) {
        if ($container.Health -and $container.Health -ne "healthy") {
            $allHealthy = $false
            break
        }
    }
    
    if ($allHealthy) {
        $healthy = $true
    } else {
        Start-Sleep -Seconds 2
        $elapsed += 2
    }
}

$startupEnd = Get-Date
$startupDuration = ($startupEnd - $startupStart).TotalSeconds

Write-Host "Startup Time: $([math]::Round($startupDuration, 2))s" -ForegroundColor $(if ($startupDuration -lt 30) { "Green" } elseif ($startupDuration -lt 60) { "Yellow" } else { "Red" })

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "PERFORMANCE SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nClean Build:       $([math]::Round($cleanDuration, 2))s" -ForegroundColor White
Write-Host "Cached Build:      $([math]::Round($cacheDuration, 2))s" -ForegroundColor White
Write-Host "Startup Time:      $([math]::Round($startupDuration, 2))s" -ForegroundColor White
Write-Host "Total (cached):    $([math]::Round($cacheDuration + $startupDuration, 2))s" -ForegroundColor White

$totalTarget = 30
$totalCached = $cacheDuration + $startupDuration

Write-Host "`nTarget: <$($totalTarget)s total" -ForegroundColor Gray
if ($totalCached -lt $totalTarget) {
    Write-Host "STATUS: TARGET MET!" -ForegroundColor Green
} else {
    $overTime = [math]::Round($totalCached - $totalTarget, 2)
    Write-Host "STATUS: Needs optimization ($overTime seconds over target)" -ForegroundColor Red
}

# Image sizes
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "IMAGE SIZES" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

docker images --format "table {{.Repository}}\t{{.Size}}" | Select-String "iiot"

Write-Host ""

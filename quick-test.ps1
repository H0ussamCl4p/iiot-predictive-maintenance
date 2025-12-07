# Quick Docker Build Test
# Tests incremental build speed only

Write-Host "`n=== Quick Build Test ===" -ForegroundColor Cyan
Write-Host "Testing incremental build speed...`n" -ForegroundColor Gray

$env:DOCKER_BUILDKIT = "1"

# Test incremental build
$start = Get-Date
docker-compose build --parallel 2>&1 | Out-Null
$end = Get-Date
$duration = ($end - $start).TotalSeconds

Write-Host "Build Time: $([math]::Round($duration, 2))s" -ForegroundColor $(if ($duration -lt 30) { "Green" } else { "Yellow" })

# Show images
Write-Host "`n=== Images ===" -ForegroundColor Cyan
docker images --format "table {{.Repository}}\t{{.Size}}" | Select-String "iiot"

Write-Host "`nDone!" -ForegroundColor Green

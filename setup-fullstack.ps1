# Full-Stack IIoT Application Setup Script
# Run this in PowerShell from your project root

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "[IIoT Full-Stack Application Setup]" -ForegroundColor Yellow
Write-Host ("=" * 71) -ForegroundColor Cyan

# Step 1: Install FastAPI dependencies
Write-Host "`n[Step 1] Installing Python Backend Dependencies..." -ForegroundColor Green
pip install fastapi uvicorn influxdb python-multipart

# Step 2: Test the API server
Write-Host "`n[Step 2] Testing FastAPI Server..." -ForegroundColor Green
Write-Host "To start the backend, run:" -ForegroundColor Yellow
Write-Host "  python api_server.py" -ForegroundColor White
Write-Host "`nAPI will be available at:" -ForegroundColor Yellow
Write-Host "  http://localhost:8000" -ForegroundColor White
Write-Host "  http://localhost:8000/docs (Swagger UI)" -ForegroundColor White

# Step 3: Create Next.js project
Write-Host "`n[Step 3] Creating Next.js Frontend..." -ForegroundColor Green
Write-Host "Run the following commands:" -ForegroundColor Yellow
Write-Host @"
  
  npx create-next-app@latest iiot-frontend --typescript --tailwind --app
  cd iiot-frontend
  npm install next-auth@beta recharts swr lucide-react date-fns
  
"@ -ForegroundColor White

# Step 4: File structure guide
Write-Host "`n[Step 4] Next.js File Structure" -ForegroundColor Green
Write-Host @"
Copy the component files from 'nextjs-components/' folder to your Next.js project:

  nextjs-components/types-index.ts               -> iiot-frontend/types/index.ts
  nextjs-components/lib-auth.ts                  -> iiot-frontend/lib/auth.ts
  nextjs-components/api-auth-nextauth-route.ts   -> iiot-frontend/app/api/auth/[...nextauth]/route.ts
  nextjs-components/app-page.tsx                 -> iiot-frontend/app/page.tsx
  nextjs-components/app-dashboard-page.tsx       -> iiot-frontend/app/dashboard/page.tsx
  nextjs-components/MetricCard.tsx               -> iiot-frontend/components/MetricCard.tsx
  nextjs-components/StatusBadge.tsx              -> iiot-frontend/components/StatusBadge.tsx
  nextjs-components/LiveChart.tsx                -> iiot-frontend/components/LiveChart.tsx

"@ -ForegroundColor White

# Step 5: Environment variables
Write-Host "`n[Step 5] Environment Configuration" -ForegroundColor Green
Write-Host "Create 'iiot-frontend/.env.local' with:" -ForegroundColor Yellow
Write-Host @"

NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-generate-with-openssl
GITHUB_CLIENT_ID=your-github-oauth-client-id
GITHUB_CLIENT_SECRET=your-github-oauth-secret
NEXT_PUBLIC_API_URL=http://localhost:8000

"@ -ForegroundColor White

Write-Host "Generate NEXTAUTH_SECRET with:" -ForegroundColor Yellow
Write-Host "  openssl rand -base64 32" -ForegroundColor White

# Step 6: Running the stack
Write-Host "`n[Step 6] Running the Full Stack" -ForegroundColor Green
Write-Host @"

Terminal 1 - InfluxDB:
  docker-compose up -d

Terminal 2 - Data Simulator:
  python simulate_wear.py

Terminal 3 - AI Engine:
  python main.py

Terminal 4 - FastAPI Backend:
  python api_server.py

Terminal 5 - Next.js Frontend:
  cd iiot-frontend
  npm run dev

"@ -ForegroundColor White

# Summary
Write-Host "`n" + ("=" * 71) -ForegroundColor Cyan
Write-Host "[Setup Complete!]" -ForegroundColor Green
Write-Host ("=" * 71) -ForegroundColor Cyan

Write-Host "`nAccess your application at:" -ForegroundColor Yellow
Write-Host "  Frontend:  http://localhost:3000" -ForegroundColor White
Write-Host "  Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Grafana:   http://localhost:3000 (legacy)" -ForegroundColor White

Write-Host "`nArchitecture:" -ForegroundColor Yellow
Write-Host "  Next.js (Frontend) -> FastAPI (Backend) -> InfluxDB (Database)" -ForegroundColor White
Write-Host "  Python ML Engine writes to InfluxDB in real-time" -ForegroundColor White

Write-Host ""

# Full-Stack IIoT Application

Professional Industrial IoT Predictive Maintenance Platform with FastAPI backend and Next.js 14 frontend.

## Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Next.js 14    │─────▶│   FastAPI       │─────▶│   InfluxDB      │
│   (Frontend)    │ HTTP │   (Backend)     │ Query│   (Database)    │
│   Port 3000     │◀─────│   Port 8000     │◀─────│   Port 8086     │
└─────────────────┘ JSON └─────────────────┘      └─────────────────┘
                                                            ▲
                                                            │
                                                     ┌──────┴──────┐
                                                     │   main.py   │
                                                     │  (AI Engine)│
                                                     └─────────────┘
```

## Quick Start

### 1. Backend Setup (FastAPI)

```powershell
# Install dependencies
pip install fastapi uvicorn influxdb

# Start API server
python api_server.py
```

API will be available at:
- http://localhost:8000
- http://localhost:8000/docs (Swagger UI)

### 2. Frontend Setup (Next.js)

```powershell
# Create Next.js project
npx create-next-app@latest iiot-frontend --typescript --tailwind --app

cd iiot-frontend

# Install dependencies
npm install next-auth@beta recharts swr lucide-react date-fns

# Create directory structure
mkdir -p types lib components app/api/auth/[...nextauth] app/dashboard

# Copy component files from nextjs-components/ folder
# (See file mapping in NEXTJS_SETUP.md)

# Create .env.local
echo "NEXTAUTH_URL=http://localhost:3000" > .env.local
echo "NEXTAUTH_SECRET=$(openssl rand -base64 32)" >> .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" >> .env.local

# Start development server
npm run dev
```

## File Mapping

Copy these files from `nextjs-components/` to your Next.js project:

| Source File | Destination |
|------------|-------------|
| `types-index.ts` | `iiot-frontend/types/index.ts` |
| `lib-auth.ts` | `iiot-frontend/lib/auth.ts` |
| `api-auth-nextauth-route.ts` | `iiot-frontend/app/api/auth/[...nextauth]/route.ts` |
| `app-page.tsx` | `iiot-frontend/app/page.tsx` |
| `app-dashboard-page.tsx` | `iiot-frontend/app/dashboard/page.tsx` |
| `MetricCard.tsx` | `iiot-frontend/components/MetricCard.tsx` |
| `StatusBadge.tsx` | `iiot-frontend/components/StatusBadge.tsx` |
| `LiveChart.tsx` | `iiot-frontend/components/LiveChart.tsx` |

## API Endpoints

### GET /api/live
Returns the latest sensor reading and AI prediction.

**Response:**
```json
{
  "vibration": 12.45,
  "temperature": 48.2,
  "score": 0.1523,
  "status": "NORMAL",
  "timestamp": "2025-12-06T10:30:00Z"
}
```

### GET /api/history?limit=50
Returns historical data for charting.

**Response:**
```json
[
  {
    "timestamp": "2025-12-06T10:29:00Z",
    "vibration": 12.30,
    "temperature": 48.0,
    "score": 0.1500,
    "status": "NORMAL"
  }
]
```

### GET /api/stats
Returns aggregated statistics.

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **InfluxDB Client** - Time-series database connector
- **Uvicorn** - ASGI server

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **NextAuth.js v5** - Authentication
- **Recharts** - Data visualization
- **SWR** - Real-time data fetching
- **Lucide React** - Icon library

## Development Workflow

### Terminal 1: InfluxDB
```powershell
docker-compose up -d
```

### Terminal 2: Data Simulator
```powershell
python simulate_wear.py
```

### Terminal 3: AI Engine
```powershell
python main.py
```

### Terminal 4: FastAPI Backend
```powershell
python api_server.py
```

### Terminal 5: Next.js Frontend
```powershell
cd iiot-frontend
npm run dev
```

## Features

### Landing Page
- High-conversion SaaS design
- Hero section with gradient CTA
- Feature highlights
- Industrial dark theme

### Dashboard (Protected)
- Real-time metrics (1-second polling)
- Vibration & temperature monitoring
- AI health score visualization
- Status badges with animations
- Interactive charts
- Session authentication

## Environment Variables

### Frontend (.env.local)
```env
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key
GITHUB_CLIENT_ID=your-github-id (optional)
GITHUB_CLIENT_SECRET=your-github-secret (optional)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (Optional)
The FastAPI server uses hardcoded values for development. For production:
- Configure CORS origins
- Set InfluxDB connection details
- Add environment variable management

## Production Deployment

### Backend
```powershell
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend
```powershell
cd iiot-frontend
npm run build
npm start
```

## Troubleshooting

### CORS Issues
Ensure FastAPI CORS middleware includes your frontend origin.

### No Data in Dashboard
1. Check InfluxDB is running: `docker ps`
2. Verify data is being written: Check Grafana or InfluxDB CLI
3. Ensure `main.py` is running and connected to InfluxDB
4. Check browser console for API errors

### Authentication Issues
1. Verify `.env.local` exists with correct variables
2. Generate new NEXTAUTH_SECRET if needed
3. For GitHub OAuth, configure callback URL correctly

## License

MIT

## Support

For issues or questions, check:
- FastAPI docs: https://fastapi.tiangolo.com/
- Next.js docs: https://nextjs.org/docs
- NextAuth.js docs: https://authjs.dev/

# ✅ Frontend Setup Complete

## Google OAuth Configuration

### 1. Get Google OAuth Credentials

Visit: https://console.cloud.google.com/apis/credentials

1. **Create Project** (if needed)
   - Click "Select a project" → "New Project"
   - Name: "IIoT Predictive Maintenance"
   - Click "Create"

2. **Configure OAuth Consent Screen**
   - Go to "OAuth consent screen"
   - Choose "External" → Click "Create"
   - Fill in:
     - App name: "IIoT Dashboard"
     - User support email: Your email
     - Developer contact: Your email
   - Click "Save and Continue"
   - Skip "Scopes" (Click "Save and Continue")
   - Add test users (your email) → "Save and Continue"

3. **Create OAuth 2.0 Client ID**
   - Go to "Credentials" → "+ CREATE CREDENTIALS" → "OAuth client ID"
   - Application type: "Web application"
   - Name: "IIoT Web Client"
   - Authorized redirect URIs:
     ```
     http://localhost:3001/api/auth/callback/google
     ```
   - Click "Create"
   - **COPY** Client ID and Client Secret

### 2. Update `.env.local`

Open `frontend/.env.local` and replace placeholders:

```env
# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3001
NEXTAUTH_SECRET=your-super-secret-key-min-32-chars-long-change-this-in-production

# Google OAuth
GOOGLE_CLIENT_ID=YOUR_ACTUAL_CLIENT_ID_HERE
GOOGLE_CLIENT_SECRET=YOUR_ACTUAL_CLIENT_SECRET_HERE

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Generate NEXTAUTH_SECRET:**
```bash
openssl rand -base64 32
```

Or use: https://generate-secret.vercel.app/32

### 3. Start the Application

#### Terminal 1 - Backend (FastAPI)
```powershell
cd c:\Users\HoussamClap\Documents\Projects-app\iiot-predictive-maintenance
python api_server.py
```
✅ Backend runs on: http://localhost:8000

#### Terminal 2 - Frontend (Next.js)
```powershell
cd frontend
npm run dev
```
✅ Frontend runs on: http://localhost:3001

#### Terminal 3 - Data Simulator
```powershell
cd c:\Users\HoussamClap\Documents\Projects-app\iiot-predictive-maintenance
python simulate_wear.py
```

#### Terminal 4 - AI Engine
```powershell
cd c:\Users\HoussamClap\Documents\Projects-app\iiot-predictive-maintenance
python main.py
```

### 4. Test the Flow

1. **Landing Page**: http://localhost:3001
   - Industrial dark theme with hero section
   - "Enter Console" button → Dashboard
   - "Sign In" button → Login page

2. **Login**: http://localhost:3001/login
   - Click "Continue with Google"
   - Sign in with your Google account
   - Redirects to Dashboard

3. **Dashboard**: http://localhost:3001/dashboard
   - Real-time metrics (Vibration, Temperature, AI Score)
   - Live chart with 1-second updates
   - Status badge (NORMAL/WARNING/ANOMALY)
   - System status panel

## File Structure

```
frontend/
├── .env.local                    # Environment variables (CONFIGURE THIS!)
├── app/
│   ├── api/
│   │   └── auth/
│   │       └── [...nextauth]/
│   │           └── route.ts      # NextAuth API route
│   ├── dashboard/
│   │   └── page.tsx              # Protected dashboard page
│   ├── login/
│   │   └── page.tsx              # Google login page
│   ├── page.tsx                  # Landing page (SaaS hero)
│   ├── layout.tsx                # Root layout with SessionProvider
│   └── globals.css               # Global styles
├── components/
│   ├── LiveChart.tsx             # Recharts area chart
│   ├── MetricCard.tsx            # Metric display cards
│   ├── Providers.tsx             # SessionProvider wrapper
│   └── StatusBadge.tsx           # Status indicator (animated)
├── lib/
│   └── auth.ts                   # NextAuth Google OAuth config
├── types/
│   └── index.ts                  # TypeScript interfaces
├── package.json                  # Dependencies
├── tsconfig.json                 # TypeScript config
└── next.config.ts                # Next.js config
```

## Pages & Routes

| Route | Protection | Description |
|-------|-----------|-------------|
| `/` | Public | Landing page with hero section |
| `/login` | Public | Google OAuth login |
| `/dashboard` | Protected | Real-time monitoring (requires auth) |

## API Endpoints (Backend)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/live` | GET | Latest sensor reading + status |
| `/api/history?limit=50` | GET | Historical data for charts |
| `/api/stats` | GET | Aggregated statistics |

## Data Flow

```
simulate_wear.py → MQTT → main.py (AI) → InfluxDB
                                            ↓
                                    FastAPI (api_server.py)
                                            ↓
                                    Next.js Dashboard
```

## Color Theme

- **Background**: Slate 950/900/800 (industrial dark)
- **Success/Normal**: Emerald 500 (#10b981)
- **Warning**: Yellow 500
- **Danger/Anomaly**: Red 500
- **Text**: White/Slate-400/Slate-500

## Troubleshooting

### "Error: Invalid OAuth credentials"
- Check `.env.local` has correct GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
- Verify callback URL in Google Console: `http://localhost:3001/api/auth/callback/google`

### "Connection Error" on Dashboard
- Ensure FastAPI backend is running: `python api_server.py`
- Check CORS settings in `api_server.py` (should allow `http://localhost:3001`)

### "No data" in charts
- Start simulate_wear.py to generate sensor data
- Start main.py to run AI engine and write to InfluxDB
- Check InfluxDB is running: `docker ps`

### Port 3001 already in use
- Stop other Next.js instances: `Get-Process node | Stop-Process`
- Or change port in package.json: `"dev": "next dev -p 3002"`

## Next Steps

1. **Configure Google OAuth** (see above)
2. **Start all services** (Docker, Backend, Frontend, Simulator, AI)
3. **Visit landing page** → http://localhost:3001
4. **Sign in with Google** → Access dashboard
5. **Monitor real-time data** → Watch AI scores and metrics

## Production Checklist

- [ ] Change NEXTAUTH_SECRET to cryptographically secure value
- [ ] Update NEXTAUTH_URL to production domain
- [ ] Configure Google OAuth with production redirect URI
- [ ] Update NEXT_PUBLIC_API_URL to production backend
- [ ] Enable environment variables in Vercel/hosting platform
- [ ] Set up HTTPS for secure authentication
- [ ] Review Google OAuth consent screen for public users

---

**🎉 Your full-stack IIoT dashboard is ready!**

Frontend: http://localhost:3001  
Backend: http://localhost:8000  
Grafana: http://localhost:3001 (Docker)

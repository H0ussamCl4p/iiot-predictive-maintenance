# Next.js 14 Frontend Setup Guide
# IIoT Predictive Maintenance Dashboard

## Step 1: Create Next.js Project
# Run these commands in your project root directory

npx create-next-app@latest iiot-frontend --typescript --tailwind --app --no-src-dir --import-alias "@/*"

# When prompted, select:
# - TypeScript: Yes
# - ESLint: Yes
# - Tailwind CSS: Yes
# - `src/` directory: No
# - App Router: Yes
# - Import alias: @/*

cd iiot-frontend

## Step 2: Install Required Dependencies

npm install next-auth@beta recharts swr lucide-react date-fns

## Step 3: Install Dev Dependencies (Optional but recommended)

npm install -D @types/node @types/react @types/react-dom

## Step 4: Create Environment Variables File

# Create .env.local in the root of iiot-frontend/
# Add these variables (you'll configure GitHub OAuth later):

NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-generate-with-openssl-rand-base64-32
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
NEXT_PUBLIC_API_URL=http://localhost:8000

## Step 5: Update next.config.js

# Add API rewrites for development
# This file should already exist, update it with:

/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ]
  },
}

module.exports = nextConfig

## Step 6: Update Tailwind Config for Industrial Theme

# Update tailwind.config.ts with custom colors

import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        industrial: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617',
        },
        status: {
          normal: '#10b981',
          warning: '#f59e0b',
          anomaly: '#ef4444',
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
export default config

## Step 7: File Structure

# Your project should have this structure:
iiot-frontend/
├── app/
│   ├── api/
│   │   └── auth/
│   │       └── [...nextauth]/
│   │           └── route.ts
│   ├── dashboard/
│   │   └── page.tsx
│   ├── login/
│   │   └── page.tsx
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/
│   ├── MetricCard.tsx
│   ├── StatusBadge.tsx
│   ├── LiveChart.tsx
│   └── Sidebar.tsx
├── lib/
│   └── auth.ts
├── types/
│   └── index.ts
├── .env.local
├── next.config.js
├── tailwind.config.ts
└── package.json

## Step 8: Generate NextAuth Secret

# Run this command to generate a secure secret:
openssl rand -base64 32

# Copy the output and add it to .env.local as NEXTAUTH_SECRET

## Step 9: Run Development Servers

# Terminal 1: Start FastAPI Backend
cd ..
python api_server.py

# Terminal 2: Start Next.js Frontend
cd iiot-frontend
npm run dev

# Your app will be available at:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs

## Step 10: GitHub OAuth Setup (Optional - for authentication)

# 1. Go to https://github.com/settings/developers
# 2. Click "New OAuth App"
# 3. Set:
#    - Application name: IIoT Dashboard
#    - Homepage URL: http://localhost:3000
#    - Authorization callback URL: http://localhost:3000/api/auth/callback/github
# 4. Copy Client ID and Client Secret to .env.local

## Next Steps

After running these commands, you'll need to create the React components.
See the component files below for the full implementation.

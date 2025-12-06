// app/dashboard/page.tsx
// Protected dashboard with real-time monitoring

'use client'

import { useEffect, useState } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import useSWR from 'swr'
import { Activity, Gauge, Thermometer, TrendingUp, AlertCircle } from 'lucide-react'
import MetricCard from '@/components/MetricCard'
import StatusBadge from '@/components/StatusBadge'
import LiveChart from '@/components/LiveChart'
import type { LiveData, HistoricalData } from '@/types'

const fetcher = (url: string) => fetch(url).then(res => res.json())

export default function DashboardPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [mounted, setMounted] = useState(false)

  // Fetch live data every 1 second
  const { data: liveData, error: liveError } = useSWR<LiveData>(
    'http://localhost:8000/api/live',
    fetcher,
    { refreshInterval: 1000 }
  )

  // Fetch historical data every 5 seconds
  const { data: historyData, error: historyError } = useSWR<HistoricalData[]>(
    'http://localhost:8000/api/history?limit=50',
    fetcher,
    { refreshInterval: 5000 }
  )

  useEffect(() => {
    setMounted(true)
  }, [])

  // Redirect to login if not authenticated
  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login')
    }
  }, [status, router])

  if (!mounted || status === 'loading') {
    return (
      <div className="min-h-screen bg-industrial-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-status-normal border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-industrial-400">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (status === 'unauthenticated') {
    return null
  }

  const isError = liveError || historyError

  return (
    <div className="min-h-screen bg-gradient-to-br from-industrial-950 via-industrial-900 to-industrial-950">
      {/* Header */}
      <header className="border-b border-industrial-800 bg-industrial-900/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Activity className="w-8 h-8 text-status-normal" />
              <div>
                <h1 className="text-2xl font-bold text-white">IIoT Dashboard</h1>
                <p className="text-sm text-industrial-400">Press_001 • Real-time Monitoring</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {liveData && <StatusBadge status={liveData.status} />}
              <div className="text-right">
                <p className="text-sm text-industrial-400">Logged in as</p>
                <p className="text-sm font-medium text-white">{session?.user?.name || 'User'}</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Error State */}
        {isError && (
          <div className="mb-6 p-4 bg-status-anomaly/10 border border-status-anomaly/30 rounded-lg flex items-center space-x-3">
            <AlertCircle className="w-5 h-5 text-status-anomaly" />
            <div>
              <p className="text-status-anomaly font-medium">Connection Error</p>
              <p className="text-sm text-industrial-400">
                Unable to connect to backend API. Ensure the FastAPI server is running on port 8000.
              </p>
            </div>
          </div>
        )}

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <MetricCard
            title="Vibration Level"
            value={liveData?.vibration || 0}
            unit="units"
            status={liveData?.status === 'ANOMALY' ? 'danger' : liveData?.status === 'WARNING' ? 'warning' : 'normal'}
            icon={<Gauge className="w-5 h-5" />}
          />
          <MetricCard
            title="Temperature"
            value={liveData?.temperature || 0}
            unit="°C"
            status="normal"
            icon={<Thermometer className="w-5 h-5" />}
          />
          <MetricCard
            title="AI Health Score"
            value={liveData?.score || 0}
            unit=""
            status={liveData && liveData.score < 0 ? 'danger' : 'normal'}
            icon={<TrendingUp className="w-5 h-5" />}
          />
        </div>

        {/* Chart Section */}
        <div className="grid grid-cols-1 gap-6">
          <div className="p-6 bg-industrial-900/50 border border-industrial-800 rounded-xl backdrop-blur-sm">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-semibold text-white">AI Health Score Trend</h2>
                <p className="text-sm text-industrial-400">Last 50 readings • Updates every 5 seconds</p>
              </div>
              <div className="flex items-center space-x-2 px-3 py-1 bg-status-normal/10 border border-status-normal/30 rounded-full">
                <div className="w-2 h-2 bg-status-normal rounded-full animate-pulse"></div>
                <span className="text-xs text-status-normal font-medium">LIVE</span>
              </div>
            </div>
            <div className="h-80">
              {historyData && historyData.length > 0 ? (
                <LiveChart data={historyData} />
              ) : (
                <div className="h-full flex items-center justify-center">
                  <div className="text-center">
                    <Activity className="w-12 h-12 text-industrial-700 mx-auto mb-3" />
                    <p className="text-industrial-500">Waiting for data...</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Additional Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 bg-industrial-900/50 border border-industrial-800 rounded-xl">
              <h3 className="text-lg font-semibold text-white mb-4">System Status</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-industrial-400">Machine ID</span>
                  <span className="text-white font-medium">Press_001</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-industrial-400">Algorithm</span>
                  <span className="text-white font-medium">Isolation Forest</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-industrial-400">Last Update</span>
                  <span className="text-white font-medium">
                    {liveData?.timestamp ? new Date(liveData.timestamp).toLocaleTimeString() : '--:--:--'}
                  </span>
                </div>
              </div>
            </div>

            <div className="p-6 bg-industrial-900/50 border border-industrial-800 rounded-xl">
              <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
              <div className="space-y-2">
                <button className="w-full px-4 py-2 bg-industrial-800 hover:bg-industrial-700 text-white rounded-lg transition-colors text-sm">
                  Download Report
                </button>
                <button className="w-full px-4 py-2 bg-industrial-800 hover:bg-industrial-700 text-white rounded-lg transition-colors text-sm">
                  Configure Alerts
                </button>
                <button className="w-full px-4 py-2 bg-industrial-800 hover:bg-industrial-700 text-white rounded-lg transition-colors text-sm">
                  View History
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

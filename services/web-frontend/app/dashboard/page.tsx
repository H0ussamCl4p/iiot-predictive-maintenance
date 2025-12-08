// Protected dashboard with real-time monitoring

'use client'

import { useEffect, useState } from 'react'
import { useSession, signOut } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import useSWR from 'swr'
import { Activity, Gauge, Thermometer, TrendingUp, AlertCircle, LogOut, Clock, AlertTriangle, CheckCircle, Bell, Wrench } from 'lucide-react'
import MetricCard from '@/components/MetricCard'
import StatusBadge from '@/components/StatusBadge'
import LiveChart from '@/components/LiveChart'
import StatCard from '@/components/StatCard'
import AlertTimeline from '@/components/AlertTimeline'
import HealthScoreCard from '@/components/HealthScoreCard'
import WorkOrderList from '@/components/WorkOrderList'
import PatternAnalysis from '@/components/PatternAnalysis'
import MobileMenu from '@/components/MobileMenu'
import PredictionPanel from '@/components/PredictionPanel'
import type { LiveData, HistoricalData, Statistics, Alert, WorkOrder, AnomalyPattern } from '@/types'

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

  // Fetch statistics every 10 seconds
  const { data: statsData, error: statsError } = useSWR<Statistics>(
    'http://localhost:8000/api/stats',
    fetcher,
    { refreshInterval: 10000 }
  )

  // Fetch alerts every 15 seconds
  const { data: alertsData, error: alertsError } = useSWR<Alert[]>(
    'http://localhost:8000/api/alerts?limit=20',
    fetcher,
    { refreshInterval: 15000 }
  )

  // Fetch work orders every 30 seconds
  const { data: workOrders, error: workOrdersError } = useSWR<WorkOrder[]>(
    'http://localhost:8000/api/work-orders',
    fetcher,
    { refreshInterval: 30000 }
  )

  // Fetch patterns every 60 seconds
  const { data: patterns, error: patternsError } = useSWR<AnomalyPattern[]>(
    'http://localhost:8000/api/patterns',
    fetcher,
    { refreshInterval: 60000 }
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
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-400">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (status === 'unauthenticated') {
    return null
  }

  const isError = liveError || historyError

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 sm:px-6 py-3 sm:py-4">
          <div className="flex items-center justify-between gap-2 sm:gap-4">
            <div className="flex items-center space-x-2 sm:space-x-4">
              <Activity className="w-6 h-6 sm:w-8 sm:h-8 text-emerald-500" />
              <div>
                <h1 className="text-lg sm:text-2xl font-bold text-white">IIoT Dashboard</h1>
                <p className="text-xs sm:text-sm text-slate-400 hidden sm:block">Press_001 • Real-time Monitoring</p>
              </div>
            </div>
            <div className="flex items-center gap-2 sm:gap-4">
              <MobileMenu />
              {liveData && <StatusBadge status={liveData.status} />}
              <div className="flex items-center gap-2 sm:gap-3">
                <div className="text-right hidden lg:block">
                  <p className="text-xs text-slate-400">Logged in as</p>
                  <p className="text-sm font-medium text-white truncate max-w-[150px]">{session?.user?.name || session?.user?.email || 'User'}</p>
                </div>
                <button
                  onClick={() => signOut({ callbackUrl: '/' })}
                  className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
                  title="Sign out"
                >
                  <LogOut className="w-4 h-4 sm:w-5 sm:h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-3 sm:px-4 lg:px-6 py-4 sm:py-6 lg:py-8">
        {/* Error State */}
        {isError && (
          <div className="mb-4 sm:mb-6 p-3 sm:p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-start sm:items-center gap-2 sm:gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
            <div>
              <p className="text-sm sm:text-base text-red-500 font-medium">Connection Error</p>
              <p className="text-xs sm:text-sm text-slate-400">
                Unable to connect to backend API. Ensure the FastAPI server is running on port 8000.
              </p>
            </div>
          </div>
        )}

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 lg:gap-6 mb-4 sm:mb-6 lg:mb-8">
          <StatCard
            title="Uptime (24h)"
            value={statsData ? `${statsData.uptime_percentage}%` : '--'}
            subtitle="System availability"
            icon={<CheckCircle className="w-5 h-5 text-emerald-500" />}
            variant={statsData && statsData.uptime_percentage >= 95 ? 'success' : 'warning'}
          />
          <StatCard
            title="Anomalies Today"
            value={statsData?.anomalies_today ?? '--'}
            subtitle={`${statsData?.total_readings || 0} total readings`}
            icon={<AlertTriangle className="w-5 h-5 text-red-500" />}
            variant={statsData && statsData.anomalies_today > 0 ? 'danger' : 'success'}
          />
          <StatCard
            title="Warnings Today"
            value={statsData?.warnings_today ?? '--'}
            subtitle="Requiring attention"
            icon={<AlertCircle className="w-5 h-5 text-yellow-500" />}
            variant={statsData && statsData.warnings_today > 5 ? 'warning' : 'default'}
          />
          <StatCard
            title="Avg Temperature"
            value={statsData ? `${statsData.temperature.average}°C` : '--'}
            subtitle={`Peak: ${statsData?.temperature.max || 0}°C`}
            icon={<Thermometer className="w-5 h-5 text-slate-400" />}
            variant="default"
          />
        </div>

        {/* Health Score & Metrics Row */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-3 sm:gap-4 lg:gap-6 mb-4 sm:mb-6 lg:mb-8">
          {/* Health Score Card */}
          <div className="lg:col-span-1">
            {liveData?.health ? (
              <HealthScoreCard
                score={liveData.health.score}
                status={liveData.health.status}
                daysUntilMaintenance={liveData.health.days_until_maintenance}
                maintenanceUrgency={liveData.health.maintenance_urgency}
              />
            ) : (
              <div className="p-8 bg-slate-900/50 border border-slate-800 rounded-xl backdrop-blur-sm h-full flex items-center justify-center">
                <div className="text-center">
                  <Activity className="w-12 h-12 text-slate-700 mx-auto mb-3 animate-pulse" />
                  <p className="text-slate-500">Loading health data...</p>
                </div>
              </div>
            )}
          </div>

          {/* Metrics Grid */}
          <div className="lg:col-span-3 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 lg:gap-6">
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
        </div>

        {/* AI Prediction Panel */}
        <PredictionPanel />

        {/* Chart Section */}
        <div className="grid grid-cols-1 gap-3 sm:gap-4 lg:gap-6">
          <div className="p-4 sm:p-6 bg-slate-900/50 border border-slate-800 rounded-xl backdrop-blur-sm">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 sm:gap-0 mb-4 sm:mb-6">
              <div>
                <h2 className="text-lg sm:text-xl font-semibold text-white">AI Health Score Trend</h2>
                <p className="text-xs sm:text-sm text-slate-400">Last 50 readings • Updates every 5 seconds</p>
              </div>
              <div className="flex items-center space-x-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 rounded-full w-fit">
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                <span className="text-xs text-emerald-500 font-medium">LIVE</span>
              </div>
            </div>
            <div className="h-64 sm:h-80 min-h-[256px]">
              {historyData && historyData.length > 0 ? (
                <LiveChart data={historyData} />
              ) : (
                <div className="h-full flex items-center justify-center">
                  <div className="text-center">
                    <Activity className="w-12 h-12 text-slate-700 mx-auto mb-3" />
                    <p className="text-slate-500">Waiting for data...</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Additional Info */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 sm:gap-4 lg:gap-6">
            {/* Alert History Timeline */}
            <div className="p-4 sm:p-6 bg-slate-900/50 border border-slate-800 rounded-xl">
              <div className="flex items-center justify-between mb-3 sm:mb-4">
                <h3 className="text-base sm:text-lg font-semibold text-white">Recent Alerts</h3>
                <div className="flex items-center space-x-2 px-2 sm:px-3 py-1 bg-slate-800 rounded-full">
                  <Bell className="w-3 h-3 sm:w-4 sm:h-4 text-slate-400" />
                  <span className="text-xs text-slate-400">
                    {alertsData?.length || 0} alerts
                  </span>
                </div>
              </div>
              <AlertTimeline alerts={alertsData || []} />
            </div>

            <div className="p-4 sm:p-6 bg-slate-900/50 border border-slate-800 rounded-xl">
              <h3 className="text-base sm:text-lg font-semibold text-white mb-3 sm:mb-4">System Status</h3>
              <div className="space-y-2 sm:space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Machine ID</span>
                  <span className="text-white font-medium">Press_001</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Algorithm</span>
                  <span className="text-white font-medium">Isolation Forest</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Last Update</span>
                  <span className="text-white font-medium">
                    {liveData?.timestamp ? new Date(liveData.timestamp).toLocaleTimeString() : '--:--:--'}
                  </span>
                </div>
              </div>
              
              <div className="mt-4 sm:mt-6">
                <h4 className="text-xs sm:text-sm font-medium text-white mb-2 sm:mb-3">Quick Actions</h4>
                <div className="space-y-2">
                  <button className="w-full px-3 sm:px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors text-xs sm:text-sm">
                    Download Report
                  </button>
                  <button className="w-full px-3 sm:px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors text-xs sm:text-sm">
                    Configure Alerts
                  </button>
                  <button className="w-full px-3 sm:px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors text-xs sm:text-sm">
                    View History
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Work Orders and Pattern Analysis */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 sm:gap-4 lg:gap-6">
            {/* Maintenance Work Orders */}
            <div className="p-4 sm:p-6 bg-slate-900/50 border border-slate-800 rounded-xl">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 sm:gap-0 mb-3 sm:mb-4">
                <h3 className="text-base sm:text-lg font-semibold text-white flex items-center space-x-2">
                  <Wrench className="w-4 h-4 sm:w-5 sm:h-5" />
                  <span>Work Orders</span>
                </h3>
                <div className="flex items-center space-x-2 px-2 sm:px-3 py-1 bg-slate-800 rounded-full w-fit">
                  <span className="text-xs text-slate-400">
                    {workOrders?.length || 0} orders
                  </span>
                </div>
              </div>
              <WorkOrderList workOrders={workOrders || []} />
            </div>

            {/* AI Pattern Analysis */}
            <div className="p-4 sm:p-6 bg-slate-900/50 border border-slate-800 rounded-xl">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 sm:gap-0 mb-3 sm:mb-4">
                <h3 className="text-base sm:text-lg font-semibold text-white flex items-center space-x-2">
                  <Activity className="w-4 h-4 sm:w-5 sm:h-5" />
                  <span>AI Patterns</span>
                </h3>
                <div className="flex items-center space-x-2 px-2 sm:px-3 py-1 bg-slate-800 rounded-full w-fit">
                  <span className="text-xs text-slate-400">
                    {patterns?.length || 0} patterns
                  </span>
                </div>
              </div>
              <PatternAnalysis patterns={patterns || []} />
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

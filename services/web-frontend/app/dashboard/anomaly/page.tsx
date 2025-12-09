"use client"

import { useState } from 'react'
import useSWR from 'swr'
import LiveChart from '@/components/LiveChart'
import HealthScoreCard from '@/components/HealthScoreCard'
import AlertTimeline from '@/components/AlertTimeline'
import { Activity } from 'lucide-react'
import type { LiveData, HistoricalData, Alert } from '@/types'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

const fetcher = (url: string) => fetch(url).then(res => res.json())

export default function AnomalyPage() {
  const [equipmentId, setEquipmentId] = useState<string>('all')
  const { data: equipment } = useSWR<any[]>('http://localhost:8000/api/equipment', fetcher, { refreshInterval: 60000 })
  const { data: liveData } = useSWR<LiveData>(
    `http://localhost:8000/api/live${equipmentId !== 'all' ? `?equipmentId=${encodeURIComponent(equipmentId)}` : ''}`,
    fetcher,
    { refreshInterval: 1000 }
  )
  const { data: historyData } = useSWR<HistoricalData[]>(
    `http://localhost:8000/api/history?limit=50${equipmentId !== 'all' ? `&equipmentId=${encodeURIComponent(equipmentId)}` : ''}`,
    fetcher,
    { refreshInterval: 5000 }
  )
  const { data: alertsData } = useSWR<Alert[]>(
    'http://localhost:8000/api/alerts?limit=50',
    fetcher,
    { refreshInterval: 15000 }
  )

  return (
    <div className="space-y-6">
      {/* Equipment Selector */}
      <div className="flex items-center gap-3">
        <label className="text-slate-400 text-sm">Equipment:</label>
        <Select value={equipmentId} onValueChange={setEquipmentId}>
          <SelectTrigger className="w-[200px] bg-slate-900/60 border-slate-800 text-white">
            <SelectValue placeholder="All Equipment" />
          </SelectTrigger>
          <SelectContent className="bg-slate-900 border-slate-800">
            <SelectItem value="all" className="text-white hover:bg-slate-800">All Equipment</SelectItem>
            {(equipment || []).map((eq) => (
              <SelectItem key={eq.id} value={eq.id} className="text-white hover:bg-slate-800">{eq.id}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-1">
          {liveData?.health ? (
            <HealthScoreCard
              score={liveData.health.score}
              status={liveData.health.status}
              daysUntilMaintenance={liveData.health.days_until_maintenance}
              maintenanceUrgency={liveData.health.maintenance_urgency}
            />
          ) : (
            <Card>
              <CardContent className="p-8 h-full flex items-center justify-center">
                <div className="text-center">
                  <Activity className="w-12 h-12 text-slate-700 mx-auto mb-3 animate-pulse" />
                  <p className="text-slate-500">Loading health data...</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        <Card className="lg:col-span-2">
          <CardHeader className="flex items-center justify-between">
            <div>
              <CardTitle>AI Health Score Trend</CardTitle>
              <CardDescription>Last 50 readings</CardDescription>
            </div>
            <div className="flex items-center space-x-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 rounded-full w-fit">
              <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-emerald-500 font-medium">LIVE</span>
            </div>
          </CardHeader>
          <CardContent className="h-64 sm:h-80 min-h-64">
            {historyData && historyData.length > 0 ? (
              <LiveChart data={historyData} />
            ) : (
              <div className="h-full flex items-center justify-center text-slate-500">Waiting for data...</div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Alerts</CardTitle>
          <CardDescription>Last 50 alerts</CardDescription>
        </CardHeader>
        <CardContent>
          <AlertTimeline alerts={alertsData || []} />
        </CardContent>
      </Card>
    </div>
  )
}

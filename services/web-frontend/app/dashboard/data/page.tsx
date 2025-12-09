"use client"

import { useState } from 'react'
import useSWR from 'swr'
import TelemetryCharts from '@/components/TelemetryCharts'
import TelemetryTable from '@/components/TelemetryTable'
import MetricCard from '@/components/MetricCard'
import { Gauge, Thermometer, Activity, TrendingUp } from 'lucide-react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import type { LiveData, HistoricalData } from '@/types'

const fetcher = (url: string) => fetch(url).then(res => res.json())

export default function DataPage() {
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
      {/* Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Vibration" value={liveData?.vibration || 0} unit="units" icon={<Gauge className="w-5 h-5" />} />
        <MetricCard title="Temperature" value={liveData?.temperature || 0} unit="°C" icon={<Thermometer className="w-5 h-5" />} />
        <MetricCard title="Humidity" value={(liveData as any)?.humidity ?? 0} unit="%" icon={<Activity className="w-5 h-5" />} />
        <MetricCard title="AI Health" value={Math.max(0, Math.min(100, Math.round((liveData?.score || 0) * 100)))} unit="%" icon={<TrendingUp className="w-5 h-5" />} />
      </div>

      {/* Charts */}
      <TelemetryCharts data={historyData || []} />

      {/* Table */}
      <TelemetryTable data={historyData || []} />
    </div>
  )
}

"use client"

import useSWR from 'swr'
import ModelStatusCard from '@/components/ModelStatusCard'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import type { LiveData } from '@/types'

const fetcher = (url: string) => fetch(url).then(res => res.json())

export default function StatusPage() {
  const { data: liveData } = useSWR<LiveData>('http://localhost:8000/api/live', fetcher, { refreshInterval: 3000 })

  return (
    <div className="space-y-6">
      <ModelStatusCard />

      <Card>
        <CardHeader>
          <CardTitle>System Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Machine ID</span>
              <span className="text-white font-medium">Press_001</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Algorithm</span>
              <span className="text-white font-medium">Isolation Forest + Random Forest</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Last Update</span>
              <span className="text-white font-medium">{liveData?.timestamp ? new Date(liveData.timestamp).toLocaleTimeString() : '--:--:--'}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

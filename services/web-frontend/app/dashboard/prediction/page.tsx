"use client"

import { useState } from 'react'
import useSWR from 'swr'
import PredictionPanel from '@/components/PredictionPanel'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

const fetcher = (url: string) => fetch(url).then(res => res.json())

export default function PredictionPage() {
  const [equipmentId, setEquipmentId] = useState<string>('all')
  const { data: equipment } = useSWR<any[]>('http://localhost:8000/api/equipment', fetcher, { refreshInterval: 60000 })
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
      <PredictionPanel equipmentId={equipmentId !== 'all' ? equipmentId : undefined} />
    </div>
  )
}

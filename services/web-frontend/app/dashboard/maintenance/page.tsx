"use client"

import useSWR from 'swr'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import Link from 'next/link'

type Task = {
  id: string
  equipmentId: string
  title: string
  dueDate: string
  priority: 'LOW' | 'MEDIUM' | 'HIGH'
  status: 'PLANNED' | 'IN_PROGRESS' | 'DONE'
}

const upcomingTasks: Task[] = [
  { id: 'T-1001', equipmentId: 'PRESS_001', title: 'Lubrication & inspection', dueDate: '2025-12-15', priority: 'MEDIUM', status: 'PLANNED' },
  { id: 'T-1002', equipmentId: 'CONV_014', title: 'Belt tension check', dueDate: '2025-12-12', priority: 'HIGH', status: 'IN_PROGRESS' },
  { id: 'T-1003', equipmentId: 'MOTOR_207', title: 'Bearing replacement', dueDate: '2025-12-20', priority: 'LOW', status: 'PLANNED' },
]

function Pill({ children }: { children: React.ReactNode }) {
  return <span className="px-2 py-1 rounded-full bg-slate-800 text-slate-300 text-xs border border-slate-700">{children}</span>
}

export default function MaintenancePage() {
  const fetcher = (url: string) => fetch(url).then(res => res.json())
  const { data, error } = useSWR<Task[]>(
    'http://localhost:8000/api/maintenance/tasks',
    fetcher,
    { refreshInterval: 30000 }
  )
  const tasks = data && Array.isArray(data) ? data : upcomingTasks
  return (
    <div className="grid grid-cols-1 gap-4">
      <Card>
        <CardHeader>
          <CardTitle>Maintenance Planning</CardTitle>
          <CardDescription>Upcoming tasks and priorities</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-900/60">
                <tr className="text-slate-400">
                  <th className="text-left px-3 py-2">Task</th>
                  <th className="text-left px-3 py-2">Equipment</th>
                  <th className="text-left px-3 py-2">Due</th>
                  <th className="text-left px-3 py-2">Priority</th>
                  <th className="text-left px-3 py-2">Status</th>
                  <th className="text-left px-3 py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {tasks.map(t => (
                  <tr key={t.id} className="border-t border-slate-800">
                    <td className="px-3 py-2 text-white font-medium">{t.title}</td>
                    <td className="px-3 py-2 text-slate-300">{t.equipmentId}</td>
                    <td className="px-3 py-2 text-slate-300">{t.dueDate}</td>
                    <td className="px-3 py-2"><Pill>{t.priority}</Pill></td>
                    <td className="px-3 py-2"><Pill>{t.status}</Pill></td>
                    <td className="px-3 py-2">
                      <div className="flex gap-2">
                        <Link href="#" className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-white rounded-md text-xs">View</Link>
                        <Link href="#" className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-white rounded-md text-xs">Edit</Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {error && (
              <p className="text-xs text-slate-500 mt-2">Showing sample tasks (API unavailable).</p>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Planning Notes</CardTitle>
          <CardDescription>Guidelines for scheduling maintenance</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="list-disc list-inside text-slate-300 space-y-1">
            <li>Prioritize HIGH tasks within 72 hours.</li>
            <li>Group tasks by equipment to minimize downtime.</li>
            <li>Verify parts availability before scheduling replacements.</li>
            <li>Record outcomes and update the next maintenance cycle.</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}

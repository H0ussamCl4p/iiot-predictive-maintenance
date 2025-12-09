// Protected dashboard with real-time monitoring

'use client'

import { useEffect, useState } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

// Overview page: simple welcome only, no data fetching

export default function DashboardPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [mounted, setMounted] = useState(false)


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

  // No error state needed; no data on this page

  return (
    <div className="mb-6">
      <div className="grid grid-cols-1">
        <div className="p-6 bg-slate-900/50 border border-slate-800 rounded-xl">
          <h2 className="text-xl font-bold text-white">Welcome</h2>
          <p className="text-slate-400 mt-1">Choose a section from the sidebar: Data, Anomaly, Prediction, or Status.</p>
          <div className="mt-4 flex gap-2">
            <Link href="/dashboard/data" className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-md text-sm">View Data</Link>
            <Link href="/dashboard/anomaly" className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-md text-sm">Anomaly Detection</Link>
            <Link href="/dashboard/prediction" className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-md text-sm">Future Prediction</Link>
            <Link href="/dashboard/status" className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-md text-sm">System Status</Link>
          </div>
        </div>
      </div>
    </div>
  )
}

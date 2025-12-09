"use client"

import { useSession, signOut } from "next-auth/react"
import { useEffect, useState } from "react"
import { Activity, LogOut } from "lucide-react"
import StatusBadge from "@/components/StatusBadge"
import MobileMenu from "@/components/MobileMenu"
import DashboardNav from "@/components/DashboardNav"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession()
  const [mounted, setMounted] = useState(false)
  useEffect(() => setMounted(true), [])

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

  return (
    <div className="min-h-screen bg-linear-to-br from-slate-950 via-slate-900 to-slate-950">
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
              {/* Session name */}
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
          {/* Nav moved to sidebar */}
        </div>
      </header>

      <main className="container mx-auto px-3 sm:px-4 lg:px-6 py-4 sm:py-6 lg:py-8">
        <div className="flex flex-col lg:flex-row gap-4">
          <DashboardNav />
          <div className="flex-1">
            {children}
          </div>
        </div>
      </main>
    </div>
  )
}

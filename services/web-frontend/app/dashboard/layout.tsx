"use client"

import { useEffect, useState } from "react"
import { Activity, LogOut, Menu, X } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import DashboardNav from "@/components/DashboardNav"
import Link from "next/link"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false)
  const [userName, setUserName] = useState<string | null>(null)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  
  useEffect(() => setMounted(true), [])

  useEffect(() => {
    const storedUser = typeof window !== 'undefined' ? window.localStorage.getItem('user') : null
    if (storedUser) {
      try {
        const parsed = JSON.parse(storedUser)
        setUserName(parsed.name || parsed.email || null)
      } catch {
        setUserName(null)
      }
    }
  }, [])

  if (!mounted) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
        <div className="text-center">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="w-16 h-16 border-4 border-emerald-500 border-t-transparent rounded-full mx-auto mb-4"
          />
          <p className="text-zinc-400">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-white">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-white/10 bg-black/50 backdrop-blur-xl">
        <div className="container mx-auto px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <Link href="/dashboard" className="flex items-center space-x-3 group">
              <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 group-hover:bg-emerald-500/20 transition-colors">
                <Activity className="w-6 h-6 text-emerald-500" />
              </div>
              <div className="hidden sm:block">
                <h1 className="text-xl font-bold tracking-tight">Smart Energy Guardien</h1>
                <p className="text-xs text-zinc-500">Real-time Industrial Monitoring</p>
              </div>
            </Link>

            {/* Right Side */}
            <div className="flex items-center gap-3">
              {/* User Info - Desktop */}
              <div className="hidden lg:flex items-center gap-3 px-4 py-2 rounded-full bg-white/5 border border-white/10">
                <div className="text-right">
                  <p className="text-xs text-zinc-500">Logged in as</p>
                  <p className="text-sm font-medium text-white">{userName || 'User'}</p>
                </div>
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-blue-500 flex items-center justify-center text-sm font-bold">
                  {(userName || 'U')[0].toUpperCase()}
                </div>
              </div>

              {/* Logout Button */}
              <button
                onClick={() => {
                  if (typeof window !== 'undefined') {
                    window.localStorage.removeItem('token')
                    window.localStorage.removeItem('user')
                  }
                  window.location.href = '/'
                }}
                className="p-2.5 text-zinc-400 hover:text-white hover:bg-white/5 rounded-xl transition-colors border border-white/10"
                title="Sign out"
              >
                <LogOut className="w-5 h-5" />
              </button>

              {/* Mobile Menu Toggle */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="lg:hidden p-2.5 text-zinc-400 hover:text-white hover:bg-white/5 rounded-xl transition-colors border border-white/10"
              >
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="lg:hidden border-b border-white/10 bg-zinc-900/95 backdrop-blur-xl overflow-hidden"
          >
            <div className="container mx-auto px-4 py-4">
              <DashboardNav mobile onNavigate={() => setMobileMenuOpen(false)} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className="container mx-auto px-4 sm:px-6 py-6 lg:py-8">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Desktop Sidebar */}
          <aside className="hidden lg:block w-64 shrink-0">
            <div className="sticky top-24">
              <DashboardNav />
            </div>
          </aside>

          {/* Content Area */}
          <div className="flex-1 min-w-0">
            {children}
          </div>
        </div>
      </main>
    </div>
  )
}

// app/page.tsx
// Landing Page - High-conversion SaaS style

import Link from 'next/link'
import { ArrowRight, Activity, Shield, TrendingUp, Zap } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-industrial-950 via-industrial-900 to-industrial-950">
      {/* Navigation */}
      <nav className="container mx-auto px-6 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Activity className="w-8 h-8 text-status-normal" />
            <span className="text-2xl font-bold text-white">IIoT Edge</span>
          </div>
          <Link
            href="/login"
            className="px-6 py-2 text-sm font-medium text-white bg-industrial-700 rounded-lg hover:bg-industrial-600 transition-colors"
          >
            Sign In
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="container mx-auto px-6 py-20">
        <div className="max-w-4xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center space-x-2 px-4 py-2 bg-industrial-800/50 border border-industrial-700 rounded-full mb-8">
            <Zap className="w-4 h-4 text-status-normal" />
            <span className="text-sm text-industrial-300">
              Real-time Edge Computing
            </span>
          </div>

          {/* Main Headline */}
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
            Industrial Intelligence
            <br />
            <span className="bg-gradient-to-r from-status-normal to-emerald-400 bg-clip-text text-transparent">
              at the Edge
            </span>
          </h1>

          {/* Subheadline */}
          <p className="text-xl text-industrial-300 mb-12 max-w-2xl mx-auto leading-relaxed">
            AI-powered predictive maintenance for industrial machinery. 
            Detect anomalies before they become failures. 
            Reduce downtime by 70%.
          </p>

          {/* CTA Button */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
            <Link
              href="/dashboard"
              className="group px-8 py-4 bg-gradient-to-r from-status-normal to-emerald-500 text-white font-semibold rounded-lg shadow-lg shadow-status-normal/20 hover:shadow-status-normal/40 transition-all duration-300 flex items-center space-x-2"
            >
              <span>Enter Console</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              href="#features"
              className="px-8 py-4 bg-industrial-800 text-white font-semibold rounded-lg hover:bg-industrial-700 transition-colors"
            >
              Learn More
            </Link>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-3xl mx-auto">
            <div className="p-6 bg-industrial-800/50 border border-industrial-700 rounded-xl backdrop-blur-sm">
              <div className="text-3xl font-bold text-status-normal mb-2">99.9%</div>
              <div className="text-sm text-industrial-400">Uptime Guaranteed</div>
            </div>
            <div className="p-6 bg-industrial-800/50 border border-industrial-700 rounded-xl backdrop-blur-sm">
              <div className="text-3xl font-bold text-status-normal mb-2">&lt;100ms</div>
              <div className="text-sm text-industrial-400">Response Time</div>
            </div>
            <div className="p-6 bg-industrial-800/50 border border-industrial-700 rounded-xl backdrop-blur-sm">
              <div className="text-3xl font-bold text-status-normal mb-2">24/7</div>
              <div className="text-sm text-industrial-400">Monitoring</div>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div id="features" className="mt-32 max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-16">
            Enterprise-Grade Features
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-8 bg-industrial-800/30 border border-industrial-700 rounded-xl hover:border-status-normal/50 transition-colors">
              <Shield className="w-12 h-12 text-status-normal mb-4" />
              <h3 className="text-xl font-semibold text-white mb-3">
                Anomaly Detection
              </h3>
              <p className="text-industrial-400">
                ML-powered Isolation Forest algorithm identifies equipment failures before they happen.
              </p>
            </div>
            <div className="p-8 bg-industrial-800/30 border border-industrial-700 rounded-xl hover:border-status-normal/50 transition-colors">
              <Activity className="w-12 h-12 text-status-normal mb-4" />
              <h3 className="text-xl font-semibold text-white mb-3">
                Real-time Monitoring
              </h3>
              <p className="text-industrial-400">
                Live vibration and temperature sensors with sub-second refresh rates.
              </p>
            </div>
            <div className="p-8 bg-industrial-800/30 border border-industrial-700 rounded-xl hover:border-status-normal/50 transition-colors">
              <TrendingUp className="w-12 h-12 text-status-normal mb-4" />
              <h3 className="text-xl font-semibold text-white mb-3">
                Predictive Analytics
              </h3>
              <p className="text-industrial-400">
                Historical trend analysis and forecasting for maintenance planning.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="container mx-auto px-6 py-8 mt-32 border-t border-industrial-800">
        <div className="text-center text-industrial-500">
          <p>&copy; 2025 IIoT Edge Intelligence. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}

import Link from 'next/link'
import { Activity } from 'lucide-react'
import Hero from '@/components/landing/Hero'
import BentoGrid from '@/components/landing/BentoGrid'
import DeveloperSection from '@/components/landing/DeveloperSection'
import StackMarquee from '@/components/landing/StackMarquee'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-zinc-950 text-white selection:bg-emerald-500/30">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 border-b border-white/10 bg-black/50 backdrop-blur-xl">
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Activity className="w-6 h-6 text-emerald-500" />
            <span className="text-lg font-bold tracking-tight">Smart Energy Guardien</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/login" className="text-sm text-zinc-400 hover:text-white transition-colors">
              Log In
            </Link>
            <Link
              href="/dashboard"
              className="px-4 py-2 text-sm font-medium text-black bg-white rounded-full hover:bg-zinc-200 transition-colors"
            >
              Enter Console
            </Link>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <Hero />
      <BentoGrid />
      <DeveloperSection />
      <StackMarquee />

      {/* Final CTA */}
      <section className="relative py-32 px-6 bg-black">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-5xl md:text-6xl font-bold tracking-tighter mb-6 text-white">
            Ready to prevent downtime?
          </h2>
          <p className="text-xl text-zinc-400 mb-12">
            Join hundreds of factories already using Smart Energy Guardien.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/dashboard"
              className="px-8 py-4 bg-white text-black font-semibold rounded-full hover:bg-zinc-200 transition-all shadow-2xl shadow-white/20"
            >
              Let's Get Started
            </Link>
            <Link
              href="https://github.com/H0ussamCl4p/iiot-predictive-maintenance"
              target="_blank"
              className="px-8 py-4 bg-zinc-900 text-white font-semibold rounded-full hover:bg-zinc-800 transition-all border border-zinc-700"
            >
              View Documentation
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}

"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"

const items = [
  { href: "/dashboard", label: "Overview" },
  { href: "/dashboard/data", label: "Data" },
  { href: "/dashboard/anomaly", label: "Anomaly" },
  { href: "/dashboard/prediction", label: "Prediction" },
    { href: "/dashboard/equipment", label: "Equipment", icon: 'wrench' },
    { href: "/dashboard/maintenance", label: "Maintenance", icon: 'calendar' },
    { href: "/dashboard/shifts", label: "Shifts", icon: 'clock' },
    { href: "/dashboard/reports", label: "Reports", icon: 'file' },
    { href: "/dashboard/status", label: "Status" },
]

export default function DashboardNav() {
  const pathname = usePathname()
  return (
    <aside className="w-full lg:w-56 shrink-0">
      <nav className="flex flex-col gap-1 p-2 bg-slate-900/50 border border-slate-800 rounded-xl">
        {items.map((item) => {
          const active = pathname === item.href
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "px-3 py-2 rounded-md transition-colors",
                active
                  ? "bg-slate-700 text-white"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              )}
            >
              {item.label}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}

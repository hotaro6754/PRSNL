'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  Activity, Zap, Terminal, Target, Skull, Radar, BarChart3, Server, 
  Search, Shield, Cpu, ChevronRight, Command
} from 'lucide-react'
import { Badge } from '@/components/ui/Badge'

interface NavGroup {
  label: string
  items: {
    name: string
    href: string
    icon: React.ComponentType<{ className?: string }>
    badge?: string
  }[]
}

const NAV_GROUPS: NavGroup[] = [
  {
    label: 'MONITORING & TELEMETRY',
    items: [
      { name: 'Diode Overview', href: '/', icon: Activity },
      { name: 'Simplex Live Stream', href: '/live', icon: Radar, badge: 'LIVE' },
      { name: 'Flow Analytics', href: '/analytics', icon: BarChart3 }
    ]
  },
  {
    label: 'INCIDENT & FORENSICS',
    items: [
      { name: 'Tunnel Investigations', href: '/cases', icon: Target },
      { name: 'Simplex Flow Ingestion', href: '/scan', icon: Search }
    ]
  },
  {
    label: 'SYSTEM & REPLAY',
    items: [
      { name: 'Attack Replay Lab', href: '/simulator', icon: Skull },
      { name: 'AI/ML Anomaly Lab', href: '/ml', icon: Cpu },
      { name: 'Diode Gateway Health', href: '/health', icon: Server },
      { name: 'Ingress Audit Logs', href: '/logs', icon: Terminal }
    ]
  }
]

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const [mounted, setMounted] = useState(false)
  const [timeStr, setTimeStr] = useState('')

  useEffect(() => {
    setMounted(true)
    const updateTime = () => {
      const now = new Date()
      setTimeStr(now.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) + ' UTC')
    }
    updateTime()
    const timer = setInterval(updateTime, 1000)
    return () => clearInterval(timer)
  }, [])

  // Calculate current breadcrumb
  let currentTitle = 'Diode Overview'
  if (pathname === '/live') currentTitle = 'Simplex Live Stream'
  else if (pathname === '/analytics') currentTitle = 'Flow Analytics'
  else if (pathname === '/cases') currentTitle = 'Tunnel Investigations'
  else if (pathname.startsWith('/cases/')) currentTitle = 'Forensic Investigation'
  else if (pathname === '/scan') currentTitle = 'Simplex Flow Ingestion'
  else if (pathname === '/simulator') currentTitle = 'Attack Replay Lab'
  else if (pathname === '/ml') currentTitle = 'AI/ML Anomaly Lab'
  else if (pathname === '/health') currentTitle = 'Diode Gateway Health'
  else if (pathname === '/logs') currentTitle = 'Ingress Audit Logs'

  return (
    <div className="flex h-screen overflow-hidden bg-[#090a0d] text-zinc-100 font-sans antialiased">
      {/* SIDEBAR */}
      <aside className="w-60 border-r border-white/[0.08] bg-[#0d0f14] flex-shrink-0 flex flex-col justify-between select-none">
        <div>
          {/* Brand Header */}
          <div className="h-13 flex items-center px-4 border-b border-white/[0.08]">
            <Link href="/" className="flex items-center gap-2.5 group">
              <div className="h-7 w-7 rounded bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 group-hover:bg-blue-600/30 transition-colors">
                <Shield className="w-3.5 h-3.5" />
              </div>
              <div>
                <div className="text-xs font-bold tracking-wider text-white font-mono leading-none">SENTINEL-26145</div>
                <div className="text-[10px] text-zinc-500 tracking-widest uppercase font-mono mt-0.5">NTRO Simplex NDR</div>
              </div>
            </Link>
          </div>

          {/* Navigation Groups */}
          <nav className="p-3 space-y-5 overflow-y-auto max-h-[calc(100vh-140px)]">
            {NAV_GROUPS.map((group) => (
              <div key={group.label} className="space-y-1">
                <div className="px-2.5 text-[10px] font-mono font-semibold tracking-wider text-zinc-500 uppercase">
                  {group.label}
                </div>
                <div className="space-y-0.5 pt-1">
                  {group.items.map((item) => {
                    const Icon = item.icon
                    const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href))
                    return (
                      <Link
                        key={item.name}
                        href={item.href}
                        className={`flex items-center justify-between px-2.5 py-1.5 rounded-md text-xs font-mono transition-all ${
                          isActive
                            ? 'bg-white/[0.08] text-white font-medium border border-white/[0.06] shadow-sm'
                            : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.04]'
                        }`}
                      >
                        <div className="flex items-center gap-2.5 truncate">
                          <Icon className={`w-3.5 h-3.5 shrink-0 ${isActive ? 'text-blue-400' : 'text-zinc-500'}`} />
                          <span className="truncate">{item.name}</span>
                        </div>
                        {item.badge && (
                          <span className="text-[9px] font-bold px-1.5 py-0.2 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded">
                            {item.badge}
                          </span>
                        )}
                      </Link>
                    )
                  })}
                </div>
              </div>
            ))}
          </nav>
        </div>

        {/* Physical Diode Hardware Status Card */}
        <div className="p-3 border-t border-white/[0.08]">
          <div className="p-2.5 rounded-md bg-[#12151c] border border-white/[0.06] flex flex-col gap-1.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0" />
                <span className="text-[10px] font-bold tracking-wider text-zinc-300 font-mono uppercase">Diode Link: Simplex Rx</span>
              </div>
              <Badge variant="secure" size="xs">ACTIVE</Badge>
            </div>
            <p className="text-[10px] text-zinc-500 font-mono leading-tight">
              Physical Rx-only tap on eth0. Zero reverse packets on wire.
            </p>
          </div>
        </div>
      </aside>

      {/* MAIN VIEWPORT */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden bg-[#090a0d] relative">
        {/* Topbar */}
        <header className="h-13 flex items-center justify-between px-6 border-b border-white/[0.08] bg-[#0d0f14]/80 backdrop-blur-md shrink-0 sticky top-0 z-20">
          <div className="flex items-center gap-2 text-xs font-mono">
            <span className="text-zinc-500">Sentinel</span>
            <ChevronRight className="w-3 h-3 text-zinc-600" />
            <span className="text-zinc-200 font-medium">{currentTitle}</span>
          </div>

          <div className="flex items-center gap-4">
            {/* Quick Search Shortcut Pill */}
            <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 bg-[#12151c] border border-white/[0.08] rounded text-zinc-500 text-xs font-mono">
              <Search className="w-3.5 h-3.5 text-zinc-500" />
              <span>Jump to flow or case...</span>
              <kbd className="text-[10px] bg-black/40 border border-white/10 px-1 rounded text-zinc-400">⌘K</kbd>
            </div>

            {/* Time Indicator */}
            {mounted && (
              <span className="hidden md:inline-block text-[11px] font-mono text-zinc-400">
                {timeStr}
              </span>
            )}

            {/* Link Security Status Badge */}
            <Badge variant="secure" size="xs" dot>
              OPTICAL LINK SECURE
            </Badge>
          </div>
        </header>

        {/* Canvas Area */}
        <div className="flex-1 overflow-y-auto bg-[#090a0d] p-6">
          {children}
        </div>
      </main>
    </div>
  )
}

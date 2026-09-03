'use client'

import React, { useEffect, useState, useRef, useCallback } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  Shield, Activity, Layers, Terminal, AlertTriangle, 
  Settings, ChevronRight, Search, Bell, ExternalLink,
  Lock, Radio, Cpu, Network, FileText, Database, PanelLeftClose, PanelLeft, GripVertical
} from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'

interface NavItem {
  href: string
  label: string
  icon: React.ReactNode
  badge?: string
}

interface NavGroup {
  label: string
  items: NavItem[]
}

const NAV_GROUPS: NavGroup[] = [
  {
    label: 'MONITORING',
    items: [
      { href: '/', label: 'Diode Overview', icon: <Activity className="w-3.5 h-3.5" /> },
      { href: '/live', label: 'Simplex Live Stream', icon: <Radio className="w-3.5 h-3.5" />, badge: 'LIVE' },
      { href: '/analytics', label: 'Flow Analytics', icon: <Network className="w-3.5 h-3.5" /> },
    ]
  },
  {
    label: 'INVESTIGATION',
    items: [
      { href: '/cases', label: 'Tunnel Investigations', icon: <AlertTriangle className="w-3.5 h-3.5" /> },
      { href: '/scan', label: 'Simplex Flow Ingestion', icon: <Terminal className="w-3.5 h-3.5" /> },
    ]
  },
  {
    label: 'SYSTEM / RESEARCH',
    items: [
      { href: '/simulator', label: 'Attack Replay Lab', icon: <Cpu className="w-3.5 h-3.5" /> },
      { href: '/ml', label: 'AI/ML Anomaly Lab', icon: <Layers className="w-3.5 h-3.5" /> },
      { href: '/health', label: 'Diode Gateway Health', icon: <Shield className="w-3.5 h-3.5" /> },
      { href: '/logs', label: 'Ingress Audit Logs', icon: <FileText className="w-3.5 h-3.5" /> },
    ]
  }
]

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const [mounted, setMounted] = useState(false)
  const [timeStr, setTimeStr] = useState('')
  
  // DRAGGABLE RESIZABLE SIDEBAR STATE
  const [sidebarWidth, setSidebarWidth] = useState(240)
  const [isDragging, setIsDragging] = useState(false)
  const [isCollapsed, setIsCollapsed] = useState(false)
  const sidebarRef = useRef<HTMLElement | null>(null)

  useEffect(() => {
    setMounted(true)
    const updateTime = () => {
      const now = new Date()
      setTimeStr(now.toLocaleTimeString('en-US', { hour12: false, timeZone: 'UTC' }) + ' UTC')
    }
    updateTime()
    const timer = setInterval(updateTime, 1000)

    // Load saved width from localStorage
    const savedWidth = localStorage.getItem('sentinel_sidebar_width')
    if (savedWidth) {
      const parsed = parseInt(savedWidth, 10)
      if (parsed >= 180 && parsed <= 420) {
        setSidebarWidth(parsed)
      }
    }

    return () => clearInterval(timer)
  }, [])

  // Mouse Dragging Logic for Resizing
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging) return
      const newWidth = Math.max(180, Math.min(420, e.clientX))
      setSidebarWidth(newWidth)
    }

    const handleMouseUp = () => {
      if (isDragging) {
        setIsDragging(false)
        localStorage.setItem('sentinel_sidebar_width', sidebarWidth.toString())
      }
    }

    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove)
      window.addEventListener('mouseup', handleMouseUp)
      document.body.style.cursor = 'col-resize'
      document.body.style.userSelect = 'none'
    } else {
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseup', handleMouseUp)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }
  }, [isDragging, sidebarWidth])

  const handleDoubleClickReset = () => {
    setSidebarWidth(240)
    localStorage.setItem('sentinel_sidebar_width', '240')
  }

  // Determine current active section for breadcrumb
  let currentGroup = 'Monitoring'
  let currentTitle = 'Diode Overview'
  if (pathname === '/live') { currentGroup = 'Monitoring'; currentTitle = 'Simplex Live Stream'; }
  else if (pathname === '/analytics') { currentGroup = 'Monitoring'; currentTitle = 'Flow Analytics'; }
  else if (pathname === '/cases') { currentGroup = 'Incidents'; currentTitle = 'Tunnel Investigations'; }
  else if (pathname.startsWith('/cases/')) { currentGroup = 'Incidents'; currentTitle = 'Forensic Investigation'; }
  else if (pathname === '/scan') { currentGroup = 'Incidents'; currentTitle = 'Simplex Flow Ingestion'; }
  else if (pathname === '/simulator') { currentGroup = 'System'; currentTitle = 'Attack Replay Lab'; }
  else if (pathname === '/ml') { currentGroup = 'System'; currentTitle = 'AI/ML Anomaly Lab'; }
  else if (pathname === '/health') { currentGroup = 'System'; currentTitle = 'Diode Gateway Health'; }
  else if (pathname === '/logs') { currentGroup = 'System'; currentTitle = 'Ingress Audit Logs'; }

  return (
    <div className="flex h-screen overflow-hidden bg-[#07080b] text-zinc-100 font-sans antialiased select-none">
      
      {/* DRAGGABLE & RESIZABLE SIDEBAR */}
      <aside 
        ref={sidebarRef}
        style={{ width: isCollapsed ? 64 : sidebarWidth }}
        className={`glass-sidebar flex-shrink-0 flex flex-col justify-between relative transition-[width] ${
          isDragging ? 'transition-none duration-0' : 'duration-200 ease-out'
        }`}
      >
        <div>
          {/* Brand Header */}
          <div className="h-13 flex items-center justify-between px-3.5 border-b border-white/[0.08]">
            <Link href="/" className="flex items-center gap-2.5 group overflow-hidden">
              <div className="h-7 w-7 rounded bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 group-hover:bg-blue-600/30 transition-colors shrink-0">
                <Shield className="w-3.5 h-3.5" />
              </div>
              {!isCollapsed && (
                <div className="overflow-hidden">
                  <div className="text-xs font-bold tracking-wider text-white font-mono leading-none truncate">SENTINEL-26145</div>
                  <div className="text-[9px] text-zinc-500 tracking-widest uppercase font-mono mt-0.5 truncate">NTRO Simplex NDR</div>
                </div>
              )}
            </Link>

            <button
              onClick={() => setIsCollapsed(!isCollapsed)}
              className="p-1 rounded text-zinc-500 hover:text-zinc-300 hover:bg-white/[0.06] transition-colors"
              title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            >
              {isCollapsed ? <PanelLeft className="w-3.5 h-3.5" /> : <PanelLeftClose className="w-3.5 h-3.5" />}
            </button>
          </div>

          {/* Navigation Groups */}
          <div className="p-2 space-y-4 overflow-y-auto max-h-[calc(100vh-170px)]">
            {NAV_GROUPS.map((group, gIdx) => (
              <div key={gIdx} className="space-y-1">
                {!isCollapsed && (
                  <div className="px-2.5 py-1 text-[10px] font-bold text-zinc-500 tracking-wider uppercase font-mono">
                    {group.label}
                  </div>
                )}
                <div className="space-y-0.5">
                  {group.items.map((item) => {
                    const isActive = pathname === item.href
                    return (
                      <Link
                        key={item.href}
                        href={item.href}
                        title={isCollapsed ? item.label : undefined}
                        className={`flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-xs font-mono transition-all ${
                          isActive 
                            ? 'bg-blue-600/15 text-blue-400 border border-blue-500/25 font-semibold shadow-sm' 
                            : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.04]'
                        } ${isCollapsed ? 'justify-center px-0' : ''}`}
                      >
                        <span className={`shrink-0 ${isActive ? 'text-blue-400' : 'text-zinc-400'}`}>
                          {item.icon}
                        </span>
                        {!isCollapsed && (
                          <span className="flex-1 truncate">{item.label}</span>
                        )}
                        {!isCollapsed && item.badge && (
                          <span className="text-[9px] px-1 py-0.2 rounded bg-red-500/20 text-red-400 font-mono font-semibold">
                            {item.badge}
                          </span>
                        )}
                      </Link>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Simplex Physical Diode Status Card */}
        {!isCollapsed && (
          <div className="p-2.5 border-t border-white/[0.08] bg-[#0c0e14]/40">
            <div className="p-2 rounded bg-[#10131a]/80 border border-white/[0.06] flex flex-col gap-1 font-mono">
              <div className="flex items-center justify-between">
                <span className="text-[9px] uppercase tracking-wider text-zinc-500 font-semibold">DIODE LINK</span>
                <Badge variant="secure" size="xs">ACTIVE</Badge>
              </div>
              <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-400">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0" />
                <span>SIMPLEX RX</span>
              </div>
              <p className="text-[9px] text-zinc-500 leading-tight">
                Physical RX-only tap · eth0<br />0 reverse packets
              </p>
            </div>
          </div>
        )}

        {/* DRAGGABLE RESIZE HANDLE */}
        {!isCollapsed && (
          <div
            onMouseDown={handleMouseDown}
            onDoubleClick={handleDoubleClickReset}
            title="Drag to resize sidebar (double-click to reset)"
            className={`absolute top-0 right-0 w-1.5 h-full cursor-col-resize group z-30 flex items-center justify-center hover:bg-blue-500/40 transition-colors ${
              isDragging ? 'bg-blue-500/80 w-2' : 'bg-transparent'
            }`}
          >
            {/* Subtle Grip Indicator on Hover */}
            <div className="hidden group-hover:flex flex-col gap-0.5 items-center justify-center h-8 w-1 rounded bg-blue-500/80 shadow-md">
              <span className="w-0.5 h-0.5 bg-white rounded-full" />
              <span className="w-0.5 h-0.5 bg-white rounded-full" />
              <span className="w-0.5 h-0.5 bg-white rounded-full" />
            </div>
          </div>
        )}
      </aside>

      {/* MAIN VIEWPORT */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden bg-transparent relative select-text">
        {/* Topbar */}
        <header className="h-13 flex items-center justify-between px-6 glass-topbar shrink-0 sticky top-0 z-20">
          <div className="flex items-center gap-2 text-xs font-mono">
            <span className="text-zinc-500">Sentinel</span>
            <ChevronRight className="w-3 h-3 text-zinc-600" />
            <span className="text-zinc-400">{currentGroup}</span>
            <ChevronRight className="w-3 h-3 text-zinc-600" />
            <span className="text-zinc-200 font-medium">{currentTitle}</span>
          </div>

          <div className="flex items-center gap-4">
            {/* Quick Search Shortcut Pill */}
            <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 bg-[#12151c]/80 border border-white/[0.08] rounded text-zinc-500 text-xs font-mono">
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

            {/* Status Dot */}
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              <span className="text-xs font-mono text-zinc-300">100% SIMPLEX</span>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <div className="flex-1 overflow-y-auto p-5">
          {children}
        </div>
      </main>

    </div>
  )
}

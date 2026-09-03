'use client'

import React, { useEffect, useState, useRef, useCallback } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  Shield, Activity, Layers, Terminal, AlertTriangle, 
  Settings, ChevronRight, Search, Bell, ExternalLink,
  Lock, Radio, Cpu, Network, FileText, Database, PanelLeftClose, PanelLeft, GripVertical,
  BookOpen
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
      { href: '/', label: 'Diode Overview', icon: <Activity className="w-4 h-4" /> },
      { href: '/live', label: 'Simplex Live Stream', icon: <Radio className="w-4 h-4" />, badge: 'LIVE' },
      { href: '/analytics', label: 'Flow Analytics', icon: <Network className="w-4 h-4" /> },
    ]
  },
  {
    label: 'INVESTIGATION',
    items: [
      { href: '/cases', label: 'Tunnel Investigations', icon: <AlertTriangle className="w-4 h-4" /> },
      { href: '/scan', label: 'Simplex Flow Ingestion', icon: <Terminal className="w-4 h-4" /> },
    ]
  },
  {
    label: 'SYSTEM / RESEARCH',
    items: [
      { href: '/simulator', label: 'Attack Replay Lab', icon: <Cpu className="w-4 h-4" /> },
      { href: '/ml', label: 'AI/ML Anomaly Lab', icon: <Layers className="w-4 h-4" /> },
      { href: '/health', label: 'Diode Gateway Health', icon: <Shield className="w-4 h-4" /> },
      { href: '/logs', label: 'Ingress Audit Logs', icon: <FileText className="w-4 h-4" /> },
    ]
  },
  {
    label: 'ACADEMY & TRAINING',
    items: [
      { href: '/course', label: 'Master Course (PS26145)', icon: <BookOpen className="w-4 h-4" />, badge: '53 MODS' },
    ]
  }
]

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const [mounted, setMounted] = useState(false)
  const [timeStr, setTimeStr] = useState('')
  
  // DRAGGABLE & TWO-MODE SIDEBAR (EXPANDED OR COMPACT ICON-RAIL)
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

    // Load saved width & state from localStorage
    const savedWidth = localStorage.getItem('sentinel_sidebar_width')
    if (savedWidth) {
      const parsed = parseInt(savedWidth, 10)
      if (parsed >= 200 && parsed <= 400) {
        setSidebarWidth(parsed)
      }
    }
    const savedCollapsed = localStorage.getItem('sentinel_sidebar_collapsed')
    if (savedCollapsed === 'true') {
      setIsCollapsed(true)
    }

    return () => clearInterval(timer)
  }, [])

  const toggleCollapse = () => {
    const next = !isCollapsed
    setIsCollapsed(next)
    localStorage.setItem('sentinel_sidebar_collapsed', next ? 'true' : 'false')
  }

  // Mouse Dragging Logic for Resizing
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging) return
      const currentX = e.clientX

      // If dragged very narrow, snap directly to icon mode
      if (currentX < 150) {
        if (!isCollapsed) {
          setIsCollapsed(true)
          localStorage.setItem('sentinel_sidebar_collapsed', 'true')
        }
      } else {
        if (isCollapsed) {
          setIsCollapsed(false)
          localStorage.setItem('sentinel_sidebar_collapsed', 'false')
        }
        const newWidth = Math.max(200, Math.min(380, currentX))
        setSidebarWidth(newWidth)
      }
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
  }, [isDragging, isCollapsed, sidebarWidth])

  const handleDoubleClickReset = () => {
    setSidebarWidth(240)
    setIsCollapsed(false)
    localStorage.setItem('sentinel_sidebar_width', '240')
    localStorage.setItem('sentinel_sidebar_collapsed', 'false')
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
      
      {/* DRAGGABLE & CLEAN TWO-MODE SIDEBAR */}
      <aside 
        ref={sidebarRef}
        style={{ width: isCollapsed ? 64 : sidebarWidth }}
        className={`glass-sidebar flex-shrink-0 flex flex-col justify-between relative transition-[width] ${
          isDragging ? 'transition-none duration-0' : 'duration-200 ease-out'
        }`}
      >
        <div>
          {/* BRAND HEADER: NO OVERLAPPING / NO CLIPPING */}
          {isCollapsed ? (
            <div className="h-13 flex items-center justify-center border-b border-white/[0.08]">
              <button
                onClick={toggleCollapse}
                className="h-8 w-8 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 hover:bg-blue-600/30 hover:border-blue-400/50 transition-all cursor-pointer shadow-sm group"
                title="Expand Sidebar (SENTINEL-26145)"
              >
                <Shield className="w-4 h-4 group-hover:scale-110 transition-transform" />
              </button>
            </div>
          ) : (
            <div className="h-13 flex items-center justify-between px-3.5 border-b border-white/[0.08]">
              <Link href="/" className="flex items-center gap-2.5 group overflow-hidden">
                <div className="h-7 w-7 rounded bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 group-hover:bg-blue-600/30 transition-colors shrink-0">
                  <Shield className="w-3.5 h-3.5" />
                </div>
                <div className="overflow-hidden">
                  <div className="text-xs font-bold tracking-wider text-white font-mono leading-none truncate">SENTINEL-26145</div>
                  <div className="text-[9px] text-zinc-500 tracking-widest uppercase font-mono mt-0.5 truncate">NTRO Simplex NDR</div>
                </div>
              </Link>

              <button
                onClick={toggleCollapse}
                className="p-1.5 rounded text-zinc-500 hover:text-zinc-200 hover:bg-white/[0.08] transition-colors cursor-pointer"
                title="Collapse to Icon Rail"
              >
                <PanelLeftClose className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {/* NAVIGATION ITEMS */}
          <div className={`p-2 space-y-3 overflow-y-auto max-h-[calc(100vh-140px)] ${isCollapsed ? 'px-1.5' : 'px-2'}`}>
            {NAV_GROUPS.map((group, gIdx) => (
              <div key={gIdx} className="space-y-1">
                {/* Section title (Expanded Mode Only) */}
                {!isCollapsed ? (
                  <div className="px-2.5 py-1 text-[10px] font-bold text-zinc-500 tracking-wider uppercase font-mono">
                    {group.label}
                  </div>
                ) : gIdx > 0 ? (
                  // Subtle divider between icon groups in collapsed mode
                  <div className="w-6 h-[1px] bg-white/[0.06] mx-auto my-2" />
                ) : null}

                <div className="space-y-1">
                  {group.items.map((item) => {
                    const isActive = pathname === item.href
                    
                    if (isCollapsed) {
                      // Compact Icon-Rail Pill
                      return (
                        <Link
                          key={item.href}
                          href={item.href}
                          title={item.label}
                          className={`w-10 h-10 mx-auto rounded-lg flex items-center justify-center transition-all cursor-pointer relative group ${
                            isActive
                              ? 'bg-blue-600/25 text-blue-400 border border-blue-500/40 shadow-[0_0_12px_rgba(59,130,246,0.25)]'
                              : 'text-zinc-400 hover:text-zinc-100 hover:bg-white/[0.06]'
                          }`}
                        >
                          <span className={isActive ? 'text-blue-400' : 'text-zinc-400 group-hover:text-white'}>
                            {item.icon}
                          </span>
                          
                          {/* Dot indicator for live items */}
                          {item.badge && (
                            <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-red-500" />
                          )}
                        </Link>
                      )
                    }

                    // Expanded Normal Mode Item
                    return (
                      <Link
                        key={item.href}
                        href={item.href}
                        className={`flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-xs font-mono transition-all ${
                          isActive 
                            ? 'bg-blue-600/15 text-blue-400 border border-blue-500/25 font-semibold shadow-sm' 
                            : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.04]'
                        }`}
                      >
                        <span className={`shrink-0 ${isActive ? 'text-blue-400' : 'text-zinc-400'}`}>
                          {item.icon}
                        </span>
                        <span className="flex-1 truncate">{item.label}</span>
                        {item.badge && (
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

        {/* BOTTOM STATUS FOOTER: FILLED & BALANCED */}
        {isCollapsed ? (
          <div className="p-2 border-t border-white/[0.08] bg-[#0c0e14]/60 flex flex-col items-center justify-center gap-1.5">
            <button 
              onClick={toggleCollapse}
              className="w-10 h-10 rounded-lg bg-[#11141d] border border-white/[0.08] flex flex-col items-center justify-center text-emerald-400 hover:border-emerald-500/40 hover:bg-emerald-500/10 transition-all cursor-pointer group"
              title="Optical Simplex Link: ACTIVE (eth0 · 0 Reverse Pkts)"
            >
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-[7px] font-mono font-bold text-emerald-400 mt-0.5">1-WAY</span>
            </button>
          </div>
        ) : (
          <div className="p-2.5 border-t border-white/[0.08] bg-[#0c0e14]/40">
            <div className="p-2.5 rounded bg-[#10131a]/80 border border-white/[0.06] flex flex-col gap-1.5 font-mono">
              <div className="flex items-center justify-between">
                <span className="text-[9px] uppercase tracking-wider text-zinc-500 font-semibold">DIODE HARDWARE</span>
                <Badge variant="secure" size="xs">ACTIVE</Badge>
              </div>
              <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-400">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0 animate-pulse" />
                <span>SIMPLEX RX · ETH0</span>
              </div>
              <div className="flex items-center justify-between text-[9px] text-zinc-400 pt-1 border-t border-white/[0.04]">
                <span>Leakage: 0 PKTS</span>
                <span className="text-emerald-400 font-semibold">0 ACKs</span>
              </div>
            </div>
          </div>
        )}

        {/* DRAGGABLE RESIZE HANDLE (EXPANDED MODE ONLY) */}
        {!isCollapsed && (
          <div
            onMouseDown={handleMouseDown}
            onDoubleClick={handleDoubleClickReset}
            title="Drag to resize sidebar (double-click to reset to 240px)"
            className={`absolute top-0 right-0 w-1.5 h-full cursor-col-resize group z-30 flex items-center justify-center hover:bg-blue-500/40 transition-colors ${
              isDragging ? 'bg-blue-500/80 w-2' : 'bg-transparent'
            }`}
          >
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
            {isCollapsed && (
              <button
                onClick={toggleCollapse}
                className="mr-2 p-1.5 rounded text-zinc-400 hover:text-white hover:bg-white/[0.08] transition-colors cursor-pointer"
                title="Expand Sidebar"
              >
                <PanelLeft className="w-4 h-4" />
              </button>
            )}
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
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
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

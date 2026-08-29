'use client'
import Link from 'next/link'
import { Activity, Zap, Terminal, Target, Skull, Radar, BarChart3, Server, Search } from 'lucide-react'

const NAV_ITEMS = [
  { name: 'Overview', href: '/', icon: <Activity className="w-4 h-4" /> },
  { name: 'Live Threats', href: '/live', icon: <Radar className="w-4 h-4" /> },
  { name: 'Investigations', href: '/cases', icon: <Target className="w-4 h-4" /> },
  { name: 'Analytics', href: '/analytics', icon: <BarChart3 className="w-4 h-4" /> },
  { name: 'ML Intelligence', href: '/ml', icon: <Zap className="w-4 h-4" /> },
  { name: 'System Health', href: '/health', icon: <Server className="w-4 h-4" /> },
  { name: 'Logs & Audit', href: '/logs', icon: <Terminal className="w-4 h-4" /> },
  { name: 'Action Center', href: '/simulator', icon: <Skull className="w-4 h-4" /> },
  { name: 'Scan Content', href: '/scan', icon: <Search className="w-4 h-4" /> },
]

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800 bg-[#0c0f17] flex-shrink-0 flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-slate-800 shrink-0">
          <div className="flex items-center gap-3 font-bold text-lg tracking-tight">
            <img src="/cyberos-logo.jpeg" alt="CyberOS" className="h-8 w-8 rounded-md object-cover" />
            Cyber<span className="text-blue-500">OS</span>
          </div>
        </div>
        <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
          <div className="text-xs font-semibold text-slate-500 mb-4 px-2 uppercase tracking-wider">Navigation</div>
          {NAV_ITEMS.map((item) => (
            <Link key={item.name} href={item.href} className="flex items-center gap-3 px-3 py-2 text-slate-400 hover:text-white hover:bg-slate-800/50 rounded-md font-medium text-sm transition-colors">
              {item.icon}
              {item.name}
            </Link>
          ))}
        </nav>
        <div className="p-4 m-4 rounded-xl bg-slate-800/30 border border-slate-700/50 shrink-0">
          <div className="flex items-center gap-2 mb-2">
            <div className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
            </div>
            <span className="text-xs font-medium text-slate-300 uppercase tracking-wider">Engine Online</span>
          </div>
          <p className="text-xs text-slate-500">System is actively enforcing security policies.</p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden bg-black relative">
        {/* Topbar */}
        <header className="h-16 flex items-center justify-between px-8 border-b border-slate-800/60 shrink-0 sticky top-0 z-10 bg-black/50 backdrop-blur-md">
          <h1 className="text-lg font-semibold tracking-tight">CyberOS Command Center</h1>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-slate-400 bg-slate-800/40 px-3 py-1.5 rounded-md border border-slate-700/50">
              <div className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
              </div>
              <span className="font-semibold text-green-400">All Systems Operational</span>
            </div>
          </div>
        </header>
        
        {/* Scrollable Canvas */}
        <div className="flex-1 overflow-auto bg-[#0a0a0a]">
          {children}
        </div>
      </main>
    </div>
  )
}

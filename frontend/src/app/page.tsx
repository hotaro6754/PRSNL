'use client'
import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, YAxis, CartesianGrid, AreaChart, Area } from 'recharts'
import { Activity, ShieldAlert, Zap, Server, Shield } from 'lucide-react'

const COLORS = {
  CRITICAL: '#ef4444',
  HIGH: '#f97316',
  MEDIUM: '#eab308',
  LOW: '#3b82f6',
}

export default function Overview() {
  const [stats, setStats] = useState<any>({
    flows_processed: 0,
    ml_inferences: 0,
    alerts_per_min: 0,
    throughput_fps: 0,
    active_cases: 0,
    critical_cases: 0
  })
  
  const [health, setHealth] = useState<any>(null)
  const [metricsHistory, setMetricsHistory] = useState<any[]>([])

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, healthRes, metricsRes] = await Promise.all([
          fetch('http://localhost:8000/api/stats'),
          fetch('http://localhost:8000/health'),
          fetch('http://localhost:8000/api/metrics/history')
        ])
        if (statsRes.ok) setStats(await statsRes.json())
        if (healthRes.ok) setHealth(await healthRes.json())
        if (metricsRes.ok) setMetricsHistory(await metricsRes.json())
      } catch (err) {}
    }
    fetchData()
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [])

  // Time formatting for charts
  const formatTime = (isoString: string) => {
    if (!isoString) return ''
    const d = new Date(isoString)
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`
  }

  const isHealthy = health?.status === "ok"

  return (
    <div className="space-y-6 animate-in fade-in duration-500 max-w-[1600px]">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">SOC Overview</h2>
          <p className="text-sm text-slate-400">Live operational awareness from all sensors.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {[
          { label: "Active Cases", value: (stats?.active_cases || 0).toLocaleString(), icon: <ShieldAlert className="w-4 h-4 text-orange-400"/>, sub: `${stats?.critical_cases || 0} critical` },
          { label: "Alerts / Min", value: (stats?.alerts_per_min || 0).toFixed(1), icon: <Activity className="w-4 h-4 text-red-400"/>, sub: "Last 60s avg" },
          { label: "Throughput", value: `${(stats?.throughput_fps || 0).toFixed(1)} fps`, icon: <Zap className="w-4 h-4 text-blue-400"/>, sub: "Network flows/sec" },
          { label: "ML Inferences", value: (stats?.ml_inferences || 0).toLocaleString(), icon: <Shield className="w-4 h-4 text-purple-400"/>, sub: "Evaluated by XGBoost" },
          { label: "System Health", value: isHealthy ? "HEALTHY" : "DEGRADED", icon: <Server className={`w-4 h-4 ${isHealthy ? 'text-green-400' : 'text-red-400'}`}/>, sub: isHealthy ? "All sensors active" : (health?.error || "Check diagnostics") },
        ].map((stat, i) => (
          <div key={i} className="rounded-xl border border-slate-800 bg-[#0c0f17] p-5 shadow-sm">
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-sm font-medium text-slate-400 tracking-tight">{stat.label}</h3>
              {stat.icon}
            </div>
            <div className="text-2xl font-semibold text-white tracking-tight">{stat.value}</div>
            <div className="text-xs text-slate-500 mt-1">{stat.sub}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Network Throughput Chart */}
        <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-5">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-white">Network Flow Rate (fps)</h3>
            <p className="text-xs text-slate-500">Real-time throughput processed by Zeek Adapter</p>
          </div>
          <div className="h-64">
            {metricsHistory.length === 0 ? (
              <div className="h-full flex items-center justify-center text-slate-500">Awaiting telemetry...</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={metricsHistory} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorFps" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="timestamp" tickFormatter={formatTime} stroke="#64748b" fontSize={12} tickMargin={10} minTickGap={30} />
                  <YAxis stroke="#64748b" fontSize={12} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff' }} 
                    labelFormatter={(l) => formatTime(l as string)}
                  />
                  <Area type="monotone" dataKey="flows_per_sec" stroke="#3b82f6" fillOpacity={1} fill="url(#colorFps)" isAnimationActive={false} />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Alerts per minute chart */}
        <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-5">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-white">Threat Activity (alerts/min)</h3>
            <p className="text-xs text-slate-500">Aggregated alert volume from detection engines</p>
          </div>
          <div className="h-64">
            {metricsHistory.length === 0 ? (
              <div className="h-full flex items-center justify-center text-slate-500">Awaiting telemetry...</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={metricsHistory} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorAlerts" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="timestamp" tickFormatter={formatTime} stroke="#64748b" fontSize={12} tickMargin={10} minTickGap={30} />
                  <YAxis stroke="#64748b" fontSize={12} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff' }} 
                    labelFormatter={(l) => formatTime(l as string)}
                  />
                  <Area type="monotone" dataKey="alerts_per_min" stroke="#ef4444" fillOpacity={1} fill="url(#colorAlerts)" isAnimationActive={false} />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>
      
    </div>
  )
}

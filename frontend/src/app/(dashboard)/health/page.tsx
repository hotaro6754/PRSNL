'use client'

import React, { useEffect, useState } from 'react'
import { Activity, Server, Database, ShieldAlert, Cpu, Network, Zap } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { StatCard } from '@/components/ui/StatCard'
import { Badge } from '@/components/ui/Badge'

const CustomChartTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-md border border-white/[0.12] bg-[#141720] p-2.5 shadow-lg text-xs font-mono">
        <div className="text-zinc-400 mb-1">{label}</div>
        {payload.map((p: any, i: number) => (
          <div key={i} className="font-semibold text-zinc-100 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full" style={{ background: p.color || '#3b82f6' }} />
            <span>{p.name || 'Value'}: {p.value}</span>
          </div>
        ))}
      </div>
    )
  }
  return null
}

export default function SystemHealthDashboard() {
  const [health, setHealth] = useState<any>(null)
  const [stats, setStats] = useState<any>(null)
  const [metrics, setMetrics] = useState<any[]>([])

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [healthRes, statsRes, metricsRes] = await Promise.all([
          fetch("http://localhost:8000/health").then(res => res.json()).catch(() => null),
          fetch("http://localhost:8000/api/stats").then(res => res.json()).catch(() => null),
          fetch("http://localhost:8000/api/metrics/history").then(res => res.json()).catch(() => [])
        ])
        
        setHealth(healthRes)
        setStats(statsRes)
        setMetrics(metricsRes || [])
      } catch (err) {
        console.error("Failed to fetch system data", err)
      }
    }
    
    fetchData()
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [])

  const isHealthy = health?.status === 'ok'

  return (
    <div className="space-y-6 max-w-[1500px] mx-auto animate-in fade-in duration-300 font-mono">
      {/* PAGE HEADER */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-white/[0.06] pb-4">
        <div>
          <h1 className="text-base font-bold tracking-tight text-white font-mono uppercase flex items-center gap-2">
            <Server className="w-4 h-4 text-emerald-400" />
            Diode Gateway Health & Telemetry
          </h1>
          <p className="text-xs text-zinc-400 mt-0.5">
            Unified telemetry of infrastructure containers, ML inference engines, and raw stream throughput.
          </p>
        </div>

        <Badge variant={isHealthy ? 'secure' : 'critical'} size="xs" dot>
          {isHealthy ? 'GATEWAY OPERATIONAL' : 'DEGRADED STATE'}
        </Badge>
      </div>

      {/* 4 PRIMARY METRIC CARDS */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5">
        <StatCard
          label="THROUGHPUT RATE"
          value={`${stats?.processed_eps || 0} EPS`}
          subtext="Processed Events / Sec"
          icon={<Activity className="w-4 h-4 text-emerald-400" />}
        />
        <StatCard
          label="ACTIVE INCIDENTS"
          value={stats?.active || 0}
          subtext={`${stats?.critical || 0} Critical Alerts`}
          highlight={stats?.critical > 0 ? 'critical' : 'default'}
          icon={<ShieldAlert className="w-4 h-4 text-red-400" />}
        />
        <StatCard
          label="DATABASE ENGINE"
          value={health?.components?.database || 'HEALTHY'}
          subtext="MongoDB Persistence"
          highlight="secure"
          icon={<Database className="w-4 h-4 text-blue-400" />}
        />
        <StatCard
          label="GATEWAY UPTIME"
          value={`${(stats?.uptime / 3600)?.toFixed(1) || '0.0'}h`}
          subtext="Continuous Simplex Tap"
          icon={<Server className="w-4 h-4 text-purple-400" />}
        />
      </div>

      {/* STREAM CHARTS ROW */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="py-3 px-4">
            <div className="flex items-center justify-between">
              <CardTitle>Pipeline Event Throughput</CardTitle>
              <Badge variant="secure" size="xs">LIVE FLOW</Badge>
            </div>
          </CardHeader>
          <CardContent className="p-4 pt-1">
            <div className="h-[220px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={metrics} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorEps" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.25}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis 
                    dataKey="timestamp" 
                    tick={{ fill: '#71717a', fontSize: 10, fontFamily: 'monospace' }} 
                    tickFormatter={(t) => new Date(t).toLocaleTimeString('en-US', { hour12: false })} 
                    axisLine={false} 
                  />
                  <YAxis tick={{ fill: '#71717a', fontSize: 10, fontFamily: 'monospace' }} axisLine={false} />
                  <Tooltip content={<CustomChartTooltip />} />
                  <Area type="monotone" dataKey="flows_processed" stroke="#10b981" fillOpacity={1} fill="url(#colorEps)" strokeWidth={1.5} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="py-3 px-4">
            <div className="flex items-center justify-between">
              <CardTitle>ML Classifier Inference Rate</CardTitle>
              <Badge variant="info" size="xs">INFERENCE</Badge>
            </div>
          </CardHeader>
          <CardContent className="p-4 pt-1">
            <div className="h-[220px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={metrics} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis 
                    dataKey="timestamp" 
                    tick={{ fill: '#71717a', fontSize: 10, fontFamily: 'monospace' }} 
                    tickFormatter={(t) => new Date(t).toLocaleTimeString('en-US', { hour12: false })} 
                    axisLine={false} 
                  />
                  <YAxis tick={{ fill: '#71717a', fontSize: 10, fontFamily: 'monospace' }} axisLine={false} />
                  <Tooltip content={<CustomChartTooltip />} />
                  <Line type="monotone" dataKey="ml_inferences" stroke="#3b82f6" strokeWidth={1.5} dot={false} activeDot={{ r: 4, fill: '#3b82f6' }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* GRAFANA LIVE TELEMETRY EMBED */}
      <Card className="overflow-hidden">
        <CardHeader className="py-3 px-4 flex-row justify-between items-center space-y-0">
          <div className="flex items-center gap-2">
            <Network className="w-4 h-4 text-blue-400" />
            <CardTitle>Grafana / Prometheus Live Infrastructure Fabric</CardTitle>
          </div>
          <span className="text-[11px] text-zinc-500 font-mono">:3001</span>
        </CardHeader>
        <div className="h-[340px] p-0 border-t border-white/[0.06] bg-[#07080a]">
          <iframe 
            src="http://localhost:3001/d/cyber-01/cyberos-realtime?orgId=1&kiosk=tv&theme=dark" 
            width="100%" 
            height="100%" 
            className="border-0 opacity-85" 
          />
        </div>
      </Card>
    </div>
  )
}

'use client'

import React, { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, CartesianGrid, YAxis } from 'recharts'
import { BarChart3, AlertCircle, Activity } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'

const SEV_COLORS: Record<string, string> = {
  CRITICAL: '#ef4444',
  HIGH: '#f59e0b',
  MEDIUM: '#eab308',
  LOW: '#10b981',
}

const VECTOR_COLORS = ['#3b82f6', '#a855f7', '#06b6d4', '#f97316', '#ef4444', '#ec4899', '#10b981']

const CustomChartTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-md border border-white/[0.12] bg-[#141720] p-2.5 shadow-lg text-xs font-mono">
        <div className="text-zinc-400 mb-1">{label}</div>
        <div className="font-semibold text-zinc-100 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full" style={{ background: payload[0].payload.fill || '#3b82f6' }} />
          <span>{payload[0].name || 'Count'}: {payload[0].value}</span>
        </div>
      </div>
    )
  }
  return null
}

export default function AnalyticsPage() {
  const [alerts, setAlerts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/alerts?limit=1000')
        if (res.ok) setAlerts(await res.json())
      } catch (err) {
        console.error("Failed to load alerts")
      } finally {
        setLoading(false)
      }
    }
    fetchAlerts()
  }, [])

  const severityCounts = alerts.reduce((acc, a) => {
    acc[a.severity] = (acc[a.severity] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const severityData = Object.keys(severityCounts).map(key => ({
    name: key,
    value: severityCounts[key],
    fill: SEV_COLORS[key] || '#71717a'
  }))

  const threatCounts = alerts.reduce((acc, a) => {
    acc[a.threat_class] = (acc[a.threat_class] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const threatData = Object.keys(threatCounts).map((key, idx) => ({
    name: key,
    count: threatCounts[key],
    fill: VECTOR_COLORS[idx % VECTOR_COLORS.length]
  })).sort((a, b) => b.count - a.count)

  const entityCounts = alerts.reduce((acc, a) => {
    acc[a.source_ip] = (acc[a.source_ip] || 0) + 1
    return acc
  }, {} as Record<string, number>)
  
  const entityData = Object.keys(entityCounts).map(key => ({
    ip: key,
    alerts: entityCounts[key]
  })).sort((a, b) => b.alerts - a.alerts).slice(0, 10)

  if (loading) {
    return (
      <div className="min-h-[400px] flex items-center justify-center p-12 text-center text-zinc-500 font-mono">
        <div className="flex flex-col items-center gap-3">
          <span className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-xs">Aggregating historical threat analytics...</span>
        </div>
      </div>
    )
  }

  if (alerts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-16 text-zinc-500 border border-white/[0.08] rounded-lg bg-[#111318] max-w-[1500px] mx-auto font-mono text-xs">
        <AlertCircle className="w-8 h-8 mb-3 text-zinc-600" />
        <h3 className="text-sm font-semibold text-zinc-200 mb-1">No Analytic Telemetry Available</h3>
        <p className="text-zinc-500">Replay PCAP traffic or start the passive line-rate sniffer to generate telemetry events.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-[1500px] mx-auto animate-in fade-in duration-300 font-mono">
      {/* PAGE HEADER */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-white/[0.06] pb-4">
        <div>
          <h1 className="text-base font-bold tracking-tight text-white font-mono uppercase flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-blue-400" />
            Unidirectional Traffic Analytics
          </h1>
          <p className="text-xs text-zinc-400 mt-0.5">
            Aggregated historical telemetry, severity distributions, and source frequency rankings.
          </p>
        </div>

        <Badge variant="info" size="xs">
          {alerts.length} AGGREGATED EVENTS
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Severity Distribution */}
        <Card>
          <CardHeader className="py-3 px-4">
            <CardTitle>Historical Severity Distribution</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-1">
            <div className="h-[220px] w-full flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={severityData}
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={3}
                    dataKey="value"
                    stroke="rgba(0,0,0,0.5)"
                    strokeWidth={1}
                  >
                    {severityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomChartTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Threat Class Distribution */}
        <Card>
          <CardHeader className="py-3 px-4">
            <CardTitle>Threat Vectors by Frequency</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-1">
            <div className="h-[220px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={threatData} layout="vertical" margin={{ top: 5, right: 20, left: 30, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                  <XAxis type="number" tick={{ fill: '#71717a', fontSize: 10, fontFamily: 'monospace' }} axisLine={false} />
                  <YAxis dataKey="name" type="category" tick={{ fill: '#a1a1aa', fontSize: 9, fontFamily: 'monospace' }} width={90} axisLine={false} />
                  <Tooltip content={<CustomChartTooltip />} />
                  <Bar dataKey="count" radius={[0, 3, 3, 0]} barSize={12}>
                    {threatData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Top Adversary Source IPs */}
        <Card className="md:col-span-2">
          <CardHeader className="py-3 px-4">
            <CardTitle>Top Ingress Attacker IPs (by Alert Volume)</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-1">
            <div className="h-[240px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={entityData} margin={{ top: 10, right: 20, left: -10, bottom: 25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis dataKey="ip" tick={{ fill: '#71717a', fontSize: 10, fontFamily: 'monospace' }} angle={-25} textAnchor="end" axisLine={false} />
                  <YAxis tick={{ fill: '#71717a', fontSize: 10, fontFamily: 'monospace' }} axisLine={false} />
                  <Tooltip content={<CustomChartTooltip />} />
                  <Bar dataKey="alerts" fill="#3b82f6" radius={[3, 3, 0, 0]} barSize={16} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

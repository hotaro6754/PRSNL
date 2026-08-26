'use client'
import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, CartesianGrid, YAxis, Legend } from 'recharts'
import { BarChart3, AlertCircle } from 'lucide-react'

const COLORS = {
  CRITICAL: '#ef4444',
  HIGH: '#f97316',
  MEDIUM: '#eab308',
  LOW: '#3b82f6',
}

const THREAT_COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316', '#eab308', '#22c55e']

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

  // Aggregate Data
  const severityCounts = alerts.reduce((acc, a) => {
    acc[a.severity] = (acc[a.severity] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const severityData = Object.keys(severityCounts).map(key => ({
    name: key,
    value: severityCounts[key]
  }))

  const threatCounts = alerts.reduce((acc, a) => {
    acc[a.threat_class] = (acc[a.threat_class] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const threatData = Object.keys(threatCounts).map(key => ({
    name: key,
    count: threatCounts[key]
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
    return <div className="p-12 text-center text-slate-500">Aggregating threat data...</div>
  }

  if (alerts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-24 text-slate-500 border border-slate-800 rounded-xl bg-[#0c0f17]">
        <AlertCircle className="w-12 h-12 mb-4 text-slate-600" />
        <h3 className="text-lg font-semibold text-white mb-2">No Analytic Data</h3>
        <p>There are no historical alerts in the database to aggregate.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-[1600px] animate-in fade-in duration-500">
      <div>
        <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <BarChart3 className="w-6 h-6 text-blue-500" />
          Threat Analytics
        </h2>
        <p className="text-sm text-slate-400">Aggregated historical metrics from all detection sources.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Severity Distribution */}
        <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-6">
          <h3 className="text-sm font-semibold text-white mb-6 uppercase tracking-wider">Severity Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={severityData}
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[entry.name as keyof typeof COLORS] || '#8884d8'} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Threat Class Distribution */}
        <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-6">
          <h3 className="text-sm font-semibold text-white mb-6 uppercase tracking-wider">Threat Vectors</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={threatData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" stroke="#64748b" fontSize={12} />
                <YAxis dataKey="name" type="category" stroke="#64748b" fontSize={12} width={100} />
                <Tooltip cursor={{ fill: '#1e293b' }} contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }} />
                <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                  {threatData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={THREAT_COLORS[index % THREAT_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Entities */}
        <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-6 md:col-span-2">
          <h3 className="text-sm font-semibold text-white mb-6 uppercase tracking-wider">Top Attackers (by Alert Volume)</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={entityData} margin={{ top: 5, right: 30, left: 20, bottom: 25 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="ip" stroke="#64748b" fontSize={12} angle={-45} textAnchor="end" />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip cursor={{ fill: '#1e293b' }} contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }} />
                <Bar dataKey="alerts" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  )
}

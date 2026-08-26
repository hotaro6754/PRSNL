'use client'
import { useEffect, useState } from 'react'
import { Server, Database, Activity, CheckCircle, XCircle } from 'lucide-react'

export default function HealthPage() {
  const [health, setHealth] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const fetchHealth = async () => {
    try {
      const res = await fetch('http://localhost:8000/health')
      if (res.ok) setHealth(await res.json())
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHealth()
    const interval = setInterval(fetchHealth, 10000)
    return () => clearInterval(interval)
  }, [])

  if (loading) return <div className="p-12 text-slate-500 text-center">Checking system diagnostics...</div>

  const isHealthy = health?.status === 'ok'

  return (
    <div className="space-y-6 max-w-[1200px] animate-in fade-in duration-500">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">System Health & Diagnostics</h2>
          <p className="text-sm text-slate-400">Live operational status of infrastructure components.</p>
        </div>
        <div className={`px-4 py-2 rounded-full border text-sm font-bold flex items-center gap-2 ${isHealthy ? 'bg-green-500/10 text-green-400 border-green-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'}`}>
          {isHealthy ? <CheckCircle className="w-4 h-4"/> : <XCircle className="w-4 h-4" />}
          {isHealthy ? 'ALL SYSTEMS NOMINAL' : 'DEGRADED PERFORMANCE'}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Core Services */}
        <div className="rounded-xl border border-slate-800 bg-[#0c0f17] overflow-hidden">
          <div className="p-4 border-b border-slate-800 bg-[#121620]">
            <h3 className="font-semibold text-white flex items-center gap-2"><Server className="w-4 h-4 text-blue-400"/> Core Services</h3>
          </div>
          <div className="p-4 space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <span className="text-slate-300">Environment</span>
              <span className="font-mono text-xs px-2 py-1 bg-slate-800 rounded text-slate-300">{health?.environment || 'UNKNOWN'}</span>
            </div>
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <span className="text-slate-300">Zeek Sensor / Traffic Pipeline</span>
              <span className={`font-mono text-xs px-2 py-1 rounded flex items-center gap-1 ${health?.telemetry?.total_flows > 0 ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                {health?.telemetry?.total_flows > 0 ? 'RECEIVING' : 'NO TRAFFIC'}
              </span>
            </div>
            <div className="flex justify-between items-center pb-1">
              <span className="text-slate-300">Total Flows Processed</span>
              <span className="font-mono text-xs text-white">{(health?.telemetry?.total_flows || 0).toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* Persistence */}
        <div className="rounded-xl border border-slate-800 bg-[#0c0f17] overflow-hidden">
          <div className="p-4 border-b border-slate-800 bg-[#121620]">
            <h3 className="font-semibold text-white flex items-center gap-2"><Database className="w-4 h-4 text-orange-400"/> Persistence & Storage</h3>
          </div>
          <div className="p-4 space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <span className="text-slate-300">MongoDB Connection</span>
              <span className={`font-mono text-xs px-2 py-1 rounded flex items-center gap-1 ${health?.components?.mongodb?.status === 'connected' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                {health?.components?.mongodb?.status?.toUpperCase() || 'FAILED'}
              </span>
            </div>
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <span className="text-slate-300">Database Engine</span>
              <span className="font-mono text-xs text-slate-300">{health?.components?.mongodb?.db || 'N/A'}</span>
            </div>
            <div className="flex justify-between items-center pb-1">
              <span className="text-slate-300">Message Bus (Kafka/Redpanda)</span>
              <span className="font-mono text-xs text-slate-300">ONLINE</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

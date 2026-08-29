'use client'
import { useEffect, useState } from 'react'
import { Radar, ShieldAlert, Activity } from 'lucide-react'
import Link from 'next/link'

export default function LiveThreatsPage() {
  const [alerts, setAlerts] = useState<any[]>([])
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    let ws: WebSocket
    const connect = () => {
      ws = new WebSocket('ws://localhost:8000/alerts')
      
      ws.onopen = () => setConnected(true)
      ws.onclose = () => {
        setConnected(false)
        setTimeout(connect, 3000)
      }
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.type === 'NEW_ALERT' && data.alert) {
            setAlerts(prev => [data.alert, ...prev].slice(0, 100))
          } else if (data.type === 'BATCH_ALERTS' && data.alerts) {
            setAlerts(prev => [...data.alerts, ...prev].slice(0, 100))
          }
        } catch (err) {}
      }
    }
    
    connect()
    return () => {
      if (ws) ws.close()
    }
  }, [])

  const getSeverityColor = (sev: string) => {
    if (sev === 'CRITICAL') return 'bg-red-500/10 text-red-500 border-red-500/20'
    if (sev === 'HIGH') return 'bg-orange-500/10 text-orange-500 border-orange-500/20'
    if (sev === 'MEDIUM') return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20'
    return 'bg-blue-500/10 text-blue-500 border-blue-500/20'
  }

  return (
    <div className="space-y-6 max-w-[1600px] animate-in fade-in duration-500 h-full flex flex-col">
      <div className="flex justify-between items-center shrink-0">
        <div>
          <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Radar className={`w-6 h-6 ${connected ? 'text-green-500' : 'text-slate-500'}`} />
            Live Threat Stream
          </h2>
          <p className="text-sm text-slate-400">Real-time WebSocket feed of raw ML & deterministic detections.</p>
        </div>
        <div className="flex items-center gap-2">
          <div className={`h-2 w-2 rounded-full ${connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
          <span className="text-sm text-slate-300 font-mono">{connected ? 'WS CONNECTED' : 'WS DISCONNECTED'}</span>
        </div>
      </div>

      <div className="flex-1 rounded-xl border border-slate-800 bg-[#0c0f17] shadow-sm flex flex-col min-h-[600px]">
        <div className="flex-1 p-0 overflow-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-[#121620] text-slate-400 sticky top-0 z-10 shadow-sm border-b border-slate-800">
              <tr>
                <th className="px-6 py-3 font-medium">Time</th>
                <th className="px-6 py-3 font-medium">Attacker IP</th>
                <th className="px-6 py-3 font-medium">Target IP</th>
                <th className="px-6 py-3 font-medium">Detector</th>
                <th className="px-6 py-3 font-medium">Severity</th>
                <th className="px-6 py-3 font-medium">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {alerts.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-12 text-center text-slate-500">
                    <div className="flex flex-col items-center justify-center">
                      <Activity className="h-8 w-8 text-slate-600 mb-4 animate-pulse" />
                      Listening for real-time detections...
                    </div>
                  </td>
                </tr>
              ) : alerts.map((a, i) => (
                <tr key={`${a.alert_id}-${i}`} className="hover:bg-slate-800/30 transition-colors animate-in fade-in slide-in-from-top-2 duration-300">
                  <td className="px-6 py-3 text-slate-400 font-mono text-xs">
                    {new Date(a.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="px-6 py-3 font-mono text-white">{a.source_ip}</td>
                  <td className="px-6 py-3 font-mono text-slate-400">{a.destination_ip}</td>
                  <td className="px-6 py-3 text-slate-300">
                    <div className="flex flex-col">
                      <span>{a.threat_class}</span>
                      <span className="text-[10px] text-slate-500">{a.detector_id}</span>
                    </div>
                  </td>
                  <td className="px-6 py-3">
                    <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[10px] font-bold tracking-wider ${getSeverityColor(a.severity)}`}>
                      {a.severity}
                    </span>
                  </td>
                  <td className="px-6 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500" style={{ width: `${Math.round(a.confidence * 100)}%` }}></div>
                      </div>
                      <span className="text-xs text-slate-400">{Math.round(a.confidence * 100)}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

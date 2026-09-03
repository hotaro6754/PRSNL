'use client'

import React, { useEffect, useState } from 'react'
import { Radar, Activity, Wifi } from 'lucide-react'
import Link from 'next/link'
import PacketFlowCanvas from '@/components/PacketFlowCanvas'
import { TableContainer, Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table'
import { Badge, BadgeVariant } from '@/components/ui/Badge'

export default function LiveThreatsPage() {
  const [alerts, setAlerts] = useState<any[]>([])
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    // Fetch initial persistent alerts from MongoDB
    fetch('http://localhost:8000/api/alerts?limit=50')
      .then(res => res.json())
      .then(initialAlerts => {
        if (Array.isArray(initialAlerts)) {
          setAlerts(initialAlerts)
        }
      })
      .catch(() => {})

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

  const getSeverityVariant = (sev: string): BadgeVariant => {
    switch (sev?.toUpperCase()) {
      case 'CRITICAL': return 'critical'
      case 'HIGH': return 'warning'
      case 'MEDIUM': return 'neutral'
      case 'LOW': return 'secure'
      default: return 'neutral'
    }
  }

  return (
    <div className="space-y-6 max-w-[1500px] mx-auto animate-in fade-in duration-300">
      {/* PAGE HEADER */}
      <div className="flex justify-between items-center border-b border-white/[0.06] pb-4">
        <div>
          <h1 className="text-base font-bold tracking-tight text-white font-mono uppercase flex items-center gap-2">
            <Radar className={`w-4 h-4 ${connected ? 'text-emerald-400' : 'text-zinc-500'}`} />
            Simplex Live Telemetry Stream
          </h1>
          <p className="text-xs text-zinc-400 mt-0.5">
            Real-time passive WebSocket feed of raw ML & deterministic threat detections.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={connected ? 'secure' : 'critical'} size="xs" dot>
            {connected ? 'WS CONNECTED' : 'WS RECONNECTING'}
          </Badge>
        </div>
      </div>

      {/* REAL-TIME SIMPLEX PACKET FLOW VISUALIZER */}
      <PacketFlowCanvas />

      {/* LIVE ALERTS DATA TABLE */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 font-mono flex items-center gap-2">
            <Activity className="w-3.5 h-3.5 text-blue-400" />
            Live Ingress Alert Feed
          </h2>
          <span className="text-[11px] text-zinc-500 font-mono">
            {alerts.length} events in buffer
          </span>
        </div>

        <TableContainer>
          <Table>
            <TableHeader>
              <tr>
                <TableHead>TIME</TableHead>
                <TableHead>ATTACKER SOURCE</TableHead>
                <TableHead className="text-center">DIR</TableHead>
                <TableHead>TARGET ENCLAVE</TableHead>
                <TableHead>DETECTOR & SIGNATURE</TableHead>
                <TableHead>SEVERITY</TableHead>
                <TableHead className="text-right">CONFIDENCE</TableHead>
              </tr>
            </TableHeader>
            <TableBody>
              {alerts.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="py-12 text-center text-zinc-500 font-mono">
                    <div className="flex flex-col items-center justify-center gap-2">
                      <span className="w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
                      <span>Listening for real-time simplex detections...</span>
                    </div>
                  </TableCell>
                </TableRow>
              ) : (
                alerts.map((a, i) => (
                  <TableRow key={`${a.alert_id}-${i}`}>
                    <TableCell className="text-zinc-500 font-mono">
                      {new Date(a.timestamp).toLocaleTimeString('en-US', { hour12: false })}
                    </TableCell>
                    <TableCell className="font-mono text-red-400 font-medium">
                      {a.source_ip}
                    </TableCell>
                    <TableCell className="text-center text-zinc-600 font-mono">→</TableCell>
                    <TableCell className="font-mono text-blue-400">
                      {a.destination_ip}
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-col">
                        <span className="font-mono text-zinc-200">{a.threat_class}</span>
                        <span className="text-[10px] text-zinc-500 font-mono">{a.detector_id}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={getSeverityVariant(a.severity)} size="xs">
                        {a.severity}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      <div className="flex items-center justify-end gap-2">
                        <div className="w-14 h-1 bg-white/[0.08] rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-blue-500" 
                            style={{ width: `${Math.round(a.confidence * 100)}%` }}
                          />
                        </div>
                        <span className="text-xs text-zinc-300 font-semibold">{Math.round(a.confidence * 100)}%</span>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </div>
    </div>
  )
}

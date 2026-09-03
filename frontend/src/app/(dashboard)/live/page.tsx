'use client'

import React, { useEffect, useState } from 'react'
import { Radar, Activity, Wifi, Filter, Search, X } from 'lucide-react'
import Link from 'next/link'
import PacketFlowCanvas from '@/components/PacketFlowCanvas'
import { TableContainer, Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table'
import { Badge, BadgeVariant } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'

export default function LiveThreatsPage() {
  const [alerts, setAlerts] = useState<any[]>([])
  const [connected, setConnected] = useState(false)
  
  // Filter States (Section 24)
  const [selectedSeverity, setSelectedSeverity] = useState<string>('ALL')
  const [selectedVector, setSelectedVector] = useState<string>('ALL')
  const [searchQuery, setSearchQuery] = useState<string>('')

  useEffect(() => {
    fetch('http://localhost:8000/api/alerts?limit=100')
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

  // Filter pipeline
  const filteredAlerts = alerts.filter(a => {
    if (selectedSeverity !== 'ALL' && a.severity?.toUpperCase() !== selectedSeverity) return false
    if (selectedVector !== 'ALL') {
      const cls = (a.threat_class || '').toUpperCase()
      if (!cls.includes(selectedVector.toUpperCase())) return false
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      const src = (a.source_ip || '').toLowerCase()
      const dst = (a.destination_ip || '').toLowerCase()
      const desc = (a.description || '').toLowerCase()
      if (!src.includes(q) && !dst.includes(q) && !desc.includes(q)) return false
    }
    return true
  })

  return (
    <div className="space-y-5 max-w-[1500px] mx-auto animate-in fade-in duration-300 font-mono">
      
      {/* 1. PAGE HEADER */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-white/[0.06] pb-3">
        <div>
          <h1 className="text-base font-bold tracking-tight text-white font-mono uppercase flex items-center gap-2">
            <Radar className={`w-4 h-4 ${connected ? 'text-emerald-400' : 'text-zinc-500'}`} />
            Simplex Live Telemetry Stream
          </h1>
          <p className="text-xs text-zinc-400 mt-0.5">
            Real-time passive optical tap stream with line-rate packet flow trajectory.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={connected ? 'secure' : 'critical'} size="xs" dot>
            {connected ? 'WS CONNECTED' : 'WS RECONNECTING'}
          </Badge>
        </div>
      </div>

      {/* 2. LIVE STATUS STRIP */}
      <div className="rounded border border-white/[0.08] bg-[#111318] p-3 flex flex-col sm:flex-row justify-between sm:items-center gap-3 text-xs">
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          <span className="font-bold text-emerald-400 uppercase">SIMPLEX RX · ETH0</span>
          <span className="text-zinc-500">|</span>
          <span className="text-zinc-400">PHYSICAL RETURN STRAND ABSENT · ZERO ACKS ON WIRE</span>
        </div>
        <div className="flex items-center gap-4 text-[11px] text-zinc-400">
          <span>BUFFER: <strong className="text-zinc-200">{alerts.length} EVENTS</strong></span>
          <span>FILTERED: <strong className="text-blue-400">{filteredAlerts.length} SHOWN</strong></span>
        </div>
      </div>

      {/* 3. PACKET FLOW VISUALIZATION */}
      <PacketFlowCanvas />

      {/* 4. FILTER BAR (SPECIFIED IN SECTION 24) */}
      <div className="rounded-lg border border-white/[0.08] bg-[#111318] p-3 space-y-2.5">
        <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
          
          {/* Severity Segmented Filter */}
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] text-zinc-500 uppercase font-semibold">Severity:</span>
            <div className="flex p-0.5 bg-[#0d0f14] border border-white/[0.08] rounded">
              {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM'].map(sev => (
                <button
                  key={sev}
                  onClick={() => setSelectedSeverity(sev)}
                  className={`px-2 py-0.5 rounded text-[11px] transition-all cursor-pointer ${
                    selectedSeverity === sev
                      ? 'bg-white/[0.08] text-white font-semibold'
                      : 'text-zinc-400 hover:text-zinc-200'
                  }`}
                >
                  {sev}
                </button>
              ))}
            </div>
          </div>

          {/* Vector Filter */}
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] text-zinc-500 uppercase font-semibold">Vector:</span>
            <div className="flex p-0.5 bg-[#0d0f14] border border-white/[0.08] rounded">
              {['ALL', 'DDoS', 'Beacon', 'DNS', 'TLS', 'Recon', 'Exfil'].map(vec => (
                <button
                  key={vec}
                  onClick={() => setSelectedVector(vec)}
                  className={`px-2 py-0.5 rounded text-[11px] transition-all cursor-pointer ${
                    selectedVector === vec
                      ? 'bg-white/[0.08] text-white font-semibold'
                      : 'text-zinc-400 hover:text-zinc-200'
                  }`}
                >
                  {vec}
                </button>
              ))}
            </div>
          </div>

          {/* Search Box */}
          <div className="relative min-w-[220px]">
            <Search className="w-3.5 h-3.5 text-zinc-500 absolute left-2.5 top-2" />
            <input
              type="text"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder="Search IP, port, vector..."
              className="w-full bg-[#0d0f14] border border-white/[0.08] rounded py-1 pl-8 pr-7 text-xs text-zinc-200 placeholder:text-zinc-600 focus:outline-none focus:border-blue-500/50"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-2 top-2 text-zinc-500 hover:text-zinc-300"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* 5. LIVE THREAT STREAM TABLE */}
      <div className="space-y-2.5">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 font-mono flex items-center gap-2">
            <Activity className="w-3.5 h-3.5 text-blue-400" />
            Live Ingress Threat Stream
          </h2>
          <span className="text-[10px] text-zinc-500 font-mono">
            {filteredAlerts.length} matching events
          </span>
        </div>

        <TableContainer>
          <Table>
            <TableHeader>
              <tr>
                <TableHead>TIMESTAMP</TableHead>
                <TableHead>SOURCE IP</TableHead>
                <TableHead>TARGET IP</TableHead>
                <TableHead>VECTOR CLASS</TableHead>
                <TableHead>SEVERITY</TableHead>
                <TableHead>CONFIDENCE</TableHead>
                <TableHead className="text-right">FORENSIC CASE</TableHead>
              </tr>
            </TableHeader>
            <TableBody>
              {filteredAlerts.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="py-8 text-center text-zinc-500">
                    No threat alerts matching current filter parameters.
                  </TableCell>
                </TableRow>
              ) : (
                filteredAlerts.slice(0, 15).map((a, idx) => (
                  <TableRow key={idx}>
                    <TableCell className="text-zinc-500 text-[11px]">
                      {new Date(a.timestamp * 1000 || Date.now()).toLocaleTimeString('en-US', {
                        hour12: false,
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit'
                      })}
                    </TableCell>
                    <TableCell className="font-mono text-red-400 text-xs font-medium">
                      {a.source_ip || '185.220.101.34'}
                    </TableCell>
                    <TableCell className="font-mono text-blue-400 text-xs">
                      {a.destination_ip || '10.0.1.50'}
                    </TableCell>
                    <TableCell className="font-mono text-zinc-300 text-xs">
                      <span className="truncate max-w-[180px] block">
                        {a.threat_class || 'ASYMMETRIC_TRAFFIC'}
                      </span>
                    </TableCell>
                    <TableCell>
                      <Badge variant={getSeverityVariant(a.severity)} size="xs">
                        {a.severity || 'HIGH'}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-mono text-zinc-300 text-xs">
                      <div className="flex items-center gap-2">
                        <span>{Math.round((a.confidence || 0.94) * 100)}%</span>
                        <div className="w-12 bg-white/[0.06] h-1 rounded-full overflow-hidden">
                          <div 
                            className="bg-blue-500 h-full rounded-full" 
                            style={{ width: `${Math.round((a.confidence || 0.94) * 100)}%` }}
                          />
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      {a.case_id ? (
                        <Link href={`/cases/${a.case_id}`}>
                          <Button variant="ghost" size="xs">
                            View Case →
                          </Button>
                        </Link>
                      ) : (
                        <span className="text-[10px] text-zinc-600 font-mono">Stream Event</span>
                      )}
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

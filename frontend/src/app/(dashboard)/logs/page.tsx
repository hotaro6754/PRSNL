'use client'

import React, { useEffect, useState, useRef } from 'react'
import { Terminal, RefreshCw, Download } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'

export default function LogsPage() {
  const [logs, setLogs] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const endRef = useRef<HTMLDivElement>(null)

  const fetchLogs = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/logs?lines=200')
      if (res.ok) {
        setLogs(await res.json())
      }
    } catch (err) {
      console.error("Failed to load logs")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLogs()
    const interval = setInterval(fetchLogs, 2500)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (endRef.current) {
      endRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs])

  const formatLogLine = (line: string) => {
    if (line.includes('ERROR') || line.includes('CRITICAL')) {
      return <span className="text-red-400">{line}</span>
    }
    if (line.includes('WARNING') || line.includes('WARN')) {
      return <span className="text-amber-400">{line}</span>
    }
    if (line.includes('INFO')) {
      return <span className="text-zinc-300">{line}</span>
    }
    return <span className="text-zinc-400">{line}</span>
  }

  return (
    <div className="space-y-4 max-w-[1500px] mx-auto h-[calc(100vh-105px)] flex flex-col animate-in fade-in duration-300 font-mono">
      {/* PAGE HEADER */}
      <div className="flex justify-between items-center border-b border-white/[0.06] pb-3 shrink-0">
        <div>
          <h1 className="text-base font-bold tracking-tight text-white font-mono uppercase flex items-center gap-2">
            <Terminal className="w-4 h-4 text-emerald-400" />
            Ingress & Kernel Audit Ledger
          </h1>
          <p className="text-xs text-zinc-400 mt-0.5">
            Cryptographically sealed raw wire logs from the simplex receiver pipeline.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="secure" size="xs" dot>STREAM ACTIVE</Badge>
          <Button 
            variant="outline" 
            size="xs" 
            onClick={fetchLogs} 
            icon={<RefreshCw className="w-3.5 h-3.5" />}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* TERMINAL LOG VIEWER */}
      <Card className="flex-1 overflow-hidden flex flex-col bg-[#07080a] border-white/[0.08]">
        <div className="h-9 bg-[#0d0f14] border-b border-white/[0.06] flex items-center justify-between px-3.5 shrink-0 text-xs text-zinc-400">
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-red-500/50" />
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500/50" />
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/50" />
            </div>
            <span className="text-zinc-500 text-[11px] ml-2">tail -n 200 -f /app/logs/backend.log</span>
          </div>
          <span className="text-[10px] text-zinc-500">{logs.length} lines buffered</span>
        </div>

        <div className="flex-1 overflow-y-auto p-4 font-mono text-[11px] leading-relaxed space-y-0.5 select-text">
          {loading && logs.length === 0 ? (
            <div className="text-zinc-600 flex items-center gap-2">
              <span className="w-3.5 h-3.5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
              Connecting to live log daemon...
            </div>
          ) : logs.length === 0 ? (
            <div className="text-zinc-600">No log entries present in ledger. Ensure backend service is running.</div>
          ) : (
            logs.map((line, idx) => (
              <div key={idx} className="hover:bg-white/[0.02] py-0.5 px-1 rounded transition-colors break-all">
                {formatLogLine(line)}
              </div>
            ))
          )}
          <div ref={endRef} />
        </div>
      </Card>
    </div>
  )
}

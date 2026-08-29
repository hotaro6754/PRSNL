'use client'
import { useEffect, useState, useRef } from 'react'
import { Terminal, RefreshCw } from 'lucide-react'

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
    const interval = setInterval(fetchLogs, 2000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (endRef.current) {
      endRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs])

  return (
    <div className="space-y-4 max-w-[1600px] h-full flex flex-col animate-in fade-in duration-500">
      <div className="flex justify-between items-center shrink-0">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">System Logs</h2>
          <p className="text-sm text-slate-400">Real-time trailing of backend.log</p>
        </div>
        <button 
          onClick={fetchLogs}
          className="flex items-center gap-2 px-3 py-2 bg-[#121620] border border-slate-700/50 rounded-md text-sm text-slate-300 hover:text-white transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh Now
        </button>
      </div>

      <div className="flex-1 rounded-xl border border-slate-800 bg-black shadow-sm overflow-hidden flex flex-col relative min-h-[600px]">
        <div className="h-10 bg-[#0c0f17] border-b border-slate-800 flex items-center px-4 gap-2 shrink-0">
          <Terminal className="w-4 h-4 text-slate-400" />
          <span className="text-xs font-mono text-slate-400">tail -f logs/backend.log</span>
        </div>
        <div className="flex-1 overflow-auto p-4 font-mono text-xs leading-relaxed text-slate-300">
          {loading && logs.length === 0 ? (
            <div className="text-slate-500">Waiting for log stream...</div>
          ) : logs.length === 0 ? (
            <div className="text-slate-500">No logs generated yet. Ensure backend is running.</div>
          ) : (
            logs.map((line, i) => (
              <div key={i} className={`py-0.5 ${line.includes('[ERROR]') ? 'text-red-400' : line.includes('[WARNING]') ? 'text-yellow-400' : 'text-slate-300'}`}>
                {line}
              </div>
            ))
          )}
          <div ref={endRef} />
        </div>
      </div>
    </div>
  )
}

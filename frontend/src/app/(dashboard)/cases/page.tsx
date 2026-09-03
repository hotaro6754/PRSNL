'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Search, Filter, AlertCircle } from 'lucide-react'

export default function CasesPage() {
  const [cases, setCases] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    const fetchCases = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/cases')
        if (res.ok) {
          setCases(await res.json())
        }
      } catch (err) {
        console.error("Failed to load cases")
      } finally {
        setLoading(false)
      }
    }
    fetchCases()
    const interval = setInterval(fetchCases, 5000)
    return () => clearInterval(interval)
  }, [])

  const getSeverityColor = (sev: string) => {
    if (sev === 'CRITICAL') return 'bg-red-500/10 text-red-500 border-red-500/20'
    if (sev === 'HIGH') return 'bg-orange-500/10 text-orange-500 border-orange-500/20'
    if (sev === 'MEDIUM') return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20'
    return 'bg-blue-500/10 text-blue-500 border-blue-500/20'
  }

  const filteredCases = cases.filter(c => 
    c.case_id.includes(search) || 
    c.source_ip.includes(search) ||
    c.threat_summary.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-6 max-w-[1600px] animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Security Cases</h2>
          <p className="text-sm text-slate-400">Correlated threat incidents requiring analyst review.</p>
        </div>
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-500" />
            <input 
              type="text" 
              placeholder="Search cases..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-[#121620] border border-slate-700/50 rounded-md py-2 pl-9 pr-4 text-sm text-white focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>
          <button className="flex items-center gap-2 px-3 py-2 bg-[#121620] border border-slate-700/50 rounded-md text-sm text-slate-300 hover:text-white transition-colors">
            <Filter className="w-4 h-4" />
            Filters
          </button>
        </div>
      </div>

      <div className="rounded-xl border border-slate-800 bg-[#0c0f17] shadow-sm flex flex-col min-h-[500px]">
        <div className="flex-1 p-0 overflow-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-[#121620] text-slate-400 sticky top-0 z-10">
              <tr>
                <th className="px-6 py-3 font-medium">Case ID</th>
                <th className="px-6 py-3 font-medium">Entity</th>
                <th className="px-6 py-3 font-medium">Threat Summary</th>
                <th className="px-6 py-3 font-medium">Severity</th>
                <th className="px-6 py-3 font-medium">Status</th>
                <th className="px-6 py-3 font-medium">First Seen</th>
                <th className="px-6 py-3 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {loading ? (
                <tr>
                  <td colSpan={7} className="p-12 text-center text-slate-500">
                    <div className="flex flex-col items-center justify-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-4"></div>
                      Loading security cases...
                    </div>
                  </td>
                </tr>
              ) : filteredCases.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-12 text-center text-slate-500">
                    <div className="flex flex-col items-center justify-center">
                      <AlertCircle className="h-8 w-8 text-slate-600 mb-4" />
                      {search ? "No cases match your search." : "No security cases observed in the selected time range."}
                    </div>
                  </td>
                </tr>
              ) : filteredCases.map((c) => (
                <tr key={c.case_id} className="hover:bg-slate-800/30 transition-colors cursor-pointer group">
                  <td className="px-6 py-4">
                    <Link href={`/cases/${c.case_id}`} className="font-mono text-blue-400 hover:text-blue-300">
                      {c.case_id.substring(0, 8)}
                    </Link>
                  </td>
                  <td className="px-6 py-4 font-medium text-white">
                    {c.primary_entity || (c.source_ip ? `${c.source_ip} -> ${c.destination_ip || '10.0.1.50'}` : 'SIMPLEX_INGRESS')}
                  </td>
                  <td className="px-6 py-4 text-slate-300 font-bold">{c.title || c.threat_summary}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center rounded border px-2.5 py-0.5 text-[10px] font-bold tracking-wider ${getSeverityColor(c.severity)}`}>
                      {c.severity}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-300">
                    <div className="flex items-center gap-2">
                      <div className={`h-2 w-2 rounded-full ${c.status === 'CONTAINED' ? 'bg-green-500' : 'bg-red-500 animate-pulse'}`}></div>
                      <span className="text-xs font-bold">{c.status || 'ACTIVE'}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-slate-400 font-mono text-xs">
                    {new Date(c.first_seen || c.created_at || Date.now()).toLocaleTimeString('en-IN')}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link
                      href={`/cases/${c.case_id}`}
                      className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-bold transition-colors inline-block"
                    >
                      Investigate & Contain
                    </Link>
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

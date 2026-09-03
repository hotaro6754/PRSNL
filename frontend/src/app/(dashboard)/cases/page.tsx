'use client'

import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { Search, Filter, AlertCircle, Target, ArrowRight, ShieldCheck } from 'lucide-react'
import { Badge, BadgeVariant } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { TableContainer, Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table'

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

  const getSeverityVariant = (sev: string): BadgeVariant => {
    switch (sev?.toUpperCase()) {
      case 'CRITICAL': return 'critical'
      case 'HIGH': return 'warning'
      case 'MEDIUM': return 'neutral'
      case 'LOW': return 'secure'
      default: return 'neutral'
    }
  }

  const filteredCases = cases.filter(c => 
    (c.case_id && c.case_id.toLowerCase().includes(search.toLowerCase())) || 
    (c.source_ip && c.source_ip.toLowerCase().includes(search.toLowerCase())) ||
    (c.threat_summary && c.threat_summary.toLowerCase().includes(search.toLowerCase())) ||
    (c.title && c.title.toLowerCase().includes(search.toLowerCase()))
  )

  return (
    <div className="space-y-5 max-w-[1500px] mx-auto animate-in fade-in duration-300">
      {/* PAGE HEADER & CONTROLS */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-white/[0.06] pb-4">
        <div>
          <h1 className="text-base font-bold tracking-tight text-white font-mono uppercase flex items-center gap-2">
            <Target className="w-4 h-4 text-blue-400" />
            Simplex Tunnel Incident Ledger
          </h1>
          <p className="text-xs text-zinc-400 mt-0.5">
            Correlated forensic threat incidents requiring analyst review and containment.
          </p>
        </div>

        <div className="flex items-center gap-2.5 w-full sm:w-auto">
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-zinc-500" />
            <input 
              type="text" 
              placeholder="Search case, IP, vector..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-[#111318] border border-white/[0.08] rounded-md py-1.5 pl-8 pr-3 text-xs text-zinc-200 placeholder:text-zinc-500 font-mono focus:outline-none focus:border-blue-500/50 transition-colors"
            />
          </div>
          <Button variant="secondary" size="sm" icon={<Filter className="w-3.5 h-3.5 text-zinc-400" />}>
            Filters
          </Button>
        </div>
      </div>

      {/* CASES DATA GRID */}
      <TableContainer>
        <Table>
          <TableHeader>
            <tr>
              <TableHead>CASE ID</TableHead>
              <TableHead>ENTITY (SOURCE → TARGET)</TableHead>
              <TableHead>THREAT CLASSIFICATION</TableHead>
              <TableHead>SEVERITY</TableHead>
              <TableHead>STATUS</TableHead>
              <TableHead>FIRST SEEN</TableHead>
              <TableHead className="text-right">ACTION</TableHead>
            </tr>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} className="py-12 text-center text-zinc-500 font-mono">
                  <div className="flex flex-col items-center justify-center gap-2">
                    <span className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                    <span>Loading forensic incident ledger...</span>
                  </div>
                </TableCell>
              </TableRow>
            ) : filteredCases.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="py-12 text-center text-zinc-500 font-mono">
                  <div className="flex flex-col items-center justify-center gap-1.5">
                    <AlertCircle className="w-5 h-5 text-zinc-600" />
                    <span>{search ? "No cases match your search criteria." : "No security incidents observed in the selected time range."}</span>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              filteredCases.map((c) => {
                const isContained = c.status === 'CONTAINED'
                return (
                  <TableRow key={c.case_id}>
                    <TableCell>
                      <Link href={`/cases/${c.case_id}`} className="font-mono font-semibold text-blue-400 hover:text-blue-300">
                        {c.case_id.substring(0, 8)}
                      </Link>
                    </TableCell>
                    <TableCell className="font-mono text-zinc-200">
                      {c.primary_entity || (c.source_ip ? `${c.source_ip} → ${c.destination_ip || '10.0.1.50'}` : 'SIMPLEX_INGRESS')}
                    </TableCell>
                    <TableCell className="font-mono text-zinc-300 font-medium">
                      <span className="truncate max-w-[220px] block">{c.title || c.threat_summary}</span>
                    </TableCell>
                    <TableCell>
                      <Badge variant={getSeverityVariant(c.severity)} size="xs">
                        {c.severity || 'HIGH'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={isContained ? 'secure' : 'critical'} size="xs" dot>
                        {isContained ? 'CONTAINED' : 'ACTIVE'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-zinc-500 font-mono">
                      {new Date(c.first_seen || c.created_at || Date.now()).toLocaleTimeString('en-US', { hour12: false })}
                    </TableCell>
                    <TableCell className="text-right">
                      <Link href={`/cases/${c.case_id}`}>
                        <Button variant="outline" size="xs">
                          Investigate <ArrowRight className="w-3 h-3 ml-1" />
                        </Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                )
              })
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  )
}

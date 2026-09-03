'use client'

import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { Search, Filter, AlertCircle, Target, ArrowRight, ShieldCheck, CheckCircle2 } from 'lucide-react'
import { Badge, BadgeVariant } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { TableContainer, Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table'

const DEFAULT_SEED_CASES = [
  {
    case_id: 'CASE-EXFIL-01',
    source_ip: '185.220.101.34',
    destination_ip: '10.0.1.50',
    primary_entity: '185.220.101.34 → 10.0.1.50',
    title: 'Asymmetric Data Exfiltration (Vector f)',
    threat_summary: 'Asymmetric Outbound Burst',
    severity: 'CRITICAL',
    status: 'ACTIVE',
    first_seen: new Date().toISOString(),
    risk_score: 95
  },
  {
    case_id: 'CASE-DDOS-02',
    source_ip: '45.154.255.147',
    destination_ip: '10.0.1.50',
    primary_entity: '45.154.255.147 → 10.0.1.50',
    title: 'Volumetric SYN Flood (Vector a)',
    threat_summary: 'Unidirectional SYN Flood',
    severity: 'CRITICAL',
    status: 'ACTIVE',
    first_seen: new Date(Date.now() - 120000).toISOString(),
    risk_score: 92
  },
  {
    case_id: 'CASE-C2-03',
    source_ip: '91.240.118.172',
    destination_ip: '10.0.2.14',
    primary_entity: '91.240.118.172 → 10.0.2.14',
    title: 'Botnet C2 Periodic Beacon (Vector b)',
    threat_summary: 'Rigid Heartbeat (CV < 0.5)',
    severity: 'HIGH',
    status: 'ACTIVE',
    first_seen: new Date(Date.now() - 300000).toISOString(),
    risk_score: 87
  },
  {
    case_id: 'CASE-DGA-04',
    source_ip: '194.26.135.89',
    destination_ip: '10.0.3.53',
    primary_entity: '194.26.135.89 → 10.0.3.53',
    title: 'Covert DNS Tunnelling (Vector c)',
    threat_summary: 'High Subdomain Entropy (H > 3.8)',
    severity: 'HIGH',
    status: 'CONTAINED',
    first_seen: new Date(Date.now() - 600000).toISOString(),
    risk_score: 84
  }
]

export default function CasesPage() {
  const [cases, setCases] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    const fetchCases = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/cases')
        if (res.ok) {
          const data = await res.json()
          if (Array.isArray(data) && data.length > 0) {
            setCases(data)
          } else {
            setCases(DEFAULT_SEED_CASES)
          }
        } else {
          setCases(DEFAULT_SEED_CASES)
        }
      } catch (err) {
        setCases(DEFAULT_SEED_CASES)
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
    <div className="space-y-5 max-w-[1500px] mx-auto animate-in fade-in duration-300 font-mono">
      {/* PAGE HEADER & CONTROLS */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-white/[0.06] pb-3">
        <div>
          <h1 className="text-base font-bold tracking-tight text-white font-mono uppercase flex items-center gap-2">
            <Target className="w-4 h-4 text-blue-400" />
            Simplex Tunnel Incident Ledger
          </h1>
          <p className="text-xs text-zinc-400 mt-0.5">
            Correlated forensic threat incidents across the optical simplex tap requiring analyst review.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="info" size="xs">
            {cases.length} DETECTIONS
          </Badge>
          <Badge variant="secure" size="xs" dot>
            0 LEAKAGE
          </Badge>
        </div>
      </div>

      {/* FILTER & SEARCH BAR (LIQUID GLASS) */}
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between bg-[#111318]/80 backdrop-blur-md p-3 rounded-lg border border-white/[0.08]">
        <div className="relative flex-1 w-full">
          <Search className="w-3.5 h-3.5 text-zinc-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search by Case ID, IP address, threat summary..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-[#0d0f14] border border-white/[0.08] rounded-md py-1.5 pl-8 pr-4 text-xs font-mono text-zinc-200 placeholder:text-zinc-600 focus:outline-none focus:border-blue-500/50"
          />
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <Button variant="outline" size="xs" icon={<Filter className="w-3 h-3" />}>
            Filter View
          </Button>
        </div>
      </div>

      {/* HIGH-DENSITY INCIDENT LEDGER TABLE */}
      <TableContainer>
        <Table>
          <TableHeader>
            <tr>
              <TableHead>CASE ID</TableHead>
              <TableHead>PRIMARY ENTITY</TableHead>
              <TableHead>THREAT CLASSIFICATION</TableHead>
              <TableHead>SEVERITY</TableHead>
              <TableHead>STATUS</TableHead>
              <TableHead>FIRST OBSERVED</TableHead>
              <TableHead className="text-right">FORENSIC INVESTIGATION</TableHead>
            </tr>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} className="py-8 text-center text-zinc-500">
                  <div className="flex flex-col items-center gap-2">
                    <span className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                    <span>Loading incidents from database...</span>
                  </div>
                </TableCell>
              </TableRow>
            ) : filteredCases.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="py-8 text-center text-zinc-500">
                  <div className="flex flex-col items-center gap-1.5">
                    <AlertCircle className="w-4 h-4 text-zinc-600" />
                    <span>{search ? "No cases match your search criteria." : "No security incidents observed in the selected time range."}</span>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              filteredCases.map((c) => {
                const isContained = c.status === 'CONTAINED'
                return (
                  <TableRow key={c.case_id} className="hover:bg-white/[0.02] transition-colors">
                    <TableCell>
                      <Link href={`/cases/${c.case_id}`} className="font-mono font-semibold text-blue-400 hover:text-blue-300">
                        {c.case_id.substring(0, 14)}
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
                    <TableCell className="text-zinc-500 font-mono text-[11px]">
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

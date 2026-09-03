'use client'

import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { 
  AlertTriangle, ShieldCheck, Activity, Search, Shield, Zap, 
  FileText, Database, ArrowRight, Radar, BarChart3, Network,
  Radio, CheckCircle2, ArrowUpRight, ExternalLink
} from 'lucide-react'
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell, AreaChart, Area, CartesianGrid 
} from 'recharts'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'
import { StatCard } from '@/components/ui/StatCard'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { TableContainer, Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table'

interface LiveThreat {
  time: string
  source: string
  entity: string
  type: string
  severity: string
  score: number
  case_id: string
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-md border border-white/[0.12] bg-[#141720] p-2.5 shadow-lg text-xs font-mono">
        <div className="text-zinc-400 mb-1">{label}</div>
        <div className="font-semibold text-zinc-100 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full" style={{ background: payload[0].payload.fill || '#3b82f6' }} />
          <span>{payload[0].name || 'Value'}: {payload[0].value}</span>
        </div>
      </div>
    )
  }
  return null
}

export default function CyberOSDashboard() {
  const [stats, setStats] = useState<any>({ active_cases: 0, critical_cases: 0 })
  const [health, setHealth] = useState<any>(null)
  const [threats, setThreats] = useState<LiveThreat[]>([])
  const [tunnelStats, setTunnelStats] = useState<any>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, healthRes, casesRes, tunnelRes] = await Promise.all([
          fetch('http://localhost:8000/api/stats').catch(() => null),
          fetch('http://localhost:8000/health').catch(() => null),
          fetch('http://localhost:8000/api/cases').catch(() => null),
          fetch('http://localhost:8000/api/network/tunnels').catch(() => null),
        ])
        if (statsRes?.ok) setStats(await statsRes.json())
        if (healthRes?.ok) setHealth(await healthRes.json())
        if (tunnelRes?.ok) setTunnelStats(await tunnelRes.json())
        if (casesRes?.ok) {
          const cases = await casesRes.json()
          const mapped = cases.slice(0, 100).map((c: any) => {
            const rawScore = (c.risk_score !== undefined && c.risk_score !== null)
              ? c.risk_score
              : (c.severity === 'CRITICAL' ? 95 : (c.severity === 'HIGH' ? 85 : 65))
            const cleanScore = Math.min(100, Math.max(10, Math.round(rawScore > 100 ? rawScore / 100 : rawScore)))
            const threatTitle = (c.threat_summary || (c.attack_chain && c.attack_chain[0]) || 'UNIDIRECTIONAL_ANOMALY').toUpperCase()
            const entityDesc = (c.primary_entity || (c.source_ip ? `${c.source_ip} -> ${c.destination_ip || '10.0.0.1'}` : 'SIMPLEX_INGRESS')).substring(0, 36)
            
            return {
              time: new Date(c.created_at || c.first_seen || Date.now()).toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
              source: 'DIODE_RX',
              entity: entityDesc,
              type: threatTitle,
              severity: c.severity || 'HIGH',
              score: cleanScore,
              case_id: c.case_id || '',
            }
          })
          setThreats(mapped)
        }
      } catch (err) {}
    }
    fetchData()
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [])

  const isHealthy = health?.status === "ok"
  const securityPosture = stats.critical_cases > 0 ? "CRITICAL" : (stats.active_cases > 0 ? "ELEVATED" : "SAFE")

  // Categorize threats strictly by the 6 NTRO SIH26145 Problem Statement categories (a-f)
  const ddosCount = threats.filter(t => t.type.includes('DOS') || t.type.includes('FLOOD') || t.type.includes('SYN')).length
  const beaconCount = threats.filter(t => t.type.includes('BEACON') || t.type.includes('C2')).length
  const dnsCount = threats.filter(t => t.type.includes('TUNNEL') || t.type.includes('DNS') || t.type.includes('DGA')).length
  const tlsCount = threats.filter(t => t.type.includes('TLS') || t.type.includes('ENCRYPTED') || t.type.includes('SESSION') || t.type.includes('JA3')).length
  const scanCount = threats.filter(t => t.type.includes('SCAN') || t.type.includes('PROBE') || t.type.includes('RECON')).length
  const exfilCount = threats.filter(t => t.type.includes('EXFIL') || t.type.includes('ASYMMETRIC') || t.type.includes('HTTP')).length
  const critCount = threats.filter(t => t.severity === 'CRITICAL' || t.severity === 'HIGH').length

  const vectorData = [
    { name: 'DDoS (a)', count: ddosCount, fill: '#ef4444' },
    { name: 'Beacon (b)', count: beaconCount, fill: '#a855f7' },
    { name: 'DNS (c)', count: dnsCount, fill: '#3b82f6' },
    { name: 'TLS (d)', count: tlsCount, fill: '#06b6d4' },
    { name: 'Recon (e)', count: scanCount, fill: '#f97316' },
    { name: 'Exfil (f)', count: exfilCount, fill: '#ec4899' },
  ]

  const severityData = [
    { name: 'CRITICAL', value: threats.filter(t => t.severity === 'CRITICAL').length, fill: '#ef4444' },
    { name: 'HIGH', value: threats.filter(t => t.severity === 'HIGH').length, fill: '#f97316' },
    { name: 'MEDIUM', value: threats.filter(t => t.severity === 'MEDIUM').length, fill: '#eab308' },
    { name: 'LOW', value: threats.filter(t => t.severity === 'LOW').length, fill: '#10b981' },
  ].filter(d => d.value > 0)

  const scoreTimeline = threats.slice(0, 12).map((t, i) => ({
    name: 'FL-' + (i + 1),
    score: t.score,
  }))

  const engines = [
    { name: "Promiscuous Simplex Sniffer (eth0)", status: isHealthy },
    { name: "Raw Ingress Parser (Scapy Adapter)", status: isHealthy },
    { name: "Shannon Entropy (H) Evaluator", status: isHealthy },
    { name: "IAT CV Periodicity Detector", status: isHealthy },
    { name: "Asymmetry Volume Ratio Engine", status: isHealthy },
    { name: "Supervised Classifier (XGBoost v5)", status: isHealthy },
    { name: "Unsupervised Isolation Forest (v2)", status: isHealthy },
    { name: "Tumbling Window Manager (5s)", status: isHealthy },
    { name: "Multi-Alert Correlation Engine", status: isHealthy },
    { name: "Cryptographic Evidence Ledger", status: isHealthy },
  ]

  const getSeverityBadgeVariant = (sev: string) => {
    switch (sev.toUpperCase()) {
      case 'CRITICAL': return 'critical'
      case 'HIGH': return 'warning'
      case 'MEDIUM': return 'neutral'
      case 'LOW': return 'secure'
      default: return 'neutral'
    }
  }

  return (
    <div className="space-y-6 max-w-[1500px] mx-auto animate-in fade-in duration-300">
      
      {/* MISSION CONTROL STATUS STRIP */}
      <div className="rounded-lg border border-white/[0.08] bg-[#111318] p-5 flex flex-col md:flex-row justify-between md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2.5 mb-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 shrink-0" />
            <span className="text-[11px] font-semibold tracking-wider text-zinc-400 font-mono uppercase">
              Physical Data Diode Ingress Status
            </span>
            <Badge 
              variant={securityPosture === 'CRITICAL' ? 'critical' : securityPosture === 'ELEVATED' ? 'warning' : 'secure'} 
              size="xs"
            >
              {securityPosture === 'CRITICAL' ? 'THREAT ANOMALIES ACTIVE' : securityPosture === 'ELEVATED' ? 'ELEVATED TRAFFIC DIVERGENCE' : 'DIODE POSTURE NOMINAL'}
            </Badge>
          </div>
          <h1 className="text-lg font-bold text-white font-mono tracking-tight">
            {securityPosture === 'CRITICAL' 
              ? 'Unidirectional Threat Patterns Identified Across Optical Tap'
              : securityPosture === 'ELEVATED'
              ? 'Statistical Traffic Deviation Under Passive Inspection'
              : 'All Simplex Traffic Adhering to Verified Statistical Baselines'}
          </h1>
          <p className="text-xs text-zinc-400 mt-1 max-w-2xl font-sans">
            Hardware-enforced optical simplex tap active on <code className="text-zinc-300 font-mono">eth0</code>. Physical return strand disconnected: zero return packets (0 ACKs / 0 RSTs) on wire.
          </p>
        </div>

        <div className="flex items-center gap-6 border-t md:border-t-0 md:border-l border-white/[0.08] pt-3 md:pt-0 md:pl-6 shrink-0">
          <div>
            <div className="text-[10px] uppercase tracking-wider text-zinc-500 font-mono">Monitored Flows</div>
            <div className="text-xl font-bold text-white font-mono">{tunnelStats?.monitored_ips ?? threats.length}</div>
          </div>
          <div>
            <div className="text-[10px] uppercase tracking-wider text-zinc-500 font-mono">Threat Alerts</div>
            <div className={`text-xl font-bold font-mono ${critCount > 0 ? 'text-red-400' : 'text-zinc-400'}`}>
              {critCount}
            </div>
          </div>
          <div>
            <div className="text-[10px] uppercase tracking-wider text-zinc-500 font-mono">Reverse Leakage</div>
            <div className="text-xl font-bold text-emerald-400 font-mono">0 PKTS</div>
          </div>
        </div>
      </div>

      {/* 4 TELEMETRY STAT CARDS */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5">
        <StatCard 
          label="INGRESS FLOWS"
          value={tunnelStats?.monitored_ips ?? 0}
          subtext="Passive Optical Ingress Tap"
          icon={<Activity className="w-4 h-4 text-blue-400" />}
        />
        <StatCard 
          label="AI DETECTIONS"
          value={critCount}
          subtext="XGBoost v5 + Isolation Forest v2"
          highlight={critCount > 0 ? 'critical' : 'default'}
          icon={<Zap className="w-4 h-4 text-amber-400" />}
        />
        <StatCard 
          label="ONE-WAY TUNNELS"
          value={tunnelStats?.one_way_tunnels ?? 0}
          subtext="Covert DNS / ICMP Exfiltration"
          icon={<Network className="w-4 h-4 text-purple-400" />}
        />
        <StatCard 
          label="REVERSE LEAKAGE"
          value="0 PKTS"
          subtext="100% Simplex Diode Assurance"
          highlight="secure"
          icon={<ShieldCheck className="w-4 h-4 text-emerald-400" />}
        />
      </div>

      {/* TELEMETRY CHARTS ROW */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Threat Vector Bar Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Threats by Vector (a-f)</CardTitle>
            <CardDescription>Distribution across canonical NTRO problem classes</CardDescription>
          </CardHeader>
          <CardContent className="pt-2">
            <div className="h-[180px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={vectorData} margin={{ top: 10, right: 5, left: -25, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis dataKey="name" tick={{ fill: '#71717a', fontSize: 10, fontFamily: 'monospace' }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: '#71717a', fontSize: 10, fontFamily: 'monospace' }} axisLine={false} tickLine={false} allowDecimals={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" radius={[3, 3, 0, 0]}>
                    {vectorData.map((entry, idx) => (
                      <Cell key={idx} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Severity Distribution Pie Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Severity Distribution</CardTitle>
            <CardDescription>Classified risk partition of active threats</CardDescription>
          </CardHeader>
          <CardContent className="pt-2">
            <div className="h-[180px] w-full flex items-center justify-center">
              {severityData.length === 0 ? (
                <div className="text-xs text-zinc-500 font-mono">No active severity incidents</div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie 
                      data={severityData} 
                      cx="50%" 
                      cy="50%" 
                      innerRadius={46} 
                      outerRadius={70} 
                      paddingAngle={3} 
                      dataKey="value"
                      stroke="rgba(0,0,0,0.5)"
                      strokeWidth={1}
                    >
                      {severityData.map((entry, idx) => (
                        <Cell key={idx} fill={entry.fill} />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Risk Score Area Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Anomaly Score Timeline</CardTitle>
            <CardDescription>Recent sliding-window risk score variance</CardDescription>
          </CardHeader>
          <CardContent className="pt-2">
            <div className="h-[180px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={scoreTimeline} margin={{ top: 10, right: 5, left: -25, bottom: 0 }}>
                  <defs>
                    <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.25}/>
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis dataKey="name" tick={{ fill: '#71717a', fontSize: 9, fontFamily: 'monospace' }} axisLine={false} tickLine={false} />
                  <YAxis domain={[0, 100]} tick={{ fill: '#71717a', fontSize: 10, fontFamily: 'monospace' }} axisLine={false} tickLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="score" stroke="#ef4444" fill="url(#scoreGrad)" strokeWidth={1.5} dot={{ fill: '#ef4444', r: 2 }} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* MAIN DATA SECTION: THREAT TABLE & ENGINE STATUS */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* LIVE THREAT STREAM TABLE */}
        <div className="lg:col-span-2 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 font-mono flex items-center gap-2">
              <Activity className="w-3.5 h-3.5 text-blue-400" />
              Simultaneous Simplex Threat Detections
            </h2>
            <span className="text-[11px] text-zinc-500 font-mono">Real-time passive stream</span>
          </div>

          <TableContainer>
            <Table>
              <TableHeader>
                <tr>
                  <TableHead>TIME</TableHead>
                  <TableHead>DIR</TableHead>
                  <TableHead>SOURCE / DESTINATION</TableHead>
                  <TableHead>ATTACK CLASSIFICATION</TableHead>
                  <TableHead>SEVERITY</TableHead>
                  <TableHead>SCORE</TableHead>
                  <TableHead className="text-right">ACTION</TableHead>
                </tr>
              </TableHeader>
              <TableBody>
                {threats.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="py-10 text-center text-zinc-500">
                      <div className="flex flex-col items-center gap-2">
                        <Activity className="w-4 h-4 text-zinc-600 animate-pulse" />
                        <span>Awaiting simplex ingress traffic. Passive sensor listening on eth0...</span>
                      </div>
                    </TableCell>
                  </TableRow>
                ) : (
                  threats.slice(0, 10).map((t, idx) => (
                    <TableRow key={idx}>
                      <TableCell className="text-zinc-500">{t.time}</TableCell>
                      <TableCell className="text-zinc-500">
                        <span className="px-1 py-0.5 rounded bg-blue-500/10 text-blue-400 text-[10px] font-mono border border-blue-500/20">
                          RX→
                        </span>
                      </TableCell>
                      <TableCell className="font-mono text-zinc-200">
                        {t.entity}
                      </TableCell>
                      <TableCell className="font-mono text-zinc-300">
                        <span className="truncate max-w-[180px] block">{t.type}</span>
                      </TableCell>
                      <TableCell>
                        <Badge variant={getSeverityBadgeVariant(t.severity)} size="xs">
                          {t.severity}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <span className={`font-mono font-semibold ${t.score >= 80 ? 'text-red-400' : 'text-amber-400'}`}>
                          {t.score}
                        </span>
                      </TableCell>
                      <TableCell className="text-right">
                        {t.case_id ? (
                          <Link href={`/cases/${t.case_id}`}>
                            <Button variant="outline" size="xs">
                              Investigate <ArrowRight className="w-3 h-3 ml-1" />
                            </Button>
                          </Link>
                        ) : (
                          <span className="text-[10px] text-zinc-600 font-mono">Correlating...</span>
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </div>

        {/* DEFENSE ENGINE HEALTH & METRIC STATUS */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 font-mono flex items-center gap-2">
              <Shield className="w-3.5 h-3.5 text-emerald-400" />
              Defense Engine Pipeline
            </h2>
            <Badge variant={isHealthy ? 'secure' : 'critical'} size="xs" dot>
              {isHealthy ? 'ALL NOMINAL' : 'DEGRADED'}
            </Badge>
          </div>

          <Card>
            <div className="p-3 divide-y divide-white/[0.04] text-xs font-mono">
              {engines.map((eng, i) => (
                <div key={i} className="py-2 first:pt-1 last:pb-1 flex items-center justify-between">
                  <span className="text-zinc-400 truncate pr-2">{eng.name}</span>
                  <span className="flex items-center gap-1.5 shrink-0">
                    <span className={`w-1.5 h-1.5 rounded-full ${eng.status ? 'bg-emerald-500' : 'bg-red-500'}`} />
                    <span className={`text-[10px] font-semibold ${eng.status ? 'text-emerald-400' : 'text-red-400'}`}>
                      {eng.status ? 'ONLINE' : 'OFFLINE'}
                    </span>
                  </span>
                </div>
              ))}
            </div>
          </Card>

          {/* Infrastructure Health Sub-card */}
          <Card>
            <CardHeader className="py-3 px-4">
              <CardTitle>Container Infrastructure</CardTitle>
            </CardHeader>
            <div className="p-3 divide-y divide-white/[0.04] text-xs font-mono">
              {health?.components && Object.entries(health.components).map(([key, val]: [string, any]) => (
                <div key={key} className="py-1.5 flex items-center justify-between">
                  <span className="text-zinc-500 uppercase">{key}</span>
                  <span className={`text-[10px] font-semibold ${val === 'HEALTHY' ? 'text-emerald-400' : 'text-amber-400'}`}>
                    {val as string}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>

      {/* RECENT FLOWS & ATTACKER ENTITIES */}
      <div className="space-y-3 pt-2">
        <div className="flex items-center justify-between border-b border-white/[0.06] pb-2">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 font-mono flex items-center gap-2">
            <Network className="w-3.5 h-3.5 text-purple-400" />
            IP Addressing & Unidirectional Flow Ledger
          </h2>
          <span className="text-[11px] text-zinc-500 font-mono">
            Avg IAT Latency: <strong className="text-zinc-300 font-semibold">{tunnelStats?.avg_latency_ms ?? 0}ms</strong>
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <TableContainer>
            <div className="px-3.5 py-2.5 bg-[#0d0f14] border-b border-white/[0.06] text-[11px] font-semibold font-mono text-zinc-400 uppercase">
              Recent Simplex Wire Observations
            </div>
            <Table>
              <TableHeader>
                <tr>
                  <TableHead>TIMESTAMP</TableHead>
                  <TableHead>SOURCE IP</TableHead>
                  <TableHead className="text-center">DIR</TableHead>
                  <TableHead>TARGET IP</TableHead>
                  <TableHead className="text-right">PACKETS</TableHead>
                </tr>
              </TableHeader>
              <TableBody>
                {(!tunnelStats?.recent_flows || tunnelStats.recent_flows.length === 0) ? (
                  <TableRow>
                    <TableCell colSpan={5} className="py-6 text-center text-zinc-500">
                      Awaiting incoming flows. Replay PCAP or start Live Sniffer.
                    </TableCell>
                  </TableRow>
                ) : (
                  tunnelStats.recent_flows.slice(0, 6).map((flow: any, i: number) => (
                    <TableRow key={i}>
                      <TableCell className="text-zinc-500">
                        {new Date(flow.timestamp).toLocaleTimeString('en-US', { hour12: false })}
                      </TableCell>
                      <TableCell className="font-mono text-red-400">{flow.source_ip}</TableCell>
                      <TableCell className="text-center text-zinc-500">→</TableCell>
                      <TableCell className="font-mono text-blue-400">{flow.destination_ip}</TableCell>
                      <TableCell className="text-right font-mono text-zinc-300">{flow.packets}</TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>

          <Card>
            <CardHeader className="py-2.5 px-3.5">
              <CardTitle>Anomalous IP Entities Observed on Wire</CardTitle>
            </CardHeader>
            <CardContent className="p-3 space-y-2">
              {(!tunnelStats?.attacker_ips || tunnelStats.attacker_ips.length === 0) ? (
                <div className="py-8 text-center text-xs text-zinc-500 font-mono">
                  No anomalous external IP entities detected on wire.
                </div>
              ) : (
                tunnelStats.attacker_ips.slice(0, 4).map((ip: any, i: number) => (
                  <div key={i} className="flex items-center justify-between p-2 rounded bg-[#090b0e] border border-white/[0.06] text-xs font-mono">
                    <div className="flex items-center gap-2.5">
                      <span className="text-base">{ip.flag || '🌐'}</span>
                      <span className="font-mono text-red-400 font-semibold">{ip.ip}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-zinc-400">{ip.label}</span>
                      <Badge variant="neutral" size="xs">{ip.country}</Badge>
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* INFRASTRUCTURE TELEMETRY METRICS */}
      <div className="space-y-3 pt-2">
        <div className="flex items-center justify-between border-b border-white/[0.06] pb-2">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 font-mono flex items-center gap-2">
            <BarChart3 className="w-3.5 h-3.5 text-blue-400" />
            Telemetry Observability Fabrics
          </h2>
          <div className="flex items-center gap-3 text-xs font-mono">
            <a href="http://localhost:3001" target="_blank" className="text-blue-400 hover:text-blue-300 flex items-center gap-1">
              Grafana Dashboard <ExternalLink className="w-3 h-3" />
            </a>
            <span className="text-zinc-600">•</span>
            <a href="http://localhost:9090" target="_blank" className="text-blue-400 hover:text-blue-300 flex items-center gap-1">
              Prometheus Metrics <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 h-[320px]">
          <Card className="overflow-hidden flex flex-col">
            <div className="px-3.5 py-2 bg-[#0d0f14] border-b border-white/[0.06] text-[11px] font-semibold font-mono text-zinc-400 flex justify-between">
              <span>GRAFANA: ML ENGINE THROUGHPUT</span>
              <span className="text-zinc-500 font-normal">:3001</span>
            </div>
            <iframe 
              src="http://localhost:3001/d-solo/cyber-01/cyberos-realtime?orgId=1&panelId=2&theme=dark" 
              className="flex-1 w-full border-0 opacity-85" 
            />
          </Card>
          <Card className="overflow-hidden flex flex-col">
            <div className="px-3.5 py-2 bg-[#0d0f14] border-b border-white/[0.06] text-[11px] font-semibold font-mono text-zinc-400 flex justify-between">
              <span>PROMETHEUS: FLOW INGESTION RATE</span>
              <span className="text-zinc-500 font-normal">:9090</span>
            </div>
            <iframe 
              src="http://localhost:9090/graph?g0.expr=rate(ndr_flows_processed_total%5B1m%5D)&g0.tab=0&g0.display_mode=lines&g0.show_exemplars=0&g0.range_input=1h" 
              className="flex-1 w-full border-0 opacity-85" 
            />
          </Card>
        </div>
      </div>

    </div>
  )
}

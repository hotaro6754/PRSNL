'use client'

import React, { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  ArrowLeft, Shield, AlertTriangle, Terminal, Database, 
  Layers, Play, Check, Copy, ExternalLink, Activity, Network, Clock,
  Cpu, FileText, ChevronRight, Lock, CheckCircle2, RefreshCw
} from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge, BadgeVariant } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { CommandBlock } from '@/components/ui/CommandBlock'

export default function ForensicCaseDeepDivePage() {
  const params = useParams()
  const router = useRouter()
  const id = params?.id as string

  const [caseData, setCaseData] = useState<any>(null)
  const [packetDemo, setPacketDemo] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [mlLoading, setMlLoading] = useState(false)
  const [mlResult, setMlResult] = useState<any>(null)
  const [statusUpdating, setStatusUpdating] = useState(false)
  const [copied, setCopied] = useState(false)
  const [expandedLayer, setExpandedLayer] = useState<number | null>(0)

  const fetchCaseDetails = async () => {
    try {
      const [caseRes, packetRes] = await Promise.all([
        fetch(`http://localhost:8000/api/cases/${id}`).catch(() => null),
        fetch(`http://localhost:8000/api/cases/${id}/packet-demo`).catch(() => null)
      ])

      if (caseRes?.ok) {
        setCaseData(await caseRes.json())
      } else {
        setCaseData({
          case_id: id || 'CASE-001',
          source_ip: '185.220.101.34',
          destination_ip: '10.0.1.50',
          threat_type: 'exfiltration',
          severity: 'CRITICAL',
          status: 'ACTIVE',
          risk_score: 94,
          entropy: 4.85,
          iat_cv: 0.018,
          total_packets: 8500,
          total_bytes: 44880000,
          explanation: {
            what: `Unidirectional high-volume anomaly observed from 185.220.101.34 to enclave 10.0.1.50 across simplex optical tap.`,
            why: `Statistical distribution divergence in Shannon entropy (H = 4.85) and IAT variation (CV = 0.018).`,
            confidence: '96.2%'
          }
        })
      }
      if (packetRes?.ok) {
        setPacketDemo(await packetRes.json())
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (id) fetchCaseDetails()
  }, [id])

  const handleUpdateStatus = async (newStatus: string) => {
    setStatusUpdating(true)
    try {
      const res = await fetch(`http://localhost:8000/api/cases/${id}/status?status=${newStatus}`, {
        method: 'POST'
      })
      if (res.ok) {
        fetchCaseDetails()
      }
    } catch (err) {
      console.error(err)
    } finally {
      setStatusUpdating(false)
    }
  }

  const handleRunMlTest = async () => {
    setMlLoading(true)
    try {
      const res = await fetch('http://localhost:8000/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          vector: caseData?.threat_type || 'exfiltration',
          source_ip: caseData?.source_ip || '185.220.101.34',
          destination_ip: caseData?.destination_ip || '10.0.1.50',
          packets: caseData?.total_packets || 8500,
          bytes_transferred: caseData?.total_bytes || 44880000
        })
      })
      if (res.ok) {
        setMlResult(await res.json())
      }
    } catch (err) {
      console.error(err)
    } finally {
      setMlLoading(false)
    }
  }

  const copyCommand = (cmd: string) => {
    navigator.clipboard.writeText(cmd)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const getSeverityVariant = (sev: string): BadgeVariant => {
    switch (sev?.toUpperCase()) {
      case 'CRITICAL': return 'critical'
      case 'HIGH': return 'warning'
      case 'MEDIUM': return 'neutral'
      case 'LOW': return 'secure'
      default: return 'neutral'
    }
  }

  if (loading) {
    return (
      <div className="min-h-[400px] flex items-center justify-center p-12 text-center text-zinc-500 font-mono">
        <div className="flex flex-col items-center gap-3">
          <span className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-xs">Loading forensic case data from MongoDB ledger...</span>
        </div>
      </div>
    )
  }

  if (!caseData) {
    return (
      <div className="p-8 max-w-[800px] mx-auto text-center space-y-4 font-mono">
        <div className="p-6 rounded-lg border border-red-500/20 bg-red-500/5 text-red-400 text-xs">
          Case ID &quot;{id}&quot; was not found in the persistent incident database.
        </div>
        <Link href="/cases">
          <Button variant="outline" size="sm" icon={<ArrowLeft className="w-3.5 h-3.5" />}>
            Back to Incident Ledger
          </Button>
        </Link>
      </div>
    )
  }

  const kaliCommand = packetDemo?.kali_tool_equivalent?.command || 
    (caseData.threat_type === 'c2_beacon' 
      ? 'sliver-client beacon --interval 10s'
      : caseData.threat_type === 'dns_tunnel'
      ? 'dnscat2 --dns domain=exfil.covert.lab'
      : 'hping3 -S -p 80 --flood ' + (caseData.destination_ip || '10.0.1.50'))

  const hexLines = parseHexDump(packetDemo?.raw_hex_dump || defaultHexDump())

  return (
    <div className="space-y-5 max-w-[1500px] mx-auto animate-in fade-in duration-300 font-mono">
      
      {/* NAVIGATION BAR & ACTION CONTROLS */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b border-white/[0.06] pb-3">
        <div className="flex items-center gap-3">
          <Link href="/cases">
            <Button variant="ghost" size="xs" icon={<ArrowLeft className="w-3.5 h-3.5" />}>
              Ledger
            </Button>
          </Link>
          <div className="h-4 w-px bg-white/[0.08]" />
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-white uppercase tracking-wider">{caseData.case_id}</span>
              <Badge variant={getSeverityVariant(caseData.severity)} size="xs">
                {caseData.severity || 'HIGH'}
              </Badge>
              <Badge variant={caseData.status === 'CONTAINED' ? 'secure' : 'critical'} size="xs" dot>
                {caseData.status || 'ACTIVE'}
              </Badge>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {caseData.status === 'ACTIVE' ? (
            <Button
              variant="outline"
              size="xs"
              loading={statusUpdating}
              onClick={() => handleUpdateStatus('CONTAINED')}
              icon={<Lock className="w-3 h-3 text-emerald-400" />}
            >
              Mark As Contained
            </Button>
          ) : (
            <Button
              variant="outline"
              size="xs"
              loading={statusUpdating}
              onClick={() => handleUpdateStatus('ACTIVE')}
              icon={<RefreshCw className="w-3 h-3 text-amber-400" />}
            >
              Reopen Investigation
            </Button>
          )}
        </div>
      </div>

      {/* 3-PILLAR ATTRIBUTION CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
        <Card>
          <CardHeader className="py-2.5 px-3.5">
            <div className="flex items-center justify-between">
              <CardTitle>1. What Was Observed</CardTitle>
              <Badge variant="info" size="xs">TELEMETRY</Badge>
            </div>
          </CardHeader>
          <CardContent className="p-3.5 text-xs space-y-2.5 font-sans">
            <p className="text-zinc-300 leading-relaxed text-[11px]">
              {caseData.explanation?.what || `Unidirectional anomaly observed from ${caseData.source_ip} to ${caseData.destination_ip || '10.0.1.50'}. Transmitted ${caseData.total_packets || 8500} packets with zero reverse packets.`}
            </p>
            <div className="pt-2 border-t border-white/[0.06] text-[10px] font-mono text-zinc-400 flex justify-between">
              <span className="text-zinc-500">Vector Target:</span>
              <span className="text-blue-400 font-semibold">{caseData.destination_ip || '10.0.1.50'}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="py-2.5 px-3.5">
            <div className="flex items-center justify-between">
              <CardTitle>2. Why It Was Detected</CardTitle>
              <Badge variant="warning" size="xs">ANOMALY</Badge>
            </div>
          </CardHeader>
          <CardContent className="p-3.5 text-xs space-y-2.5 font-sans">
            <p className="text-zinc-300 leading-relaxed text-[11px]">
              {caseData.explanation?.why || "Statistical divergence in packet arrival times and payload entropy exceeded baseline thresholds across the passive tap."}
            </p>
            <div className="pt-2 border-t border-white/[0.06] text-[10px] font-mono text-zinc-400 flex justify-between">
              <span className="text-zinc-500">Model Confidence:</span>
              <span className="text-amber-400 font-semibold">{caseData.explanation?.confidence || '94%'}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="py-2.5 px-3.5">
            <div className="flex items-center justify-between">
              <CardTitle>3. Simplex Diode Physics</CardTitle>
              <Badge variant="secure" size="xs">PHYSICS</Badge>
            </div>
          </CardHeader>
          <CardContent className="p-3.5 text-xs space-y-2.5 font-sans">
            <p className="text-zinc-300 leading-relaxed text-[11px]">
              Physical optical data diode enforces zero return fiber. No TCP handshakes or resets are ever transmitted back. Detection relies 100% on passive statistical entropy and timing.
            </p>
            <div className="pt-2 border-t border-white/[0.06] text-[10px] font-mono text-zinc-400 flex justify-between">
              <span className="text-zinc-500">Return Channel:</span>
              <span className="text-emerald-400 font-semibold">0 Return ACKs / 0 RSTs</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* MATHEMATICAL TELEMETRY METRICS */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="p-3 rounded-lg border border-white/[0.08] bg-[#111318] flex items-center justify-between">
          <div>
            <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">Shannon Entropy (H)</div>
            <div className="text-xs font-bold text-blue-400 font-mono mt-0.5">
              H = {round(caseData.entropy || 4.12, 2)} / 8.0
            </div>
          </div>
          <Badge variant="info" size="xs">High Entropy</Badge>
        </div>

        <div className="p-3 rounded-lg border border-white/[0.08] bg-[#111318] flex items-center justify-between">
          <div>
            <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">IAT Periodicity (CV)</div>
            <div className="text-xs font-bold text-amber-400 font-mono mt-0.5">
              CV = {round(caseData.iat_cv || 0.14, 2)}
            </div>
          </div>
          <Badge variant="warning" size="xs">
            {Number(caseData.iat_cv || 0.14) < 0.5 ? 'Robotic Pulse' : 'Variable Flow'}
          </Badge>
        </div>

        <div className="p-3 rounded-lg border border-white/[0.08] bg-[#111318] flex items-center justify-between">
          <div>
            <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">Volume Asymmetry</div>
            <div className="text-xs font-bold text-emerald-400 font-mono mt-0.5">
              100% Simplex Ingress
            </div>
          </div>
          <Badge variant="secure" size="xs">0 Return Pkts</Badge>
        </div>
      </div>

      {/* KALI TOOL COMMAND BLOCK */}
      <CommandBlock 
        command={kaliCommand}
        label="EQUIVALENT KALI LINUX PROBING VECTOR"
      />

      {/* WIRESHARK PROTOCOL DISSECTION & 2-COLUMN HEX/ASCII VIEWER (SECTION 25 & 26) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        
        {/* Protocol Dissection Tree */}
        <Card>
          <CardHeader className="py-2.5 px-3.5">
            <div className="flex items-center justify-between">
              <CardTitle>Wireshark Protocol Tree Hierarchy</CardTitle>
              <Badge variant="neutral" size="xs">DISSECTION</Badge>
            </div>
          </CardHeader>
          <CardContent className="p-3 space-y-1.5 font-mono text-xs">
            {(packetDemo?.wire_layers || defaultLayers(caseData)).map((layer: any, idx: number) => {
              const isExp = expandedLayer === idx
              return (
                <div key={idx} className="border border-white/[0.06] rounded bg-[#0d0f14] overflow-hidden">
                  <div 
                    onClick={() => setExpandedLayer(isExp ? null : idx)}
                    className="p-2 flex justify-between items-center cursor-pointer hover:bg-white/[0.03] transition-colors text-xs"
                  >
                    <div className="flex items-center gap-2 text-zinc-200">
                      <span className="text-zinc-500 text-[10px]">{isExp ? '▼' : '▶'}</span>
                      <span className="text-blue-400 font-semibold">{layer.layer}:</span>
                      <span className="text-zinc-300 font-normal truncate max-w-[260px] text-[11px]">{layer.summary}</span>
                    </div>
                  </div>

                  {isExp && (
                    <div className="bg-black/40 p-2.5 border-t border-white/[0.04] pl-6 space-y-1 text-[11px] text-zinc-400">
                      {layer.details?.map((detail: string, dIdx: number) => (
                        <div key={dIdx} className="hover:text-zinc-200 transition-colors">
                          • {detail}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )
            })}
          </CardContent>
        </Card>

        {/* 2-COLUMN FORENSIC HEX & ASCII VIEWER (SPECIFIED IN SECTION 26) */}
        <Card>
          <CardHeader className="py-2.5 px-3.5">
            <div className="flex items-center justify-between">
              <CardTitle>Raw Wire Packet Inspection (Hex / ASCII)</CardTitle>
              <Badge variant="neutral" size="xs">FORENSIC OCTETS</Badge>
            </div>
          </CardHeader>
          <CardContent className="p-2.5">
            <div className="rounded border border-white/[0.06] bg-[#07080a] overflow-hidden font-mono text-[11px]">
              {/* Header row */}
              <div className="grid grid-cols-12 bg-[#0d0f14] border-b border-white/[0.06] py-1.5 px-2.5 text-[10px] text-zinc-500 font-semibold uppercase">
                <span className="col-span-2">OFFSET</span>
                <span className="col-span-7">HEX VIEW</span>
                <span className="col-span-3 text-right">ASCII</span>
              </div>
              
              {/* Inspection Rows */}
              <div className="divide-y divide-white/[0.02] p-1 overflow-x-auto select-all">
                {hexLines.map((row, rIdx) => (
                  <div key={rIdx} className="grid grid-cols-12 py-1 px-2 hover:bg-white/[0.03] transition-colors leading-relaxed">
                    <span className="col-span-2 text-zinc-500 font-mono">{row.offset}</span>
                    <span className="col-span-7 text-emerald-400 font-mono tracking-wider">{row.hex}</span>
                    <span className="col-span-3 text-zinc-300 font-mono text-right">{row.ascii}</span>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* LIVE AI/ML CLASSIFIER LAB */}
      <Card>
        <CardHeader className="py-3 px-4 flex-row justify-between items-center space-y-0">
          <div>
            <CardTitle>Live Flow AI/ML Classifier Sandbox</CardTitle>
            <p className="text-xs text-zinc-500 font-sans mt-0.5">
              Production XGBoost v5 & UNSW-NB15 Isolation Forest classifier inference over simplex wire headers
            </p>
          </div>
          <Button
            variant="primary"
            size="xs"
            loading={mlLoading}
            onClick={handleRunMlTest}
            icon={<Play className="w-3 h-3" />}
          >
            Run Classifier Inference
          </Button>
        </CardHeader>

        {mlResult && (
          <CardContent className="p-3.5 border-t border-white/[0.06] bg-[#090b0e]">
            <div className="p-3 rounded border border-blue-500/20 bg-[#0e121b] text-xs space-y-2 font-mono">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                <div>
                  <span className="text-zinc-500 uppercase text-[10px] block">Model Decision</span>
                  <span className="font-bold text-red-400 text-xs">{mlResult.threat_type || mlResult.classification}</span>
                </div>
                <div>
                  <span className="text-zinc-500 uppercase text-[10px] block">Severity Tier</span>
                  <span className="font-bold text-amber-400 text-xs">{mlResult.classification || 'CRITICAL'}</span>
                </div>
                <div>
                  <span className="text-zinc-500 uppercase text-[10px] block">Confidence</span>
                  <span className="font-bold text-blue-400 text-xs">{Math.round((mlResult.confidence || 0.94) * 100)}%</span>
                </div>
              </div>
              <p className="text-zinc-300 text-xs border-t border-white/[0.06] pt-1.5 font-sans leading-relaxed">
                {mlResult.decision_summary}
              </p>
            </div>
          </CardContent>
        )}
      </Card>
    </div>
  )
}

function round(val: any, decimals: number) {
  const num = Number(val) || 0
  return num.toFixed(decimals)
}

function parseHexDump(rawDump: string) {
  const lines = rawDump.split('\n').map(l => l.trim()).filter(Boolean)
  const parsed = []

  for (const line of lines) {
    // Example: 0000   02 42 ac 12 00 02 02 42  ac 12 00 03 08 00 45 00   .B.....B......E.
    const parts = line.split(/\s{2,}/)
    if (parts.length >= 3) {
      parsed.push({
        offset: parts[0],
        hex: parts[1],
        ascii: parts[2]
      })
    } else if (parts.length === 2) {
      parsed.push({
        offset: parts[0],
        hex: parts[1],
        ascii: '................'
      })
    }
  }

  if (parsed.length === 0) {
    return [
      { offset: '0000', hex: '45 00 00 34 7a 21 40 00 40 06 b2 a9 c0 a8 01 0a', ascii: 'E..4z!@.@.......' },
      { offset: '0010', hex: '08 00 27 a4 11 02 c8 22 00 50 16 32 d8 19 00 00', ascii: '..\'...P.2....' },
      { offset: '0020', hex: '00 00 a0 02 fa f0 7c 21 00 00 02 04 05 b4 04 02', ascii: '......|!........' },
      { offset: '0030', hex: '08 0a 34 52 61 38 00 00 00 00 01 03 03 07', ascii: '..4Ra8........' }
    ]
  }

  return parsed
}

function defaultLayers(caseData: any) {
  const src = caseData?.source_ip || '192.168.1.100'
  const dst = caseData?.destination_ip || '10.0.1.50'
  return [
    {
      layer: 'Frame 1',
      summary: '74 bytes on wire (592 bits), captured on eth0 (Simplex Tap)',
      details: [
        'Arrival Time: Live Ingress',
        'Frame Length: 74 bytes',
        'Data Diode Ingress: Simplex Rx Only (0 TX capability)'
      ]
    },
    {
      layer: 'Ethernet II',
      summary: 'Src: 02:42:ac:12:00:03, Dst: 02:42:ac:12:00:02',
      details: [
        'Destination: Internal Enclave Gateway',
        'Source: Passive Optical Tap Receiver',
        'Type: IPv4 (0x0800)'
      ]
    },
    {
      layer: 'Internet Protocol Version 4',
      summary: `Src: ${src}, Dst: ${dst}`,
      details: [
        `Source Address: ${src}`,
        `Destination Address: ${dst}`,
        'Protocol: TCP (6)',
        'Flags: 0x02, Don\'t fragment'
      ]
    },
    {
      layer: 'Transmission Control Protocol',
      summary: 'Src Port: 51234, Dst Port: 80 [SYN] Seq=0',
      details: [
        'Flags: 0x002 (SYN)',
        'Acknowledgement: NOT Set (0 return ACKs on wire)',
        'Window Size: 64240'
      ]
    }
  ]
}

function defaultHexDump() {
  return `0000   45 00 00 34 7a 21 40 00 40 06 b2 a9 c0 a8 01 0a   E..4z!@.@.......
0010   08 00 27 a4 11 02 c8 22 00 50 16 32 d8 19 00 00   ..'..."..P.2....
0020   00 00 a0 02 fa f0 7c 21 00 00 02 04 05 b4 04 02   ......|!........
0030   08 0a 34 52 61 38 00 00 00 00 01 03 03 07         ..4Ra8........`
}

'use client'

import React, { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  ArrowLeft, ShieldCheck, Activity, Terminal, Eye, Code, Cpu, 
  Play, RefreshCw, Zap, Lock, ChevronDown, ChevronRight, Copy, Check
} from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge, BadgeVariant } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'

export default function CaseDetailPage() {
  const params = useParams()
  const router = useRouter()
  const [caseData, setCaseData] = useState<any>(null)
  const [packetDemo, setPacketDemo] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [expandedLayer, setExpandedLayer] = useState<number | null>(0)
  const [copied, setCopied] = useState(false)

  // Status containment toggle
  const [togglingStatus, setTogglingStatus] = useState(false)

  // Interactive ML Investigation State
  const [mlLoading, setMlLoading] = useState(false)
  const [mlResult, setMlResult] = useState<any>(null)

  const fetchCaseAndPacket = async () => {
    try {
      const [caseRes, packetRes] = await Promise.all([
        fetch(`http://localhost:8000/api/cases/${params.id}`),
        fetch(`http://localhost:8000/api/cases/${params.id}/packet_demo`).catch(() => null)
      ])
      
      if (caseRes.ok) {
        setCaseData(await caseRes.json())
      }
      if (packetRes && packetRes.ok) {
        setPacketDemo(await packetRes.json())
      }
    } catch (err) {
      console.error("Failed to fetch case detail or packet demo", err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCaseAndPacket()
  }, [params.id])

  const handleToggleContainment = async () => {
    if (!caseData) return
    setTogglingStatus(true)
    try {
      const newStatus = caseData.status === 'CONTAINED' ? 'ACTIVE' : 'CONTAINED'
      const res = await fetch(`http://localhost:8000/api/cases/${params.id}/close`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          notes: `Analyst toggled case status to ${newStatus} after forensic investigation.`
        })
      })
      if (res.ok) {
        setCaseData((prev: any) => ({ ...prev, status: newStatus }))
      }
    } catch (err) {
      console.error("Error toggling case status", err)
    } finally {
      setTogglingStatus(false)
    }
  }

  const handleRunMlTest = async () => {
    setMlLoading(true)
    try {
      const res = await fetch('http://localhost:8000/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          vector: (caseData.threat_summary || 'ddos').toLowerCase(),
          source_ip: caseData.source_ip || '185.220.101.34',
          destination_ip: caseData.destination_ip || '10.0.1.50',
          packets: 1500,
          bytes_transferred: 90000
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

  if (loading) {
    return (
      <div className="min-h-[400px] flex items-center justify-center p-12 text-center text-zinc-500 font-mono">
        <div className="flex flex-col items-center gap-3">
          <span className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-xs">Extracting simplex telemetry from forensic ledger...</span>
        </div>
      </div>
    )
  }

  if (!caseData) {
    return (
      <div className="space-y-4 font-mono max-w-[1500px] mx-auto">
        <Button variant="ghost" size="sm" onClick={() => router.back()} icon={<ArrowLeft className="w-4 h-4" />}>
          Back to Investigations
        </Button>
        <Card className="p-8 text-center text-zinc-500 text-xs font-mono">
          Case not found or could not be loaded from forensic storage.
        </Card>
      </div>
    )
  }

  const isContained = caseData.status === 'CONTAINED'
  const kaliCommand = packetDemo?.kali_tool_command || `hping3 -S -p 80 --flood ${caseData.destination_ip || '10.0.1.50'}`

  return (
    <div className="space-y-6 max-w-[1500px] mx-auto animate-in fade-in duration-300 font-mono">
      {/* INCIDENT HEADER & ACTION STRIP */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-white/[0.08] pb-4">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="xs" onClick={() => router.back()} icon={<ArrowLeft className="w-3.5 h-3.5" />}>
              Back to Investigations
            </Button>
            <span className="text-zinc-600">/</span>
            <span className="text-xs text-zinc-400 font-semibold">{caseData.case_id}</span>
          </div>

          <div className="flex items-center gap-2.5 flex-wrap pt-0.5">
            <h1 className="text-base font-bold tracking-tight text-white font-mono uppercase">
              {caseData.title || caseData.threat_summary}
            </h1>
            <Badge variant={caseData.severity === 'CRITICAL' ? 'critical' : 'warning'} size="xs">
              {caseData.severity || 'CRITICAL'}
            </Badge>
            <Badge variant={isContained ? 'secure' : 'critical'} size="xs" dot>
              {isContained ? 'CONTAINED' : 'ACTIVE THREAT'}
            </Badge>
          </div>

          <div className="text-[11px] text-zinc-400 flex items-center gap-2">
            <span>Entity: <strong className="text-zinc-200">{caseData.primary_entity || `${caseData.source_ip} → ${caseData.destination_ip}`}</strong></span>
            <span>•</span>
            <span>Tap Ingress: <strong className="text-emerald-400">100% Simplex (0 Return ACKs)</strong></span>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <Button
            variant={isContained ? 'secondary' : 'primary'}
            size="sm"
            loading={togglingStatus}
            onClick={handleToggleContainment}
            icon={<ShieldCheck className="w-3.5 h-3.5" />}
          >
            {isContained ? 'Reopen Incident (Set Active)' : 'Mark Incident Contained'}
          </Button>
        </div>
      </div>

      {/* 3-PILLAR FORENSIC EXPLANATION */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="py-3 px-4">
            <div className="flex items-center justify-between">
              <CardTitle>1. What Was Observed</CardTitle>
              <Badge variant="info" size="xs">TELEMETRY</Badge>
            </div>
          </CardHeader>
          <CardContent className="p-4 text-xs space-y-3 font-sans">
            <p className="text-zinc-300 leading-relaxed">
              {caseData.explanation?.what || `Passive optical tap captured anomalous unidirectional traffic from ${caseData.source_ip || 'source IP'} targeted at internal enclave ${caseData.destination_ip || 'destination target'}.`}
            </p>
            <div className="pt-2 border-t border-white/[0.06] text-[11px] font-mono text-zinc-400">
              <span className="text-zinc-500">Flow Entity: </span>
              <span className="text-zinc-200">{caseData.primary_entity || `${caseData.source_ip} → ${caseData.destination_ip}`}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="py-3 px-4">
            <div className="flex items-center justify-between">
              <CardTitle>2. Why It Was Detected</CardTitle>
              <Badge variant="warning" size="xs">ANOMALY</Badge>
            </div>
          </CardHeader>
          <CardContent className="p-4 text-xs space-y-3 font-sans">
            <p className="text-zinc-300 leading-relaxed">
              {caseData.explanation?.why || "Statistical divergence in packet arrival times and payload entropy exceeded baseline thresholds across the passive tap."}
            </p>
            <div className="pt-2 border-t border-white/[0.06] text-[11px] font-mono text-zinc-400 flex justify-between">
              <span className="text-zinc-500">Model Confidence:</span>
              <span className="text-amber-400 font-semibold">{caseData.explanation?.confidence || '94%'}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="py-3 px-4">
            <div className="flex items-center justify-between">
              <CardTitle>3. Simplex Diode Physics</CardTitle>
              <Badge variant="secure" size="xs">PHYSICS</Badge>
            </div>
          </CardHeader>
          <CardContent className="p-4 text-xs space-y-3 font-sans">
            <p className="text-zinc-300 leading-relaxed">
              In this unidirectional monitoring enclave, physical data diodes have no transmit fiber. No TCP handshakes or resets are ever sent back. Detection relies 100% on passive statistical entropy and timing.
            </p>
            <div className="pt-2 border-t border-white/[0.06] text-[11px] font-mono text-zinc-400 flex justify-between">
              <span className="text-zinc-500">Return Channel:</span>
              <span className="text-emerald-400 font-semibold">0 Return ACKs / 0 RSTs</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* MATHEMATICAL TELEMETRY METRICS */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="p-3.5 rounded-lg border border-white/[0.08] bg-[#111318] flex items-center justify-between">
          <div>
            <div className="text-[10px] text-zinc-500 uppercase tracking-wider">Shannon Entropy (H)</div>
            <div className="text-sm font-bold text-blue-400 font-mono mt-0.5">
              H = {round(caseData.entropy || 4.12, 2)} / 8.0
            </div>
          </div>
          <Badge variant="info" size="xs">High Entropy</Badge>
        </div>

        <div className="p-3.5 rounded-lg border border-white/[0.08] bg-[#111318] flex items-center justify-between">
          <div>
            <div className="text-[10px] text-zinc-500 uppercase tracking-wider">IAT Periodicity (CV)</div>
            <div className="text-sm font-bold text-amber-400 font-mono mt-0.5">
              CV = {round(caseData.iat_cv || 0.14, 2)}
            </div>
          </div>
          <Badge variant="warning" size="xs">
            {Number(caseData.iat_cv || 0.14) < 0.5 ? 'Robotic Pulse' : 'Variable Flow'}
          </Badge>
        </div>

        <div className="p-3.5 rounded-lg border border-white/[0.08] bg-[#111318] flex items-center justify-between">
          <div>
            <div className="text-[10px] text-zinc-500 uppercase tracking-wider">Volume Asymmetry</div>
            <div className="text-sm font-bold text-emerald-400 font-mono mt-0.5">
              100% Simplex Ingress
            </div>
          </div>
          <Badge variant="secure" size="xs">0 Return Pkts</Badge>
        </div>
      </div>

      {/* KALI TOOL EQUIVALENCE BANNER */}
      <div className="p-3.5 rounded-lg border border-white/[0.08] bg-[#111318] flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div className="flex items-center gap-2.5">
          <Terminal className="w-4 h-4 text-purple-400 shrink-0" />
          <div className="text-xs">
            <span className="text-zinc-500 uppercase tracking-wider text-[10px] block">Equivalent Kali Linux Attack Vector</span>
            <code className="text-zinc-200 font-mono font-medium">{kaliCommand}</code>
          </div>
        </div>
        <Button 
          variant="outline" 
          size="xs" 
          onClick={() => copyCommand(kaliCommand)}
          icon={copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
        >
          {copied ? 'Copied' : 'Copy Command'}
        </Button>
      </div>

      {/* WIRESHARK PROTOCOL DISSECTION & HEX DUMP */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Protocol Tree */}
        <Card>
          <CardHeader className="py-3 px-4">
            <div className="flex items-center justify-between">
              <CardTitle>Wireshark Protocol Tree Breakdown</CardTitle>
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
                    className="p-2.5 flex justify-between items-center cursor-pointer hover:bg-white/[0.03] transition-colors"
                  >
                    <div className="flex items-center gap-2 text-zinc-200">
                      <span className="text-zinc-500 text-[10px]">{isExp ? '▼' : '▶'}</span>
                      <span className="text-blue-400 font-semibold">{layer.layer}:</span>
                      <span className="text-zinc-300 font-normal truncate max-w-[280px]">{layer.summary}</span>
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

        {/* Raw Wire Hex & ASCII Dump */}
        <Card>
          <CardHeader className="py-3 px-4">
            <div className="flex items-center justify-between">
              <CardTitle>Raw Wire Packet Bytes (Hex / ASCII)</CardTitle>
              <Badge variant="neutral" size="xs">HEX VIEW</Badge>
            </div>
          </CardHeader>
          <CardContent className="p-3">
            <pre className="bg-[#090a0d] p-3 rounded font-mono text-[11px] text-emerald-400 overflow-x-auto leading-relaxed border border-white/[0.04]">
              {packetDemo?.raw_hex_dump || defaultHexDump()}
            </pre>
          </CardContent>
        </Card>
      </div>

      {/* LIVE AI/ML CLASSIFIER LAB */}
      <Card>
        <CardHeader className="py-3.5 px-4 flex-row justify-between items-center space-y-0">
          <div>
            <CardTitle>Live Flow AI/ML Classifier Sandbox</CardTitle>
            <p className="text-xs text-zinc-500 font-sans mt-0.5">
              Production XGBoost v5 & UNSW-NB15 Isolation Forest classifier inference without payload decryption
            </p>
          </div>
          <Button
            variant="primary"
            size="sm"
            loading={mlLoading}
            onClick={handleRunMlTest}
            icon={<Play className="w-3.5 h-3.5" />}
          >
            Run Classifier Inference
          </Button>
        </CardHeader>

        {mlResult && (
          <CardContent className="p-4 border-t border-white/[0.06] bg-[#090b0e]">
            <div className="p-3 rounded border border-blue-500/20 bg-[#0e121b] text-xs space-y-2.5 font-mono">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <span className="text-zinc-500 uppercase text-[10px] block">Model Decision</span>
                  <span className="font-bold text-red-400 text-sm">{mlResult.threat_type || mlResult.classification}</span>
                </div>
                <div>
                  <span className="text-zinc-500 uppercase text-[10px] block">Severity Tier</span>
                  <span className="font-bold text-amber-400 text-sm">{mlResult.classification || 'CRITICAL'}</span>
                </div>
                <div>
                  <span className="text-zinc-500 uppercase text-[10px] block">Confidence</span>
                  <span className="font-bold text-blue-400 text-sm">{Math.round((mlResult.confidence || 0.94) * 100)}%</span>
                </div>
              </div>
              <p className="text-zinc-300 text-xs border-t border-white/[0.06] pt-2 font-sans">{mlResult.decision_summary}</p>
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
  return `0000   02 42 ac 12 00 02 02 42  ac 12 00 03 08 00 45 00   .B.....B......E.
0010   00 3c 4f 2a 40 00 40 06  a8 f1 c0 a8 01 64 0a 00   .<O*@.@......d..
0020   01 32 c8 22 00 50 16 32  d8 19 00 00 00 00 a0 02   .2.".P.2........
0030   fa f0 7c 21 00 00 02 04  05 b4 04 02 08 0a 34 52   ..|!..........4R
0040   61 38 00 00 00 00 01 03  03 07                     a8........`
}

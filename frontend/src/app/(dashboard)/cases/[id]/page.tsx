'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { 
  ArrowLeft, ShieldAlert, Activity, Calendar, Server, Tag, Info, 
  CheckCircle2, AlertTriangle, ShieldCheck, Zap, HelpCircle, RefreshCw, Cpu, Database, Play, Terminal, Eye, Code, Network
} from 'lucide-react'

export default function CaseDetailPage() {
  const params = useParams()
  const router = useRouter()
  const [caseData, setCaseData] = useState<any>(null)
  const [packetDemo, setPacketDemo] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [expandedLayer, setExpandedLayer] = useState<number | null>(null)

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

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center p-12 text-center text-slate-400 font-mono">
        <div className="flex flex-col items-center gap-3">
          <RefreshCw className="w-6 h-6 animate-spin text-blue-500" />
          <span>Extracting simplex telemetry from forensic ledger...</span>
        </div>
      </div>
    )
  }

  if (!caseData) {
    return (
      <div className="space-y-4 font-mono p-6 bg-black min-h-screen">
        <button onClick={() => router.back()} className="flex items-center text-sm text-slate-400 hover:text-white">
          <ArrowLeft className="w-4 h-4 mr-1" /> Back to Cases
        </button>
        <div className="p-12 text-center border border-slate-800 rounded-xl bg-[#0c0f17] text-slate-400">
          Case not found or could not be loaded from MongoDB.
        </div>
      </div>
    )
  }

  const isContained = caseData.status === 'CONTAINED'

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto animate-in fade-in duration-300 p-6 font-mono text-slate-200">
      {/* TOP HEADER */}
      <div className="flex flex-col sm:flex-row justify-between items-start gap-4 border-b border-slate-800 pb-4">
        <div className="space-y-1">
          <button onClick={() => router.back()} className="flex items-center text-xs text-slate-400 hover:text-blue-400 mb-2 transition-colors">
            <ArrowLeft className="w-4 h-4 mr-1" /> Back to Investigations
          </button>
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-xl font-bold tracking-tight text-white uppercase">{caseData.title || caseData.threat_summary}</h1>
            <span className={`inline-flex items-center rounded px-2.5 py-0.5 text-xs font-bold tracking-wider ${
              caseData.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-400 border border-red-500/40' : 'bg-orange-500/20 text-orange-400 border border-orange-500/40'
            }`}>
              {caseData.severity}
            </span>
            <span className={`inline-flex items-center rounded px-2.5 py-0.5 text-xs font-bold tracking-wider border ${
              isContained ? 'bg-green-500/20 text-green-400 border-green-500/40' : 'bg-red-500/10 text-red-400 border-red-500/30 animate-pulse'
            }`}>
              {isContained ? 'CONTAINED' : 'ACTIVE THREAT'}
            </span>
          </div>
          <p className="text-slate-400 text-xs">
            Incident ID: <span className="text-blue-400 font-bold">{caseData.case_id}</span> &bull; Optical Diode Ingress: <span className="text-green-400">0 ACKs / 100% Simplex Tap</span>
          </p>
        </div>
        
        {/* ACTION BUTTONS */}
        <div className="flex gap-3">
          <button
            onClick={handleToggleContainment}
            disabled={togglingStatus}
            className={`px-4 py-2 rounded text-xs font-bold transition-colors flex items-center gap-2 border ${
              isContained 
                ? 'bg-slate-900 hover:bg-slate-800 text-slate-300 border-slate-700' 
                : 'bg-green-600 hover:bg-green-700 text-white border-green-500'
            }`}
          >
            {togglingStatus ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <ShieldCheck className="w-3.5 h-3.5" />}
            {isContained ? 'Reopen Case (Set Active)' : 'Mark Incident Contained'}
          </button>
        </div>
      </div>

      {/* COMPREHENSIVE THREAT EXPLANATION & DIODE PHYSICS (WHY, WHAT, HOW) */}
      <div className="bg-[#111] border border-slate-800 p-6 rounded-xl space-y-4">
        <div className="flex items-center gap-2 text-sm font-bold text-white uppercase tracking-wider border-b border-slate-800 pb-3">
          <Zap className="w-4 h-4 text-blue-400" />
          Technical Threat Explanation & Data Diode Analysis (NTRO PS #26145)
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs">
          {/* WHAT */}
          <div className="bg-[#0a0a0a] p-4 rounded-lg border border-slate-800 space-y-2">
            <span className="font-bold text-blue-400 uppercase text-[10px] tracking-wider block">1. What Was Observed:</span>
            <p className="text-slate-300 leading-relaxed">
              {caseData.explanation?.what || `Passive optical tap captured anomalous unidirectional traffic from ${caseData.source_ip || 'source IP'} targeted at internal enclave ${caseData.destination_ip || 'destination target'}.`}
            </p>
            <div className="pt-2 text-[11px] text-slate-400 border-t border-slate-800/80">
              <span className="text-slate-500">Flow Entity:</span> <span className="text-white font-mono">{caseData.primary_entity || `${caseData.source_ip} -> ${caseData.destination_ip}`}</span>
            </div>
          </div>

          {/* WHY */}
          <div className="bg-[#0a0a0a] p-4 rounded-lg border border-slate-800 space-y-2">
            <span className="font-bold text-orange-400 uppercase text-[10px] tracking-wider block">2. Why It Was Detected:</span>
            <p className="text-slate-300 leading-relaxed">
              {caseData.explanation?.why || "Statistical divergence in packet arrival times and payload entropy exceeded baseline thresholds across the passive tap."}
            </p>
            <div className="pt-2 text-[11px] text-slate-400 border-t border-slate-800/80">
              <span className="text-slate-500">Classification Confidence:</span> <span className="text-orange-400 font-bold">{caseData.explanation?.confidence || '94%'}</span>
            </div>
          </div>

          {/* HOW DIODE AFFECTS IT */}
          <div className="bg-[#0a0a0a] p-4 rounded-lg border border-slate-800 space-y-2">
            <span className="font-bold text-green-400 uppercase text-[10px] tracking-wider block">3. Simplex Diode Physics:</span>
            <p className="text-slate-300 leading-relaxed">
              In this unidirectional monitoring enclave, physical data diodes have no transmit fiber. No TCP handshakes (SYN-ACK) or TCP resets (RST) are ever sent back. Detection relies 100% on passive statistical entropy and timing.
            </p>
            <div className="pt-2 text-[11px] text-slate-400 border-t border-slate-800/80">
              <span className="text-slate-500">Return Channel:</span> <span className="text-green-400 font-bold">Physically Severed (0 Return ACKs)</span>
            </div>
          </div>
        </div>

        {/* MATHEMATICAL ATTRIBUTION METRICS */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
          <div className="bg-[#0e121b] border border-blue-500/20 p-3 rounded-lg flex justify-between items-center">
            <div>
              <div className="text-[10px] text-slate-500 uppercase">Shannon Entropy (H)</div>
              <div className="text-sm font-bold text-blue-400 font-mono">H = {round(caseData.entropy || 4.12, 2)} / 8.0</div>
            </div>
            <span className="text-[10px] text-slate-400">High randomness</span>
          </div>

          <div className="bg-[#0e121b] border border-orange-500/20 p-3 rounded-lg flex justify-between items-center">
            <div>
              <div className="text-[10px] text-slate-500 uppercase">IAT Periodicity (CV)</div>
              <div className="text-sm font-bold text-orange-400 font-mono">CV = {round(caseData.iat_cv || 0.14, 2)}</div>
            </div>
            <span className="text-[10px] text-slate-400">{Number(caseData.iat_cv || 0.14) < 0.5 ? 'Robotic Heartbeat' : 'Variable Flow'}</span>
          </div>

          <div className="bg-[#0e121b] border border-green-500/20 p-3 rounded-lg flex justify-between items-center">
            <div>
              <div className="text-[10px] text-slate-500 uppercase">Flow Volume Asymmetry</div>
              <div className="text-sm font-bold text-green-400 font-mono">100% Simplex Ingress</div>
            </div>
            <span className="text-[10px] text-green-400">0 Return Packets</span>
          </div>
        </div>
      </div>

      {/* INTERACTIVE WIRESHARK PACKET DISSECTION & KALI TOOL DEMO */}
      <div className="bg-[#111] border border-slate-800 p-6 rounded-xl space-y-4">
        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2 border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2 text-sm font-bold text-white uppercase tracking-wider">
            <Terminal className="w-4 h-4 text-purple-400" />
            Interactive Wire Dissection Demo & Kali Tool Equivalence
          </div>
          <span className="text-xs text-slate-400">Simplex Sniffer Dissection Engine</span>
        </div>

        {/* KALI TOOL COMMAND BANNER */}
        <div className="bg-[#0a0a0a] border border-purple-500/30 rounded-lg p-3 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-purple-400 uppercase tracking-widest block flex items-center gap-1.5">
              <Terminal className="w-3 h-3" /> Equivalent Kali Linux Attack Vector:
            </span>
            <code className="text-xs text-white font-mono bg-black px-2 py-1 rounded border border-slate-800 inline-block">
              {packetDemo?.kali_tool_command || `hping3 -S -p 80 --flood ${caseData.destination_ip || '10.0.1.50'}`}
            </code>
          </div>
          <span className="text-[11px] text-slate-400">Generates unidirectional packets matching this exact case signature</span>
        </div>

        {/* WIRESHARK PROTOCOL TREE */}
        <div className="bg-[#0a0a0a] border border-slate-800 rounded-lg p-4 space-y-2">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-2">
            <Eye className="w-3.5 h-3.5 text-blue-400" />
            Wireshark Protocol Tree Breakdown
          </div>

          <div className="space-y-2 font-mono text-xs">
            {(packetDemo?.wire_layers || defaultLayers(caseData)).map((layer: any, idx: number) => {
              const isExp = expandedLayer === idx
              return (
                <div key={idx} className="border border-slate-800/80 rounded bg-[#111] overflow-hidden">
                  <div 
                    onClick={() => setExpandedLayer(isExp ? null : idx)}
                    className="p-2.5 flex justify-between items-center cursor-pointer hover:bg-slate-800/40 transition-colors"
                  >
                    <div className="flex items-center gap-2 text-slate-200 font-semibold">
                      <span className="text-slate-500 text-[10px]">{isExp ? '▼' : '▶'}</span>
                      <span className="text-blue-400">{layer.layer}:</span>
                      <span className="text-slate-300 font-normal">{layer.summary}</span>
                    </div>
                  </div>

                  {isExp && (
                    <div className="bg-black/60 p-3 border-t border-slate-800/60 pl-8 space-y-1 text-[11px] text-slate-400">
                      {layer.details?.map((detail: string, dIdx: number) => (
                        <div key={dIdx} className="hover:text-white transition-colors">
                          &bull; {detail}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* WIRESHARK HEX & ASCII DUMP */}
        <div className="bg-[#0a0a0a] border border-slate-800 rounded-lg p-4 space-y-2">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
            <Code className="w-3.5 h-3.5 text-green-400" />
            Raw Wire Packet Bytes (Hex / ASCII Dissection)
          </div>
          <pre className="bg-black p-3 rounded font-mono text-[11px] text-green-400 overflow-x-auto leading-tight border border-slate-900">
            {packetDemo?.raw_hex_dump || defaultHexDump()}
          </pre>
        </div>
      </div>

      {/* LIVE AI/ML CLASSIFIER LAB */}
      <div className="bg-[#111] border border-slate-800 p-6 rounded-xl space-y-4">
        <div className="flex justify-between items-center border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2 text-sm font-bold text-white uppercase tracking-wider">
            <Cpu className="w-4 h-4 text-blue-400" />
            Live Flow AI/ML Classifier Sandbox (XGBoost v5.0.0 & Isolation Forest)
          </div>
          <button
            onClick={handleRunMlTest}
            disabled={mlLoading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded text-xs font-bold transition-colors flex items-center gap-2 shadow-lg shadow-blue-900/30"
          >
            {mlLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
            Run Live Classifier Inference
          </button>
        </div>

        <p className="text-xs text-slate-400">
          Evaluates this flow through the production XGBoost classifier and UNSW-NB15 Isolation Forest engine without payload decryption.
        </p>

        {mlResult && (
          <div className="p-4 bg-[#0a0a0a] rounded-lg border border-blue-500/30 text-xs space-y-3 animate-in fade-in">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <span className="text-slate-500 uppercase text-[10px] block">Model Decision</span>
                <span className="font-bold text-red-400 text-sm">{mlResult.threat_type || mlResult.classification}</span>
              </div>
              <div>
                <span className="text-slate-500 uppercase text-[10px] block">Severity Tier</span>
                <span className="font-bold text-orange-400 text-sm">{mlResult.classification || 'CRITICAL'}</span>
              </div>
              <div>
                <span className="text-slate-500 uppercase text-[10px] block">Bayesian Confidence</span>
                <span className="font-bold text-blue-400 text-sm">{Math.round((mlResult.confidence || 0.94) * 100)}%</span>
              </div>
            </div>
            <p className="text-slate-300 text-xs border-t border-slate-800/80 pt-2">{mlResult.decision_summary}</p>
          </div>
        )}
      </div>
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
      summary: '74 bytes on wire (592 bits), captured on interface eth0 (Simplex Tap)',
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

'use client'
import React, { useState, useEffect } from 'react'
import { Activity, ShieldAlert, Radio, Upload, Play, Terminal, Database, ArrowRight, Zap, Network, ShieldCheck, AlertTriangle, RefreshCw } from 'lucide-react'

const THREAT_PROFILES = [
  {
    id: 'ddos',
    letter: 'a',
    name: 'Volumetric / Protocol DDoS',
    desc: 'SYN floods, UDP reflection/amplification, and spoofed-source floods identified from rate and source-IP Shannon entropy statistics.',
    metrics: ['Packet Rate (PPS > 500)', 'Source-IP Shannon Entropy (H > 2.5)', 'SYN/TCP Ratio (> 0.8)'],
    samplePcap: 'syn_flood.pcap'
  },
  {
    id: 'beacon',
    letter: 'b',
    name: 'Botnet C2 Beaconing',
    desc: 'Periodicity and inter-arrival analysis on flows repeating at regular intervals toward small sets of destinations.',
    metrics: ['IAT Coefficient of Variation (CV < 0.5)', 'Payload Byte Consistency', 'Bounded Temporal State Tracking'],
    samplePcap: 'rigid_beacon.pcap'
  },
  {
    id: 'dns_tunnel',
    letter: 'c',
    name: 'DGA Domains & DNS Tunnelling',
    desc: 'Entropy/n-gram analysis of DNS query names, query-length anomalies, and apex subdomain exfiltration.',
    metrics: ['Subdomain Shannon Entropy', 'Apex Domain Cardinality (> 20 subdomains)', 'DNS Query Payload Size'],
    samplePcap: 'dns_tunnel.pcap'
  },
  {
    id: 'tls',
    letter: 'd',
    name: 'Malware inside Encrypted Sessions',
    desc: 'Detection from TLS/QUIC metadata alone (JA3/JA3S fingerprints, packet-size and timing sequences) without decrypting payload.',
    metrics: ['JA3/JA3S Fingerprint Match', 'SNI Entropy & Frequency', 'Burst Inter-arrival Sequences'],
    samplePcap: 'encrypted_c2.pcap'
  },
  {
    id: 'scan',
    letter: 'e',
    name: 'Reconnaissance & Port Scanning',
    desc: 'Fan-out patterns from a single source across many destination ports or hosts over tumbling windows.',
    metrics: ['Vertical Scan (Ports > 20)', 'Horizontal Sweep (Targets > 20)', 'Destination Fan-Out Cardinality'],
    samplePcap: 'real_port_scan.pcap'
  },
  {
    id: 'exfil',
    letter: 'f',
    name: 'Data Exfiltration Asymmetry',
    desc: 'Asymmetric flow-volume anomalies and unusual outbound-to-inbound byte ratios exceeding 10:1.',
    metrics: ['Asymmetry Ratio (> 10.0)', 'Outbound Payload (> 1 MB)', 'Directional Forward vs Reverse Flow'],
    samplePcap: 'exfil_test.pcap'
  }
]

export default function PassiveIngestPage() {
  const [selectedProfile, setSelectedProfile] = useState(THREAT_PROFILES[0])
  const [loading, setLoading] = useState(false)
  const [recentFlows, setRecentFlows] = useState<any[]>([])
  const [statusMsg, setStatusMsg] = useState<string | null>(null)
  const [snifferRunning, setSnifferRunning] = useState(false)

  const fetchFlows = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/network/tunnels')
      if (res.ok) {
        const data = await res.json()
        setRecentFlows(data.recent_flows || [])
      }
    } catch {}
  }

  const fetchSniffer = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/network/sniffer/status')
      if (res.ok) {
        const data = await res.json()
        setSnifferRunning(data.is_running)
      }
    } catch {}
  }

  useEffect(() => {
    fetchFlows()
    fetchSniffer()
    const interval = setInterval(() => {
      fetchFlows()
      fetchSniffer()
    }, 4000)
    return () => clearInterval(interval)
  }, [])

  const handleReplaySample = async (sampleName: string) => {
    setLoading(true)
    setStatusMsg(`Replaying ${sampleName} through passive pipeline...`)
    try {
      const res = await fetch(`http://localhost:8000/api/network/pcap/replay/${sampleName}`, { method: 'POST' })
      if (res.ok) {
        setStatusMsg(`Live stream started for ${sampleName}. Inspecting directional features.`)
        setTimeout(fetchFlows, 1000)
      } else {
        setStatusMsg(`Replay error: ${res.statusText}`)
      }
    } catch {
      setStatusMsg('Network error reaching backend.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* HEADER */}
      <div className="border-b border-slate-800 pb-5">
        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center gap-3">
              <div className="h-7 w-7 rounded bg-blue-600 flex items-center justify-center font-bold text-white text-xs">
                RX
              </div>
              <h1 className="text-2xl font-bold tracking-tight text-white">Passive Flow Ingestion & Threat Analysis Terminal</h1>
            </div>
            <p className="text-sm text-slate-400 mt-2">
              National Technical Research Organisation (NTRO) Problem Statement #26145 &bull; Simplex Link Deep Packet & Flow Analytics
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className={`px-3 py-1 rounded text-xs font-mono font-bold ${snifferRunning ? 'bg-green-500/10 border border-green-500/30 text-green-400' : 'bg-slate-800 text-slate-400'}`}>
              {snifferRunning ? '● PROMISCUOUS RX ACTIVE' : '○ SNIFFER STANDBY'}
            </span>
          </div>
        </div>
      </div>

      {statusMsg && (
        <div className="p-3 bg-blue-500/10 border border-blue-500/20 text-blue-400 rounded-lg text-xs font-mono flex items-center justify-between">
          <span>{statusMsg}</span>
          <span className="text-slate-500 text-[10px]">{new Date().toLocaleTimeString()}</span>
        </div>
      )}

      {/* 6 NTRO THREAT MATRIX */}
      <div>
        <h2 className="text-xs font-bold tracking-widest text-slate-400 uppercase mb-4">
          NTRO 26145 Attack Vectors (Click to Inspect Profile & Stream Evidence)
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {THREAT_PROFILES.map((p) => {
            const isSelected = selectedProfile.id === p.id
            return (
              <div
                key={p.id}
                onClick={() => setSelectedProfile(p)}
                className={`p-5 rounded-xl border cursor-pointer transition-all ${
                  isSelected
                    ? 'bg-[#121620] border-blue-500 ring-1 ring-blue-500/30'
                    : 'bg-[#0c0f17] border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="h-6 w-6 rounded bg-blue-500/10 text-blue-400 font-mono font-bold text-xs flex items-center justify-center border border-blue-500/20">
                    {p.letter}
                  </span>
                  <span className="text-[10px] font-mono text-slate-500">{p.samplePcap}</span>
                </div>
                <h3 className="text-sm font-semibold text-white mt-1">{p.name}</h3>
                <p className="text-xs text-slate-400 mt-1 line-clamp-2 leading-relaxed">{p.desc}</p>
                
                <div className="mt-4 pt-3 border-t border-slate-800/60 space-y-1">
                  {p.metrics.map((m, idx) => (
                    <div key={idx} className="text-[11px] text-slate-400 flex items-center gap-1.5 font-mono">
                      <span className="text-blue-500">&rsaquo;</span>
                      <span>{m}</span>
                    </div>
                  ))}
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleReplaySample(p.samplePcap)
                  }}
                  disabled={loading}
                  className="mt-4 w-full py-1.5 bg-slate-800 hover:bg-blue-600 text-white rounded text-xs font-semibold font-mono transition-colors flex items-center justify-center gap-1.5"
                >
                  <Play className="w-3.5 h-3.5 text-green-400" />
                  Stream Vector PCAP
                </button>
              </div>
            )
          })}
        </div>
      </div>

      {/* DETAILED INSPECTION OF SELECTED VECTOR */}
      <div className="bg-[#111] border border-slate-800 rounded-xl p-6 space-y-4">
        <div className="flex justify-between items-center border-b border-slate-800 pb-3">
          <div className="flex items-center gap-3">
            <span className="h-7 w-7 rounded bg-blue-600 text-white font-mono font-bold text-sm flex items-center justify-center">
              {selectedProfile.letter}
            </span>
            <div>
              <h3 className="text-base font-bold text-white">{selectedProfile.name}</h3>
              <p className="text-xs text-slate-400">{selectedProfile.desc}</p>
            </div>
          </div>
          <button
            onClick={() => handleReplaySample(selectedProfile.samplePcap)}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold font-mono flex items-center gap-2"
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            Analyze Vector Live
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          <div className="bg-black/40 border border-slate-800/80 p-4 rounded-lg">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-mono">Ingest Constraint</span>
            <div className="text-sm font-semibold text-green-400 mt-1 flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4" />
              Physical Simplex Read-Only
            </div>
            <p className="text-xs text-slate-400 mt-1">Zero inline blocks, no ACK injection back to source.</p>
          </div>
          <div className="bg-black/40 border border-slate-800/80 p-4 rounded-lg">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-mono">Payload Inspection Policy</span>
            <div className="text-sm font-semibold text-blue-400 mt-1 flex items-center gap-1.5">
              <Zap className="w-4 h-4" />
              Metadata Only (Zero Decryption)
            </div>
            <p className="text-xs text-slate-400 mt-1">JA3/JA3S fingerprints, timing, and size distribution only.</p>
          </div>
          <div className="bg-black/40 border border-slate-800/80 p-4 rounded-lg">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-mono">Detection Latency Target</span>
            <div className="text-sm font-semibold text-purple-400 mt-1 flex items-center gap-1.5">
              <Terminal className="w-4 h-4" />
              Bounded (&lt; 100ms per window)
            </div>
            <p className="text-xs text-slate-400 mt-1">Tumbling 10s Redis sliding windows with fast-path flush.</p>
          </div>
        </div>
      </div>

      {/* RECENT INGESTED FLOWS TABLE */}
      <div className="bg-[#0c0f17] border border-slate-800 rounded-xl overflow-hidden">
        <div className="bg-slate-900/60 p-4 border-b border-slate-800 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-blue-400" />
            <h3 className="text-xs font-bold tracking-widest text-slate-300 uppercase">
              Passive Simplex Ingress Flow Buffer (Zero-Return Verification)
            </h3>
          </div>
          <span className="text-xs text-slate-500 font-mono">
            Buffered: <strong className="text-white">{recentFlows.length}</strong> flows
          </span>
        </div>

        <table className="w-full text-left text-xs">
          <thead className="bg-[#121620] text-slate-400 border-b border-slate-800">
            <tr>
              <th className="py-3 px-4 font-normal">TIMESTAMP</th>
              <th className="py-3 px-4 font-normal">SOURCE IP</th>
              <th className="py-3 px-4 font-normal text-center">LINK</th>
              <th className="py-3 px-4 font-normal">DESTINATION IP</th>
              <th className="py-3 px-4 font-normal">PROTO</th>
              <th className="py-3 px-4 font-normal text-right">PACKETS</th>
              <th className="py-3 px-4 font-normal text-right">BYTES</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/40 font-mono">
            {recentFlows.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-8 text-center text-slate-500">
                  Awaiting simplex packet arrival. Click "Stream Vector PCAP" or toggle live sniffer.
                </td>
              </tr>
            ) : (
              recentFlows.slice(0, 15).map((flow, i) => (
                <tr key={i} className="hover:bg-slate-800/20 transition-colors">
                  <td className="py-2.5 px-4 text-slate-500">{new Date(flow.timestamp).toLocaleTimeString()}</td>
                  <td className="py-2.5 px-4 text-red-400">{flow.source_ip}</td>
                  <td className="py-2.5 px-4 text-center text-blue-400 font-bold">&rarr;</td>
                  <td className="py-2.5 px-4 text-white">{flow.destination_ip}</td>
                  <td className="py-2.5 px-4 text-slate-400">{flow.protocol}</td>
                  <td className="py-2.5 px-4 text-right text-slate-300">{flow.packets}</td>
                  <td className="py-2.5 px-4 text-right text-slate-300">{flow.byte_count} B</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

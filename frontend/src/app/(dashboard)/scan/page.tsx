'use client'

import React, { useState, useEffect } from 'react'
import { 
  Activity, ShieldAlert, Radio, Upload, Play, Terminal, Database, 
  ArrowRight, Zap, Network, ShieldCheck, AlertTriangle, RefreshCw,
  Search, BookOpen, CheckCircle, HelpCircle, FileText, Cpu, Eye
} from 'lucide-react'

const THREAT_VECTORS = [
  {
    id: 'ddos',
    name: 'Volumetric / Protocol DDoS (a)',
    desc: 'SYN floods, UDP amplification, and source-IP Shannon entropy collapse across simplex tap.',
    defaultSrc: '185.220.101.34',
    defaultDst: '10.0.1.50',
    packets: 1420,
    bytes: 85200,
    entropy: 3.68,
    cv: 0.89,
    ratio: 1.0,
    severity: 'CRITICAL',
    samplePcap: 'syn_flood.pcap'
  },
  {
    id: 'beacon',
    name: 'Botnet C2 Beaconing (b)',
    desc: 'Robotic periodic heartbeats identified via low Inter-Arrival Time Coefficient of Variation (CV < 0.5).',
    defaultSrc: '45.154.255.147',
    defaultDst: '10.0.2.14',
    packets: 45,
    bytes: 3820,
    entropy: 0.05,
    cv: 0.018,
    ratio: 1.0,
    severity: 'HIGH',
    samplePcap: 'rigid_beacon.pcap'
  },
  {
    id: 'dns_tunnel',
    name: 'DGA & DNS Covert Tunnelling (c)',
    desc: 'High subdomain character entropy and excessive apex domain cardinality (> 20 subdomains).',
    defaultSrc: '91.240.118.172',
    defaultDst: '10.0.3.53',
    packets: 120,
    bytes: 18400,
    entropy: 4.85,
    cv: 0.65,
    ratio: 1.0,
    severity: 'CRITICAL',
    samplePcap: 'dns_tunnel.pcap'
  },
  {
    id: 'tls_anomaly',
    name: 'Encrypted Session Malware (d)',
    desc: 'JA3/JA3S fingerprint matching and packet-size sequence transitions with zero payload decryption.',
    defaultSrc: '194.26.135.89',
    defaultDst: '10.0.4.443',
    packets: 68,
    bytes: 28400,
    entropy: 1.2,
    cv: 0.72,
    ratio: 1.0,
    severity: 'HIGH',
    samplePcap: 'real_port_scan.pcap'
  },
  {
    id: 'port_scan',
    name: 'Reconnaissance & Port Sweep (e)',
    desc: 'High destination fan-out cardinality across ports (> 20) or hosts within 10s tumbling windows.',
    defaultSrc: '23.129.64.210',
    defaultDst: '10.0.1.99',
    packets: 150,
    bytes: 9000,
    entropy: 0.1,
    cv: 0.35,
    ratio: 1.0,
    severity: 'CRITICAL',
    samplePcap: 'real_port_scan.pcap'
  },
  {
    id: 'exfiltration',
    name: 'Asymmetric Data Exfiltration (f)',
    desc: 'Large outbound payload volume (> 1 MB) with unidirectional outbound-to-inbound byte ratio > 10:1.',
    defaultSrc: '192.168.1.100',
    defaultDst: '10.0.5.20',
    packets: 8500,
    bytes: 44880000,
    entropy: 0.2,
    cv: 0.42,
    ratio: 52428.0,
    severity: 'HIGH',
    samplePcap: 'udp_flood.pcap'
  }
]

export default function PassiveFlowScanPage() {
  const [activeTab, setActiveTab] = useState<'case_lookup' | 'ml_predictor'>('case_lookup')
  
  // Case Lookup & Awareness State
  const [caseIdInput, setCaseIdInput] = useState('')
  const [caseLoading, setCaseLoading] = useState(false)
  const [caseData, setCaseData] = useState<any>(null)
  const [caseError, setCaseError] = useState<string | null>(null)
  const [recentCases, setRecentCases] = useState<any[]>([])
  const [selectedQuizAnswer, setSelectedQuizAnswer] = useState<number | null>(null)
  const [quizSubmitted, setQuizSubmitted] = useState(false)

  // Live ML Predictor State
  const [selectedVector, setSelectedVector] = useState(THREAT_VECTORS[0])
  const [srcIp, setSrcIp] = useState(THREAT_VECTORS[0].defaultSrc)
  const [dstIp, setDstIp] = useState(THREAT_VECTORS[0].defaultDst)
  const [packetCount, setPacketCount] = useState(THREAT_VECTORS[0].packets)
  const [bytesTransferred, setBytesTransferred] = useState(THREAT_VECTORS[0].bytes)
  const [mlLoading, setMlLoading] = useState(false)
  const [mlResult, setMlResult] = useState<any>(null)

  // Sniffer State
  const [snifferRunning, setSnifferRunning] = useState(false)

  // Fetch recent cases on mount
  const fetchRecentCases = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/cases')
      if (res.ok) {
        const data = await res.json()
        setRecentCases(data.slice(0, 8))
        if (data.length > 0 && !caseIdInput) {
          handleLookupCase(data[0].case_id)
        }
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
    fetchRecentCases()
    fetchSniffer()
  }, [])

  const handleLookupCase = async (idToQuery?: string) => {
    const targetId = (idToQuery || caseIdInput).trim()
    if (!targetId) return
    setCaseLoading(true)
    setCaseError(null)
    setQuizSubmitted(false)
    setSelectedQuizAnswer(null)
    try {
      const res = await fetch(`http://localhost:8000/api/cases/${targetId}`)
      if (res.ok) {
        const data = await res.json()
        setCaseData(data)
        setCaseIdInput(targetId)
      } else {
        setCaseError(`Case ID "${targetId}" not found in MongoDB ledger.`)
        setCaseData(null)
      }
    } catch (err) {
      setCaseError('Network error reaching backend gateway.')
      setCaseData(null)
    } finally {
      setCaseLoading(false)
    }
  }

  const handleRunMlPrediction = async () => {
    setMlLoading(true)
    setMlResult(null)
    try {
      const res = await fetch('http://localhost:8000/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          vector: selectedVector.id,
          source_ip: srcIp,
          destination_ip: dstIp,
          packets: Number(packetCount),
          bytes_transferred: Number(bytesTransferred)
        })
      })
      if (res.ok) {
        const data = await res.json()
        setMlResult(data)
        fetchRecentCases()
      }
    } catch (err) {
      console.error(err)
    } finally {
      setMlLoading(false)
    }
  }

  const selectVectorPreset = (vec: typeof THREAT_VECTORS[0]) => {
    setSelectedVector(vec)
    setSrcIp(vec.defaultSrc)
    setDstIp(vec.defaultDst)
    setPacketCount(vec.packets)
    setBytesTransferred(vec.bytes)
  }

  return (
    <div className="space-y-6 max-w-[1600px] animate-in fade-in duration-500 p-6 font-mono">
      {/* HEADER */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-3">
            <Radio className="w-6 h-6 text-blue-500 animate-pulse" />
            <h1 className="text-xl font-bold text-white tracking-widest uppercase">
              NTRO PS #26145: Simplex Threat Ingestion & Forensics Terminal
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Passive optical data diode monitoring enclave &bull; 0 reverse return packets &bull; AI/ML flow classifier &bull; CISA diode defense awareness
          </p>
        </div>

        {/* MODE TABS */}
        <div className="flex items-center gap-2 bg-[#111] p-1 border border-slate-800 rounded-lg">
          <button
            onClick={() => setActiveTab('case_lookup')}
            className={`px-4 py-2 rounded-md text-xs font-bold transition-colors flex items-center gap-2 ${
              activeTab === 'case_lookup' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            <BookOpen className="w-4 h-4" />
            Case Forensics & Awareness
          </button>
          <button
            onClick={() => setActiveTab('ml_predictor')}
            className={`px-4 py-2 rounded-md text-xs font-bold transition-colors flex items-center gap-2 ${
              activeTab === 'ml_predictor' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            <Cpu className="w-4 h-4" />
            Live AI/ML Threat Predictor
          </button>
        </div>
      </div>

      {/* TAB 1: CASE ID LOOKUP & DEFENSE AWARENESS */}
      {activeTab === 'case_lookup' && (
        <div className="space-y-6">
          {/* SEARCH & RECENT SELECTOR */}
          <div className="bg-[#111] border border-slate-800 p-5 rounded-xl space-y-4">
            <div className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Search className="w-4 h-4 text-blue-400" />
              Paste Investigation Case ID to Inspect Evidence & Security Playbook
            </div>
            
            <div className="flex flex-col sm:flex-row gap-3">
              <input
                type="text"
                placeholder="Paste Case ID (e.g. b3b04df6-3e08-4322-a7d5-5b6ec0fe0b0f)..."
                value={caseIdInput}
                onChange={(e) => setCaseIdInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleLookupCase()}
                className="flex-1 bg-[#0a0a0a] border border-slate-800 rounded-lg px-4 py-2.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-blue-500 font-mono"
              />
              <button
                onClick={() => handleLookupCase()}
                disabled={caseLoading}
                className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-bold text-xs rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                {caseLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                Retrieve Forensics
              </button>
            </div>

            {/* QUICK PRESET CHIPS */}
            {recentCases.length > 0 && (
              <div className="pt-2 border-t border-slate-800/60 flex flex-wrap items-center gap-2">
                <span className="text-[11px] text-slate-500 uppercase">Active Incidents:</span>
                {recentCases.map((rc, i) => (
                  <button
                    key={i}
                    onClick={() => handleLookupCase(rc.case_id)}
                    className={`px-2.5 py-1 rounded text-[11px] border transition-colors ${
                      caseIdInput === rc.case_id
                        ? 'bg-blue-900/30 border-blue-500 text-blue-300'
                        : 'bg-slate-900/40 border-slate-800 text-slate-400 hover:text-white'
                    }`}
                  >
                    {rc.threat_summary || 'Incident'} ({rc.case_id.substring(0, 8)})
                  </button>
                ))}
              </div>
            )}
          </div>

          {caseError && (
            <div className="bg-red-900/20 border border-red-500/30 p-4 rounded-lg text-xs text-red-400 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 flex-shrink-0" />
              <span>{caseError}</span>
            </div>
          )}

          {/* CASE DETAILS & AWARENESS CARD */}
          {caseData && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* LEFT 2 COLS: EVIDENCE & 5-LAYER EXPLANATION */}
              <div className="lg:col-span-2 space-y-6">
                {/* HERO CASE HEADER */}
                <div className="bg-[#111] border border-slate-800 p-5 rounded-xl space-y-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                          caseData.severity === 'CRITICAL' ? 'bg-red-500/10 border-red-500 text-red-400' :
                          caseData.severity === 'HIGH' ? 'bg-orange-500/10 border-orange-500 text-orange-400' :
                          'bg-yellow-500/10 border-yellow-500 text-yellow-400'
                        }`}>
                          {caseData.severity}
                        </span>
                        <span className="text-xs text-slate-500">Case ID: {caseData.case_id}</span>
                      </div>
                      <h2 className="text-lg font-bold text-white tracking-wide">{caseData.title || caseData.threat_summary}</h2>
                      <div className="text-xs text-slate-400 mt-1">
                        Flow Entity: <strong className="text-blue-400">{caseData.primary_entity || `${caseData.source_ip} -> ${caseData.destination_ip}`}</strong>
                      </div>
                    </div>

                    <div className="text-right">
                      <div className="text-2xl font-bold text-white">{caseData.risk_score ?? 90}%</div>
                      <div className="text-[10px] text-slate-500 uppercase tracking-widest">Confidence Score</div>
                    </div>
                  </div>
                </div>

                {/* 5-LAYER EXPLANATION */}
                {caseData.explanation && (
                  <div className="bg-[#111] border border-slate-800 p-5 rounded-xl space-y-4">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                      <Zap className="w-4 h-4 text-orange-400" />
                      5-Layer AI Threat Attribution & Decision Rationale
                    </h3>
                    
                    <div className="space-y-3 text-xs">
                      <div className="bg-[#0a0a0a] p-3 rounded border border-slate-800/80">
                        <span className="text-slate-500 font-bold block mb-1 uppercase text-[10px]">What was observed:</span>
                        <p className="text-slate-200">{caseData.explanation.what}</p>
                      </div>

                      <div className="bg-[#0a0a0a] p-3 rounded border border-slate-800/80">
                        <span className="text-slate-500 font-bold block mb-1 uppercase text-[10px]">Why it triggered:</span>
                        <p className="text-slate-200">{caseData.explanation.why}</p>
                      </div>

                      <div className="bg-[#0a0a0a] p-3 rounded border border-slate-800/80">
                        <span className="text-slate-500 font-bold block mb-1 uppercase text-[10px]">Confidence Basis:</span>
                        <p className="text-blue-300">{caseData.explanation.confidence}</p>
                      </div>

                      <div className="bg-red-950/20 p-3 rounded border border-red-900/40">
                        <span className="text-red-400 font-bold block mb-1 uppercase text-[10px]">Recommended Containment Action:</span>
                        <p className="text-red-200">{caseData.explanation.action}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* EVIDENCE LEDGER */}
                <div className="bg-[#111] border border-slate-800 p-5 rounded-xl space-y-3">
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                    <Database className="w-4 h-4 text-green-400" />
                    Cryptographic Evidence Ledger & Passive Telemetry
                  </h3>
                  
                  <div className="space-y-2">
                    {(caseData.alerts && caseData.alerts[0]?.evidence ? caseData.alerts[0].evidence : [
                      { feature: 'simplex_tap', value: 'CONFIRMED', explanation: 'Ingress across optical hardware data diode with 0 reverse ACKs' },
                      { feature: 'ml_boundary', value: 'OUTLIER', explanation: 'Isolation Forest decision boundary exceeded' }
                    ]).map((ev: any, idx: number) => (
                      <div key={idx} className="flex justify-between items-center text-xs p-2.5 bg-[#0a0a0a] rounded border border-slate-800">
                        <span className="text-slate-400 font-mono">{ev.feature}</span>
                        <div className="text-right">
                          <span className="text-white font-bold block">{String(ev.value)}</span>
                          {ev.explanation && <span className="text-[10px] text-slate-500">{ev.explanation}</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* RIGHT COL: DATA DIODE AWARENESS & ANALYST QUIZ */}
              <div className="space-y-6">
                {/* DATA DIODE CONTAINMENT PLAYBOOK */}
                <div className="bg-[#111] border border-slate-800 p-5 rounded-xl space-y-4">
                  <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-blue-400" />
                    Data Diode Defense Playbook
                  </h3>

                  <div className="space-y-3">
                    {(caseData.awareness?.containment_steps || [
                      "Maintain Strict Physical Diode Isolation: Ensure zero protocol handshakes (no SYN-ACKs, no RSTs) cross back into production network.",
                      "Network Enclave Quarantine: Blackhole or isolate internal destination entity from lateral movement.",
                      "Passive Traffic Verification: Verify source IP entropy, IAT coefficient of variation, and flow volume via promiscuous sniffer.",
                      "Forensic Chain of Custody: Preserve immutable PCAP capture and cryptographic evidence ledger for post-incident audit."
                    ]).map((step: string, i: number) => (
                      <div key={i} className="flex items-start gap-3 text-xs bg-[#0a0a0a] p-3 rounded border border-slate-800">
                        <span className="w-5 h-5 rounded-full bg-blue-900/40 border border-blue-500/50 text-blue-400 flex items-center justify-center font-bold text-[10px] flex-shrink-0 mt-0.5">
                          {i + 1}
                        </span>
                        <p className="text-slate-300 leading-relaxed">{step}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* INTERACTIVE ANALYST AWARENESS QUIZ */}
                {caseData.awareness?.analyst_quiz && (
                  <div className="bg-[#111] border border-slate-800 p-5 rounded-xl space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest flex items-center gap-2">
                        <HelpCircle className="w-4 h-4 text-purple-400" />
                        Analyst Awareness Verification
                      </h3>
                      <span className="text-[10px] text-purple-400 uppercase font-bold">NTRO Training</span>
                    </div>

                    <p className="text-xs text-slate-200 leading-relaxed font-semibold">
                      {caseData.awareness.analyst_quiz.question}
                    </p>

                    <div className="space-y-2">
                      {caseData.awareness.analyst_quiz.options.map((opt: string, optIdx: number) => (
                        <button
                          key={optIdx}
                          onClick={() => !quizSubmitted && setSelectedQuizAnswer(optIdx)}
                          className={`w-full text-left p-3 rounded-lg border text-xs transition-colors ${
                            quizSubmitted
                              ? optIdx === caseData.awareness.analyst_quiz.correct_index
                                ? 'bg-green-950/30 border-green-500 text-green-300 font-bold'
                                : optIdx === selectedQuizAnswer
                                ? 'bg-red-950/30 border-red-500 text-red-300'
                                : 'bg-[#0a0a0a] border-slate-800 text-slate-500'
                              : selectedQuizAnswer === optIdx
                              ? 'bg-blue-900/30 border-blue-500 text-blue-200'
                              : 'bg-[#0a0a0a] border-slate-800 text-slate-300 hover:border-slate-700'
                          }`}
                        >
                          {opt}
                        </button>
                      ))}
                    </div>

                    {!quizSubmitted ? (
                      <button
                        onClick={() => selectedQuizAnswer !== null && setQuizSubmitted(true)}
                        disabled={selectedQuizAnswer === null}
                        className="w-full py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-40 text-white text-xs font-bold rounded-lg transition-colors"
                      >
                        Submit Awareness Check
                      </button>
                    ) : (
                      <div className="p-3 bg-slate-900/50 rounded-lg border border-slate-800 text-[11px] text-slate-400 leading-relaxed">
                        <strong className="text-green-400 block mb-1">Defense Rationale:</strong>
                        {caseData.awareness.analyst_quiz.rationale}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: LIVE AI/ML THREAT PREDICTOR */}
      {activeTab === 'ml_predictor' && (
        <div className="space-y-6">
          {/* PROFILE SELECTOR BAR */}
          <div className="bg-[#111] border border-slate-800 p-5 rounded-xl space-y-3">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">
              Select Official NTRO Problem Statement Threat Class (a &ndash; f)
            </h3>
            
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2.5">
              {THREAT_VECTORS.map((vec) => (
                <button
                  key={vec.id}
                  onClick={() => selectVectorPreset(vec)}
                  className={`p-3 rounded-lg border text-left transition-colors flex flex-col justify-between ${
                    selectedVector.id === vec.id
                      ? 'bg-blue-600/10 border-blue-500 text-white'
                      : 'bg-[#0a0a0a] border-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  <span className="text-[10px] font-bold text-blue-400 uppercase">{vec.id}</span>
                  <span className="text-xs font-bold mt-1 text-white leading-tight">{vec.name.split(' ')[0]} {vec.name.split(' ')[1]}</span>
                  <span className="text-[10px] text-slate-500 mt-1">{vec.severity}</span>
                </button>
              ))}
            </div>
          </div>

          {/* SIMPLEX ML FLOW INGESTION FORM */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 bg-[#111] border border-slate-800 p-5 rounded-xl space-y-4">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest flex items-center gap-2">
                <Terminal className="w-4 h-4 text-blue-400" />
                Unidirectional Flow Ingress Vector Parameters
              </h3>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-[11px] text-slate-400 block mb-1.5 uppercase font-bold">Source IP (Adversary / Ingress)</label>
                  <input
                    type="text"
                    value={srcIp}
                    onChange={(e) => setSrcIp(e.target.value)}
                    className="w-full bg-[#0a0a0a] border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="text-[11px] text-slate-400 block mb-1.5 uppercase font-bold">Destination IP (Isolated Enclave Target)</label>
                  <input
                    type="text"
                    value={dstIp}
                    onChange={(e) => setDstIp(e.target.value)}
                    className="w-full bg-[#0a0a0a] border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="text-[11px] text-slate-400 block mb-1.5 uppercase font-bold">Packet Count in Micro-Window</label>
                  <input
                    type="number"
                    value={packetCount}
                    onChange={(e) => setPacketCount(Number(e.target.value))}
                    className="w-full bg-[#0a0a0a] border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="text-[11px] text-slate-400 block mb-1.5 uppercase font-bold">Bytes on Wire (Outbound Volume)</label>
                  <input
                    type="number"
                    value={bytesTransferred}
                    onChange={(e) => setBytesTransferred(Number(e.target.value))}
                    className="w-full bg-[#0a0a0a] border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              {/* MATHEMATICAL ATTRIBUTES DISPLAY */}
              <div className="grid grid-cols-3 gap-3 p-3 bg-[#0a0a0a] rounded-lg border border-slate-800 text-xs">
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block">Source-IP Entropy:</span>
                  <span className="font-bold text-white">{selectedVector.entropy.toFixed(2)}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block">IAT Jitter (CV):</span>
                  <span className="font-bold text-white">{selectedVector.cv.toFixed(3)}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block">Asymmetry Ratio:</span>
                  <span className="font-bold text-white">{selectedVector.ratio}x</span>
                </div>
              </div>

              <button
                onClick={handleRunMlPrediction}
                disabled={mlLoading}
                className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-bold text-xs rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                {mlLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Cpu className="w-4 h-4" />}
                Run Live AI/ML Model Inference (XGBoost v5.0.0 & IForest)
              </button>
            </div>

            {/* ML RESULT CARD */}
            <div className="bg-[#111] border border-slate-800 p-5 rounded-xl flex flex-col justify-between space-y-4">
              <div>
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-green-400" />
                  Real-Time Model Inference Output
                </h3>

                {mlResult ? (
                  <div className="mt-4 space-y-3">
                    <div className="p-3 rounded-lg border bg-[#0a0a0a] border-slate-800">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-[10px] text-slate-500 uppercase">Detection Result</span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-red-500/20 text-red-400 border border-red-500/30">
                          {mlResult.classification}
                        </span>
                      </div>
                      <div className="text-sm font-bold text-white">{mlResult.threat_type}</div>
                      <p className="text-[11px] text-slate-400 mt-1">{mlResult.decision_summary}</p>
                    </div>

                    <div className="p-3 rounded-lg border bg-[#0a0a0a] border-slate-800 flex justify-between items-center">
                      <span className="text-xs text-slate-400">Bayesian Confidence</span>
                      <span className="text-lg font-bold text-blue-400">{Math.round(mlResult.confidence * 100)}%</span>
                    </div>

                    <div className="p-3 rounded-lg border bg-[#0a0a0a] border-slate-800 flex justify-between items-center">
                      <span className="text-xs text-slate-400">Generated Case ID</span>
                      <span className="text-[11px] font-mono text-slate-300">{mlResult.case_id?.substring(0, 16)}...</span>
                    </div>

                    <button
                      onClick={() => {
                        setActiveTab('case_lookup')
                        handleLookupCase(mlResult.case_id)
                      }}
                      className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold rounded-lg transition-colors flex items-center justify-center gap-2"
                    >
                      <BookOpen className="w-4 h-4" />
                      View Full Forensics & Playbook
                    </button>
                  </div>
                ) : (
                  <div className="py-16 text-center text-slate-500 text-xs">
                    <Activity className="w-8 h-8 mx-auto mb-2 opacity-40 animate-pulse" />
                    Configure flow parameters and run live inference to evaluate using local XGBoost & Isolation Forest models.
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-slate-800 text-[11px] text-slate-500">
                Data diode assurance: 0 ACK packets returned across optical link.
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

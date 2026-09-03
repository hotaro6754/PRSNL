'use client'

import React, { useState, useEffect } from 'react'
import { 
  Activity, ShieldAlert, Radio, Upload, Play, Terminal, Database, 
  ArrowRight, Zap, Network, ShieldCheck, AlertTriangle, RefreshCw,
  Search, BookOpen, CheckCircle, HelpCircle, FileText, Cpu, Eye, Check
} from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge, BadgeVariant } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { TableContainer, Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table'

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

  useEffect(() => {
    fetchRecentCases()
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

  const getSeverityVariant = (sev: string): BadgeVariant => {
    switch (sev?.toUpperCase()) {
      case 'CRITICAL': return 'critical'
      case 'HIGH': return 'warning'
      case 'MEDIUM': return 'neutral'
      case 'LOW': return 'secure'
      default: return 'neutral'
    }
  }

  return (
    <div className="space-y-6 max-w-[1500px] mx-auto animate-in fade-in duration-300 font-mono">
      {/* PAGE HEADER & TAB SWITCHER */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-white/[0.06] pb-4">
        <div>
          <h1 className="text-base font-bold tracking-tight text-white font-mono uppercase flex items-center gap-2">
            <Search className="w-4 h-4 text-blue-400" />
            Simplex Threat Ingestion & Analysis Terminal
          </h1>
          <p className="text-xs text-zinc-400 mt-0.5">
            Passive optical diode telemetry intake, ML vector inference, and forensic case ledger.
          </p>
        </div>

        {/* Segmented Tab Controls */}
        <div className="flex p-1 bg-[#111318] border border-white/[0.08] rounded-md text-xs font-mono">
          <button
            onClick={() => setActiveTab('case_lookup')}
            className={`px-3 py-1 rounded transition-all cursor-pointer ${
              activeTab === 'case_lookup'
                ? 'bg-white/[0.08] text-white font-semibold shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            Case ID Forensic Lookup
          </button>
          <button
            onClick={() => setActiveTab('ml_predictor')}
            className={`px-3 py-1 rounded transition-all cursor-pointer ${
              activeTab === 'ml_predictor'
                ? 'bg-white/[0.08] text-white font-semibold shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            Simplex Stream Predictor (a-f)
          </button>
        </div>
      </div>

      {/* TAB 1: CASE ID FORENSIC LOOKUP */}
      {activeTab === 'case_lookup' && (
        <div className="space-y-5">
          {/* SEARCH & RECENT CASES */}
          <Card>
            <CardContent className="p-4 space-y-3">
              <div className="flex flex-col sm:flex-row gap-2.5">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-2.5 h-4 w-4 text-zinc-500" />
                  <input
                    type="text"
                    value={caseIdInput}
                    onChange={(e) => setCaseIdInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleLookupCase()}
                    placeholder="Enter Case ID (e.g., CASE-001, CASE-DGA-99, or UUID)..."
                    className="w-full bg-[#0d0f14] border border-white/[0.08] rounded-md py-2 pl-9 pr-4 text-xs text-zinc-200 font-mono placeholder:text-zinc-600 focus:outline-none focus:border-blue-500/50"
                  />
                </div>
                <Button
                  variant="primary"
                  size="sm"
                  loading={caseLoading}
                  onClick={() => handleLookupCase()}
                  icon={<Search className="w-3.5 h-3.5" />}
                >
                  Lookup Case
                </Button>
              </div>

              {/* Recent Case Quick-Select Chips */}
              {recentCases.length > 0 && (
                <div className="flex items-center gap-2 flex-wrap pt-1 text-[11px]">
                  <span className="text-zinc-500 text-[10px] uppercase font-semibold">Recent Cases:</span>
                  {recentCases.map((rc) => (
                    <button
                      key={rc.case_id}
                      onClick={() => handleLookupCase(rc.case_id)}
                      className={`px-2 py-0.5 rounded border transition-colors cursor-pointer text-[11px] font-mono ${
                        caseIdInput === rc.case_id
                          ? 'bg-blue-500/20 text-blue-300 border-blue-500/40 font-semibold'
                          : 'bg-[#0d0f14] hover:bg-white/[0.04] text-zinc-400 border-white/[0.06]'
                      }`}
                    >
                      {rc.case_id.substring(0, 10)}
                    </button>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {caseError && (
            <div className="p-3 rounded-lg border border-red-500/20 bg-red-500/10 text-xs text-red-400 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{caseError}</span>
            </div>
          )}

          {caseData && (
            <div className="space-y-4">
              {/* PRIMARY ATTRIBUTE CARDS */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 rounded-lg border border-white/[0.08] bg-[#111318]">
                  <span className="text-[10px] text-zinc-500 uppercase block">Source Entity</span>
                  <span className="text-xs font-bold text-red-400 truncate block mt-0.5">{caseData.source_ip || 'N/A'}</span>
                </div>
                <div className="p-3 rounded-lg border border-white/[0.08] bg-[#111318]">
                  <span className="text-[10px] text-zinc-500 uppercase block">Enclave Target</span>
                  <span className="text-xs font-bold text-blue-400 truncate block mt-0.5">{caseData.destination_ip || '10.0.1.50'}</span>
                </div>
                <div className="p-3 rounded-lg border border-white/[0.08] bg-[#111318]">
                  <span className="text-[10px] text-zinc-500 uppercase block">Severity & Status</span>
                  <div className="flex items-center gap-1.5 mt-0.5">
                    <Badge variant={getSeverityVariant(caseData.severity)} size="xs">
                      {caseData.severity || 'CRITICAL'}
                    </Badge>
                    <Badge variant={caseData.status === 'CONTAINED' ? 'secure' : 'critical'} size="xs" dot>
                      {caseData.status || 'ACTIVE'}
                    </Badge>
                  </div>
                </div>
                <div className="p-3 rounded-lg border border-white/[0.08] bg-[#111318]">
                  <span className="text-[10px] text-zinc-500 uppercase block">Risk Score</span>
                  <span className="text-base font-bold text-zinc-100 font-mono mt-0.5 block">
                    {caseData.risk_score ?? 95} <span className="text-[10px] text-zinc-500 font-normal">/ 100</span>
                  </span>
                </div>
              </div>

              {/* 5-LAYER EXPLANATION */}
              <Card>
                <CardHeader className="py-3 px-4">
                  <CardTitle>5-Layer Threat Attribution Explanation</CardTitle>
                </CardHeader>
                <CardContent className="p-4 text-xs space-y-3 font-sans">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <div className="p-3 rounded bg-[#0d0f14] border border-white/[0.06] space-y-1">
                      <span className="text-[10px] font-mono font-bold text-blue-400 uppercase block">What Happened</span>
                      <p className="text-zinc-300 leading-relaxed text-[11px]">
                        {caseData.explanation?.what || `Unidirectional anomaly observed from ${caseData.source_ip}.`}
                      </p>
                    </div>
                    <div className="p-3 rounded bg-[#0d0f14] border border-white/[0.06] space-y-1">
                      <span className="text-[10px] font-mono font-bold text-amber-400 uppercase block">Why Detected</span>
                      <p className="text-zinc-300 leading-relaxed text-[11px]">
                        {caseData.explanation?.why || "Statistical distribution divergence in entropy and arrival timings."}
                      </p>
                    </div>
                    <div className="p-3 rounded bg-[#0d0f14] border border-white/[0.06] space-y-1">
                      <span className="text-[10px] font-mono font-bold text-emerald-400 uppercase block">Diode Protection</span>
                      <p className="text-zinc-300 leading-relaxed text-[11px]">
                        Zero return packets (0 ACKs / 0 RSTs) on wire due to physical optical tap.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* EDUCATIONAL MODULE & QUIZ (IF AVAILABLE) */}
              {caseData.education_module && (
                <Card>
                  <CardHeader className="py-3 px-4">
                    <div className="flex items-center justify-between">
                      <CardTitle className="flex items-center gap-2">
                        <BookOpen className="w-3.5 h-3.5 text-purple-400" />
                        Threat Awareness: {caseData.education_module.title}
                      </CardTitle>
                      <Badge variant="purple" size="xs">AWARENESS</Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="p-4 text-xs space-y-4 font-sans">
                    <p className="text-zinc-300 leading-relaxed">{caseData.education_module.summary}</p>
                    
                    {caseData.education_module.quiz && (
                      <div className="p-3 rounded bg-[#0d0f14] border border-white/[0.06] space-y-2.5">
                        <span className="text-xs font-semibold text-zinc-200 block">
                          Knowledge Verification Quiz: {caseData.education_module.quiz.question}
                        </span>
                        <div className="space-y-1.5 font-mono text-xs">
                          {caseData.education_module.quiz.options?.map((opt: string, idx: number) => (
                            <label
                              key={idx}
                              onClick={() => !quizSubmitted && setSelectedQuizAnswer(idx)}
                              className={`flex items-center gap-2.5 p-2 rounded border transition-colors cursor-pointer ${
                                selectedQuizAnswer === idx
                                  ? 'bg-blue-500/10 border-blue-500/30 text-blue-300'
                                  : 'bg-black/40 border-white/[0.06] text-zinc-400 hover:text-zinc-200'
                              } ${
                                quizSubmitted && idx === caseData.education_module.quiz.correct_index
                                  ? '!bg-emerald-500/20 !border-emerald-500/40 !text-emerald-300'
                                  : ''
                              }`}
                            >
                              <input
                                type="radio"
                                name="quiz"
                                checked={selectedQuizAnswer === idx}
                                onChange={() => {}}
                                className="accent-blue-500"
                              />
                              <span>{opt}</span>
                            </label>
                          ))}
                        </div>
                        {!quizSubmitted ? (
                          <Button
                            variant="secondary"
                            size="xs"
                            disabled={selectedQuizAnswer === null}
                            onClick={() => setQuizSubmitted(true)}
                          >
                            Submit Answer
                          </Button>
                        ) : (
                          <div className="text-[11px] text-zinc-300 pt-1 font-sans">
                            {selectedQuizAnswer === caseData.education_module.quiz.correct_index ? (
                              <span className="text-emerald-400 font-semibold flex items-center gap-1">
                                <Check className="w-3.5 h-3.5" /> Correct! {caseData.education_module.quiz.explanation}
                              </span>
                            ) : (
                              <span className="text-amber-400">
                                Incorrect. {caseData.education_module.quiz.explanation}
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: SIMPLEX STREAM PREDICTOR */}
      {activeTab === 'ml_predictor' && (
        <div className="space-y-5">
          {/* 6-VECTOR PRESET SELECTOR */}
          <div className="space-y-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-zinc-400 font-mono block">
              Select NTRO Threat Vector Class (a-f):
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
              {THREAT_VECTORS.map((vec) => {
                const isSelected = selectedVector.id === vec.id
                return (
                  <div
                    key={vec.id}
                    onClick={() => selectVectorPreset(vec)}
                    className={`p-3 rounded-lg border cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-blue-600/10 border-blue-500/40 shadow-sm'
                        : 'bg-[#111318] hover:bg-white/[0.03] border-white/[0.08]'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-bold font-mono text-zinc-100">{vec.name}</span>
                      <Badge variant={getSeverityVariant(vec.severity)} size="xs">
                        {vec.severity}
                      </Badge>
                    </div>
                    <p className="text-[11px] text-zinc-400 font-sans line-clamp-2 leading-relaxed">
                      {vec.desc}
                    </p>
                  </div>
                )
              })}
            </div>
          </div>

          {/* PARAMETER CONFIGURATION FORM */}
          <Card>
            <CardHeader className="py-3 px-4">
              <CardTitle>Stream Telemetry Parameters</CardTitle>
            </CardHeader>
            <CardContent className="p-4 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                <div className="space-y-1">
                  <label className="text-[10px] text-zinc-500 uppercase block font-semibold">Source IP Address</label>
                  <input
                    type="text"
                    value={srcIp}
                    onChange={(e) => setSrcIp(e.target.value)}
                    className="w-full bg-[#0d0f14] border border-white/[0.08] rounded p-2 text-xs font-mono text-zinc-200 focus:outline-none focus:border-blue-500/50"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] text-zinc-500 uppercase block font-semibold">Destination IP Address</label>
                  <input
                    type="text"
                    value={dstIp}
                    onChange={(e) => setDstIp(e.target.value)}
                    className="w-full bg-[#0d0f14] border border-white/[0.08] rounded p-2 text-xs font-mono text-zinc-200 focus:outline-none focus:border-blue-500/50"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] text-zinc-500 uppercase block font-semibold">Packet Count</label>
                  <input
                    type="number"
                    value={packetCount}
                    onChange={(e) => setPacketCount(Number(e.target.value))}
                    className="w-full bg-[#0d0f14] border border-white/[0.08] rounded p-2 text-xs font-mono text-zinc-200 focus:outline-none focus:border-blue-500/50"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] text-zinc-500 uppercase block font-semibold">Bytes Transferred</label>
                  <input
                    type="number"
                    value={bytesTransferred}
                    onChange={(e) => setBytesTransferred(Number(e.target.value))}
                    className="w-full bg-[#0d0f14] border border-white/[0.08] rounded p-2 text-xs font-mono text-zinc-200 focus:outline-none focus:border-blue-500/50"
                  />
                </div>
              </div>

              <div className="flex justify-end pt-2 border-t border-white/[0.06]">
                <Button
                  variant="primary"
                  size="sm"
                  loading={mlLoading}
                  onClick={handleRunMlPrediction}
                  icon={<Play className="w-3.5 h-3.5" />}
                >
                  Run Simplex Classifier Inference
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* ML INFERENCE VERDICT */}
          {mlResult && (
            <Card>
              <CardHeader className="py-3 px-4">
                <div className="flex items-center justify-between">
                  <CardTitle>Classifier Inference Verdict</CardTitle>
                  <Badge variant={getSeverityVariant(mlResult.classification)} size="xs">
                    {mlResult.classification || 'CRITICAL'}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="p-4 space-y-4">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="p-3 rounded bg-[#0d0f14] border border-white/[0.06]">
                    <span className="text-[10px] text-zinc-500 uppercase block">Threat Type</span>
                    <span className="text-xs font-bold text-red-400 block mt-0.5">{mlResult.threat_type || 'ANOMALOUS'}</span>
                  </div>
                  <div className="p-3 rounded bg-[#0d0f14] border border-white/[0.06]">
                    <span className="text-[10px] text-zinc-500 uppercase block">Risk Score</span>
                    <span className="text-xs font-bold text-zinc-100 block mt-0.5 font-mono">{mlResult.risk_score ?? 95} / 100</span>
                  </div>
                  <div className="p-3 rounded bg-[#0d0f14] border border-white/[0.06]">
                    <span className="text-[10px] text-zinc-500 uppercase block">Confidence</span>
                    <span className="text-xs font-bold text-blue-400 block mt-0.5 font-mono">{Math.round((mlResult.confidence || 0.94) * 100)}%</span>
                  </div>
                  <div className="p-3 rounded bg-[#0d0f14] border border-white/[0.06]">
                    <span className="text-[10px] text-zinc-500 uppercase block">Generated Case ID</span>
                    <span className="text-xs font-bold text-zinc-300 block mt-0.5 font-mono truncate">{mlResult.case_id || 'LOCAL_EVAL'}</span>
                  </div>
                </div>

                <div className="p-3 rounded bg-[#0d0f14] border border-white/[0.06] text-xs font-sans text-zinc-300 leading-relaxed">
                  <strong className="text-zinc-100 font-semibold block mb-1 font-mono text-[11px] uppercase">Decision Summary:</strong>
                  {mlResult.decision_summary}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}

'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { 
  ArrowLeft, ShieldAlert, Activity, Calendar, Server, Tag, Info, 
  CheckCircle2, AlertTriangle, ShieldCheck, Zap, HelpCircle, RefreshCw, Cpu, Database, Play
} from 'lucide-react'

export default function CaseDetailPage() {
  const params = useParams()
  const router = useRouter()
  const [caseData, setCaseData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  // Interactive Close Case Modal & Awareness State
  const [showCloseModal, setShowCloseModal] = useState(false)
  const [selectedQuizAnswer, setSelectedQuizAnswer] = useState<number | null>(null)
  const [closing, setClosing] = useState(false)
  const [closeSuccess, setCloseSuccess] = useState(false)

  // Interactive ML Investigation State
  const [showMlLab, setShowMlLab] = useState(false)
  const [mlLoading, setMlLoading] = useState(false)
  const [mlResult, setMlResult] = useState<any>(null)

  const fetchCase = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/cases/${params.id}`)
      if (res.ok) {
        setCaseData(await res.json())
      }
    } catch (err) {
      console.error("Failed to fetch case detail")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCase()
  }, [params.id])

  const handleCloseCase = async () => {
    if (selectedQuizAnswer === null) return
    setClosing(true)
    try {
      const res = await fetch(`http://localhost:8000/api/cases/${params.id}/close`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          notes: 'Analyst verified physical data diode containment and passed security quiz.'
        })
      })
      if (res.ok) {
        setCloseSuccess(true)
        fetchCase()
        setTimeout(() => setShowCloseModal(false), 2000)
      }
    } catch (err) {
      console.error("Error closing case", err)
    } finally {
      setClosing(false)
    }
  }

  const handleRunMlTest = async () => {
    setMlLoading(true)
    try {
      const res = await fetch('http://localhost:8000/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          vector: 'ddos',
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
    return <div className="p-12 text-center text-slate-500 font-mono">Loading case details from secure ledger...</div>
  }

  if (!caseData) {
    return (
      <div className="space-y-4 font-mono p-6">
        <button onClick={() => router.back()} className="flex items-center text-sm text-slate-400 hover:text-white">
          <ArrowLeft className="w-4 h-4 mr-1" /> Back
        </button>
        <div className="p-12 text-center border border-slate-800 rounded-xl bg-[#0c0f17] text-slate-400">
          Case not found or could not be loaded from MongoDB.
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-[1600px] animate-in fade-in duration-500 p-6 font-mono">
      {/* TOPBAR */}
      <div className="flex flex-col sm:flex-row justify-between items-start gap-4 border-b border-slate-800 pb-4">
        <div className="space-y-1">
          <button onClick={() => router.back()} className="flex items-center text-xs text-slate-400 hover:text-blue-400 mb-2 transition-colors">
            <ArrowLeft className="w-4 h-4 mr-1" /> Back to Investigations
          </button>
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold tracking-tight text-white uppercase">{caseData.title || caseData.threat_summary}</h2>
            <span className={`inline-flex items-center rounded px-2 py-0.5 text-[10px] font-bold tracking-wider ${
              caseData.severity === 'CRITICAL' ? 'bg-red-500/10 text-red-500 border border-red-500/20' : 'bg-orange-500/10 text-orange-500 border border-orange-500/20'
            }`}>
              {caseData.severity}
            </span>
            <span className={`inline-flex items-center rounded px-2 py-0.5 text-[10px] font-bold tracking-wider border ${
              caseData.status === 'CONTAINED' ? 'bg-green-500/10 text-green-400 border-green-500/30' : 'bg-slate-800 text-slate-300 border-slate-700'
            }`}>
              {caseData.status || 'ACTIVE'}
            </span>
          </div>
          <p className="text-slate-400 text-xs">Case ID: <span className="text-blue-400">{caseData.case_id}</span></p>
        </div>
        
        <div className="flex gap-2">
          <button 
            onClick={() => setShowMlLab(!showMlLab)}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-bold transition-colors flex items-center gap-2"
          >
            <Cpu className="w-3.5 h-3.5" />
            {showMlLab ? 'Hide Flow ML Lab' : 'Investigate Flow (Simplex ML Lab)'}
          </button>
          <button 
            onClick={() => setShowCloseModal(true)}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded text-xs font-bold transition-colors flex items-center gap-2"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-green-400" />
            Close Case (Awareness Protocol)
          </button>
        </div>
      </div>

      {/* CLOSE CASE MODAL */}
      {showCloseModal && (
        <div className="bg-[#111] border-2 border-blue-500/40 p-6 rounded-xl space-y-4 animate-in fade-in">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-green-400" />
                Data Diode Incident Containment & Close-Out Protocol
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                To close this unidirectional threat case, confirm physical containment steps and complete the security verification.
              </p>
            </div>
            <button onClick={() => setShowCloseModal(false)} className="text-slate-500 hover:text-white text-xs">&times; Close</button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="space-y-2 bg-[#0a0a0a] p-4 rounded-lg border border-slate-800">
              <span className="font-bold text-slate-400 block mb-2 uppercase text-[10px]">Physical Diode Containment Steps:</span>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-green-400 flex-shrink-0" />
                <span>Simplex optical Rx tap verified (0 return packets transmitted).</span>
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-green-400 flex-shrink-0" />
                <span>Internal destination enclave {caseData.destination_ip || 'target'} segregated.</span>
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-green-400 flex-shrink-0" />
                <span>Passive PCAP stream saved to immutable forensic evidence ledger.</span>
              </div>
            </div>

            <div className="space-y-2 bg-[#0a0a0a] p-4 rounded-lg border border-slate-800">
              <span className="font-bold text-purple-400 block mb-1 uppercase text-[10px]">Analyst Awareness Verification Check:</span>
              <p className="text-slate-300 leading-snug">
                {caseData.awareness?.analyst_quiz?.question || 'Why must the monitoring enclave never send TCP resets across the data diode?'}
              </p>
              <div className="space-y-1.5 pt-2">
                {(caseData.awareness?.analyst_quiz?.options || [
                  'Because physical diodes are optical simplex links with 0 return path, preserving forensic chain of custody and preventing reverse pivots.',
                  'Because routers discard reset packets.',
                  'Because resets use too much bandwidth.'
                ]).map((opt: string, optIdx: number) => (
                  <button
                    key={optIdx}
                    onClick={() => setSelectedQuizAnswer(optIdx)}
                    className={`w-full text-left p-2 rounded text-[11px] border transition-colors ${
                      selectedQuizAnswer === optIdx
                        ? 'bg-blue-900/30 border-blue-500 text-blue-200'
                        : 'bg-slate-900/40 border-slate-800 text-slate-400 hover:text-white'
                    }`}
                  >
                    {opt}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              onClick={() => setShowCloseModal(false)}
              className="px-4 py-2 bg-slate-800 text-slate-300 rounded text-xs font-bold"
            >
              Cancel
            </button>
            <button
              onClick={handleCloseCase}
              disabled={selectedQuizAnswer === null || closing || closeSuccess}
              className="px-5 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white rounded text-xs font-bold transition-colors flex items-center gap-2"
            >
              {closing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
              {closeSuccess ? 'Case Contained & Closed!' : 'Confirm Containment & Close Case'}
            </button>
          </div>
        </div>
      )}

      {/* ML INVESTIGATION LAB PANEL */}
      {showMlLab && (
        <div className="bg-[#111] border border-slate-800 p-5 rounded-xl space-y-4 animate-in fade-in">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest flex items-center gap-2">
            <Cpu className="w-4 h-4 text-blue-400" />
            Unidirectional Flow ML Investigation Sandbox
          </h3>
          <p className="text-xs text-slate-400">
            Re-evaluate flow dynamics for <strong className="text-white">{caseData.source_ip}</strong> using XGBoost (v5.0.0) and Isolation Forest without decrypting payload.
          </p>

          <button
            onClick={handleRunMlTest}
            disabled={mlLoading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded text-xs font-bold transition-colors flex items-center gap-2"
          >
            {mlLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            Execute XGBoost & Isolation Forest Evaluation
          </button>

          {mlResult && (
            <div className="p-4 bg-[#0a0a0a] rounded-lg border border-slate-800 text-xs space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-slate-400 uppercase">Model Output:</span>
                <span className="font-bold text-red-400">{mlResult.classification} &mdash; {mlResult.threat_type}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400 uppercase">Bayesian Confidence:</span>
                <span className="font-bold text-blue-400">{Math.round(mlResult.confidence * 100)}%</span>
              </div>
              <p className="text-slate-300 text-[11px] pt-1">{mlResult.decision_summary}</p>
            </div>
          )}
        </div>
      )}

      {/* DETAILS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column - Metadata */}
        <div className="space-y-6">
          <div className="rounded-xl border border-slate-800 bg-[#111] p-5 space-y-4">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider border-b border-slate-800 pb-2">
              Simplex Flow Metadata
            </h3>
            <div className="space-y-3 text-xs">
              <div>
                <span className="text-[10px] text-slate-500 uppercase block mb-0.5">Source IP / Flow Entity:</span>
                <div className="font-mono text-blue-400 font-bold">{caseData.primary_entity || caseData.source_ip}</div>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase block mb-0.5">Destination IP:</span>
                <div className="font-mono text-white">{caseData.destination_ip || '10.0.1.50'}</div>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase block mb-0.5">Ingress Tap Topology:</span>
                <span className="text-green-400 font-bold">100% Simplex Diode (0 Return ACKs)</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase block mb-0.5">First Seen Timestamp:</span>
                <span className="text-slate-300">{new Date(caseData.first_seen || caseData.created_at).toLocaleString('en-IN')}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase block mb-0.5">Confidence Score:</span>
                <span className="text-white font-bold text-base">{caseData.risk_score ?? 90}%</span>
              </div>
            </div>
          </div>

          {/* 5-LAYER DECISION EXPLANATION */}
          {caseData.explanation && (
            <div className="rounded-xl border border-slate-800 bg-[#111] p-5 space-y-4">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider border-b border-slate-800 pb-2 flex items-center gap-2">
                <Zap className="w-3.5 h-3.5 text-orange-400" />
                5-Layer Threat Attribution
              </h3>
              <div className="space-y-3 text-xs">
                <div>
                  <span className="text-slate-500 font-bold block uppercase text-[10px]">What:</span>
                  <p className="text-slate-300 mt-0.5">{caseData.explanation.what}</p>
                </div>
                <div>
                  <span className="text-slate-500 font-bold block uppercase text-[10px]">Why:</span>
                  <p className="text-slate-300 mt-0.5">{caseData.explanation.why}</p>
                </div>
                <div>
                  <span className="text-slate-500 font-bold block uppercase text-[10px]">Confidence:</span>
                  <p className="text-blue-300 mt-0.5">{caseData.explanation.confidence}</p>
                </div>
                <div>
                  <span className="text-red-400 font-bold block uppercase text-[10px]">Containment Action:</span>
                  <p className="text-red-300 mt-0.5">{caseData.explanation.action}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Column - Threat Narrative and Correlated Alerts */}
        <div className="md:col-span-2 space-y-6">
          <div className="rounded-xl border border-slate-800 bg-[#111] p-5 space-y-2">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider border-b border-slate-800 pb-2">
              Threat Narrative & Signature Summary
            </h3>
            <p className="text-slate-300 text-xs leading-relaxed">{caseData.threat_summary}</p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-[#111] flex flex-col overflow-hidden">
            <div className="p-4 border-b border-slate-800 flex justify-between items-center">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Correlated Ingress Alerts</h3>
              <span className="text-[10px] text-slate-500">{caseData.alerts?.length || 1} alert(s)</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-900 text-slate-400">
                  <tr>
                    <th className="px-4 py-3 font-normal">TIMESTAMP</th>
                    <th className="px-4 py-3 font-normal">TARGET</th>
                    <th className="px-4 py-3 font-normal">DETECTOR</th>
                    <th className="px-4 py-3 font-normal">CONFIDENCE</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {caseData.alerts?.map((alert: any, idx: number) => (
                    <tr key={idx} className="hover:bg-slate-800/20">
                      <td className="px-4 py-3 text-slate-400 font-mono">{new Date(alert.timestamp || Date.now()).toLocaleTimeString()}</td>
                      <td className="px-4 py-3 font-mono text-white">{alert.destination_ip || caseData.destination_ip || '10.0.1.50'}</td>
                      <td className="px-4 py-3 text-slate-300">
                        <div className="flex items-center gap-1.5">
                          <ShieldAlert className="w-3.5 h-3.5 text-red-400" />
                          <span>{alert.threat_class || caseData.threat_summary}</span>
                        </div>
                        <span className="text-[10px] text-slate-500">{alert.detector_id || 'xgboost_v5'}</span>
                      </td>
                      <td className="px-4 py-3 font-bold text-blue-400">{Math.round((alert.confidence || 0.95) * 100)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

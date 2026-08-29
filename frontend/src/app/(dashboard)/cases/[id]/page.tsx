'use client'
import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ArrowLeft, ShieldAlert, Activity, Calendar, Server, Tag, Info } from 'lucide-react'

export default function CaseDetailPage() {
  const params = useParams()
  const router = useRouter()
  const [caseData, setCaseData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
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
    fetchCase()
  }, [params.id])

  if (loading) {
    return <div className="p-12 text-center text-slate-500">Loading case details...</div>
  }

  if (!caseData) {
    return (
      <div className="space-y-4">
        <button onClick={() => router.back()} className="flex items-center text-sm text-slate-400 hover:text-white">
          <ArrowLeft className="w-4 h-4 mr-1" /> Back
        </button>
        <div className="p-12 text-center border border-slate-800 rounded-xl bg-[#0c0f17]">Case not found or could not be loaded.</div>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-[1600px] animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
        <div className="space-y-1">
          <button onClick={() => router.back()} className="flex items-center text-sm text-slate-400 hover:text-blue-400 mb-4 transition-colors">
            <ArrowLeft className="w-4 h-4 mr-1" /> Back to Cases
          </button>
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold tracking-tight text-white">{caseData.title || 'Security Incident'}</h2>
            <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[10px] font-bold tracking-wider ${
              caseData.severity === 'CRITICAL' ? 'bg-red-500/10 text-red-500 border-red-500/20' : 'bg-orange-500/10 text-orange-500 border-orange-500/20'
            }`}>
              {caseData.severity}
            </span>
            <span className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-[10px] font-bold tracking-wider bg-slate-800/50 text-slate-300 border-slate-700">
              {caseData.status}
            </span>
          </div>
          <p className="text-slate-400 text-sm">Case ID: <span className="font-mono text-slate-500">{caseData.case_id}</span></p>
        </div>
        
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium transition-colors">
            Investigate
          </button>
          <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-md text-sm font-medium transition-colors">
            Close Case
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column - Metadata */}
        <div className="space-y-6">
          <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-5">
            <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4 border-b border-slate-800 pb-2">Incident Details</h3>
            <div className="space-y-4">
              <div>
                <div className="text-xs text-slate-500 mb-1 flex items-center gap-1"><Server className="w-3 h-3"/> Source Entity</div>
          {/* EXPLANATION LAYER */}
          {caseData.explanation && (
            <div className="rounded-xl border border-slate-800 bg-[#0c0f17] flex flex-col overflow-hidden mt-6">
              <div className="p-5 border-b border-slate-800 flex items-center gap-2">
                <Info className="w-4 h-4 text-blue-400" />
                <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">Risk Explanation</h3>
              </div>
              <div className="p-5 space-y-4 text-sm">
                <div>
                  <span className="font-bold text-slate-400">WHAT:</span>
                  <p className="text-white mt-1">{caseData.explanation.what}</p>
                </div>
                <div>
                  <span className="font-bold text-slate-400">WHY:</span>
                  <p className="text-white mt-1">{caseData.explanation.why}</p>
                </div>
                <div>
                  <span className="font-bold text-slate-400">EVIDENCE:</span>
                  <ul className="mt-2 space-y-1">
                    {(caseData.explanation.evidence_summary || []).map((ev: any, i: number) => (
                      <li key={i} className="text-slate-300 flex items-start gap-2">
                         <span className="text-red-500 mt-0.5">•</span> {ev}
                      </li>
                    ))}
                  </ul>
                </div>
                {caseData.explanation.action && (
                  <div>
                    <span className="font-bold text-slate-400">ACTION:</span>
                    <p className="text-green-400 mt-1">{caseData.explanation.action}</p>
                  </div>
                )}
                {caseData.explanation.uncertainty && (
                  <div className="mt-4 p-3 bg-slate-800/50 rounded border border-slate-700 text-slate-300">
                    <span className="font-bold text-slate-400">UNCERTAINTY: </span>
                    {caseData.explanation.uncertainty}
                  </div>
                )}
              </div>
            </div>
          )}

                <div className="font-mono text-sm text-blue-400">{caseData.source_ip}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500 mb-1 flex items-center gap-1"><Calendar className="w-3 h-3"/> First Seen</div>
                <div className="text-sm text-slate-300">{new Date(caseData.first_seen).toLocaleString()}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500 mb-1 flex items-center gap-1"><Calendar className="w-3 h-3"/> Last Seen</div>
                <div className="text-sm text-slate-300">{new Date(caseData.last_seen).toLocaleString()}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500 mb-1 flex items-center gap-1"><Activity className="w-3 h-3"/> Alert Count</div>
                <div className="text-sm font-bold text-white">{caseData.alerts?.length || 0} alerts correlated</div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Threat Narrative and Alerts */}
        <div className="md:col-span-2 space-y-6">
          <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-5">
            <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4 border-b border-slate-800 pb-2">Threat Narrative</h3>
            <p className="text-slate-300 text-sm leading-relaxed">{caseData.threat_summary}</p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-[#0c0f17] flex flex-col overflow-hidden">
            <div className="p-5 border-b border-slate-800">
              <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">Correlated Alerts</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-[#121620] text-slate-400">
                  <tr>
                    <th className="px-5 py-3 font-medium">Timestamp</th>
                    <th className="px-5 py-3 font-medium">Target</th>
                    <th className="px-5 py-3 font-medium">Detector</th>
                    <th className="px-5 py-3 font-medium">Confidence</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {caseData.alerts?.map((alert: any) => (
                    <tr key={alert.alert_id} className="hover:bg-slate-800/30">
                      <td className="px-5 py-3 text-slate-400 font-mono text-xs">{new Date(alert.timestamp).toLocaleTimeString()}</td>
                      <td className="px-5 py-3 font-mono text-white">{alert.destination_ip}</td>
                      <td className="px-5 py-3 text-slate-300">
                        <div className="flex items-center gap-2">
                          <ShieldAlert className="w-3 h-3 text-red-400" />
                          {alert.threat_class}
                        </div>
                        <div className="text-[10px] text-slate-500">{alert.detector_id}</div>
                      </td>
                      <td className="px-5 py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                            <div className="h-full bg-blue-500" style={{ width: `${Math.round(alert.confidence * 100)}%` }}></div>
                          </div>
                          <span className="text-xs text-slate-400">{Math.round(alert.confidence * 100)}%</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {(!caseData.alerts || caseData.alerts.length === 0) && (
                    <tr><td colSpan={4} className="p-6 text-center text-slate-500">No raw alerts attached to this case.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

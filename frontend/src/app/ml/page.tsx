'use client'
import { useEffect, useState } from 'react'
import { Zap, Shield, GitBranch, Cpu, Database } from 'lucide-react'

export default function MLIntelligencePage() {
  const [mlData, setMlData] = useState<any>(null)
  const [models, setModels] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [mlRes, modelsRes] = await Promise.all([
          fetch('http://localhost:8000/health/ml'),
          fetch('http://localhost:8000/api/models')
        ])
        if (mlRes.ok) setMlData(await mlRes.json())
        if (modelsRes.ok) setModels(await modelsRes.json())
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading) return <div className="p-12 text-slate-500 text-center">Loading ML model registry...</div>

  return (
    <div className="space-y-6 max-w-[1600px] animate-in fade-in duration-500">
      <div>
        <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Zap className="w-6 h-6 text-purple-500" />
          ML Intelligence Hub
        </h2>
        <p className="text-sm text-slate-400">Manage, inspect, and monitor active machine learning models enforcing network security.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* XGBoost Active Models */}
        <div className="rounded-xl border border-purple-500/20 bg-[#0c0f17] overflow-hidden">
          <div className="p-4 border-b border-purple-500/20 bg-purple-500/5">
            <h3 className="font-semibold text-purple-400 flex items-center gap-2">XGBoost Supervised Classification</h3>
          </div>
          <div className="p-5">
            <div className="space-y-6">
              <div>
                <div className="flex items-center gap-2 mb-2 text-sm font-medium text-slate-300">
                  <GitBranch className="w-4 h-4 text-green-400" />
                  Production Slot
                </div>
                {mlData?.xgb_supervised?.production ? (
                  <div className="p-3 bg-[#121620] rounded border border-slate-800 text-sm">
                    <div className="flex justify-between mb-1"><span className="text-slate-500">Version</span><span className="font-mono text-white">{mlData.xgb_supervised.production.version}</span></div>
                    <div className="flex justify-between mb-1"><span className="text-slate-500">F1 Score</span><span className="font-mono text-white">{(mlData.xgb_supervised.production.metrics?.f1_score || 0).toFixed(4)}</span></div>
                    <div className="flex justify-between"><span className="text-slate-500">Artifact</span><span className="font-mono text-xs text-blue-400 truncate max-w-[200px]">{mlData.xgb_supervised.production.artifact_uri}</span></div>
                  </div>
                ) : <div className="text-sm text-slate-500 italic">No model promoted to production.</div>}
              </div>
              
              <div>
                <div className="flex items-center gap-2 mb-2 text-sm font-medium text-slate-300">
                  <GitBranch className="w-4 h-4 text-yellow-400" />
                  Canary Slot
                </div>
                {mlData?.xgb_supervised?.canary ? (
                  <div className="p-3 bg-[#121620] rounded border border-slate-800 text-sm">
                    <div className="flex justify-between mb-1"><span className="text-slate-500">Version</span><span className="font-mono text-white">{mlData.xgb_supervised.canary.version}</span></div>
                  </div>
                ) : <div className="text-sm text-slate-500 italic">No canary model active.</div>}
              </div>
            </div>
          </div>
        </div>

        {/* Isolation Forest Active Models */}
        <div className="rounded-xl border border-blue-500/20 bg-[#0c0f17] overflow-hidden">
          <div className="p-4 border-b border-blue-500/20 bg-blue-500/5">
            <h3 className="font-semibold text-blue-400 flex items-center gap-2">Isolation Forest Anomaly Detection</h3>
          </div>
          <div className="p-5">
            <div className="space-y-6">
              <div>
                <div className="flex items-center gap-2 mb-2 text-sm font-medium text-slate-300">
                  <GitBranch className="w-4 h-4 text-green-400" />
                  Production Slot
                </div>
                {mlData?.iforest_anomaly?.production ? (
                  <div className="p-3 bg-[#121620] rounded border border-slate-800 text-sm">
                    <div className="flex justify-between mb-1"><span className="text-slate-500">Version</span><span className="font-mono text-white">{mlData.iforest_anomaly.production.version}</span></div>
                    <div className="flex justify-between mb-1"><span className="text-slate-500">Precision</span><span className="font-mono text-white">{(mlData.iforest_anomaly.production.metrics?.precision || 0).toFixed(4)}</span></div>
                    <div className="flex justify-between"><span className="text-slate-500">Artifact</span><span className="font-mono text-xs text-blue-400 truncate max-w-[200px]">{mlData.iforest_anomaly.production.artifact_uri}</span></div>
                  </div>
                ) : <div className="text-sm text-slate-500 italic">No model promoted to production.</div>}
              </div>
              
              <div>
                <div className="flex items-center gap-2 mb-2 text-sm font-medium text-slate-300">
                  <GitBranch className="w-4 h-4 text-yellow-400" />
                  Canary Slot
                </div>
                {mlData?.iforest_anomaly?.canary ? (
                  <div className="p-3 bg-[#121620] rounded border border-slate-800 text-sm">
                    <div className="flex justify-between mb-1"><span className="text-slate-500">Version</span><span className="font-mono text-white">{mlData.iforest_anomaly.canary.version}</span></div>
                  </div>
                ) : <div className="text-sm text-slate-500 italic">No canary model active.</div>}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-slate-800 bg-[#0c0f17] overflow-hidden">
        <div className="p-4 border-b border-slate-800 bg-[#121620] flex items-center justify-between">
          <h3 className="font-semibold text-white flex items-center gap-2"><Database className="w-4 h-4 text-slate-400"/> Model Registry History</h3>
          <span className="text-xs text-slate-500">{models.length} registered artifacts</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-[#121620] text-slate-400">
              <tr>
                <th className="px-6 py-3 font-medium">Model ID</th>
                <th className="px-6 py-3 font-medium">Version</th>
                <th className="px-6 py-3 font-medium">Stage</th>
                <th className="px-6 py-3 font-medium">F1 Score</th>
                <th className="px-6 py-3 font-medium">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {models.length === 0 ? (
                <tr><td colSpan={5} className="p-8 text-center text-slate-500">No models in registry.</td></tr>
              ) : models.map((m: any, i: number) => (
                <tr key={i} className="hover:bg-slate-800/30">
                  <td className="px-6 py-3 font-mono text-white">{m.model_id}</td>
                  <td className="px-6 py-3 font-mono text-blue-400">{m.version}</td>
                  <td className="px-6 py-3">
                    <span className={`inline-flex rounded px-2 py-0.5 text-xs font-bold ${m.stage === 'PRODUCTION' ? 'bg-green-500/20 text-green-400' : m.stage === 'CANARY' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-slate-800 text-slate-400'}`}>
                      {m.stage}
                    </span>
                  </td>
                  <td className="px-6 py-3 text-slate-300">{(m.metrics?.f1_score || 0).toFixed(4)}</td>
                  <td className="px-6 py-3 text-slate-400 text-xs">{new Date(m.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

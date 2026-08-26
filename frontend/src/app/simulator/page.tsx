'use client'
import { useState } from 'react'
import { Skull, Target, Zap, Activity } from 'lucide-react'

export default function SimulatorPage() {
  const [loading, setLoading] = useState<string | null>(null)
  const [status, setStatus] = useState<{type: string, msg: string} | null>(null)

  const triggerAttack = async (type: string) => {
    setLoading(type)
    setStatus(null)
    try {
      const res = await fetch(`http://localhost:8000/api/simulate/${type}`, { method: 'POST' })
      if (res.ok) {
        setStatus({ type: 'success', msg: `Successfully launched ${type} simulation against internal sensor.` })
      } else {
        setStatus({ type: 'error', msg: `Failed to trigger ${type}: ${res.statusText}` })
      }
    } catch (err) {
      setStatus({ type: 'error', msg: `Network error reaching backend simulator.` })
    } finally {
      setLoading(null)
    }
  }

  return (
    <div className="space-y-6 max-w-[1200px] animate-in fade-in duration-500">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Attack Simulator</h2>
        <p className="text-sm text-slate-400">Generate real internal network traffic to validate sensor health and ML pipelines.</p>
      </div>

      {status && (
        <div className={`p-4 rounded-md border ${status.type === 'success' ? 'bg-green-500/10 border-green-500/20 text-green-400' : 'bg-red-500/10 border-red-500/20 text-red-400'}`}>
          {status.msg}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        
        {/* Port Scan */}
        <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-6 flex flex-col items-start gap-4">
          <div className="p-3 bg-blue-500/10 rounded-lg">
            <Target className="w-6 h-6 text-blue-500" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Aggressive Port Scan</h3>
            <p className="text-sm text-slate-400 mt-1">Simulates a rapid sequential connection attempt across 150 ports against the Zeek sensor.</p>
          </div>
          <button 
            onClick={() => triggerAttack('port_scan')}
            disabled={loading !== null}
            className="mt-auto w-full py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-md text-sm font-medium transition-colors"
          >
            {loading === 'port_scan' ? 'Executing...' : 'Trigger Port Scan'}
          </button>
        </div>

        {/* Brute Force */}
        <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-6 flex flex-col items-start gap-4">
          <div className="p-3 bg-orange-500/10 rounded-lg">
            <Skull className="w-6 h-6 text-orange-500" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">SSH Brute Force</h3>
            <p className="text-sm text-slate-400 mt-1">Generates rapid bursts of failed authentication attempts against Port 22 to test deterministic detectors.</p>
          </div>
          <button 
            onClick={() => triggerAttack('brute_force')}
            disabled={loading !== null}
            className="mt-auto w-full py-2 bg-orange-600 hover:bg-orange-700 disabled:opacity-50 text-white rounded-md text-sm font-medium transition-colors"
          >
            {loading === 'brute_force' ? 'Executing...' : 'Trigger Brute Force'}
          </button>
        </div>

        {/* DGA */}
        <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-6 flex flex-col items-start gap-4">
          <div className="p-3 bg-purple-500/10 rounded-lg">
            <Activity className="w-6 h-6 text-purple-500" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">DGA Beaconing</h3>
            <p className="text-sm text-slate-400 mt-1">Simulates high-entropy DNS queries to test Domain Generation Algorithm detection.</p>
          </div>
          <button 
            onClick={() => triggerAttack('dga')}
            disabled={loading !== null}
            className="mt-auto w-full py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white rounded-md text-sm font-medium transition-colors"
          >
            {loading === 'dga' ? 'Executing...' : 'Trigger DGA Payload'}
          </button>
        </div>

      </div>

      <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-6 mt-8">
        <h3 className="text-md font-semibold text-white mb-2 flex items-center gap-2">
          <Zap className="w-4 h-4 text-yellow-400" />
          How this works
        </h3>
        <p className="text-sm text-slate-400 leading-relaxed">
          Unlike simulated UI dashboards, these buttons do not inject fake data into the database. 
          Instead, they instruct the backend API to open raw TCP/UDP sockets and transmit malicious patterns 
          directly into the Zeek sensor container on the Docker network. The sensor observes the raw traffic, 
          forwards it to Redpanda, and the standard NDR detection pipeline processes it identically to external threats.
        </p>
      </div>
    </div>
  )
}

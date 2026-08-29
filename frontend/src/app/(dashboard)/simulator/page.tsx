'use client'
import { useState } from 'react'
import { Skull, Target, Zap, Activity, Mail, MessageSquare, QrCode, Wifi } from 'lucide-react'

const ATTACKS = [
  {
    type: 'port_scan', name: 'Aggressive Port Scan', icon: Target, color: 'blue',
    desc: 'Simulates rapid sequential connection attempts across 150 ports against the Zeek sensor.',
  },
  {
    type: 'brute_force', name: 'SSH Brute Force', icon: Skull, color: 'orange',
    desc: 'Generates rapid bursts of failed authentication attempts against Port 22.',
  },
  {
    type: 'dga', name: 'DGA Beaconing', icon: Activity, color: 'purple',
    desc: 'Simulates high-entropy DNS queries to test Domain Generation Algorithm detection.',
  },
  {
    type: 'uni_directional', name: 'Uni-directional IP Tunnel', icon: Wifi, color: 'red',
    desc: 'Simulates SYN flood with uni-directional flows (no SYN-ACK) to blackholed IPs.',
  },
  {
    type: 'qr', name: 'QR Quishing Attack', icon: QrCode, color: 'amber',
    desc: 'Injects a malicious QR payload containing a phishing URL for credential theft.',
  },
  {
    type: 'sms', name: 'SMS Smishing Blast', icon: MessageSquare, color: 'green',
    desc: 'Fires an SMS phishing payload with fake bank/logistics social engineering.',
  },
  {
    type: 'email', name: 'Email Phishing Payload', icon: Mail, color: 'indigo',
    desc: 'Pushes a Business Email Compromise (BEC) wire-transfer phishing email.',
  },
]

export default function ActionCenterPage() {
  const [loading, setLoading] = useState<string | null>(null)
  const [results, setResults] = useState<{type: string, msg: string, attack: string}[]>([])

  const triggerAttack = async (type: string) => {
    setLoading(type)
    try {
      const res = await fetch(`http://localhost:8000/api/simulate/${type}`, { method: 'POST' })
      if (res.ok) {
        setResults(prev => [{ type: 'success', msg: `${type.replace(/_/g, ' ').toUpperCase()} triggered successfully. Check Live Threats for real-time detection.`, attack: type }, ...prev].slice(0, 10))
      } else {
        setResults(prev => [{ type: 'error', msg: `Failed: ${res.statusText}`, attack: type }, ...prev].slice(0, 10))
      }
    } catch {
      setResults(prev => [{ type: 'error', msg: 'Network error reaching backend.', attack: type }, ...prev].slice(0, 10))
    } finally {
      setLoading(null)
    }
  }

  const getColor = (c: string) => {
    const map: Record<string, string> = {
      blue: 'bg-blue-600 hover:bg-blue-700', orange: 'bg-orange-600 hover:bg-orange-700',
      purple: 'bg-purple-600 hover:bg-purple-700', red: 'bg-red-600 hover:bg-red-700',
      amber: 'bg-amber-600 hover:bg-amber-700', green: 'bg-green-600 hover:bg-green-700',
      indigo: 'bg-indigo-600 hover:bg-indigo-700',
    }
    return map[c] || 'bg-blue-600 hover:bg-blue-700'
  }
  const getIconBg = (c: string) => {
    const map: Record<string, string> = {
      blue: 'bg-blue-500/10 text-blue-500', orange: 'bg-orange-500/10 text-orange-500',
      purple: 'bg-purple-500/10 text-purple-500', red: 'bg-red-500/10 text-red-500',
      amber: 'bg-amber-500/10 text-amber-500', green: 'bg-green-500/10 text-green-500',
      indigo: 'bg-indigo-500/10 text-indigo-500',
    }
    return map[c] || 'bg-blue-500/10 text-blue-500'
  }

  return (
    <div className="space-y-6 max-w-[1400px] animate-in fade-in duration-500 p-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Action Center</h2>
        <p className="text-sm text-slate-400">Launch real attack simulations against the CyberOS sensor network. Detections appear in Live Threats.</p>
      </div>

      {/* Attack execution log */}
      {results.length > 0 && (
        <div className="space-y-2">
          {results.slice(0, 3).map((r, i) => (
            <div key={i} className={`p-3 rounded-md border text-sm ${r.type === 'success' ? 'bg-green-500/10 border-green-500/20 text-green-400' : 'bg-red-500/10 border-red-500/20 text-red-400'}`}>
              {r.msg}
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
        {ATTACKS.map((atk) => {
          const Icon = atk.icon
          return (
            <div key={atk.type} className="rounded-xl border border-slate-800 bg-[#0c0f17] p-5 flex flex-col items-start gap-3">
              <div className={`p-3 rounded-lg ${getIconBg(atk.color)}`}>
                <Icon className="w-6 h-6" />
              </div>
              <div className="flex-1">
                <h3 className="text-base font-semibold text-white">{atk.name}</h3>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">{atk.desc}</p>
              </div>
              <button
                onClick={() => triggerAttack(atk.type)}
                disabled={loading !== null}
                className={`w-full py-2 ${getColor(atk.color)} disabled:opacity-50 text-white rounded-md text-sm font-medium transition-colors`}
              >
                {loading === atk.type ? 'Executing...' : `Launch ${atk.name.split(' ')[0]}`}
              </button>
            </div>
          )
        })}
      </div>

      <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-6">
        <h3 className="text-md font-semibold text-white mb-2 flex items-center gap-2">
          <Zap className="w-4 h-4 text-yellow-400" />
          How this works
        </h3>
        <p className="text-sm text-slate-400 leading-relaxed">
          Unlike simulated UI dashboards, these buttons do not inject fake data into the database.
          Instead, they instruct the backend API to open raw TCP/UDP sockets and transmit malicious patterns
          directly into the Zeek sensor container on the Docker network. The sensor observes the raw traffic,
          forwards it to Redpanda, and the standard CyberOS detection pipeline processes it identically to external threats.
          Results appear in real-time on the <strong className="text-white">Live Threats</strong> page via WebSocket.
        </p>
      </div>
    </div>
  )
}

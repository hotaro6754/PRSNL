'use client'
import { useState, useEffect } from 'react'
import { Skull, Target, Zap, Activity, Wifi, Radio, Upload, Play, CheckCircle2, Shield, RefreshCw } from 'lucide-react'

const ATTACKS = [
  {
    type: 'uni_directional', name: 'Unidirectional SYN Flood', icon: Wifi, color: 'red',
    kali: 'hping3 -S -p 80 --flood',
    desc: 'Fires high-rate simplex SYN packets to blackholed targets with 0 SYN-ACK return packets.',
  },
  {
    type: 'port_scan', name: 'Simplex Reconnaissance Scan', icon: Target, color: 'blue',
    kali: 'nmap -sS -Pn -p 1-150',
    desc: 'Simulates rapid sequential port probing (1-150) without waiting for response handshakes.',
  },
  {
    type: 'dga', name: 'Covert DGA & DNS Beaconing', icon: Activity, color: 'purple',
    kali: 'dnscat2 / iodine covert channel',
    desc: 'Transmits high-entropy domain queries to test covert channel and DGA detection over gateway.',
  },
  {
    type: 'brute_force', name: 'Edge Service Brute Force', icon: Skull, color: 'orange',
    kali: 'hydra -l admin -P wordlist ssh',
    desc: 'Fires rapid bursts of authentication attempts directed into isolated service ports.',
  },
]

const PCAP_SAMPLES = [
  { name: 'syn_flood.pcap', label: 'Volumetric SYN Flood', category: 'SIMPLEX_DDOS', size: '55.9 KB' },
  { name: 'real_port_scan.pcap', label: 'Real Port Scan', category: 'PORT_SCAN', size: '2.8 KB' },
  { name: 'dns_tunnel.pcap', label: 'DNS Covert Tunnel', category: 'DNS_EXFILTRATION', size: '3.1 KB' },
  { name: 'rigid_beacon.pcap', label: 'C2 Rigid Heartbeat', category: 'C2_BEACON', size: '764 B' },
  { name: 'udp_flood.pcap', label: 'UDP Simplex Flood', category: 'SIMPLEX_DDOS', size: '543 KB' },
  { name: 'stealth_scan.pcap', label: 'Stealth Slow Scan', category: 'PORT_SCAN', size: '2.8 KB' },
]

export default function ActionCenterPage() {
  const [loading, setLoading] = useState<string | null>(null)
  const [results, setResults] = useState<{type: string, msg: string, attack: string}[]>([])
  const [snifferStats, setSnifferStats] = useState<any>({ is_running: false, packets_captured: 0, bytes_captured: 0, interface: 'default' })
  const [uploading, setUploading] = useState(false)

  const fetchSniffer = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/network/sniffer/status')
      if (res.ok) setSnifferStats(await res.json())
    } catch {}
  }

  useEffect(() => {
    fetchSniffer()
    const interval = setInterval(fetchSniffer, 3000)
    return () => clearInterval(interval)
  }, [])

  const triggerAttack = async (type: string) => {
    setLoading(type)
    try {
      const res = await fetch(`http://localhost:8000/api/simulate/${type}`, { method: 'POST' })
      if (res.ok) {
        setResults(prev => [{ type: 'success', msg: `${type.replace(/_/g, ' ').toUpperCase()} triggered. Raw packets transmitted on wire. Check Live Threats.`, attack: type }, ...prev].slice(0, 8))
      } else {
        setResults(prev => [{ type: 'error', msg: `Failed: ${res.statusText}`, attack: type }, ...prev].slice(0, 8))
      }
    } catch {
      setResults(prev => [{ type: 'error', msg: 'Network error reaching backend.', attack: type }, ...prev].slice(0, 8))
    } finally {
      setLoading(null)
    }
  }

  const triggerPcapReplay = async (sampleName: string) => {
    setLoading(sampleName)
    try {
      const res = await fetch(`http://localhost:8000/api/network/pcap/replay/${sampleName}`, { method: 'POST' })
      if (res.ok) {
        setResults(prev => [{ type: 'success', msg: `PCAP Replay Started: ${sampleName}. Genuine raw packet stream entering Scapy/Zeek pipeline.`, attack: sampleName }, ...prev].slice(0, 8))
      } else {
        setResults(prev => [{ type: 'error', msg: `Failed replaying ${sampleName}: ${res.statusText}`, attack: sampleName }, ...prev].slice(0, 8))
      }
    } catch {
      setResults(prev => [{ type: 'error', msg: 'Network error reaching backend.', attack: sampleName }, ...prev].slice(0, 8))
    } finally {
      setLoading(null)
    }
  }

  const toggleSniffer = async () => {
    try {
      if (snifferStats.is_running) {
        const res = await fetch('http://localhost:8000/api/network/sniffer/stop', { method: 'POST' })
        if (res.ok) {
          const data = await res.json()
          setResults(prev => [{ type: 'success', msg: `Live Sniffer Stopped. Captured ${data.packets_captured} packets (${data.bytes_captured} bytes).`, attack: 'sniffer' }, ...prev])
        }
      } else {
        const res = await fetch('http://localhost:8000/api/network/sniffer/start', { method: 'POST' })
        if (res.ok) {
          setResults(prev => [{ type: 'success', msg: 'Passive Line-Rate Network Sniffer Started. Promiscuously capturing real IP traffic.', attack: 'sniffer' }, ...prev])
        }
      }
      fetchSniffer()
    } catch {
      setResults(prev => [{ type: 'error', msg: 'Network error toggling sniffer.', attack: 'sniffer' }, ...prev])
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)
    try {
      const res = await fetch('http://localhost:8000/api/network/pcap/upload', {
        method: 'POST',
        body: formData,
      })
      if (res.ok) {
        const data = await res.json()
        setResults(prev => [{ type: 'success', msg: `Custom PCAP Uploaded (${data.filename} - ${data.size_bytes} bytes). Processing through ML engine...`, attack: file.name }, ...prev])
      } else {
        setResults(prev => [{ type: 'error', msg: `Upload failed: ${res.statusText}`, attack: file.name }, ...prev])
      }
    } catch {
      setResults(prev => [{ type: 'error', msg: 'Failed uploading PCAP file.', attack: file.name }, ...prev])
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  return (
    <div className="space-y-6 max-w-[1400px] animate-in fade-in duration-500 p-6">
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-3">
            <Radio className="w-6 h-6 text-blue-500 animate-pulse" />
            NTRO Unidirectional Traffic Replay & Ingestion Lab
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Replay authentic defense PCAPs, manage passive line-rate network sniffing, or inject raw socket attack streams across the data diode tap.
          </p>
        </div>
      </div>

      {/* SNIFFER CONTROL PANEL */}
      <div className="bg-[#111] border border-slate-800 p-5 rounded-xl flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className={`p-3 rounded-xl border ${snifferStats.is_running ? 'bg-green-500/10 border-green-500/30 text-green-400' : 'bg-slate-800/40 border-slate-700 text-slate-400'}`}>
            <Radio className={`w-6 h-6 ${snifferStats.is_running ? 'animate-pulse' : ''}`} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-white uppercase tracking-wider">Passive Live Network Sniffer</span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${snifferStats.is_running ? 'bg-green-500 text-black' : 'bg-slate-800 text-slate-300'}`}>
                {snifferStats.is_running ? 'PROMISCUOUS RX ACTIVE' : 'STANDBY'}
              </span>
            </div>
            <div className="text-xs text-slate-400 mt-1 flex gap-4">
              <span>Captured Packets: <strong className="text-white">{snifferStats.packets_captured}</strong></span>
              <span>Captured Bytes: <strong className="text-white">{snifferStats.bytes_captured}</strong></span>
              <span>Active Flows: <strong className="text-white">{snifferStats.active_flows_tracked}</strong></span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={toggleSniffer}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-colors ${
              snifferStats.is_running 
                ? 'bg-red-600 hover:bg-red-700 text-white' 
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            {snifferStats.is_running ? 'Stop Passive Capture' : 'Start Passive Interface Capture'}
          </button>
        </div>
      </div>

      {/* EXECUTION LOG */}
      {results.length > 0 && (
        <div className="space-y-2">
          {results.slice(0, 3).map((r, i) => (
            <div key={i} className={`p-3 rounded-md border text-xs font-mono flex items-center justify-between ${r.type === 'success' ? 'bg-green-500/10 border-green-500/20 text-green-400' : 'bg-red-500/10 border-red-500/20 text-red-400'}`}>
              <span>{r.msg}</span>
              <span className="text-[10px] text-slate-500">{new Date().toLocaleTimeString()}</span>
            </div>
          ))}
        </div>
      )}

      {/* SECTION 1: GENUINE PCAP REPLAY LAB */}
      <div className="space-y-3">
        <div className="flex justify-between items-center border-b border-slate-800 pb-2">
          <h3 className="text-sm font-bold tracking-wider text-slate-300 uppercase flex items-center gap-2">
            <Play className="w-4 h-4 text-green-400" />
            Authentic Attack PCAP Replay Pipeline (Zero-Simulation)
          </h3>
          <span className="text-xs text-slate-500">Real Scapy Parser &bull; Full Directional Feature Extraction</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {PCAP_SAMPLES.map((sample) => (
            <div key={sample.name} className="bg-[#0c0f17] border border-slate-800 p-4 rounded-lg flex flex-col justify-between hover:border-slate-700 transition-colors">
              <div>
                <div className="flex justify-between items-start mb-2">
                  <span className="px-2 py-0.5 bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[10px] font-mono rounded">
                    {sample.category}
                  </span>
                  <span className="text-[11px] text-slate-500 font-mono">{sample.size}</span>
                </div>
                <h4 className="text-sm font-semibold text-white font-mono">{sample.name}</h4>
                <p className="text-xs text-slate-400 mt-1">{sample.label}</p>
              </div>
              <button
                onClick={() => triggerPcapReplay(sample.name)}
                disabled={loading !== null}
                className="mt-4 w-full py-1.5 bg-slate-800 hover:bg-blue-600 disabled:opacity-50 text-white rounded text-xs font-semibold font-mono transition-colors flex items-center justify-center gap-1.5"
              >
                {loading === sample.name ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
                Replay Raw PCAP
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* SECTION 2: CUSTOM PCAP FILE UPLOAD */}
      <div className="bg-[#0c0f17] border border-dashed border-slate-800 hover:border-blue-500/50 p-6 rounded-xl transition-colors text-center">
        <Upload className="w-8 h-8 text-blue-400 mx-auto mb-2" />
        <h4 className="text-sm font-bold text-white">Upload External PCAP Capture for Live Inspection</h4>
        <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
          Upload any recorded network capture (.pcap, .pcapng). The Scapy ingestion adapter will extract directional flow windows and run real-time inference without mock data.
        </p>
        <label className="mt-4 inline-block cursor-pointer px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-lg transition-colors">
          {uploading ? 'Parsing & Streaming PCAP...' : 'Select .PCAP File'}
          <input type="file" accept=".pcap,.pcapng,.cap" onChange={handleFileUpload} disabled={uploading} className="hidden" />
        </label>
      </div>

      {/* SECTION 3: RAW SOCKET TEST INJECTOR */}
      <div className="space-y-3">
        <div className="border-b border-slate-800 pb-2">
          <h3 className="text-sm font-bold tracking-wider text-slate-300 uppercase flex items-center gap-2">
            <Zap className="w-4 h-4 text-yellow-400" />
            Active Raw Socket Simplex Probing Lab
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {ATTACKS.map((atk) => {
            const Icon = atk.icon
            return (
              <div key={atk.type} className="rounded-xl border border-slate-800 bg-[#0c0f17] p-4 flex flex-col justify-between">
                <div>
                  <div className="p-2.5 rounded-lg bg-slate-800/40 w-fit mb-3 text-slate-300">
                    <Icon className="w-5 h-5 text-blue-400" />
                  </div>
                  <h4 className="text-sm font-semibold text-white">{atk.name}</h4>
                  <div className="my-1.5">
                    <span className="text-[10px] font-mono bg-purple-950/40 text-purple-300 border border-purple-800/60 px-1.5 py-0.5 rounded">
                      Kali: {atk.kali}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1 leading-relaxed">{atk.desc}</p>
                </div>
                <button
                  onClick={() => triggerAttack(atk.type)}
                  disabled={loading !== null}
                  className="mt-4 w-full py-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded text-xs font-semibold transition-colors"
                >
                  {loading === atk.type ? 'Injecting Sockets...' : 'Inject Stream'}
                </button>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

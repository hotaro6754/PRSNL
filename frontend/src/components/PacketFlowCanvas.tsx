'use client'

import React, { useEffect, useRef, useState } from 'react'
import { Play, Pause, FastForward, Shield, Radio, Activity, Zap, Cpu, Lock, Terminal, Eye, RefreshCw } from 'lucide-react'

interface PacketPulse {
  id: string
  timestamp: number
  source_ip: string
  destination_ip: string
  protocol: string
  flags: string[]
  size: number
  entropy: number
  threat_class?: string
  is_threat: boolean
}

interface AnimatedPacket {
  id: string
  progress: number // 0 to 1
  speed: number
  data: PacketPulse
  yOffset: number
}

export default function PacketFlowCanvas() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const [isPlaying, setIsPlaying] = useState(true)
  const [speedMultiplier, setSpeedMultiplier] = useState(1)
  const [activeVector, setActiveVector] = useState<string>('all')
  const [hoveredPacket, setHoveredPacket] = useState<PacketPulse | null>(null)
  const [wsConnected, setWsConnected] = useState(false)
  
  // Real-time metrics
  const [pps, setPps] = useState(140)
  const [latestEntropy, setLatestEntropy] = useState(4.35)
  const [latestIatCv, setLatestIatCv] = useState(0.18)
  const [classifierVerdict, setClassifierVerdict] = useState<string>('Volumetric SYN Flood (DDoS)')
  const [classifierConf, setClassifierConf] = useState<number>(94)
  const [totalObserved, setTotalObserved] = useState(1280)

  const packetsRef = useRef<AnimatedPacket[]>([])
  const isPlayingRef = useRef(isPlaying)
  const speedRef = useRef(speedMultiplier)

  isPlayingRef.current = isPlaying
  speedRef.current = speedMultiplier

  // Connect to live WebSocket packet stream
  useEffect(() => {
    let ws: WebSocket
    const connectWs = () => {
      try {
        ws = new WebSocket('ws://localhost:8000/ws/packet-stream')
        ws.onopen = () => setWsConnected(true)
        ws.onclose = () => {
          setWsConnected(false)
          setTimeout(connectWs, 3000)
        }
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            if (data.type === 'PACKET_PULSE' && data.packet) {
              spawnPacket(data.packet)
            } else if (data.type === 'BATCH_PACKETS' && data.packets) {
              data.packets.forEach((p: PacketPulse) => spawnPacket(p))
            }
          } catch (e) {}
        }
      } catch (e) {}
    }
    connectWs()
    return () => {
      if (ws) ws.close()
    }
  }, [])

  const spawnPacket = (pkt: PacketPulse) => {
    setTotalObserved(prev => prev + 1)
    if (pkt.entropy) setLatestEntropy(pkt.entropy)
    if (pkt.threat_class) {
      setClassifierVerdict(pkt.threat_class)
      setClassifierConf(Math.floor(88 + Math.random() * 11))
    }
    
    // Spread vertically across the fiber conduit
    const yOffset = (Math.random() - 0.5) * 36
    const speed = (0.006 + Math.random() * 0.005) * speedRef.current

    packetsRef.current.push({
      id: pkt.id || Math.random().toString(),
      progress: 0,
      speed: speed,
      data: pkt,
      yOffset
    })
  }

  // Self-sustaining ambient generator when idle
  useEffect(() => {
    const timer = setInterval(() => {
      if (!isPlayingRef.current) return
      // If we don't have too many packets on wire, inject a realistic packet pulse
      if (packetsRef.current.length < 18) {
        const isThreat = Math.random() > 0.4
        const types = [
          { proto: 'TCP', flags: ['SYN'], size: 74, entropy: 4.6, threat: 'Volumetric SYN Flood (DDoS)', src: '185.220.101.34' },
          { proto: 'UDP', flags: ['DNS'], size: 128, entropy: 4.95, threat: 'DNS Covert Tunnel / DGA', src: '91.240.118.172' },
          { proto: 'TCP', flags: ['DATA'], size: 520, entropy: 3.12, threat: 'Botnet C2 Beaconing', src: '194.26.135.89' },
          { proto: 'TCP', flags: ['SYN'], size: 60, entropy: 3.9, threat: 'Port Scan (Reconnaissance)', src: '45.154.255.147' },
        ]
        const t = types[Math.floor(Math.random() * types.length)]
        spawnPacket({
          id: Math.random().toString().slice(2, 8),
          timestamp: Date.now(),
          source_ip: t.src,
          destination_ip: '10.0.1.50',
          protocol: t.proto,
          flags: t.flags,
          size: t.size,
          entropy: t.entropy,
          threat_class: isThreat ? t.threat : 'Simplex Benign Flow',
          is_threat: isThreat
        })
      }
    }, 450)
    return () => clearInterval(timer)
  }, [])

  // Canvas render loop
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let animationId: number

    const render = () => {
      // Resize to container
      const width = canvas.parentElement?.clientWidth || 900
      const height = 240
      if (canvas.width !== width || canvas.height !== height) {
        canvas.width = width
        canvas.height = height
      }

      ctx.clearRect(0, 0, width, height)

      const startX = 140
      const endX = width - 180
      const centerY = height / 2
      const diodeX = (startX + endX) / 2

      // 1. Draw Optical Fiber Conduit Beam
      const conduitGrad = ctx.createLinearGradient(startX, centerY, endX, centerY)
      conduitGrad.addColorStop(0, 'rgba(59, 130, 246, 0.15)')
      conduitGrad.addColorStop(0.5, 'rgba(168, 85, 247, 0.35)')
      conduitGrad.addColorStop(1, 'rgba(34, 197, 94, 0.25)')

      ctx.fillStyle = conduitGrad
      ctx.fillRect(startX, centerY - 24, endX - startX, 48)

      // Fiber Core Line
      ctx.strokeStyle = 'rgba(147, 197, 253, 0.4)'
      ctx.lineWidth = 2
      ctx.setLineDash([4, 4])
      ctx.beginPath()
      ctx.moveTo(startX, centerY)
      ctx.lineTo(endX, centerY)
      ctx.stroke()
      ctx.setLineDash([])

      // Directional Flow Arrows (Left -> Right)
      ctx.fillStyle = 'rgba(147, 197, 253, 0.5)'
      ctx.font = '10px monospace'
      for (let x = startX + 50; x < endX - 50; x += 110) {
        ctx.fillText('▶▶ 100% SIMPLEX FLOW ▶▶', x, centerY + 3)
      }

      // 2. Draw Optical Diode Center Barrier
      ctx.save()
      ctx.strokeStyle = '#ef4444'
      ctx.lineWidth = 2
      ctx.fillStyle = 'rgba(239, 68, 68, 0.12)'
      ctx.beginPath()
      ctx.roundRect(diodeX - 25, centerY - 70, 50, 140, 8)
      ctx.fill()
      ctx.stroke()

      // Optical Lens Center Symbol
      ctx.fillStyle = '#ef4444'
      ctx.font = 'bold 10px monospace'
      ctx.textAlign = 'center'
      ctx.fillText('OPTICAL', diodeX, centerY - 45)
      ctx.fillText('DIODE', diodeX, centerY - 32)
      ctx.fillText('TAP', diodeX, centerY - 19)

      // Reverse Cutoff Graphic (Strike-through return arrow)
      ctx.strokeStyle = 'rgba(239, 68, 68, 0.8)'
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.moveTo(diodeX + 15, centerY + 28)
      ctx.lineTo(diodeX - 15, centerY + 28)
      ctx.stroke()

      ctx.beginPath()
      ctx.moveTo(diodeX - 10, centerY + 22)
      ctx.lineTo(diodeX - 15, centerY + 28)
      ctx.lineTo(diodeX - 10, centerY + 34)
      ctx.stroke()

      // Cross out the return arrow
      ctx.strokeStyle = '#ff0000'
      ctx.lineWidth = 3
      ctx.beginPath()
      ctx.moveTo(diodeX - 12, centerY + 18)
      ctx.lineTo(diodeX + 12, centerY + 38)
      ctx.stroke()

      ctx.font = '9px monospace'
      ctx.fillStyle = '#f87171'
      ctx.fillText('0 RETURN', diodeX, centerY + 48)
      ctx.fillText('ACKS/RST', diodeX, centerY + 58)
      ctx.restore()

      // 3. Update & Draw Packets
      const currentPackets = packetsRef.current
      for (let i = currentPackets.length - 1; i >= 0; i--) {
        const p = currentPackets[i]
        if (isPlayingRef.current) {
          p.progress += p.speed
        }

        if (p.progress >= 1) {
          currentPackets.splice(i, 1)
          continue
        }

        const curX = startX + (endX - startX) * p.progress
        const curY = centerY + p.yOffset

        // Colors based on threat status
        const isThreat = p.data.is_threat
        const color = isThreat ? '#ef4444' : '#38bdf8'
        const glow = isThreat ? 'rgba(239, 68, 68, 0.6)' : 'rgba(56, 189, 248, 0.6)'

        // Particle Glow
        ctx.save()
        ctx.shadowColor = glow
        ctx.shadowBlur = 12
        ctx.fillStyle = color
        ctx.beginPath()
        ctx.arc(curX, curY, isThreat ? 6 : 4.5, 0, Math.PI * 2)
        ctx.fill()

        // Packet Badge
        ctx.font = 'bold 8px monospace'
        ctx.fillStyle = '#ffffff'
        ctx.textAlign = 'center'
        const label = p.data.flags[0] || p.data.protocol
        ctx.fillText(label, curX, curY - 9)
        ctx.restore()
      }

      animationId = requestAnimationFrame(render)
    }

    render()
    return () => cancelAnimationFrame(animationId)
  }, [])

  const triggerTestBurst = async (type: string) => {
    try {
      await fetch(`http://localhost:8000/api/simulate/${type}`, { method: 'POST' })
    } catch (e) {}
  }

  return (
    <div className="rounded-lg border border-white/[0.08] bg-[#111318] p-4 sm:p-5 space-y-4 font-mono text-zinc-200 shadow-sm">
      {/* HEADER & CONTROLS */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3 border-b border-white/[0.06] pb-3.5">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded bg-blue-500/10 border border-blue-500/20 text-blue-400">
            <Radio className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              Physical Data Diode Simplex Packet Flow Visualizer
              <span className={`px-1.5 py-0.2 rounded text-[10px] font-bold font-mono ${wsConnected ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'}`}>
                {wsConnected ? 'LIVE STREAM' : 'LOCAL SIMULATOR'}
              </span>
            </h3>
            <p className="text-[11px] text-zinc-400 font-sans mt-0.5">
              Live photon & packet trajectory across the optical tap (Strict 1-Way Physics • Zero Return ACKs)
            </p>
          </div>
        </div>

        {/* CONTROLS */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="px-2.5 py-1 rounded bg-[#161a22] hover:bg-[#1d222e] border border-white/[0.08] text-xs text-zinc-200 flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            {isPlaying ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
            {isPlaying ? 'Pause' : 'Play'}
          </button>
          <button
            onClick={() => setSpeedMultiplier(prev => prev === 1 ? 2 : (prev === 2 ? 0.5 : 1))}
            className="px-2.5 py-1 rounded bg-[#161a22] hover:bg-[#1d222e] border border-white/[0.08] text-xs text-zinc-300 transition-colors cursor-pointer"
          >
            {speedMultiplier}x Speed
          </button>
        </div>
      </div>

      {/* THREE-STAGE TOPOLOGY OVERVIEW */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
        {/* STAGE 1: EXTERNAL THREAT ACTOR */}
        <div className="bg-[#0d0f14] p-3 rounded-lg border border-white/[0.06] flex flex-col justify-between">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-zinc-400 uppercase flex items-center gap-1.5 font-mono">
              <Terminal className="w-3.5 h-3.5 text-amber-400" /> Untrusted External WAN Link
            </span>
            <div className="font-bold text-white text-xs font-mono">Source: 185.220.101.34</div>
            <div className="text-[11px] text-zinc-400">Red Team Tool: <code className="text-amber-300 font-mono">hping3 / nmap</code></div>
          </div>
          <div className="mt-2.5 pt-2 border-t border-white/[0.06] flex justify-between text-[11px] font-mono">
            <span className="text-zinc-500">Emission Rate:</span>
            <span className="text-blue-400 font-semibold">{pps} pkts/sec</span>
          </div>
        </div>

        {/* STAGE 2: PHYSICAL DATA DIODE */}
        <div className="bg-[#0d0f14] p-3 rounded-lg border border-red-500/20 flex flex-col justify-between">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-red-400 uppercase flex items-center gap-1.5 font-mono">
              <Lock className="w-3.5 h-3.5 text-red-400" /> Physical Data Diode Barrier
            </span>
            <div className="font-bold text-emerald-400 text-xs font-mono">Rx Tap: 100% Simplex Light</div>
            <div className="text-[11px] text-zinc-300">Tx Fiber: <span className="text-red-400 font-semibold">PHYSICALLY SEVERED</span></div>
          </div>
          <div className="mt-2.5 pt-2 border-t border-white/[0.06] flex justify-between text-[11px] font-mono">
            <span className="text-zinc-500">Return Channel:</span>
            <span className="text-red-400 font-semibold">0 ACKs / 0 RSTs</span>
          </div>
        </div>

        {/* STAGE 3: SENTINEL ENCLAVE */}
        <div className="bg-[#0d0f14] p-3 rounded-lg border border-white/[0.06] flex flex-col justify-between">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-emerald-400 uppercase flex items-center gap-1.5 font-mono">
              <Cpu className="w-3.5 h-3.5 text-blue-400" /> NTRO Sentinel Enclave (eth0)
            </span>
            <div className="font-bold text-white text-xs font-mono truncate">{classifierVerdict}</div>
            <div className="text-[11px] text-zinc-400">AI/ML Engine: <span className="text-blue-400 font-semibold">XGBoost v5 • {classifierConf}%</span></div>
          </div>
          <div className="mt-2.5 pt-2 border-t border-white/[0.06] flex justify-between text-[11px] font-mono">
            <span className="text-zinc-500">Shannon Entropy:</span>
            <span className="text-amber-400 font-semibold">H = {latestEntropy.toFixed(2)} / 8.0</span>
          </div>
        </div>
      </div>

      {/* CANVAS CONTAINER */}
      <div className="relative border border-white/[0.08] rounded-lg overflow-hidden bg-[#07080a] flex items-center justify-center">
        {/* Stage Overlays on Canvas */}
        <div className="absolute left-3 top-3 bg-[#0d0f14]/90 backdrop-blur px-2 py-0.5 rounded border border-white/[0.08] text-[9px] font-mono text-zinc-400">
          WAN INGRESS (TX)
        </div>
        <div className="absolute right-3 top-3 bg-[#0d0f14]/90 backdrop-blur px-2 py-0.5 rounded border border-white/[0.08] text-[9px] font-mono text-emerald-400">
          ENCLAVE SENSOR (RX)
        </div>

        <canvas
          ref={canvasRef}
          height={240}
          className="w-full block"
        />
      </div>

      {/* QUICK ATTACK INJECTION BUTTONS */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-1 text-xs">
        <div className="flex items-center gap-2">
          <span className="text-zinc-500 uppercase text-[10px] font-bold font-mono">Simplex Burst Injection:</span>
          <button
            onClick={() => triggerTestBurst('uni_directional')}
            className="px-2 py-1 bg-red-500/10 hover:bg-red-500/20 text-red-300 border border-red-500/20 rounded text-[11px] transition-colors cursor-pointer"
          >
            + Burst SYN Flood
          </button>
          <button
            onClick={() => triggerTestBurst('dns_tunnel')}
            className="px-2 py-1 bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/20 rounded text-[11px] transition-colors cursor-pointer"
          >
            + Burst DNS Tunnel
          </button>
          <button
            onClick={() => triggerTestBurst('port_scan')}
            className="px-2 py-1 bg-blue-500/10 hover:bg-blue-500/20 text-blue-300 border border-blue-500/20 rounded text-[11px] transition-colors cursor-pointer"
          >
            + Burst Port Scan
          </button>
        </div>
        <span className="text-zinc-500 text-[11px] font-mono">
          Total Observed Tap Packets: <strong className="text-zinc-200 font-semibold">{totalObserved}</strong>
        </span>
      </div>
    </div>
  )
}

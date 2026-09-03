'use client'

import React, { useEffect, useRef, useState } from 'react'
import { 
  Play, Pause, FastForward, Shield, Radio, Activity, Zap, Cpu, Lock, 
  Terminal, Eye, RefreshCw, Layers, Sliders, Waves, ArrowRight, AlertTriangle, CheckCircle2
} from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'

interface PhotonPulse {
  id: string
  progress: number // 0 to 1
  speed: number
  wavelength: 1310 | 1550
  amplitude: number
  frequency: number
  phase: number
  isThreat: boolean
  vectorName: string
  sourceIp: string
  destIp: string
  packetSize: number
  yLane: number // -1, 0, 1
}

export default function PacketFlowCanvas() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const [isPlaying, setIsPlaying] = useState(true)
  const [speedMultiplier, setSpeedMultiplier] = useState(1)
  const [selectedWavelength, setSelectedWavelength] = useState<1310 | 1550>(1310)
  const [activeVector, setActiveVector] = useState<string>('all')
  const [wsConnected, setWsConnected] = useState(false)
  
  // Real-time physical metrics
  const [txPower, setTxPower] = useState('+2.4 dBm')
  const [rxPower, setRxPower] = useState('-3.1 dBm')
  const [isolationDb, setIsolationDb] = useState('> 78.4 dB')
  const [photonCount, setPhotonCount] = useState(14820)
  const [reverseAcks, setReverseAcks] = useState(0)
  const [activeThreatDesc, setActiveThreatDesc] = useState('Benign Simplex Baseline Flow')

  const photonsRef = useRef<PhotonPulse[]>([])
  const isPlayingRef = useRef(isPlaying)
  const speedRef = useRef(speedMultiplier)
  const animFrameRef = useRef<number>(0)

  isPlayingRef.current = isPlaying
  speedRef.current = speedMultiplier

  // Spawn photon wave-packet into the optical guide
  const spawnPhoton = (isThreat = false, vector = 'Simplex Benign Flow', src = '185.220.101.34') => {
    setPhotonCount(prev => prev + 1)
    if (isThreat) {
      setActiveThreatDesc(vector)
    }

    const lanes = [-12, -4, 4, 12]
    const yLane = lanes[Math.floor(Math.random() * lanes.length)]
    
    photonsRef.current.push({
      id: Math.random().toString(),
      progress: 0,
      speed: (0.0045 + Math.random() * 0.003) * speedRef.current,
      wavelength: isThreat ? 1550 : 1310,
      amplitude: isThreat ? 14 : 9,
      frequency: isThreat ? 0.35 : 0.22,
      phase: Math.random() * Math.PI * 2,
      isThreat,
      vectorName: vector,
      sourceIp: src,
      destIp: '10.0.1.50',
      packetSize: isThreat ? 512 : 74,
      yLane
    })
  }

  // Attack Burst Injectors
  const triggerAttack = (vectorType: 'syn' | 'c2' | 'dns' | 'exfil') => {
    if (vectorType === 'syn') {
      for (let i = 0; i < 8; i++) {
        setTimeout(() => spawnPhoton(true, 'Volumetric SYN Flood (Vector a)', '45.154.255.147'), i * 80)
      }
    } else if (vectorType === 'c2') {
      for (let i = 0; i < 4; i++) {
        setTimeout(() => spawnPhoton(true, 'Botnet C2 Periodic Beacon (Vector b)', '91.240.118.172'), i * 250)
      }
    } else if (vectorType === 'dns') {
      for (let i = 0; i < 6; i++) {
        setTimeout(() => spawnPhoton(true, 'DNS Covert Tunnel / DGA (Vector c)', '194.26.135.89'), i * 120)
      }
    } else if (vectorType === 'exfil') {
      for (let i = 0; i < 12; i++) {
        setTimeout(() => spawnPhoton(true, 'Asymmetric Exfiltration (Vector f)', '185.220.101.34'), i * 50)
      }
    }
  }

  // Background ambient photon generator
  useEffect(() => {
    const timer = setInterval(() => {
      if (!isPlayingRef.current) return
      if (photonsRef.current.length < 16) {
        const isAnomaly = Math.random() > 0.65
        const threatClasses = [
          { name: 'Volumetric SYN Flood (Vector a)', src: '45.154.255.147' },
          { name: 'Botnet C2 Periodic Beacon (Vector b)', src: '91.240.118.172' },
          { name: 'DNS Covert Tunnel (Vector c)', src: '194.26.135.89' },
          { name: 'Asymmetric Exfiltration (Vector f)', src: '185.220.101.34' }
        ]
        const sample = threatClasses[Math.floor(Math.random() * threatClasses.length)]
        spawnPhoton(isAnomaly, isAnomaly ? sample.name : 'Simplex Benign Flow', isAnomaly ? sample.src : '192.168.1.105')
      }
    }, 380)
    return () => clearInterval(timer)
  }, [])

  // Canvas High-Precision Physics Render Loop
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let t = 0

    const render = () => {
      t += 0.05
      const width = canvas.parentElement?.clientWidth || 980
      const height = 240

      if (canvas.width !== width || canvas.height !== height) {
        canvas.width = width
        canvas.height = height
      }

      ctx.clearRect(0, 0, width, height)

      const startX = 140
      const endX = width - 150
      const centerY = 110
      const diodeX = (startX + endX) / 2

      // ==========================================
      // 1. SILICA OPTICAL FIBER CORE & CLADDING GUIDE
      // ==========================================
      
      // Upper & Lower Cladding Boundary Reflections
      const fiberH = 52
      const topY = centerY - fiberH / 2
      const botY = centerY + fiberH / 2

      // Subtle silica glass conduit background
      const conduitGrad = ctx.createLinearGradient(startX, centerY, endX, centerY)
      conduitGrad.addColorStop(0, 'rgba(59, 130, 246, 0.08)')
      conduitGrad.addColorStop(0.48, 'rgba(59, 130, 246, 0.14)')
      conduitGrad.addColorStop(0.52, 'rgba(16, 185, 129, 0.14)')
      conduitGrad.addColorStop(1, 'rgba(16, 185, 129, 0.08)')
      
      ctx.fillStyle = conduitGrad
      ctx.fillRect(startX, topY, endX - startX, fiberH)

      // Cladding Borders (Total Internal Reflection mirrors)
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)'
      ctx.lineWidth = 1
      ctx.beginPath()
      ctx.moveTo(startX, topY)
      ctx.lineTo(endX, topY)
      ctx.moveTo(startX, botY)
      ctx.lineTo(endX, botY)
      ctx.stroke()

      // Central Optical Waveguide Core Line
      ctx.strokeStyle = 'rgba(59, 130, 246, 0.25)'
      ctx.lineWidth = 1
      ctx.setLineDash([4, 6])
      ctx.beginPath()
      ctx.moveTo(startX, centerY)
      ctx.lineTo(endX, centerY)
      ctx.stroke()
      ctx.setLineDash([])

      // Refraction Index Label
      ctx.fillStyle = 'rgba(255, 255, 255, 0.3)'
      ctx.font = '9px monospace'
      ctx.fillText('CORE: n₁ = 1.468 (SILICA WAVEGUIDE)', startX + 10, topY - 5)
      ctx.fillText('CLADDING: n₂ = 1.463', endX - 120, topY - 5)

      // ==========================================
      // 2. SEVERED RETURN FIBER STRAND (PHYSICAL PROOF)
      // ==========================================
      const retY = centerY + 65
      
      // Right returning fiber (coming from Enclave)
      ctx.strokeStyle = 'rgba(239, 68, 68, 0.4)'
      ctx.lineWidth = 1.5
      ctx.beginPath()
      ctx.moveTo(endX, retY)
      ctx.lineTo(diodeX + 35, retY)
      ctx.stroke()

      // Physical Air Gap (Cut Fiber)
      ctx.save()
      ctx.strokeStyle = '#ef4444'
      ctx.lineWidth = 2
      // Severed end face
      ctx.beginPath()
      ctx.arc(diodeX + 35, retY, 3, 0, Math.PI * 2)
      ctx.stroke()
      
      // Cut / Air Gap Bracket
      ctx.setLineDash([2, 3])
      ctx.strokeStyle = 'rgba(239, 68, 68, 0.6)'
      ctx.beginPath()
      ctx.moveTo(diodeX - 35, retY)
      ctx.lineTo(diodeX + 35, retY)
      ctx.stroke()
      ctx.setLineDash([])

      // Left returning fiber (going nowhere)
      ctx.strokeStyle = 'rgba(239, 68, 68, 0.2)'
      ctx.beginPath()
      ctx.arc(diodeX - 35, retY, 3, 0, Math.PI * 2)
      ctx.moveTo(diodeX - 35, retY)
      ctx.lineTo(startX, retY)
      ctx.stroke()

      // Physical Break Notification
      ctx.fillStyle = '#f87171'
      ctx.font = 'bold 9px monospace'
      ctx.textAlign = 'center'
      ctx.fillText('⚡ PHYSICAL RETURN FIBER STRAND SEVERED (40mm AIR GAP)', diodeX, retY + 14)
      ctx.font = '8px monospace'
      ctx.fillStyle = 'rgba(239, 68, 68, 0.7)'
      ctx.fillText('0 TX LASER DIODE IN ENCLAVE • ZERO RETURN ACKs / RSTs IMPOSSIBLE', diodeX, retY + 25)
      ctx.restore()

      // ==========================================
      // 3. FARADAY OPTICAL ISOLATOR CRYSTAL BARRIER
      // ==========================================
      ctx.save()
      const barrierW = 64
      const barrierH = fiberH + 28
      const barrierTop = centerY - barrierH / 2

      // Outer Crystal Housing
      ctx.fillStyle = 'rgba(15, 23, 42, 0.85)'
      ctx.strokeStyle = 'rgba(59, 130, 246, 0.5)'
      ctx.lineWidth = 1.5
      ctx.beginPath()
      ctx.roundRect(diodeX - barrierW / 2, barrierTop, barrierW, barrierH, 6)
      ctx.fill()
      ctx.stroke()

      // Faraday Crystal Core (Bismuth Iron Garnet)
      const crystalGrad = ctx.createLinearGradient(diodeX - 16, centerY, diodeX + 16, centerY)
      crystalGrad.addColorStop(0, 'rgba(59, 130, 246, 0.4)')
      crystalGrad.addColorStop(0.5, 'rgba(168, 85, 247, 0.6)')
      crystalGrad.addColorStop(1, 'rgba(16, 185, 129, 0.4)')
      ctx.fillStyle = crystalGrad
      ctx.fillRect(diodeX - 16, centerY - 20, 32, 40)
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)'
      ctx.strokeRect(diodeX - 16, centerY - 20, 32, 40)

      // Crystal Magnetic Vector Arrow (B-field)
      ctx.strokeStyle = '#38bdf8'
      ctx.lineWidth = 1.5
      ctx.beginPath()
      ctx.moveTo(diodeX - 12, centerY)
      ctx.lineTo(diodeX + 12, centerY)
      ctx.lineTo(diodeX + 8, centerY - 4)
      ctx.moveTo(diodeX + 12, centerY)
      ctx.lineTo(diodeX + 8, centerY + 4)
      ctx.stroke()

      // Polarization Angle Tags
      ctx.font = '8px monospace'
      ctx.fillStyle = '#94a3b8'
      ctx.textAlign = 'center'
      ctx.fillText('FARADAY ROTATOR', diodeX, barrierTop - 4)
      ctx.fillStyle = '#38bdf8'
      ctx.fillText('0° IN', diodeX - 22, barrierTop + 10)
      ctx.fillStyle = '#34d399'
      ctx.fillText('+45° OUT', diodeX + 22, barrierTop + 10)
      ctx.fillStyle = '#f43f5e'
      ctx.fillText('REV DUMP: -78dB', diodeX, barrierTop + barrierH - 4)
      ctx.restore()

      // ==========================================
      // 4. PHOTON WAVELETS PROPAGATION & RENDERING
      // ==========================================
      const photons = photonsRef.current

      for (let i = photons.length - 1; i >= 0; i--) {
        const p = photons[i]
        if (isPlayingRef.current) {
          p.progress += p.speed
        }

        if (p.progress >= 1) {
          photons.splice(i, 1)
          continue
        }

        const curX = startX + (endX - startX) * p.progress
        const curY = centerY + p.yLane

        // Physical wave properties
        const isThreat = p.isThreat
        const primaryColor = isThreat ? '#f43f5e' : '#38bdf8'
        const glowColor = isThreat ? 'rgba(244, 63, 94, 0.8)' : 'rgba(56, 189, 248, 0.8)'

        ctx.save()
        
        // 4a. Trailing Photoluminescence Halo (Laser Beam Trail)
        const trailLength = isThreat ? 42 : 28
        const trailGrad = ctx.createLinearGradient(curX - trailLength, curY, curX, curY)
        trailGrad.addColorStop(0, 'rgba(0, 0, 0, 0)')
        trailGrad.addColorStop(1, glowColor)
        
        ctx.strokeStyle = trailGrad
        ctx.lineWidth = isThreat ? 3 : 2
        ctx.beginPath()
        ctx.moveTo(curX - trailLength, curY)
        ctx.lineTo(curX, curY)
        ctx.stroke()

        // 4b. Electromagnetic Wavelet Sinusoid (Real Physics)
        ctx.strokeStyle = primaryColor
        ctx.lineWidth = 1.5
        ctx.shadowColor = glowColor
        ctx.shadowBlur = isThreat ? 14 : 8
        ctx.beginPath()
        for (let dx = -14; dx <= 6; dx += 1) {
          const envelope = Math.exp(-Math.pow(dx / 7, 2)) // Gaussian wave packet envelope
          const waveY = curY + Math.sin(dx * p.frequency + t * 4 + p.phase) * (p.amplitude * envelope)
          if (dx === -14) ctx.moveTo(curX + dx, waveY)
          else ctx.lineTo(curX + dx, waveY)
        }
        ctx.stroke()

        // 4c. Photon Particle Core Head
        ctx.fillStyle = '#ffffff'
        ctx.beginPath()
        ctx.arc(curX, curY, isThreat ? 3 : 2, 0, Math.PI * 2)
        ctx.fill()

        // 4d. Wavelength Tag for Threats
        if (isThreat && p.progress > 0.15 && p.progress < 0.85) {
          ctx.font = 'bold 8px monospace'
          ctx.fillStyle = '#fecdd3'
          ctx.fillText(`λ:1550nm [${p.vectorName.split(' ')[0]}]`, curX - 20, curY - 14)
        }

        ctx.restore()
      }

      animFrameRef.current = requestAnimationFrame(render)
    }

    render()

    return () => {
      cancelAnimationFrame(animFrameRef.current)
    }
  }, [])

  return (
    <div className="space-y-3 font-mono">
      
      {/* 100K-WORTHY HARDWARE CHASSIS HEADER */}
      <div className="glass-panel p-3.5 rounded-lg flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-bold text-white uppercase tracking-wider">
              Physical Data Diode Simplex Packet Flow Visualizer
            </span>
            <Badge variant="secure" size="xs">STRICT 1-WAY OPTICAL PHYSICS</Badge>
          </div>
          <p className="text-[11px] text-zinc-400 font-sans">
            Faraday polarization optical tap (1310nm / 1550nm) · Permanently severed return strand · Zero reverse packets on wire
          </p>
        </div>

        {/* Live Controls */}
        <div className="flex items-center gap-2 shrink-0">
          <Button
            variant="outline"
            size="xs"
            onClick={() => setIsPlaying(!isPlaying)}
            icon={isPlaying ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
          >
            {isPlaying ? 'Pause Tap' : 'Resume'}
          </Button>

          <Button
            variant="outline"
            size="xs"
            onClick={() => setSpeedMultiplier(speedMultiplier === 1 ? 2 : speedMultiplier === 2 ? 0.5 : 1)}
            icon={<FastForward className="w-3 h-3" />}
          >
            {speedMultiplier}x Speed
          </Button>
        </div>
      </div>

      {/* THREE HARDWARE NODES & THE OPTICAL CONDUIT CANVASES */}
      <div className="glass-panel rounded-lg p-3 relative overflow-hidden">
        
        {/* TOP HARDWARE TELEMETRY READOUTS */}
        <div className="flex justify-between items-center text-[10px] text-zinc-400 border-b border-white/[0.06] pb-2 mb-2">
          {/* Node 1 */}
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
            <span className="font-bold text-zinc-200">WAN INGRESS (TX)</span>
            <span className="text-zinc-500">SFP+ 1310nm DFB Laser · Pout: {txPower}</span>
          </div>

          {/* Node 2 Center */}
          <div className="hidden sm:flex items-center gap-2">
            <Lock className="w-3 h-3 text-red-400" />
            <span className="font-bold text-red-400">FARADAY ISOLATOR BARRIER</span>
            <span className="text-zinc-500">Isolation: {isolationDb} · Return: 0 ACKs</span>
          </div>

          {/* Node 3 */}
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            <span className="font-bold text-zinc-200">ENCLAVE SENSOR (RX)</span>
            <span className="text-zinc-500">InGaAs Photodiode · eth0 · Pin: {rxPower}</span>
          </div>
        </div>

        {/* HIGH-PRECISION PHOTON CANVAS */}
        <div className="relative w-full h-[240px] bg-[#07090e] rounded border border-white/[0.06] overflow-hidden">
          
          {/* HARDWARE OVERLAY LABELS */}
          <div className="absolute left-3 top-3 z-10 pointer-events-none">
            <div className="p-2 rounded bg-black/70 backdrop-blur-md border border-white/[0.08] text-[10px] space-y-0.5">
              <div className="text-blue-400 font-bold">WAN OPTICAL INGRESS</div>
              <div className="text-zinc-400">Photons: {photonCount.toLocaleString()}</div>
              <div className="text-zinc-500">Bitrate: 1.25 Gbps</div>
            </div>
          </div>

          <div className="absolute right-3 top-3 z-10 pointer-events-none">
            <div className="p-2 rounded bg-black/70 backdrop-blur-md border border-white/[0.08] text-[10px] space-y-0.5 text-right">
              <div className="text-emerald-400 font-bold">ENCLAVE SENSOR (eth0)</div>
              <div className="text-zinc-400">Reverse Packets: 0 PKTS</div>
              <div className="text-emerald-500 font-bold">100% SIMPLEX TAP</div>
            </div>
          </div>

          <canvas ref={canvasRef} className="w-full h-full block" />
        </div>

        {/* BOTTOM REAL-TIME INTERACTIVE ATTACK INJECTORS */}
        <div className="mt-3 pt-2.5 border-t border-white/[0.06] flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-[11px] text-zinc-400 font-semibold uppercase">Inject Physical Anomaly:</span>
            <div className="flex flex-wrap gap-1.5">
              <button
                onClick={() => triggerAttack('syn')}
                className="px-2 py-1 rounded text-[10px] font-mono bg-red-500/15 border border-red-500/30 text-red-400 hover:bg-red-500/25 transition-colors cursor-pointer"
              >
                Vector (a) SYN Barrage
              </button>
              <button
                onClick={() => triggerAttack('c2')}
                className="px-2 py-1 rounded text-[10px] font-mono bg-purple-500/15 border border-purple-500/30 text-purple-400 hover:bg-purple-500/25 transition-colors cursor-pointer"
              >
                Vector (b) C2 Beacon
              </button>
              <button
                onClick={() => triggerAttack('dns')}
                className="px-2 py-1 rounded text-[10px] font-mono bg-blue-500/15 border border-blue-500/30 text-blue-400 hover:bg-blue-500/25 transition-colors cursor-pointer"
              >
                Vector (c) DNS Tunnel
              </button>
              <button
                onClick={() => triggerAttack('exfil')}
                className="px-2 py-1 rounded text-[10px] font-mono bg-rose-500/15 border border-rose-500/30 text-rose-400 hover:bg-rose-500/25 transition-colors cursor-pointer"
              >
                Vector (f) Asym Exfil
              </button>
            </div>
          </div>

          <div className="text-[10px] text-zinc-500 flex items-center gap-1.5">
            <Waves className="w-3 h-3 text-cyan-400" />
            <span>Active Stream: <strong className="text-zinc-300">{activeThreatDesc}</strong></span>
          </div>
        </div>

      </div>

    </div>
  )
}

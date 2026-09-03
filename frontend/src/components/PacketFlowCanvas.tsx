'use client'

import React, { useEffect, useRef, useState } from 'react'
import { 
  Play, Pause, FastForward, Shield, Radio, Activity, Zap, Cpu, Lock, 
  Terminal, Eye, RefreshCw, Layers, Sliders, Waves, ArrowRight, AlertTriangle, CheckCircle2
} from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'

interface PhotonicPacket {
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
  yLane: number // micro-offset in fiber core
}

export default function PacketFlowCanvas() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const [isPlaying, setIsPlaying] = useState(true)
  const [speedMultiplier, setSpeedMultiplier] = useState(1)
  const [activeVector, setActiveVector] = useState<string>('baseline')
  
  // Real-time live physical metrics
  const [txPower, setTxPower] = useState('+2.4 dBm')
  const [rxPower, setRxPower] = useState('-3.1 dBm')
  const [isolationDb, setIsolationDb] = useState('78.4 dB')
  const [photonCount, setPhotonCount] = useState(18420)
  const [reverseAcks, setReverseAcks] = useState(0)
  const [reverseRsts, setReverseRsts] = useState(0)

  const packetsRef = useRef<PhotonicPacket[]>([])
  const isPlayingRef = useRef(isPlaying)
  const speedRef = useRef(speedMultiplier)
  const animFrameRef = useRef<number>(0)

  isPlayingRef.current = isPlaying
  speedRef.current = speedMultiplier

  // Spawn photon wave packet into primary single-mode fiber
  const spawnPacket = (isThreat = false, vector = 'Benign SMF Stream', wl: 1310 | 1550 = 1310, src = '185.220.101.34') => {
    setPhotonCount(prev => prev + 1)
    const lanes = [-10, -3, 3, 10]
    const yLane = lanes[Math.floor(Math.random() * lanes.length)]

    packetsRef.current.push({
      id: Math.random().toString(),
      progress: 0,
      speed: (0.0042 + Math.random() * 0.0028) * speedRef.current,
      wavelength: wl,
      amplitude: isThreat ? 12 : 8,
      frequency: isThreat ? 0.38 : 0.24,
      phase: Math.random() * Math.PI * 2,
      isThreat,
      vectorName: vector,
      sourceIp: src,
      destIp: '10.0.1.50',
      yLane
    })
  }

  // Attack pulse injector
  const triggerAttack = (vectorType: 'syn' | 'c2' | 'dns' | 'exfil') => {
    if (vectorType === 'syn') {
      setActiveVector('SYN Flood (1310nm Burst)')
      for (let i = 0; i < 8; i++) {
        setTimeout(() => spawnPacket(true, 'SYN Flood (Vector a)', 1310, '45.154.255.147'), i * 75)
      }
    } else if (vectorType === 'c2') {
      setActiveVector('Periodic C2 (1310nm Beacon)')
      for (let i = 0; i < 4; i++) {
        setTimeout(() => spawnPacket(true, 'Botnet C2 Beacon (Vector b)', 1310, '91.240.118.172'), i * 260)
      }
    } else if (vectorType === 'dns') {
      setActiveVector('DNS Exfil (1550nm Modulated)')
      for (let i = 0; i < 6; i++) {
        setTimeout(() => spawnPacket(true, 'DNS Tunnel / DGA (Vector c)', 1550, '194.26.135.89'), i * 110)
      }
    } else if (vectorType === 'exfil') {
      setActiveVector('Data Siphon (1550nm Surge)')
      for (let i = 0; i < 12; i++) {
        setTimeout(() => spawnPacket(true, 'Asym Exfiltration (Vector f)', 1550, '185.220.101.34'), i * 45)
      }
    }
  }

  // Self-sustaining ambient photon generator
  useEffect(() => {
    const timer = setInterval(() => {
      if (!isPlayingRef.current) return
      if (packetsRef.current.length < 15) {
        const isAnomaly = Math.random() > 0.70
        const wl = isAnomaly ? 1550 : 1310
        spawnPacket(
          isAnomaly, 
          isAnomaly ? 'Unidirectional Threat Anomaly' : 'Benign Baseline Ingress', 
          wl, 
          isAnomaly ? '185.220.101.34' : '192.168.1.100'
        )
      }
    }, 420)
    return () => clearInterval(timer)
  }, [])

  // Canvas High-Precision Scientific Optical Render Loop
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let t = 0

    const render = () => {
      t += 0.04
      const dpr = window.devicePixelRatio || 1
      const rect = canvas.parentElement?.getBoundingClientRect()
      const displayWidth = rect?.width || 980
      const displayHeight = 280

      if (canvas.width !== displayWidth * dpr || canvas.height !== displayHeight * dpr) {
        canvas.width = displayWidth * dpr
        canvas.height = displayHeight * dpr
      }

      ctx.save()
      ctx.scale(dpr, dpr)
      ctx.clearRect(0, 0, displayWidth, displayHeight)

      const startX = 70
      const endX = displayWidth - 70
      const centerY = 95
      const diodeX = (startX + endX) / 2
      const fiberH = 48
      const topY = centerY - fiberH / 2
      const botY = centerY + fiberH / 2

      // ==========================================
      // A. PRIMARY OS2 SINGLE-MODE OPTICAL FIBER
      // ==========================================

      // 1. Cladding Background (n2 = 1.463)
      const fiberGrad = ctx.createLinearGradient(startX, centerY, endX, centerY)
      fiberGrad.addColorStop(0, 'rgba(14, 165, 233, 0.07)')
      fiberGrad.addColorStop(0.48, 'rgba(14, 165, 233, 0.12)')
      fiberGrad.addColorStop(0.52, 'rgba(16, 185, 129, 0.12)')
      fiberGrad.addColorStop(1, 'rgba(16, 185, 129, 0.07)')
      ctx.fillStyle = fiberGrad
      ctx.fillRect(startX, topY, endX - startX, fiberH)

      // 2. Cladding Boundary Reflections
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)'
      ctx.lineWidth = 1
      ctx.beginPath()
      ctx.moveTo(startX, topY)
      ctx.lineTo(endX, topY)
      ctx.moveTo(startX, botY)
      ctx.lineTo(endX, botY)
      ctx.stroke()

      // 3. Central Core Guide (8.2 µm OS2 SMF-28 Core Line)
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.3)'
      ctx.lineWidth = 1.5
      ctx.setLineDash([4, 6])
      ctx.beginPath()
      ctx.moveTo(startX, centerY)
      ctx.lineTo(endX, centerY)
      ctx.stroke()
      ctx.setLineDash([])

      // Scientific Labels for Fiber
      ctx.font = '9px JetBrains Mono, monospace'
      ctx.fillStyle = 'rgba(255, 255, 255, 0.35)'
      ctx.fillText('SINGLE-MODE OS2 FIBER (8.2/125 µm • n₁=1.468)', startX + 10, topY - 7)
      ctx.textAlign = 'right'
      ctx.fillText('FORWARD PROPAGATION ONLY (λ=1310/1550nm)', endX - 10, topY - 7)
      ctx.textAlign = 'left'

      // ==========================================
      // B. METALLIC FARADAY POLARIZATION OPTICAL TAP
      // ==========================================
      ctx.save()
      const boxW = 88
      const boxH = fiberH + 40
      const boxTop = centerY - boxH / 2

      // 1. Outer Metallic Beveled Housing
      const metalGrad = ctx.createLinearGradient(diodeX - boxW / 2, boxTop, diodeX + boxW / 2, boxTop + boxH)
      metalGrad.addColorStop(0, '#1a1f2c')
      metalGrad.addColorStop(0.5, '#0f1420')
      metalGrad.addColorStop(1, '#1e2433')
      ctx.fillStyle = metalGrad
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.18)'
      ctx.lineWidth = 1.5
      ctx.beginPath()
      ctx.roundRect(diodeX - boxW / 2, boxTop, boxW, boxH, 8)
      ctx.fill()
      ctx.stroke()

      // Hex Corner Mounting Screws
      const screwR = 2
      const drawScrew = (sx: number, sy: number) => {
        ctx.fillStyle = '#475569'
        ctx.beginPath()
        ctx.arc(sx, sy, screwR, 0, Math.PI * 2)
        ctx.fill()
        ctx.strokeStyle = '#94a3b8'
        ctx.lineWidth = 0.5
        ctx.stroke()
      }
      drawScrew(diodeX - boxW / 2 + 6, boxTop + 6)
      drawScrew(diodeX + boxW / 2 - 6, boxTop + 6)
      drawScrew(diodeX - boxW / 2 + 6, boxTop + boxH - 6)
      drawScrew(diodeX + boxW / 2 - 6, boxTop + boxH - 6)

      // 2. Glowing Faraday Crystal (Bismuth Iron Garnet BIG-45)
      const crystalW = 36
      const crystalH = 46
      const crystalGrad = ctx.createLinearGradient(diodeX - crystalW / 2, centerY, diodeX + crystalW / 2, centerY)
      crystalGrad.addColorStop(0, 'rgba(56, 189, 248, 0.5)')
      crystalGrad.addColorStop(0.5, 'rgba(168, 85, 247, 0.7)')
      crystalGrad.addColorStop(1, 'rgba(16, 185, 129, 0.5)')
      ctx.fillStyle = crystalGrad
      ctx.fillRect(diodeX - crystalW / 2, centerY - crystalH / 2, crystalW, crystalH)
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.45)'
      ctx.lineWidth = 1
      ctx.strokeRect(diodeX - crystalW / 2, centerY - crystalH / 2, crystalW, crystalH)

      // Magnetic Vector B-Field Arrow
      ctx.strokeStyle = '#ffffff'
      ctx.lineWidth = 1.5
      ctx.beginPath()
      ctx.moveTo(diodeX - 12, centerY)
      ctx.lineTo(diodeX + 12, centerY)
      ctx.lineTo(diodeX + 7, centerY - 4)
      ctx.moveTo(diodeX + 12, centerY)
      ctx.lineTo(diodeX + 7, centerY + 4)
      ctx.stroke()

      // 3. Polarizer Stage Angles
      ctx.font = '8px JetBrains Mono, monospace'
      ctx.fillStyle = '#38bdf8'
      ctx.textAlign = 'center'
      ctx.fillText('0° POL', diodeX - 26, boxTop + 14)
      ctx.fillStyle = '#34d399'
      ctx.fillText('+45° ANA', diodeX + 26, boxTop + 14)

      // 4. Faraday Module Identification Engraving
      ctx.font = 'bold 8px JetBrains Mono, monospace'
      ctx.fillStyle = '#f8fafc'
      ctx.fillText('FARADAY ISOLATOR', diodeX, boxTop - 6)
      
      // Bottom Internal Beam Dump Tag
      ctx.fillStyle = '#f43f5e'
      ctx.font = '7.5px JetBrains Mono, monospace'
      ctx.fillText('DUMP: -78.4dB', diodeX, boxTop + boxH + 11)
      ctx.restore()

      // ==========================================
      // C. PERMANENTLY SEVERED RETURN STRAND (40mm AIR GAP)
      // ==========================================
      const retY = centerY + 85
      const gapW = 80 // 40mm proportional scale

      // Left returning strand (severed end face)
      ctx.strokeStyle = 'rgba(239, 68, 68, 0.25)'
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.moveTo(startX, retY)
      ctx.lineTo(diodeX - gapW / 2, retY)
      ctx.stroke()

      // Right returning strand (originating from Enclave, severed end face)
      ctx.strokeStyle = 'rgba(239, 68, 68, 0.45)'
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.moveTo(diodeX + gapW / 2, retY)
      ctx.lineTo(endX, retY)
      ctx.stroke()

      // Ceramic Ferrule Connectors on both sides of break
      const drawFerrule = (fx: number, isLeft: boolean) => {
        ctx.fillStyle = '#64748b'
        ctx.strokeStyle = '#94a3b8'
        ctx.lineWidth = 1
        const fw = 8
        const fh = 12
        ctx.fillRect(isLeft ? fx - fw : fx, retY - fh / 2, fw, fh)
        ctx.strokeRect(isLeft ? fx - fw : fx, retY - fh / 2, fw, fh)
        // Red fracture tip
        ctx.fillStyle = '#ef4444'
        ctx.beginPath()
        ctx.arc(fx, retY, 2, 0, Math.PI * 2)
        ctx.fill()
      }
      drawFerrule(diodeX - gapW / 2, true)
      drawFerrule(diodeX + gapW / 2, false)

      // Physical Air Gap Dimension Line
      ctx.save()
      ctx.strokeStyle = '#ef4444'
      ctx.lineWidth = 1
      ctx.setLineDash([2, 2])
      ctx.beginPath()
      ctx.moveTo(diodeX - gapW / 2, retY)
      ctx.lineTo(diodeX + gapW / 2, retY)
      ctx.stroke()
      ctx.setLineDash([])

      // Red Hazard Pulsing LED
      const pulsePhase = Math.sin(t * 6)
      const ledGlow = pulsePhase > 0 ? 'rgba(239, 68, 68, 0.8)' : 'rgba(239, 68, 68, 0.3)'
      ctx.shadowColor = ledGlow
      ctx.shadowBlur = 8
      ctx.fillStyle = '#ef4444'
      ctx.beginPath()
      ctx.arc(diodeX, retY - 14, 3, 0, Math.PI * 2)
      ctx.fill()
      ctx.restore()

      // Primary Educational Invariant Warning Label
      ctx.font = 'bold 9px JetBrains Mono, monospace'
      ctx.fillStyle = '#fca5a5'
      ctx.textAlign = 'center'
      ctx.fillText('◄── 40mm PHYSICAL AIR GAP ──►', diodeX, retY - 4)
      ctx.font = 'bold 9px JetBrains Mono, monospace'
      ctx.fillStyle = '#ef4444'
      ctx.fillText('PHYSICAL RETURN STRAND SEVERED', diodeX, retY + 16)
      ctx.font = '8px JetBrains Mono, monospace'
      ctx.fillStyle = 'rgba(248, 113, 113, 0.85)'
      ctx.fillText('REVERSE TRANSMISSION PHYSICALLY IMPOSSIBLE (0 RETURN ACKs / 0 RSTs)', diodeX, retY + 28)

      // ==========================================
      // D. PHOTONIC PACKET WAVE PROPAGATION
      // ==========================================
      const packets = packetsRef.current

      for (let i = packets.length - 1; i >= 0; i--) {
        const p = packets[i]
        if (isPlayingRef.current) {
          p.progress += p.speed
        }

        if (p.progress >= 1) {
          packets.splice(i, 1)
          continue
        }

        const curX = startX + (endX - startX) * p.progress
        const curY = centerY + p.yLane

        // Wavelength Coloring (1310nm = Cyan / 1550nm = Magenta)
        const is1310 = p.wavelength === 1310
        const primaryColor = is1310 ? '#38bdf8' : '#f43f5e'
        const glowColor = is1310 ? 'rgba(56, 189, 248, 0.85)' : 'rgba(244, 63, 94, 0.95)'

        ctx.save()

        // 1. Trailing Photoluminescence Halo (Laser Beam Trail)
        const trailLen = is1310 ? 34 : 46
        const trailGrad = ctx.createLinearGradient(curX - trailLen, curY, curX, curY)
        trailGrad.addColorStop(0, 'rgba(0,0,0,0)')
        trailGrad.addColorStop(1, glowColor)
        ctx.strokeStyle = trailGrad
        ctx.lineWidth = 2.5
        ctx.beginPath()
        ctx.moveTo(curX - trailLen, curY)
        ctx.lineTo(curX, curY)
        ctx.stroke()

        // 2. Physical Electromagnetic Wavelet (Sinusoidal Wave Packet)
        ctx.strokeStyle = primaryColor
        ctx.lineWidth = 1.5
        ctx.shadowColor = glowColor
        ctx.shadowBlur = is1310 ? 10 : 16
        ctx.beginPath()
        for (let dx = -14; dx <= 6; dx += 1) {
          const envelope = Math.exp(-Math.pow(dx / 7, 2)) // Gaussian envelope
          const waveY = curY + Math.sin(dx * p.frequency + t * 5 + p.phase) * (p.amplitude * envelope)
          if (dx === -14) ctx.moveTo(curX + dx, waveY)
          else ctx.lineTo(curX + dx, waveY)
        }
        ctx.stroke()

        // 3. Central Photon Head Particle
        ctx.fillStyle = '#ffffff'
        ctx.beginPath()
        ctx.arc(curX, curY, 2.5, 0, Math.PI * 2)
        ctx.fill()

        // 4. Wavelength Tag for Anomalous Wave Packets
        if (p.isThreat && p.progress > 0.15 && p.progress < 0.85) {
          ctx.font = 'bold 8px JetBrains Mono, monospace'
          ctx.fillStyle = '#fecdd3'
          ctx.fillText(`λ:1550nm [${p.vectorName.split(' ')[0]}]`, curX - 18, curY - 14)
        }

        ctx.restore()
      }

      ctx.restore()
      animFrameRef.current = requestAnimationFrame(render)
    }

    render()

    return () => {
      cancelAnimationFrame(animFrameRef.current)
    }
  }, [])

  return (
    <div className="space-y-3 font-mono">
      
      {/* 1. CORE TITLE STRIP (PALANTIR / CROWDSTRIKE GRADE) */}
      <div className="glass-panel p-3.5 rounded-lg flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <h2 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
              Physical Data Diode — Simplex Packet Flow
            </h2>
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

      {/* 2. FOUR LIQUID-GLASS TELEMETRY INSTRUMENTATION CARDS */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-2.5">
        {/* WAN INGRESS */}
        <div className="glass-card p-3 rounded-lg flex flex-col justify-between">
          <div className="flex items-center justify-between text-[10px] text-zinc-400 uppercase font-semibold">
            <span className="flex items-center gap-1.5 text-blue-400">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
              WAN INGRESS
            </span>
            <span className="text-zinc-500">TX STAGE</span>
          </div>
          <div className="my-1.5">
            <div className="text-base font-bold text-zinc-100 font-mono">SFP+ DFB Laser</div>
            <div className="text-[11px] text-blue-400 font-mono mt-0.5">TX Power: {txPower}</div>
          </div>
          <div className="text-[10px] text-zinc-500 pt-1.5 border-t border-white/[0.04] flex justify-between">
            <span>Primary λ: 1310nm</span>
            <span className="text-zinc-400">Photons: {photonCount.toLocaleString()}</span>
          </div>
        </div>

        {/* FARADAY ISOLATION */}
        <div className="glass-card p-3 rounded-lg flex flex-col justify-between">
          <div className="flex items-center justify-between text-[10px] text-zinc-400 uppercase font-semibold">
            <span className="flex items-center gap-1.5 text-purple-400">
              <Lock className="w-3 h-3 text-purple-400" />
              FARADAY ISOLATION
            </span>
            <span className="text-emerald-400 font-bold">{isolationDb}</span>
          </div>
          <div className="my-1.5">
            <div className="text-base font-bold text-zinc-100 font-mono">Polarization +45°</div>
            <div className="text-[11px] text-purple-400 font-mono mt-0.5">Beam Dump Active</div>
          </div>
          <div className="text-[10px] text-zinc-500 pt-1.5 border-t border-white/[0.04] flex justify-between">
            <span>Mode: SMF-28 OS2</span>
            <span className="text-emerald-400">Leakage: -78.4dB</span>
          </div>
        </div>

        {/* ENCLAVE RX */}
        <div className="glass-card p-3 rounded-lg flex flex-col justify-between">
          <div className="flex items-center justify-between text-[10px] text-zinc-400 uppercase font-semibold">
            <span className="flex items-center gap-1.5 text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              ENCLAVE RX
            </span>
            <span className="text-zinc-500">RX STAGE</span>
          </div>
          <div className="my-1.5">
            <div className="text-base font-bold text-zinc-100 font-mono">InGaAs Photodiode</div>
            <div className="text-[11px] text-emerald-400 font-mono mt-0.5">RX Power: {rxPower}</div>
          </div>
          <div className="text-[10px] text-zinc-500 pt-1.5 border-t border-white/[0.04] flex justify-between">
            <span>Interface: eth0</span>
            <span className="text-zinc-400">BER &lt; 10⁻¹²</span>
          </div>
        </div>

        {/* SIMPLEX STATUS */}
        <div className="glass-card p-3 rounded-lg flex flex-col justify-between">
          <div className="flex items-center justify-between text-[10px] text-zinc-400 uppercase font-semibold">
            <span className="flex items-center gap-1.5 text-emerald-400">
              <Shield className="w-3 h-3 text-emerald-400" />
              SIMPLEX STATUS
            </span>
            <Badge variant="secure" size="xs">100% ASSURANCE</Badge>
          </div>
          <div className="my-1.5">
            <div className="text-base font-bold text-emerald-400 font-mono">0 Reverse ACKs</div>
            <div className="text-[11px] text-zinc-400 font-mono mt-0.5">0 Reverse RSTs</div>
          </div>
          <div className="text-[10px] text-zinc-500 pt-1.5 border-t border-white/[0.04] flex justify-between">
            <span>Duplex: Disabled</span>
            <span className="text-emerald-400 font-semibold">Hardware Proof</span>
          </div>
        </div>
      </div>

      {/* 3. CENTRAL SCIENTIFIC OPTICAL FIBER CANVASES (OBSIDIAN #090D16) */}
      <div className="glass-panel rounded-lg p-3 relative overflow-hidden bg-[#090D16]/90 border border-white/[0.10]">
        
        {/* Node Labels Header */}
        <div className="flex justify-between items-center text-[10px] text-zinc-400 border-b border-white/[0.06] pb-2 mb-2">
          <div className="flex items-center gap-2">
            <span className="font-bold text-zinc-200">OPTICAL SOURCE: TX LASER</span>
            <span className="text-zinc-500">| SFP+ Single-Mode Transceiver</span>
          </div>
          <div className="hidden sm:flex items-center gap-2">
            <Lock className="w-3 h-3 text-purple-400" />
            <span className="font-bold text-zinc-200">FARADAY CRYSTAL TAP</span>
            <span className="text-zinc-500">| Non-Reciprocal 45° Polarization</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-zinc-200">PROMISCUOUS RX SENSOR</span>
            <span className="text-zinc-500">| Linux eth0 Raw Ingress</span>
          </div>
        </div>

        {/* Precision High-DPI Canvas */}
        <div className="relative w-full h-[280px] bg-[#090D16] rounded border border-white/[0.06] overflow-hidden">
          <canvas ref={canvasRef} className="w-full h-full block" />
        </div>

        {/* 4. REAL-TIME INTERACTIVE PHYSICAL ATTACK INJECTORS */}
        <div className="mt-3 pt-2.5 border-t border-white/[0.06] flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-[11px] text-zinc-400 font-semibold uppercase">Trigger Physical Anomaly:</span>
            <div className="flex flex-wrap gap-1.5">
              <button
                onClick={() => triggerAttack('syn')}
                className="px-2.5 py-1 rounded text-[10px] font-mono bg-red-500/15 border border-red-500/30 text-red-400 hover:bg-red-500/25 transition-colors cursor-pointer"
              >
                SYN Flood (1310nm Burst)
              </button>
              <button
                onClick={() => triggerAttack('c2')}
                className="px-2.5 py-1 rounded text-[10px] font-mono bg-purple-500/15 border border-purple-500/30 text-purple-400 hover:bg-purple-500/25 transition-colors cursor-pointer"
              >
                Periodic C2 (1310nm Beacon)
              </button>
              <button
                onClick={() => triggerAttack('dns')}
                className="px-2.5 py-1 rounded text-[10px] font-mono bg-blue-500/15 border border-blue-500/30 text-blue-400 hover:bg-blue-500/25 transition-colors cursor-pointer"
              >
                DNS Exfil (1550nm Modulated)
              </button>
              <button
                onClick={() => triggerAttack('exfil')}
                className="px-2.5 py-1 rounded text-[10px] font-mono bg-rose-500/15 border border-rose-500/30 text-rose-400 hover:bg-rose-500/25 transition-colors cursor-pointer"
              >
                Data Siphon (1550nm Surge)
              </button>
            </div>
          </div>

          <div className="text-[10px] text-zinc-500 flex items-center gap-1.5">
            <Waves className="w-3.5 h-3.5 text-cyan-400" />
            <span>Active Stream: <strong className="text-zinc-300">{activeVector}</strong></span>
          </div>
        </div>

      </div>

    </div>
  )
}

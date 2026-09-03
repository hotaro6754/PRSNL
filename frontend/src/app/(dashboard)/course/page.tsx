'use client'

import React, { useState } from 'react'
import { 
  BookOpen, ExternalLink, Printer, Shield, Layers, 
  Cpu, Radio, FileText, CheckCircle2, ChevronRight, Maximize2, Download
} from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'

const GALLERY_SECTIONS = [
  { id: '01', title: '01 Hero Solution', desc: 'Unidirectional IP Monitoring & Intelligence Pipeline' },
  { id: '02', title: '02 Problem Boundary', desc: 'Zero probing, zero handshake, zero return path' },
  { id: '03', title: '03 Technical Pipeline', desc: 'Ingest -> Normalize -> Aggregate -> Features -> Detect -> Fuse' },
  { id: '04', title: '04 Feature Engineering', desc: 'Flow, DNS, TLS metadata to 18-feature vector' },
  { id: '05', title: '05 Hybrid Detection', desc: 'Deterministic Rules + Supervised XGBoost v5' },
  { id: '06', title: '06 Threat Matrix', desc: '6 Canonical Threat Families + Slowloris HTTP' },
  { id: '07', title: '07 Enterprise Infrastructure', desc: 'Data Plane -> Intelligence Plane -> SOC Plane' },
  { id: '08', title: '08 Failure & Recovery', desc: 'Resilience constraints & at-least-once semantics' },
  { id: '09', title: '09 Impact Before/After', desc: 'Manual vs Automated Behavioral Intelligence' },
  { id: '10', title: '10 Research Map', desc: 'Zeek, CICIDS2017, UNSW-NB15, Redpanda, XGBoost' },
  { id: '11', title: '11 Validation Metrics', desc: '98.69% Precision | 100% Recall | 99.34% F1 | 0% FP' },
]

export default function MasterCoursePage() {
  const [isFullscreen, setIsFullscreen] = useState(false)

  const openExternal = () => {
    window.open('/educational_dashboard/PS26145_Master_Course.html', '_blank')
  }

  return (
    <div className="space-y-4 max-w-[1700px] mx-auto animate-in fade-in duration-300 font-mono">
      
      {/* 1. HEADER & CONTROLS */}
      <div className="glass-panel p-4 rounded-lg flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <h1 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-blue-400" />
              PS26145: Passive Threat Detection Master Course
            </h1>
            <Badge variant="secure" size="xs">53 MODULES</Badge>
            <Badge variant="default" size="xs">ACADEMY</Badge>
          </div>
          <p className="text-xs text-zinc-400 font-sans">
            Comprehensive curriculum: First-principles networking, optical simplex boundaries, mathematical entropy, XGBoost, and SOC operations.
          </p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <Button
            variant="outline"
            size="xs"
            onClick={openExternal}
            icon={<ExternalLink className="w-3 h-3 text-blue-400" />}
          >
            Open Full Window
          </Button>

          <Button
            variant="outline"
            size="xs"
            onClick={openExternal}
            icon={<Printer className="w-3 h-3 text-emerald-400" />}
          >
            Print / Save PDF
          </Button>

          <Button
            variant="outline"
            size="xs"
            onClick={() => setIsFullscreen(!isFullscreen)}
            icon={<Maximize2 className="w-3 h-3 text-purple-400" />}
          >
            {isFullscreen ? 'Exit Focus' : 'Focus Mode'}
          </Button>
        </div>
      </div>

      {/* 2. GALLERY JUMP STRIP */}
      <div className="glass-panel p-3 rounded-lg overflow-x-auto">
        <div className="flex items-center gap-2 text-xs min-w-max">
          <span className="text-[10px] text-zinc-500 uppercase font-semibold mr-1">Architecture Gallery:</span>
          {GALLERY_SECTIONS.map((sec) => (
            <button
              key={sec.id}
              onClick={openExternal}
              className="px-2 py-1 rounded bg-[#090b0e] border border-white/[0.06] hover:border-blue-500/40 text-zinc-300 hover:text-blue-300 text-[11px] transition-all cursor-pointer flex items-center gap-1.5"
            >
              <span className="text-blue-400 font-bold">{sec.id}</span>
              <span>{sec.title.replace(/^\d+\s*/, '')}</span>
            </button>
          ))}
        </div>
      </div>

      {/* 3. INTERACTIVE VIEWER IFRAME */}
      <div className={`glass-panel rounded-lg overflow-hidden border border-white/[0.10] transition-all ${
        isFullscreen ? 'fixed inset-2 z-50 bg-[#07080b]/98 p-2' : 'h-[820px] p-2'
      }`}>
        <div className="flex justify-between items-center text-[10px] text-zinc-500 pb-2 px-1 border-b border-white/[0.06] mb-2 font-mono">
          <div className="flex items-center gap-2">
            <span className="text-zinc-400">SOURCE:</span>
            <code className="text-blue-400">/educational_dashboard/PS26145_Master_Course.html</code>
            <span className="text-zinc-600">|</span>
            <span className="text-emerald-400">Interactive SVG Architecture & Mermaid Workflows</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-zinc-400">STATUS:</span>
            <span className="text-zinc-200">53 / 53 Modules Loaded</span>
          </div>
        </div>

        <iframe
          src="/educational_dashboard/PS26145_Master_Course.html"
          title="PS26145 Master Course"
          className="w-full h-[calc(100%-28px)] rounded border border-white/[0.06] bg-white"
        />
      </div>

    </div>
  )
}

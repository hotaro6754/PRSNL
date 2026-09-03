'use client'

import React, { useState, useMemo } from 'react'
import { 
  BookOpen, Search, Shield, Layers, Cpu, Radio, FileText, 
  CheckCircle2, ChevronRight, ChevronLeft, Maximize2, Minimize2, 
  Copy, Check, Lightbulb, Terminal, ArrowRight, ExternalLink, Printer
} from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { MASTER_COURSE_MODULES, CourseModule } from '@/data/masterCourseData'

const CATEGORIES = [
  'ALL',
  'Foundations',
  'Ingestion',
  'Normalization',
  'Streaming',
  'Mathematics',
  'AI / ML',
  'Risk Engine',
  'Forensics',
  'Defense Pitch'
]

export default function MasterCoursePage() {
  const [selectedId, setSelectedId] = useState<string>('mod-01')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('ALL')
  const [isFocusMode, setIsFocusMode] = useState(false)
  const [copied, setCopied] = useState(false)

  // Filter modules by category and search
  const filteredModules = useMemo(() => {
    return MASTER_COURSE_MODULES.filter((m) => {
      const matchCat = selectedCategory === 'ALL' || m.category === selectedCategory
      const query = searchQuery.toLowerCase()
      const matchSearch = 
        m.title.toLowerCase().includes(query) ||
        m.number.includes(query) ||
        m.analogy.toLowerCase().includes(query) ||
        m.conceptExplanation.toLowerCase().includes(query)
      return matchCat && matchSearch
    })
  }, [selectedCategory, searchQuery])

  // Current active module
  const currentModule = useMemo(() => {
    return MASTER_COURSE_MODULES.find((m) => m.id === selectedId) || MASTER_COURSE_MODULES[0]
  }, [selectedId])

  const currentIndex = useMemo(() => {
    return MASTER_COURSE_MODULES.findIndex((m) => m.id === selectedId)
  }, [selectedId])

  const prevModule = currentIndex > 0 ? MASTER_COURSE_MODULES[currentIndex - 1] : null
  const nextModule = currentIndex < MASTER_COURSE_MODULES.length - 1 ? MASTER_COURSE_MODULES[currentIndex + 1] : null

  const handleCopyCode = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="space-y-4 max-w-[1750px] mx-auto animate-in fade-in duration-300 font-mono text-zinc-100">
      
      {/* 1. HEADER STRIP */}
      <div className="glass-panel p-4 rounded-lg flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <h1 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-blue-400" />
              SENTINEL-26145: Zero-Knowledge Master Course
            </h1>
            <Badge variant="secure" size="xs">13 CORE MODULES</Badge>
            <Badge variant="default" size="xs">ZERO PRIOR KNOWLEDGE</Badge>
            <Badge variant="outline" size="xs">0-ACK INVARIANT</Badge>
          </div>
          <p className="text-xs text-zinc-400 font-sans">
            First-principles curriculum for beginners: from physical wire bits and kernel sockets to Shannon entropy, XGBoost, and judge defense.
          </p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <Button
            variant="outline"
            size="xs"
            onClick={() => window.open('/educational_dashboard/PS26145_Master_Course.html', '_blank')}
            icon={<ExternalLink className="w-3 h-3 text-blue-400" />}
          >
            Standalone HTML
          </Button>

          <Button
            variant="outline"
            size="xs"
            onClick={() => window.print()}
            icon={<Printer className="w-3 h-3 text-emerald-400" />}
          >
            Print PDF
          </Button>

          <Button
            variant="outline"
            size="xs"
            onClick={() => setIsFocusMode(!isFocusMode)}
            icon={isFocusMode ? <Minimize2 className="w-3 h-3 text-amber-400" /> : <Maximize2 className="w-3 h-3 text-purple-400" />}
          >
            {isFocusMode ? 'Exit Focus' : 'Focus Mode'}
          </Button>
        </div>
      </div>

      {/* 2. MAIN SPLIT INTERFACE */}
      <div className={`grid gap-4 ${isFocusMode ? 'grid-cols-1' : 'grid-cols-1 lg:grid-cols-12'}`}>
        
        {/* LEFT PANEL: MODULE SELECTOR & SEARCH */}
        {!isFocusMode && (
          <div className="lg:col-span-4 space-y-3">
            
            {/* Search Input */}
            <div className="glass-panel p-3 rounded-lg space-y-2">
              <div className="relative">
                <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
                <input
                  type="text"
                  placeholder="Search modules, terms (entropy, Zeek, SYN)..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-3 py-1.5 rounded bg-[#07080b]/90 border border-white/[0.08] text-xs text-zinc-200 placeholder:text-zinc-600 focus:outline-none focus:border-blue-500/50 font-mono"
                />
              </div>

              {/* Category Pills */}
              <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-thin">
                {CATEGORIES.map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setSelectedCategory(cat)}
                    className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider transition-all whitespace-nowrap cursor-pointer ${
                      selectedCategory === cat 
                        ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40' 
                        : 'bg-white/[0.02] text-zinc-400 hover:text-zinc-200 border border-white/[0.04]'
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            {/* Scrollable Module List */}
            <div className="glass-panel p-2 rounded-lg space-y-1.5 max-h-[720px] overflow-y-auto scrollbar-thin">
              <div className="text-[10px] text-zinc-500 px-2 py-1 font-semibold uppercase flex justify-between">
                <span>Curriculum Modules</span>
                <span>{filteredModules.length} Available</span>
              </div>

              {filteredModules.map((m) => {
                const isSelected = m.id === selectedId
                return (
                  <button
                    key={m.id}
                    onClick={() => setSelectedId(m.id)}
                    className={`w-full text-left p-2.5 rounded-md transition-all flex items-start gap-3 group cursor-pointer border ${
                      isSelected
                        ? 'bg-blue-950/40 border-blue-500/50 shadow-[0_0_15px_rgba(59,130,246,0.15)]'
                        : 'bg-[#07080b]/60 border-white/[0.04] hover:bg-white/[0.03] hover:border-white/[0.10]'
                    }`}
                  >
                    <div className={`shrink-0 w-8 h-8 rounded flex items-center justify-center font-bold text-xs font-mono border ${
                      isSelected 
                        ? 'bg-blue-500/20 text-blue-400 border-blue-500/40' 
                        : 'bg-zinc-900 text-zinc-500 border-zinc-800 group-hover:text-zinc-300'
                    }`}>
                      {m.number}
                    </div>

                    <div className="flex-1 min-w-0 space-y-1">
                      <div className="flex items-center gap-2">
                        <span className={`text-[10px] font-semibold uppercase px-1.5 py-0.2 rounded border ${
                          isSelected ? 'border-blue-500/30 text-blue-300 bg-blue-500/10' : 'border-zinc-800 text-zinc-500'
                        }`}>
                          {m.category}
                        </span>
                        <span className="text-[10px] text-zinc-500">{m.readTime}</span>
                      </div>
                      <h4 className={`text-xs font-semibold truncate ${
                        isSelected ? 'text-white' : 'text-zinc-300 group-hover:text-white'
                      }`}>
                        {m.title}
                      </h4>
                    </div>

                    <ChevronRight className={`w-4 h-4 shrink-0 mt-2 transition-transform ${
                      isSelected ? 'text-blue-400 translate-x-0.5' : 'text-zinc-600 group-hover:text-zinc-400'
                    }`} />
                  </button>
                )
              })}

              {filteredModules.length === 0 && (
                <div className="p-6 text-center text-zinc-500 text-xs">
                  No modules match '{searchQuery}'
                </div>
              )}
            </div>

          </div>
        )}

        {/* RIGHT PANEL: ACTIVE MODULE READER */}
        <div className={isFocusMode ? 'col-span-1' : 'lg:col-span-8'}>
          <div className="glass-panel p-6 rounded-lg space-y-6">
            
            {/* Header / Breadcrumb */}
            <div className="border-b border-white/[0.08] pb-4 space-y-2">
              <div className="flex items-center justify-between text-xs text-zinc-500 flex-wrap gap-2">
                <div className="flex items-center gap-2">
                  <span className="text-blue-400 font-bold uppercase">MODULE {currentModule.number}</span>
                  <span>/</span>
                  <span className="text-zinc-400">{currentModule.category}</span>
                  <span>/</span>
                  <Badge variant="secure" size="xs">{currentModule.badge}</Badge>
                </div>
                <div className="flex items-center gap-3 text-[11px]">
                  <span>Estimated Read: <strong className="text-zinc-300">{currentModule.readTime}</strong></span>
                  <span className="text-emerald-400 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> 100% Beginner Friendly
                  </span>
                </div>
              </div>

              <h2 className="text-lg md:text-xl font-bold text-white tracking-wide font-mono">
                Module {currentModule.number}: {currentModule.title}
              </h2>
            </div>

            {/* 1. ANALOGY CARD */}
            <div className="p-4 rounded-lg bg-amber-500/[0.04] border border-amber-500/20 space-y-2">
              <div className="flex items-center gap-2 text-amber-400 text-xs font-bold uppercase tracking-wider">
                <Lightbulb className="w-4 h-4" />
                1. What is it? (Real-World Analogy for Beginners)
              </div>
              <p className="text-xs md:text-sm text-amber-200/90 leading-relaxed font-sans">
                {currentModule.analogy}
              </p>
            </div>

            {/* 2. IN-DEPTH CONCEPT */}
            <div className="space-y-2">
              <h3 className="text-xs font-bold text-blue-400 uppercase tracking-wider flex items-center gap-2">
                <Shield className="w-3.5 h-3.5" />
                2. In-Depth Technical Mechanics & Unidirectional Invariants
              </h3>
              <div className="p-4 rounded-lg bg-[#07080b]/80 border border-white/[0.06] text-xs md:text-sm text-zinc-300 leading-relaxed font-sans">
                {currentModule.conceptExplanation}
              </div>
            </div>

            {/* 3. STEP-BY-STEP WORKFLOW DIAGRAM */}
            <div className="space-y-2">
              <h3 className="text-xs font-bold text-purple-400 uppercase tracking-wider flex items-center gap-2">
                <Layers className="w-3.5 h-3.5" />
                3. System Architecture & Workflow Pipeline
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 pt-1">
                {currentModule.workflow.map((w, idx) => (
                  <div key={idx} className="p-3 rounded-lg bg-[#090b0e] border border-white/[0.06] flex items-start gap-3 hover:border-purple-500/30 transition-all">
                    <div className="w-6 h-6 rounded bg-purple-500/20 border border-purple-500/40 text-purple-300 font-bold text-xs flex items-center justify-center shrink-0 font-mono mt-0.5">
                      {idx + 1}
                    </div>
                    <div className="space-y-1 min-w-0">
                      <div className="text-xs font-bold text-white">{w.step}</div>
                      <div className="text-[11px] text-zinc-400 font-sans leading-relaxed">{w.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 4. REAL CODE / CLI IMPLEMENTATION */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-2">
                  <Terminal className="w-3.5 h-3.5" />
                  4. Working Implementation ({currentModule.codeLanguage.toUpperCase()})
                </h3>
                <button
                  onClick={() => handleCopyCode(currentModule.codeSnippet)}
                  className="px-2.5 py-1 rounded bg-zinc-900 border border-zinc-700 hover:border-emerald-500/50 text-[11px] text-zinc-300 hover:text-white flex items-center gap-1.5 transition-all cursor-pointer"
                >
                  {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3 text-zinc-400" />}
                  <span>{copied ? 'Copied!' : 'Copy Code'}</span>
                </button>
              </div>

              <div className="rounded-lg overflow-hidden border border-white/[0.08] bg-[#050608]">
                <div className="px-3 py-1.5 bg-white/[0.02] border-b border-white/[0.06] flex items-center justify-between text-[10px] text-zinc-500">
                  <span>SENTINEL-26145 REFERENCE IMPLEMENTATION</span>
                  <span>{currentModule.codeLanguage}</span>
                </div>
                <pre className="p-4 text-xs font-mono text-emerald-300/90 overflow-x-auto leading-relaxed scrollbar-thin">
                  <code>{currentModule.codeSnippet}</code>
                </pre>
              </div>
            </div>

            {/* 5. LINE-BY-LINE EXPLANATION */}
            <div className="space-y-2">
              <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-wider flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-blue-400" />
                5. Line-by-Line Code Breakdown
              </h3>
              <div className="space-y-1.5">
                {currentModule.lineByLine.map((line, idx) => (
                  <div key={idx} className="p-2.5 rounded bg-white/[0.015] border border-white/[0.04] text-xs flex items-start gap-2.5">
                    <span className="text-blue-400 font-bold shrink-0">[{idx + 1}]</span>
                    <span className="text-zinc-300 font-sans leading-relaxed">{line}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* 6. SUMMARY & DEFENSE TAKEAWAY */}
            <div className="p-4 rounded-lg bg-blue-950/20 border border-blue-500/30 space-y-2">
              <div className="text-xs font-bold text-blue-300 uppercase tracking-wider">
                6. Summary & Defense Judge Takeaway
              </div>
              <p className="text-xs md:text-sm text-zinc-200 font-sans leading-relaxed">
                {currentModule.summary}
              </p>
              <div className="pt-2 border-t border-blue-500/20 flex items-center gap-2 text-xs text-emerald-300 font-semibold">
                <span className="text-amber-400 font-bold">GOLDEN VERDICT:</span>
                <span>{currentModule.takeaway}</span>
              </div>
            </div>

            {/* 7. PREV / NEXT NAVIGATION */}
            <div className="pt-4 border-t border-white/[0.08] flex items-center justify-between flex-wrap gap-2">
              {prevModule ? (
                <Button
                  variant="outline"
                  size="xs"
                  onClick={() => setSelectedId(prevModule.id)}
                  icon={<ChevronLeft className="w-3.5 h-3.5" />}
                >
                  Prev: Module {prevModule.number}
                </Button>
              ) : <div />}

              <div className="text-xs text-zinc-500 font-mono">
                Module {currentModule.number} of {MASTER_COURSE_MODULES.length}
              </div>

              {nextModule ? (
                <Button
                  variant="outline"
                  size="xs"
                  onClick={() => setSelectedId(nextModule.id)}
                  icon={<ChevronRight className="w-3.5 h-3.5" />}
                >
                  Next: Module {nextModule.number}
                </Button>
              ) : <div />}
            </div>

          </div>
        </div>

      </div>

    </div>
  )
}

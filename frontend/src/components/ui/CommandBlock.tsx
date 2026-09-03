'use client'

import React, { useState } from 'react'
import { Copy, Check, Terminal } from 'lucide-react'

interface CommandBlockProps {
  command: string
  label?: string
  className?: string
}

export function CommandBlock({ command, label, className = '' }: CommandBlockProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(command)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className={`rounded border border-white/[0.08] bg-[#07080a] overflow-hidden font-mono text-xs ${className}`}>
      {label && (
        <div className="px-2.5 py-1 bg-[#0d0f14] border-b border-white/[0.06] text-[10px] uppercase tracking-wider text-zinc-500 font-semibold flex items-center justify-between">
          <span className="flex items-center gap-1.5">
            <Terminal className="w-3 h-3 text-zinc-500" />
            {label}
          </span>
        </div>
      )}
      <div className="p-2 flex items-center justify-between gap-3">
        <code className="text-zinc-200 truncate select-all">
          <span className="text-zinc-600 mr-1.5 select-none">$</span>
          {command}
        </code>
        <button
          onClick={handleCopy}
          className="p-1 rounded hover:bg-white/[0.06] text-zinc-500 hover:text-zinc-300 transition-colors shrink-0 cursor-pointer"
          title="Copy command to clipboard"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
        </button>
      </div>
    </div>
  )
}

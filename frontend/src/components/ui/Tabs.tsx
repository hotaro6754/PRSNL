'use client'

import React from 'react'

interface TabItem {
  id: string
  label: string
  badge?: string | number
  icon?: React.ReactNode
}

interface TabsProps {
  items: TabItem[]
  activeTab: string
  onChange: (id: string) => void
  size?: 'sm' | 'md'
  className?: string
}

export function Tabs({
  items,
  activeTab,
  onChange,
  size = 'sm',
  className = ''
}: TabsProps) {
  const pad = size === 'sm' ? 'px-2.5 py-1 text-xs' : 'px-3 py-1.5 text-xs'

  return (
    <div className={`inline-flex items-center p-0.5 rounded-md bg-[#0d0f14] border border-white/[0.08] font-mono ${className}`}>
      {items.map((tab) => {
        const isActive = activeTab === tab.id
        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={`inline-flex items-center gap-1.5 rounded transition-all cursor-pointer select-none ${pad} ${
              isActive
                ? 'bg-white/[0.08] text-white font-semibold shadow-sm border border-white/[0.06]'
                : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.03]'
            }`}
          >
            {tab.icon && <span className="shrink-0">{tab.icon}</span>}
            <span>{tab.label}</span>
            {tab.badge !== undefined && (
              <span className={`text-[10px] px-1 rounded ${isActive ? 'bg-blue-500/20 text-blue-300' : 'bg-white/[0.06] text-zinc-500'}`}>
                {tab.badge}
              </span>
            )}
          </button>
        )
      })}
    </div>
  )
}

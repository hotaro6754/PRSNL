import React from 'react'

interface StatCardProps {
  label: string
  value: string | number
  subtext?: string
  icon?: React.ReactNode
  badge?: React.ReactNode
  highlight?: 'default' | 'critical' | 'secure' | 'warning'
  className?: string
}

export function StatCard({
  label,
  value,
  subtext,
  icon,
  badge,
  highlight = 'default',
  className = ''
}: StatCardProps) {
  const highlightStyles = {
    default: 'text-zinc-100',
    critical: 'text-red-400',
    secure: 'text-emerald-400',
    warning: 'text-amber-400'
  }

  return (
    <div className={`p-4 rounded-lg border border-white/[0.08] bg-[#111318] flex flex-col justify-between ${className}`}>
      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          {icon && <span className="text-zinc-400 text-sm">{icon}</span>}
          <span className="text-[11px] font-semibold tracking-wider text-zinc-400 uppercase font-mono">{label}</span>
        </div>
        {badge}
      </div>
      <div>
        <div className={`text-2xl font-bold font-mono tracking-tight ${highlightStyles[highlight]}`}>
          {value}
        </div>
        {subtext && (
          <div className="text-[11px] text-zinc-400 mt-1 font-mono leading-tight truncate">
            {subtext}
          </div>
        )}
      </div>
    </div>
  )
}

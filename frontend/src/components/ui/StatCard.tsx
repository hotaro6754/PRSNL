import React from 'react'
import { Sparkline } from './Sparkline'

interface StatCardProps {
  label: string
  value: string | number
  subtext?: string
  trend?: string
  sparklineData?: number[]
  sparklineColor?: string
  icon?: React.ReactNode
  badge?: React.ReactNode
  highlight?: 'default' | 'critical' | 'secure' | 'warning' | 'info'
  className?: string
}

export function StatCard({
  label,
  value,
  subtext,
  trend,
  sparklineData,
  sparklineColor,
  icon,
  badge,
  highlight = 'default',
  className = ''
}: StatCardProps) {
  const highlightStyles = {
    default: 'text-zinc-100',
    critical: 'text-red-400',
    secure: 'text-emerald-400',
    warning: 'text-amber-400',
    info: 'text-blue-400'
  }

  const defaultSparkColors: Record<string, string> = {
    default: '#3b82f6',
    critical: '#ef4444',
    secure: '#10b981',
    warning: '#f59e0b',
    info: '#3b82f6'
  }

  const color = sparklineColor || defaultSparkColors[highlight]

  return (
    <div className={`p-4 rounded-lg border border-white/[0.08] bg-[#111318]/80 backdrop-blur-md shadow-[0_4px_20px_-2px_rgba(0,0,0,0.35)] hover:border-white/[0.14] transition-all flex flex-col justify-between group ${className}`}>
      {/* Top row: Label + Icon + Badge */}
      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-2 truncate">
          {icon && <span className="text-zinc-400 shrink-0">{icon}</span>}
          <span className="text-[10px] font-semibold tracking-wider text-zinc-400 uppercase font-mono truncate">
            {label}
          </span>
        </div>
        {badge}
      </div>

      {/* Middle row: Big Value + Bklit Trend + Sparkline */}
      <div className="flex items-end justify-between gap-2 my-1">
        <div>
          <div className={`text-2xl font-bold font-mono tracking-tight leading-none ${highlightStyles[highlight]}`}>
            {value}
          </div>
          {trend && (
            <div className="text-[10px] font-mono text-zinc-400 mt-1 flex items-center gap-1">
              <span className={highlight === 'critical' ? 'text-red-400 font-semibold' : highlight === 'secure' ? 'text-emerald-400 font-semibold' : 'text-zinc-300'}>
                {trend}
              </span>
            </div>
          )}
        </div>

        {sparklineData && (
          <Sparkline
            data={sparklineData}
            color={color}
            height={28}
            width={68}
            className="opacity-85 group-hover:opacity-100 transition-opacity"
          />
        )}
      </div>

      {/* Bottom row: Subtext explanation */}
      {subtext && (
        <div className="text-[10px] text-zinc-500 mt-2 font-mono leading-tight truncate border-t border-white/[0.04] pt-2">
          {subtext}
        </div>
      )}
    </div>
  )
}

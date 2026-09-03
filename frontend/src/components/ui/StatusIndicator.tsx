import React from 'react'

export type StatusType = 'secure' | 'critical' | 'warning' | 'info' | 'offline' | 'neutral'

interface StatusIndicatorProps {
  status: StatusType
  label?: string
  sublabel?: string
  size?: 'sm' | 'md'
  className?: string
}

const statusColors: Record<StatusType, { dot: string, text: string }> = {
  secure: { dot: 'bg-emerald-500', text: 'text-emerald-400' },
  critical: { dot: 'bg-red-500', text: 'text-red-400' },
  warning: { dot: 'bg-amber-500', text: 'text-amber-400' },
  info: { dot: 'bg-blue-500', text: 'text-blue-400' },
  offline: { dot: 'bg-zinc-600', text: 'text-zinc-500' },
  neutral: { dot: 'bg-zinc-400', text: 'text-zinc-300' },
}

export function StatusIndicator({
  status,
  label,
  sublabel,
  size = 'sm',
  className = ''
}: StatusIndicatorProps) {
  const c = statusColors[status] || statusColors.neutral
  const dotSize = size === 'sm' ? 'w-1.5 h-1.5' : 'w-2 h-2'

  return (
    <div className={`inline-flex items-center gap-2 font-mono ${className}`}>
      <span className={`${dotSize} rounded-full shrink-0 ${c.dot}`} />
      {label && (
        <div className="flex flex-col leading-none">
          <span className={`text-xs font-semibold tracking-wider uppercase ${c.text}`}>
            {label}
          </span>
          {sublabel && (
            <span className="text-[10px] text-zinc-500 font-normal mt-0.5">
              {sublabel}
            </span>
          )}
        </div>
      )}
    </div>
  )
}

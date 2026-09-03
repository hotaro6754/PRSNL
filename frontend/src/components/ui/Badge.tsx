import React from 'react'

export type BadgeVariant = 'critical' | 'warning' | 'secure' | 'info' | 'neutral' | 'purple'

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant
  size?: 'xs' | 'sm'
  dot?: boolean
  children: React.ReactNode
}

const variantStyles: Record<BadgeVariant, { bg: string, text: string, border: string, dot: string }> = {
  critical: {
    bg: 'bg-red-500/10',
    text: 'text-red-400',
    border: 'border-red-500/20',
    dot: 'bg-red-500'
  },
  warning: {
    bg: 'bg-amber-500/10',
    text: 'text-amber-400',
    border: 'border-amber-500/20',
    dot: 'bg-amber-500'
  },
  secure: {
    bg: 'bg-emerald-500/10',
    text: 'text-emerald-400',
    border: 'border-emerald-500/20',
    dot: 'bg-emerald-500'
  },
  info: {
    bg: 'bg-blue-500/10',
    text: 'text-blue-400',
    border: 'border-blue-500/20',
    dot: 'bg-blue-500'
  },
  neutral: {
    bg: 'bg-zinc-800/60',
    text: 'text-zinc-300',
    border: 'border-zinc-700/50',
    dot: 'bg-zinc-400'
  },
  purple: {
    bg: 'bg-purple-500/10',
    text: 'text-purple-400',
    border: 'border-purple-500/20',
    dot: 'bg-purple-500'
  }
}

export function Badge({
  variant = 'neutral',
  size = 'xs',
  dot = false,
  className = '',
  children,
  ...props
}: BadgeProps) {
  const v = variantStyles[variant] || variantStyles.neutral
  const sizeClasses = size === 'xs' 
    ? 'text-[10px] px-1.5 py-0.5 leading-none' 
    : 'text-xs px-2 py-0.5 leading-tight'

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-mono font-medium rounded border tracking-wider uppercase transition-colors ${v.bg} ${v.text} ${v.border} ${sizeClasses} ${className}`}
      {...props}
    >
      {dot && <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${v.dot}`} />}
      <span>{children}</span>
    </span>
  )
}

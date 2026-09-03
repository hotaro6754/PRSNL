import React from 'react'

interface EmptyStateProps {
  icon?: React.ReactNode
  title: string
  description?: string
  action?: React.ReactNode
  className?: string
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  className = ''
}: EmptyStateProps) {
  return (
    <div className={`p-10 flex flex-col items-center justify-center text-center font-mono ${className}`}>
      {icon && <div className="text-zinc-600 mb-3">{icon}</div>}
      <h3 className="text-xs font-semibold text-zinc-300 uppercase tracking-wider mb-1">
        {title}
      </h3>
      {description && (
        <p className="text-[11px] text-zinc-500 max-w-sm leading-relaxed mb-4">
          {description}
        </p>
      )}
      {action}
    </div>
  )
}

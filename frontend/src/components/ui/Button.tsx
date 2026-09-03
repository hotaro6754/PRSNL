import React from 'react'

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline'
export type ButtonSize = 'xs' | 'sm' | 'md'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
  loading?: boolean
  icon?: React.ReactNode
  children?: React.ReactNode
}

const variantStyles: Record<ButtonVariant, string> = {
  primary: 'bg-blue-600 hover:bg-blue-500 text-white shadow-sm border border-blue-500/50',
  secondary: 'bg-zinc-800/80 hover:bg-zinc-700 text-zinc-200 border border-zinc-700/60',
  ghost: 'bg-transparent hover:bg-white/[0.06] text-zinc-400 hover:text-zinc-100',
  danger: 'bg-red-600/10 hover:bg-red-600/20 text-red-400 border border-red-500/30',
  outline: 'bg-transparent hover:bg-white/[0.04] text-zinc-300 border border-white/10 hover:border-white/20'
}

const sizeStyles: Record<ButtonSize, string> = {
  xs: 'h-7 px-2.5 text-[11px] gap-1.5 rounded',
  sm: 'h-8 px-3 text-xs gap-2 rounded-md',
  md: 'h-9 px-4 text-sm gap-2.5 rounded-md'
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({
  variant = 'secondary',
  size = 'sm',
  loading = false,
  icon,
  className = '',
  disabled,
  children,
  ...props
}, ref) => {
  return (
    <button
      ref={ref}
      disabled={disabled || loading}
      className={`inline-flex items-center justify-center font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-blue-500/50 select-none ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
      {...props}
    >
      {loading ? (
        <span className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin shrink-0" />
      ) : icon ? (
        <span className="shrink-0">{icon}</span>
      ) : null}
      {children}
    </button>
  )
})
Button.displayName = 'Button'

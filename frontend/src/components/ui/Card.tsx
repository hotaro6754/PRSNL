import React from 'react'

export function Card({
  className = '',
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={`rounded-lg border border-white/[0.08] bg-[#111318]/85 backdrop-blur-md text-zinc-100 shadow-[0_4px_24px_-1px_rgba(0,0,0,0.35)] ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

export function CardHeader({
  className = '',
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={`flex flex-col space-y-1 p-4 sm:p-5 border-b border-white/[0.06] ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

export function CardTitle({
  className = '',
  children,
  ...props
}: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3
      className={`text-xs font-semibold uppercase tracking-wider text-zinc-400 font-mono ${className}`}
      {...props}
    >
      {children}
    </h3>
  )
}

export function CardDescription({
  className = '',
  children,
  ...props
}: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p
      className={`text-xs text-zinc-400 leading-relaxed ${className}`}
      {...props}
    >
      {children}
    </p>
  )
}

export function CardContent({
  className = '',
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`p-4 sm:p-5 ${className}`} {...props}>
      {children}
    </div>
  )
}

export function CardFooter({
  className = '',
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={`flex items-center p-4 border-t border-white/[0.06] bg-[#0c0e12]/50 ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

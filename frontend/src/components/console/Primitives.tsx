'use client'

import React from 'react'
import Link from 'next/link'
import type { Alert } from '@/lib/api'
import { ApiError } from '@/lib/api'

const SEVERITY_STYLE: Record<string, string> = {
  critical: 'bg-red-500/15 text-red-300 border-red-500/40',
  high: 'bg-orange-500/15 text-orange-300 border-orange-500/40',
  medium: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
  low: 'bg-slate-500/15 text-slate-300 border-slate-500/30',
}

export function SeverityPill({ severity }: { severity: string }) {
  return (
    <span className={`inline-flex items-center rounded border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${SEVERITY_STYLE[severity] ?? SEVERITY_STYLE.low}`}>
      {severity}
    </span>
  )
}

export function StatusPill({ status }: { status: string }) {
  const style =
    status === 'open' ? 'text-sky-300 border-sky-500/40 bg-sky-500/10'
    : status === 'investigating' ? 'text-amber-300 border-amber-500/40 bg-amber-500/10'
    : status === 'completed' || status === 'closed' ? 'text-emerald-300 border-emerald-500/40 bg-emerald-500/10'
    : status === 'running' ? 'text-sky-300 border-sky-500/40 bg-sky-500/10'
    : status === 'failed' ? 'text-red-300 border-red-500/40 bg-red-500/10'
    : 'text-slate-300 border-slate-500/30 bg-slate-500/10'
  return <span className={`inline-flex items-center rounded border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${style}`}>{status.replace('_', ' ')}</span>
}

export function Confidence({ value }: { value: number }) {
  const pct = Math.round(value * 100)
  return (
    <span className="inline-flex items-center gap-2 tabular-nums">
      <span className="relative h-1.5 w-12 overflow-hidden rounded-sm bg-white/10" aria-hidden>
        <span className="absolute inset-y-0 left-0 bg-sky-400" style={{ width: `${pct}%` }} />
      </span>
      <span>{value.toFixed(2)}</span>
    </span>
  )
}

export function Panel({ title, action, children, className = '' }: { title?: React.ReactNode; action?: React.ReactNode; children: React.ReactNode; className?: string }) {
  return (
    <section className={`rounded-md border border-[var(--line)] bg-[var(--surface)] ${className}`}>
      {(title || action) && (
        <header className="flex items-center justify-between gap-3 border-b border-[var(--line)] px-4 py-2.5">
          <h2 className="text-[11px] font-semibold uppercase tracking-[0.08em] text-[var(--muted)]">{title}</h2>
          {action}
        </header>
      )}
      <div>{children}</div>
    </section>
  )
}

export function KeyValue({ rows }: { rows: [React.ReactNode, React.ReactNode][] }) {
  return (
    <dl className="grid grid-cols-[minmax(120px,max-content)_1fr] gap-x-6 gap-y-1.5 px-4 py-3 text-xs">
      {rows.map(([k, v], i) => (
        <React.Fragment key={i}>
          <dt className="text-[var(--muted)]">{k}</dt>
          <dd className="min-w-0 break-words font-mono text-[var(--text)]">{v}</dd>
        </React.Fragment>
      ))}
    </dl>
  )
}

export function ErrorNotice({ error, what }: { error: Error | null; what: string }) {
  if (!error) return null
  const status = error instanceof ApiError ? error.status : 0
  const message =
    status === 401 ? `Sign-in needed to load ${what}. Enter the analyst token on the Sensor page.`
    : status === 404 ? `${what[0].toUpperCase()}${what.slice(1)} not available: ${error.message}`
    : status === 0 ? `Cannot reach the Sentinel API to load ${what}. Check that the backend is running.`
    : `Could not load ${what}: ${error.message}`
  return <div className="rounded-md border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-xs text-amber-200">{message}</div>
}

export function Empty({ children }: { children: React.ReactNode }) {
  return <div className="px-4 py-8 text-center text-xs text-[var(--muted)]">{children}</div>
}

export function ClassCell({ alert }: { alert: Pick<Alert, 'threat_class' | 'category' | 'attack_technique'> }) {
  return (
    <span className="flex flex-col">
      <span className="font-mono text-[var(--text)]">{alert.threat_class}</span>
      <span className="text-[10px] text-[var(--muted)]">
        PS ({alert.category}) · {alert.attack_technique}
      </span>
    </span>
  )
}

export function AlertRowLink({ id, children }: { id: string; children: React.ReactNode }) {
  return (
    <Link href={`/alerts/${id}`} className="block hover:text-sky-300 focus-visible:outline focus-visible:outline-1 focus-visible:outline-sky-400">
      {children}
    </Link>
  )
}

export function PageTitle({ title, subtitle, action }: { title: string; subtitle?: React.ReactNode; action?: React.ReactNode }) {
  return (
    <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 className="text-lg font-semibold tracking-tight text-[var(--text)]">{title}</h1>
        {subtitle && <p className="mt-0.5 text-xs text-[var(--muted)]">{subtitle}</p>}
      </div>
      {action}
    </div>
  )
}

export const th = 'px-3 py-2 text-left text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--muted)]'
export const td = 'px-3 py-2 align-top'

export function Btn({ children, onClick, disabled, kind = 'default', type = 'button' }: { children: React.ReactNode; onClick?: () => void; disabled?: boolean; kind?: 'default' | 'primary' | 'danger'; type?: 'button' | 'submit' }) {
  const style =
    kind === 'primary' ? 'border-sky-500/60 bg-sky-500/20 text-sky-100 hover:bg-sky-500/30'
    : kind === 'danger' ? 'border-red-500/50 bg-red-500/10 text-red-200 hover:bg-red-500/20'
    : 'border-[var(--line-strong)] bg-transparent text-[var(--text)] hover:bg-white/5'
  return (
    <button type={type} onClick={onClick} disabled={disabled} className={`inline-flex h-7 items-center gap-1.5 rounded border px-2.5 text-xs font-medium disabled:cursor-not-allowed disabled:opacity-40 focus-visible:outline focus-visible:outline-1 focus-visible:outline-sky-400 ${style}`}>
      {children}
    </button>
  )
}

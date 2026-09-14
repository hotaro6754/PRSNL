'use client'

import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { api, type StreamEvent } from '@/lib/api'
import { LiveEventsProvider, useStreamStatus } from '@/components/console/LiveEvents'

const NAV = [
  { href: '/', label: 'Overview' },
  { href: '/alerts', label: 'Alerts' },
  { href: '/cases', label: 'Cases' },
  { href: '/hunt', label: 'Retro-hunt' },
  { href: '/evaluation', label: 'Evaluation' },
  { href: '/sensor', label: 'Sensor' },
  { href: '/audit', label: 'Audit' },
]

function StreamIndicator() {
  const status = useStreamStatus()
  const dot = status === 'live' ? 'bg-emerald-400' : status === 'connecting' ? 'bg-amber-400' : 'bg-red-400'
  const text = status === 'live' ? 'Live stream connected' : status === 'connecting' ? 'Connecting to stream' : 'Stream offline'
  return (
    <span className="inline-flex items-center gap-1.5" role="status">
      <span className={`h-1.5 w-1.5 rounded-full ${dot}`} aria-hidden />
      {text}
    </span>
  )
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const [job, setJob] = useState<any>(null)
  const [sensorId, setSensorId] = useState('')

  useEffect(() => {
    api<any>('/api/health')
      .then((h) => {
        setSensorId(h.sensor_id)
        setJob(h.job)
      })
      .catch(() => setSensorId(''))
  }, [])

  const onEvent = (event: StreamEvent) => {
    if (event.type === 'heartbeat') setJob(event.data.job)
    if (event.type === 'progress') setJob((j: any) => ({ ...(j ?? {}), status: 'running', progress: event.data }))
    if (event.type === 'source_finished') setJob((j: any) => ({ ...(j ?? {}), status: event.data.status }))
  }

  return (
    <LiveEventsProvider onEvent={onEvent}>
      <div className="flex min-h-screen flex-col">
        <header className="sticky top-0 z-20 border-b border-[var(--line)] bg-[var(--ground)]">
          <div className="mx-auto flex max-w-[1440px] flex-wrap items-center gap-x-6 gap-y-2 px-4 py-2.5 sm:px-6">
            <Link href="/" className="flex items-baseline gap-2">
              <span className="font-mono text-sm font-semibold tracking-tight text-[var(--text)]">SENTINEL-26145</span>
              <span className="hidden text-[11px] text-[var(--muted)] sm:inline">passive one-way traffic detection</span>
            </Link>
            <nav className="flex flex-wrap items-center gap-1" aria-label="Primary">
              {NAV.map((item) => {
                const active = item.href === '/' ? pathname === '/' : pathname.startsWith(item.href)
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    aria-current={active ? 'page' : undefined}
                    className={`rounded px-2.5 py-1 text-xs font-medium ${active ? 'bg-white/10 text-[var(--text)]' : 'text-[var(--muted)] hover:bg-white/5 hover:text-[var(--text)]'}`}
                  >
                    {item.label}
                  </Link>
                )
              })}
            </nav>
            <div className="ml-auto flex items-center gap-4 text-[11px] text-[var(--muted)]">
              {job?.status === 'running' && (
                <span className="font-mono">
                  processing {job.capture ?? 'capture'}
                  {job.progress ? ` · ${Number(job.progress.packets).toLocaleString('en-US')} pkts · ${job.progress.alerts} alerts` : ''}
                </span>
              )}
              {sensorId && <span className="font-mono">{sensorId}</span>}
              <StreamIndicator />
            </div>
          </div>
        </header>
        <main className="mx-auto w-full max-w-[1440px] flex-1 px-4 py-5 sm:px-6">{children}</main>
        <footer className="border-t border-[var(--line)] px-6 py-3 text-center text-[10px] text-[var(--muted)]">
          Receive-only sensor. Alerts are intelligence for operators outside the enclave; nothing is sent back across the monitored link.
        </footer>
      </div>
    </LiveEventsProvider>
  )
}

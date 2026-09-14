'use client'

import React, { useCallback, useRef } from 'react'
import Link from 'next/link'
import { useApi, type Alert } from '@/lib/api'
import { useLiveEvents } from '@/components/console/LiveEvents'
import { CATEGORY_TITLES, fmtBytes, fmtNum, fmtTime, shortHash } from '@/components/console/format'
import { ClassCell, Confidence, Empty, ErrorNotice, PageTitle, Panel, SeverityPill, td, th } from '@/components/console/Primitives'

interface Overview {
  window_hours: number
  window_anchor: number
  counts: { total: number; by_class: Record<string, number>; by_severity: Record<string, number> }
  categories: Record<string, { title: string; classes: { threat_class: string; title: string; technique: string; count: number }[] }>
  open_cases: number
  recent_sources: any[]
  chain_head: Alert['custody'] | null
}

export default function OverviewPage() {
  const overview = useApi<Overview>('/api/overview?hours=24')
  const recent = useApi<Alert[]>('/api/alerts?limit=12')
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const onEvent = useCallback(
    (event: { type: string }) => {
      if (event.type !== 'alert' && event.type !== 'source_finished') return
      if (timer.current) clearTimeout(timer.current)
      timer.current = setTimeout(() => {
        overview.reload()
        recent.reload()
      }, 750)
    },
    [overview, recent],
  )
  useLiveEvents(onEvent)

  const o = overview.data
  const severities = ['critical', 'high', 'medium', 'low']

  return (
    <div className="space-y-4">
      <PageTitle
        title="Overview"
        subtitle={o ? `Alerts in the 24 h up to the latest observation (${fmtTime(o.window_anchor)})` : 'Detections across the six problem-statement threat categories'}
      />
      <ErrorNotice error={overview.error} what="the overview" />

      {o && (
        <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
          <Panel title="Threat categories (PS 26145 a–f)">
            <table className="w-full text-xs">
              <thead className="border-b border-[var(--line)]">
                <tr>
                  <th className={th}>Category</th>
                  <th className={th}>Detector classes</th>
                  <th className={`${th} text-right`}>Alerts</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--line)]">
                {Object.entries(o.categories).map(([cat, group]) => {
                  const total = group.classes.reduce((s, c) => s + c.count, 0)
                  return (
                    <tr key={cat}>
                      <td className={`${td} w-[34%]`}>
                        <span className="mr-2 font-mono text-[var(--muted)]">({cat})</span>
                        {CATEGORY_TITLES[cat]}
                      </td>
                      <td className={td}>
                        <div className="flex flex-wrap gap-x-4 gap-y-1">
                          {group.classes.map((c) => (
                            <Link key={c.threat_class} href={`/alerts?threat_class=${c.threat_class}`} className="font-mono hover:text-sky-300">
                              {c.threat_class} <span className={c.count ? 'text-[var(--text)]' : 'text-[var(--muted)]'}>{c.count}</span>
                            </Link>
                          ))}
                        </div>
                      </td>
                      <td className={`${td} text-right font-mono text-sm ${total ? 'text-[var(--text)]' : 'text-[var(--muted)]'}`}>{total}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </Panel>

          <div className="space-y-4">
            <Panel title="Severity">
              <div className="grid grid-cols-4 divide-x divide-[var(--line)]">
                {severities.map((s) => (
                  <div key={s} className="px-3 py-3">
                    <div className="font-mono text-xl text-[var(--text)]">{o.counts.by_severity[s] ?? 0}</div>
                    <div className="mt-1"><SeverityPill severity={s} /></div>
                  </div>
                ))}
              </div>
              <div className="border-t border-[var(--line)] px-4 py-2.5 text-xs text-[var(--muted)]">
                <Link href="/cases" className="hover:text-sky-300">{o.open_cases} open case{o.open_cases === 1 ? '' : 's'}</Link>
              </div>
            </Panel>
            <Panel title="Custody chain head">
              {o.chain_head ? (
                <div className="px-4 py-3 text-xs">
                  <div className="text-[var(--muted)]">record #{o.chain_head.seq}</div>
                  <div className="mt-1 break-all font-mono">{o.chain_head.hash}</div>
                  <Link href="/sensor#custody" className="mt-2 inline-block text-sky-300 hover:underline">Verify chain</Link>
                </div>
              ) : (
                <Empty>No alerts recorded yet.</Empty>
              )}
            </Panel>
          </div>
        </div>
      )}

      <Panel title="Latest alerts" action={<Link href="/alerts" className="text-xs text-sky-300 hover:underline">All alerts</Link>}>
        <ErrorNotice error={recent.error} what="alerts" />
        {recent.data && recent.data.length === 0 && <Empty>No alerts yet. Replay or upload a capture on the Sensor page.</Empty>}
        {recent.data && recent.data.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead className="border-b border-[var(--line)]">
                <tr>
                  <th className={th}>Event time</th>
                  <th className={th}>Severity</th>
                  <th className={th}>Class</th>
                  <th className={th}>Title</th>
                  <th className={th}>Source → destination</th>
                  <th className={th}>Confidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--line)]">
                {recent.data.map((a) => (
                  <tr key={a.alert_id} className="hover:bg-white/[0.03]">
                    <td className={`${td} whitespace-nowrap font-mono`}>{fmtTime(a.event_time)}</td>
                    <td className={td}><SeverityPill severity={a.severity} /></td>
                    <td className={td}><ClassCell alert={a} /></td>
                    <td className={td}><Link href={`/alerts/${a.alert_id}`} className="hover:text-sky-300">{a.title}</Link></td>
                    <td className={`${td} font-mono`}>{a.src} → {a.dst}{a.dport ? `:${a.dport}` : ''}</td>
                    <td className={td}><Confidence value={a.confidence} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>

      {o && o.recent_sources.length > 0 && (
        <Panel title="Recent capture sources" action={<Link href="/sensor" className="text-xs text-sky-300 hover:underline">Sensor</Link>}>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead className="border-b border-[var(--line)]">
                <tr>
                  <th className={th}>Source</th><th className={th}>Status</th><th className={`${th} text-right`}>Packets</th>
                  <th className={`${th} text-right`}>Traffic</th><th className={`${th} text-right`}>Throughput</th><th className={th}>SHA-256</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--line)]">
                {o.recent_sources.map((s) => (
                  <tr key={s.source_id}>
                    <td className={`${td} font-mono`}>{s.label ?? s.source_id}</td>
                    <td className={td}>{s.status}</td>
                    <td className={`${td} text-right font-mono`}>{fmtNum(s.packets)}</td>
                    <td className={`${td} text-right font-mono`}>{fmtBytes(s.bytes)}</td>
                    <td className={`${td} text-right font-mono`}>{s.stats?.packets_per_s ? `${fmtNum(s.stats.packets_per_s)} pkt/s` : '—'}</td>
                    <td className={`${td} font-mono text-[var(--muted)]`}>{shortHash(s.sha256, 16)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      )}
    </div>
  )
}

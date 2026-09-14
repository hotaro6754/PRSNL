'use client'

import React, { Suspense, useCallback, useState } from 'react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { exportAlerts, useApi, type Alert } from '@/lib/api'
import { useLiveEvents } from '@/components/console/LiveEvents'
import { fmtTime } from '@/components/console/format'
import { Btn, ClassCell, Confidence, Empty, ErrorNotice, PageTitle, Panel, SeverityPill, td, th } from '@/components/console/Primitives'

const CLASSES = ['ddos.syn_flood', 'ddos.udp_amplification', 'ddos.udp_flood', 'c2.beaconing', 'dns.dga', 'dns.tunnel',
  'tls.known_bad_fingerprint', 'tls.suspicious_session', 'recon.scan', 'exfil.volume']
const PAGE = 100

function AlertsView() {
  const router = useRouter()
  const params = useSearchParams()
  const threatClass = params.get('threat_class') ?? ''
  const severity = params.get('severity') ?? ''
  const entity = params.get('entity') ?? ''
  const [offset, setOffset] = useState(0)
  const [fresh, setFresh] = useState<Set<string>>(new Set())

  const query = new URLSearchParams({ limit: String(PAGE), offset: String(offset) })
  if (threatClass) query.set('threat_class', threatClass)
  if (severity) query.set('severity', severity)
  if (entity) query.set('entity', entity)
  const alerts = useApi<Alert[]>(`/api/alerts?${query}`)

  const setFilter = (key: string, value: string) => {
    const next = new URLSearchParams(params.toString())
    if (value) next.set(key, value)
    else next.delete(key)
    setOffset(0)
    router.replace(`/alerts${next.toString() ? `?${next}` : ''}`)
  }

  const onEvent = useCallback(
    (event: { type: string; data: any }) => {
      if (event.type !== 'alert' || offset !== 0) return
      const a = event.data as Alert
      if ((threatClass && a.threat_class !== threatClass) || (severity && a.severity !== severity)) return
      if (entity && a.src !== entity && a.dst !== entity) return
      alerts.setData((prev) => (prev ? [a, ...prev.filter((x) => x.alert_id !== a.alert_id)].slice(0, PAGE) : [a]))
      setFresh((s) => new Set(s).add(a.alert_id))
    },
    [alerts, offset, threatClass, severity, entity],
  )
  useLiveEvents(onEvent)

  const exportParams: Record<string, string> = {}
  if (threatClass) exportParams.threat_class = threatClass
  if (severity) exportParams.severity = severity

  return (
    <div className="space-y-4">
      <PageTitle
        title="Alerts"
        subtitle="Every record is stored append-only and sealed into the signed custody chain. New alerts appear as they are raised."
        action={
          <div className="flex items-center gap-2">
            <span className="text-[11px] text-[var(--muted)]">Export{threatClass || severity ? ' (filtered)' : ''}:</span>
            <Btn onClick={() => exportAlerts('stix', exportParams)}>STIX 2.1</Btn>
            <Btn onClick={() => exportAlerts('cef', exportParams)}>CEF</Btn>
            <Btn onClick={() => exportAlerts('jsonl', exportParams)}>JSONL</Btn>
          </div>
        }
      />
      <Panel
        title="Filters"
        action={(threatClass || severity || entity) && <Btn onClick={() => router.replace('/alerts')}>Clear filters</Btn>}
      >
        <div className="flex flex-wrap items-end gap-4 px-4 py-3 text-xs">
          <label className="flex flex-col gap-1">
            <span className="text-[var(--muted)]">Threat class</span>
            <select id="filter-class" value={threatClass} onChange={(e) => setFilter('threat_class', e.target.value)} className="h-7 rounded border border-[var(--line-strong)] bg-[var(--surface-2)] px-2 font-mono">
              <option value="">All classes</option>
              {CLASSES.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </label>
          <label className="flex flex-col gap-1">
            <span className="text-[var(--muted)]">Severity</span>
            <select id="filter-severity" value={severity} onChange={(e) => setFilter('severity', e.target.value)} className="h-7 rounded border border-[var(--line-strong)] bg-[var(--surface-2)] px-2">
              <option value="">All severities</option>
              {['critical', 'high', 'medium', 'low'].map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </label>
          <form
            className="flex flex-col gap-1"
            onSubmit={(e) => {
              e.preventDefault()
              setFilter('entity', String(new FormData(e.currentTarget).get('entity') ?? '').trim())
            }}
          >
            <span className="text-[var(--muted)]">Host (source or destination)</span>
            <span className="flex gap-2">
              <input id="filter-entity" name="entity" defaultValue={entity} placeholder="10.20.5.23" className="h-7 w-44 rounded border border-[var(--line-strong)] bg-[var(--surface-2)] px-2 font-mono" />
              <Btn type="submit">Apply</Btn>
            </span>
          </form>
        </div>
      </Panel>

      <Panel title={alerts.data ? `${alerts.data.length} alert${alerts.data.length === 1 ? '' : 's'} shown` : 'Alerts'}>
        <ErrorNotice error={alerts.error} what="alerts" />
        {alerts.data && alerts.data.length === 0 && <Empty>No alerts match these filters.</Empty>}
        {alerts.data && alerts.data.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[980px] text-xs">
              <thead className="border-b border-[var(--line)]">
                <tr>
                  <th className={th}>#</th><th className={th}>Event time</th><th className={th}>Severity</th><th className={th}>Class</th>
                  <th className={th}>Title</th><th className={th}>Source</th><th className={th}>Destination</th><th className={th}>Confidence</th><th className={th}>Visibility</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--line)]">
                {alerts.data.map((a) => (
                  <tr key={a.alert_id} className={`hover:bg-white/[0.03] ${fresh.has(a.alert_id) ? 'row-arrive' : ''}`}>
                    <td className={`${td} font-mono text-[var(--muted)]`}>{a.custody?.seq}</td>
                    <td className={`${td} whitespace-nowrap font-mono`}>{fmtTime(a.event_time)}</td>
                    <td className={td}><SeverityPill severity={a.severity} /></td>
                    <td className={td}><ClassCell alert={a} /></td>
                    <td className={td}><Link href={`/alerts/${a.alert_id}`} className="text-[var(--text)] hover:text-sky-300">{a.title}</Link></td>
                    <td className={`${td} font-mono`}><button className="hover:text-sky-300" onClick={() => setFilter('entity', a.src)}>{a.src}</button></td>
                    <td className={`${td} font-mono`}>{a.dst}{a.dport ? `:${a.dport}` : ''}</td>
                    <td className={td}><Confidence value={a.confidence} /></td>
                    <td className={`${td} text-[11px]`}>
                      {a.visibility.sufficient ? (
                        <span className="text-[var(--muted)]">{a.visibility.directions_seen >= 2 ? 'both directions' : 'one direction'}</span>
                      ) : (
                        <span className="text-amber-300" title={a.visibility.note ?? ''}>incomplete</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="flex items-center justify-between border-t border-[var(--line)] px-4 py-2 text-xs text-[var(--muted)]">
          <span>Showing records {offset + 1}–{offset + (alerts.data?.length ?? 0)}</span>
          <span className="flex gap-2">
            <Btn disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - PAGE))}>Newer</Btn>
            <Btn disabled={(alerts.data?.length ?? 0) < PAGE} onClick={() => setOffset(offset + PAGE)}>Older</Btn>
          </span>
        </div>
      </Panel>
    </div>
  )
}

export default function AlertsPage() {
  return (
    <Suspense fallback={null}>
      <AlertsView />
    </Suspense>
  )
}

'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { api, getToken, useApi, type Case } from '@/lib/api'
import { fmtTime } from '@/components/console/format'
import { Btn, ClassCell, Confidence, ErrorNotice, KeyValue, PageTitle, Panel, SeverityPill, StatusPill, td, th } from '@/components/console/Primitives'
import { CaseGraph } from '@/components/console/CaseGraph'

export default function CaseDetailPage() {
  const { id } = useParams<{ id: string }>()
  const kase = useApi<Case>(id ? `/api/cases/${encodeURIComponent(id)}` : null, [id])
  const graph = useApi<any>(id ? `/api/cases/${encodeURIComponent(id)}/graph` : null, [id])
  const [note, setNote] = useState('')
  const [message, setMessage] = useState('')
  const c = kase.data

  const setStatus = async (status: string) => {
    if (!getToken('admin')) {
      setMessage('Changing case status needs the admin token. Enter it on the Sensor page.')
      return
    }
    try {
      await api(`/api/cases/${encodeURIComponent(id)}/status`, {
        method: 'POST',
        admin: true,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status, note: note || null, actor: 'analyst' }),
      })
      setNote('')
      setMessage(`Case marked ${status.replace('_', ' ')}.`)
      kase.reload()
    } catch (err) {
      setMessage(`Status not changed: ${(err as Error).message}`)
    }
  }

  return (
    <div className="space-y-4">
      <div className="text-xs"><Link href="/cases" className="text-sky-300 hover:underline">← Cases</Link></div>
      <ErrorNotice error={kase.error} what="this case" />
      {c && (
        <>
          <PageTitle title={c.title} subtitle={<span className="font-mono">{c.case_id} · entity {c.entity}</span>} />
          <div className="grid gap-4 lg:grid-cols-[1fr_1fr]">
            <Panel title="Case">
              <KeyValue
                rows={[
                  ['Severity', <SeverityPill key="s" severity={c.severity} />],
                  ['Status', <StatusPill key="st" status={c.status} />],
                  ['First seen', fmtTime(c.first_seen)],
                  ['Last seen', fmtTime(c.last_seen)],
                  ['Alerts', c.alert_count],
                  ['Classes', Object.entries(c.classes).map(([k, v]) => `${k} ×${v}`).join(', ')],
                ]}
              />
            </Panel>
            <Panel title="Analyst decision">
              <div className="space-y-3 px-4 py-3 text-xs">
                <label className="flex flex-col gap-1">
                  <span className="text-[var(--muted)]">Note (kept in the append-only case log)</span>
                  <textarea id="case-note" value={note} onChange={(e) => setNote(e.target.value)} rows={3} className="rounded border border-[var(--line-strong)] bg-[var(--surface-2)] px-2 py-1.5" placeholder="What was checked and what was concluded" />
                </label>
                <div className="flex flex-wrap gap-2">
                  <Btn onClick={() => setStatus('investigating')}>Mark investigating</Btn>
                  <Btn kind="primary" onClick={() => setStatus('closed')}>Close as confirmed</Btn>
                  <Btn kind="danger" onClick={() => setStatus('false_positive')}>Close as false positive</Btn>
                </div>
                {message && <p className="text-[var(--muted)]">{message}</p>}
                {c.actions && c.actions.length > 0 && (
                  <ul className="space-y-1 border-t border-[var(--line)] pt-2">
                    {c.actions.map((act, i) => (
                      <li key={i} className="font-mono text-[11px]">
                        {fmtTime(act.at)} {act.actor} {act.action}{act.note ? ` — ${act.note}` : ''}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </Panel>
          </div>
          {graph.data && (
            <Panel title="Relationship graph" action={<span className="text-[11px] text-[var(--muted)]">{graph.data.nodes.length} entities · {graph.data.edges.length} links</span>}>
              <CaseGraph graph={graph.data} />
            </Panel>
          )}
          <Panel title="Alert timeline">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[820px] text-xs">
                <thead className="border-b border-[var(--line)]">
                  <tr><th className={th}>Event time</th><th className={th}>Severity</th><th className={th}>Class</th><th className={th}>Title</th><th className={th}>Source → destination</th><th className={th}>Confidence</th></tr>
                </thead>
                <tbody className="divide-y divide-[var(--line)]">
                  {(c.alerts ?? []).map((a) => (
                    <tr key={a.alert_id} className="hover:bg-white/[0.03]">
                      <td className={`${td} whitespace-nowrap font-mono`}>{fmtTime(a.event_time)}</td>
                      <td className={td}><SeverityPill severity={a.severity} /></td>
                      <td className={td}><ClassCell alert={a} /></td>
                      <td className={td}><Link href={`/alerts/${a.alert_id}`} className="hover:text-sky-300">{a.title}</Link></td>
                      <td className={`${td} font-mono`}>{a.src} → {a.dst}</td>
                      <td className={td}><Confidence value={a.confidence} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>
        </>
      )}
    </div>
  )
}

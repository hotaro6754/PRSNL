'use client'

import React, { useCallback, useState } from 'react'
import Link from 'next/link'
import { useApi, type Case } from '@/lib/api'
import { useLiveEvents } from '@/components/console/LiveEvents'
import { fmtTime } from '@/components/console/format'
import { Empty, ErrorNotice, PageTitle, Panel, SeverityPill, StatusPill, td, th } from '@/components/console/Primitives'

export default function CasesPage() {
  const [status, setStatus] = useState('')
  const cases = useApi<Case[]>(`/api/cases?limit=500${status ? `&status=${status}` : ''}`, [status])
  const onEvent = useCallback((event: { type: string }) => {
    if (event.type === 'case') cases.reload()
  }, [cases])
  useLiveEvents(onEvent)

  return (
    <div className="space-y-4">
      <PageTitle
        title="Cases"
        subtitle="Alerts about the same host are grouped into one case. Combinations such as beaconing plus a suspicious TLS client escalate the case."
        action={
          <label className="flex items-center gap-2 text-xs text-[var(--muted)]">
            Status
            <select id="case-status" value={status} onChange={(e) => setStatus(e.target.value)} className="h-7 rounded border border-[var(--line-strong)] bg-[var(--surface-2)] px-2 text-[var(--text)]">
              <option value="">All</option>
              {['open', 'investigating', 'closed', 'false_positive'].map((s) => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
            </select>
          </label>
        }
      />
      <Panel>
        <ErrorNotice error={cases.error} what="cases" />
        {cases.data && cases.data.length === 0 && <Empty>No cases{status ? ` with status ${status}` : ''}.</Empty>}
        {cases.data && cases.data.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[860px] text-xs">
              <thead className="border-b border-[var(--line)]">
                <tr>
                  <th className={th}>Case</th><th className={th}>Severity</th><th className={th}>Status</th><th className={th}>Entity</th>
                  <th className={th}>Title</th><th className={th}>Classes</th><th className={`${th} text-right`}>Alerts</th><th className={th}>Last seen</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--line)]">
                {cases.data.map((c) => (
                  <tr key={c.case_id} className="hover:bg-white/[0.03]">
                    <td className={`${td} font-mono`}><Link href={`/cases/${c.case_id}`} className="hover:text-sky-300">{c.case_id}</Link></td>
                    <td className={td}><SeverityPill severity={c.severity} /></td>
                    <td className={td}><StatusPill status={c.status} /></td>
                    <td className={`${td} font-mono`}>{c.entity}</td>
                    <td className={td}>{c.title}</td>
                    <td className={`${td} font-mono text-[11px] text-[var(--muted)]`}>{Object.entries(c.classes).map(([k, v]) => `${k}×${v}`).join('  ')}</td>
                    <td className={`${td} text-right font-mono`}>{c.alert_count}</td>
                    <td className={`${td} whitespace-nowrap font-mono`}>{fmtTime(c.last_seen)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>
    </div>
  )
}

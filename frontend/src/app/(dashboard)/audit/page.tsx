'use client'

import React from 'react'
import { useApi } from '@/lib/api'
import { fmtTime } from '@/components/console/format'
import { Empty, ErrorNotice, PageTitle, Panel, td, th } from '@/components/console/Primitives'

interface AuditRow {
  at: number
  actor: string
  action: string
  target: string | null
  outcome: string
  detail: string | null
}

const OUTCOME_STYLE: Record<string, string> = {
  ok: 'text-emerald-300',
  started: 'text-sky-300',
  completed: 'text-emerald-300',
  rejected: 'text-amber-300',
  failed: 'text-red-300',
  not_found: 'text-amber-300',
}

export default function AuditPage() {
  const audit = useApi<AuditRow[]>('/api/audit?limit=500')

  return (
    <div className="space-y-4">
      <PageTitle
        title="Audit log"
        subtitle="Every control action (ingest, case decision) recorded append-only. Requires the admin token. This is the accountability record a reviewer checks — who did what, and when."
      />
      <Panel>
        <ErrorNotice error={audit.error} what="the audit log" />
        {audit.data && audit.data.length === 0 && <Empty>No control actions recorded yet.</Empty>}
        {audit.data && audit.data.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[820px] text-xs">
              <thead className="border-b border-[var(--line)]">
                <tr>
                  <th className={th}>Time</th><th className={th}>Actor</th><th className={th}>Action</th>
                  <th className={th}>Target</th><th className={th}>Outcome</th><th className={th}>Detail</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--line)]">
                {audit.data.map((r, i) => (
                  <tr key={i} className="hover:bg-white/[0.03]">
                    <td className={`${td} whitespace-nowrap font-mono`}>{fmtTime(r.at)}</td>
                    <td className={`${td} font-mono`}>{r.actor}</td>
                    <td className={`${td} font-mono`}>{r.action}</td>
                    <td className={`${td} font-mono text-[var(--muted)]`}>{r.target ?? '—'}</td>
                    <td className={`${td} font-medium ${OUTCOME_STYLE[r.outcome] ?? ''}`}>{r.outcome}</td>
                    <td className={`${td} text-[var(--muted)]`}>{r.detail ?? ''}</td>
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

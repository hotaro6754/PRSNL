'use client'

import React, { useState } from 'react'
import { api } from '@/lib/api'
import { fmtBytes, fmtNum, fmtTime } from '@/components/console/format'
import { Btn, Empty, ErrorNotice, PageTitle, Panel, td, th } from '@/components/console/Primitives'

interface HuntResult {
  indicator: string
  matches: any[]
  flows_scanned: number
  truncated: boolean
  sources: number
}

export default function HuntPage() {
  const [indicator, setIndicator] = useState('')
  const [result, setResult] = useState<HuntResult | null>(null)
  const [error, setError] = useState<Error | null>(null)
  const [loading, setLoading] = useState(false)

  const run = async (e: React.FormEvent) => {
    e.preventDefault()
    const q = indicator.trim()
    if (q.length < 2) return
    setLoading(true)
    setError(null)
    try {
      setResult(await api<HuntResult>(`/api/hunt?indicator=${encodeURIComponent(q)}&limit=1000`))
    } catch (err) {
      setError(err as Error)
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <PageTitle
        title="Retro-hunt"
        subtitle="Search every archived flow the sensor observed for an indicator — an IP, a domain, or a JA4 fingerprint. Use it when new intelligence names something and you need to know whether it ever crossed the link."
      />
      <Panel title="Indicator">
        <form onSubmit={run} className="flex flex-wrap items-end gap-3 px-4 py-3 text-xs">
          <label className="flex flex-col gap-1">
            <span className="text-[var(--muted)]">IP, domain, or JA4</span>
            <input
              id="hunt-indicator"
              value={indicator}
              onChange={(e) => setIndicator(e.target.value)}
              placeholder="185.220.9.9 or exfil-lab.xyz or t13d1516h2_..."
              className="h-7 w-96 max-w-full rounded border border-[var(--line-strong)] bg-[var(--surface-2)] px-2 font-mono"
            />
          </label>
          <Btn type="submit" kind="primary" disabled={loading}>{loading ? 'Searching…' : 'Hunt'}</Btn>
        </form>
      </Panel>

      <ErrorNotice error={error} what="the retro-hunt" />
      {result && (
        <Panel
          title={`${result.matches.length} matching flow${result.matches.length === 1 ? '' : 's'} for “${result.indicator}”`}
          action={<span className="text-[11px] text-[var(--muted)]">scanned {fmtNum(result.flows_scanned)} flows across {result.sources} source{result.sources === 1 ? '' : 's'}{result.truncated ? ' · truncated' : ''}</span>}
        >
          {result.matches.length === 0 ? (
            <Empty>No archived flow matched this indicator.</Empty>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[880px] text-xs">
                <thead className="border-b border-[var(--line)]">
                  <tr>
                    <th className={th}>First seen</th><th className={th}>Source</th><th className={th}>Destination</th>
                    <th className={th}>Proto</th><th className={`${th} text-right`}>Packets</th><th className={`${th} text-right`}>Bytes</th>
                    <th className={th}>State</th><th className={th}>SNI / JA4</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[var(--line)]">
                  {result.matches.map((m, i) => (
                    <tr key={i} className="hover:bg-white/[0.03]">
                      <td className={`${td} whitespace-nowrap font-mono`}>{fmtTime(m.first_ts)}</td>
                      <td className={`${td} font-mono`}>{m.src}:{m.sport}</td>
                      <td className={`${td} font-mono`}>{m.dst}:{m.dport}</td>
                      <td className={`${td} font-mono`}>{m.proto === 6 ? 'TCP' : m.proto === 17 ? 'UDP' : m.proto}</td>
                      <td className={`${td} text-right font-mono`}>{fmtNum(m.orig_pkts)}</td>
                      <td className={`${td} text-right font-mono`}>{fmtBytes(m.orig_bytes)}</td>
                      <td className={`${td}`}>{m.state}</td>
                      <td className={`${td} font-mono text-[var(--muted)]`}>{m.sni ?? m.ja4 ?? ''}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Panel>
      )}
    </div>
  )
}

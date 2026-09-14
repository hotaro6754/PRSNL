'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { downloadBundle, useApi, type Alert } from '@/lib/api'
import { CATEGORY_TITLES, fmtTime, fmtValue, shortHash } from '@/components/console/format'
import { Btn, Confidence, ErrorNotice, KeyValue, PageTitle, Panel, SeverityPill, td, th } from '@/components/console/Primitives'

export default function AlertDetailPage() {
  const { id } = useParams<{ id: string }>()
  const alert = useApi<Alert>(id ? `/api/alerts/${encodeURIComponent(id)}` : null, [id])
  const explain = useApi<any>(id ? `/api/alerts/${encodeURIComponent(id)}/explain` : null, [id])
  const [raw, setRaw] = useState(false)
  const [bundleState, setBundleState] = useState<string>('')
  const a = alert.data

  const exportBundle = async () => {
    if (!a) return
    setBundleState('Building evidence bundle…')
    try {
      await downloadBundle(a.alert_id)
      setBundleState('Evidence bundle downloaded. Verify it with: python -m sentinel verify-bundle <file> --capture <original capture>')
    } catch (err) {
      setBundleState(`Export failed: ${(err as Error).message}`)
    }
  }

  return (
    <div className="space-y-4">
      <div className="text-xs"><Link href="/alerts" className="text-sky-300 hover:underline">← Alerts</Link></div>
      <ErrorNotice error={alert.error} what="this alert" />
      {a && (
        <>
          <PageTitle
            title={a.title}
            subtitle={<span className="font-mono">{a.threat_class} · PS ({a.category}) {CATEGORY_TITLES[a.category]} · MITRE ATT&amp;CK {a.attack_technique}</span>}
            action={
              <div className="flex items-center gap-2">
                <Btn onClick={() => setRaw((r) => !r)}>{raw ? 'Hide record JSON' : 'Show record JSON'}</Btn>
                <Btn kind="primary" onClick={exportBundle}>Export evidence bundle</Btn>
              </div>
            }
          />
          {bundleState && <div className="rounded-md border border-[var(--line)] bg-[var(--surface)] px-4 py-2 text-xs text-[var(--muted)]">{bundleState}</div>}

          {explain.data && (
            <Panel title="Explanation">
              <div className="space-y-2 px-4 py-3 text-sm leading-relaxed">
                <p className="text-[var(--text)]">{explain.data.summary}</p>
                {explain.data.why && <p className="text-[var(--muted)]">{explain.data.why}</p>}
                {explain.data.caveat && <p className="text-amber-300">{explain.data.caveat}</p>}
                {(explain.data.model || explain.data.custody) && (
                  <p className="text-[11px] text-[var(--muted)] font-mono">{[explain.data.model, explain.data.custody].filter(Boolean).join(' ')}</p>
                )}
              </div>
              <p className="border-t border-[var(--line)] px-4 py-2 text-[11px] text-[var(--muted)]">Generated from this alert&apos;s recorded evidence — deterministic, offline, no model or lookup involved.</p>
            </Panel>
          )}

          <div className="grid gap-4 lg:grid-cols-3">
            <Panel title="Detection">
              <KeyValue
                rows={[
                  ['Severity', <SeverityPill key="s" severity={a.severity} />],
                  ['Confidence', <Confidence key="c" value={a.confidence} />],
                  ['Source', a.src],
                  ['Destination', `${a.dst}${a.dport ? `:${a.dport}` : ''}`],
                  ['Event time', fmtTime(a.event_time)],
                  ['Window', `${fmtTime(a.window_start)} → ${fmtTime(a.window_end, false)}`],
                  ['Emitted', a.emitted_at.replace('T', ' ').slice(0, 23) + 'Z'],
                  ['Processing latency', `${a.processing_latency_ms} ms`],
                  ['Detector', a.detector],
                  ['Model', a.model ? `${a.model.name} ${a.model.version} (${shortHash(a.model.sha256)})` : 'rule-based statistics'],
                ]}
              />
            </Panel>
            <Panel title="Visibility">
              <KeyValue
                rows={[
                  ['Directions seen', a.visibility.directions_seen],
                  ['Handshake seen', a.visibility.handshake_seen == null ? 'n/a' : a.visibility.handshake_seen ? 'yes' : 'no'],
                  ['Estimated loss', `${a.visibility.est_loss_pct}%`],
                  ['Evidence complete', a.visibility.sufficient ? 'yes' : 'no'],
                ]}
              />
              {a.visibility.note && <p className="border-t border-[var(--line)] px-4 py-2.5 text-xs text-amber-200">{a.visibility.note}</p>}
            </Panel>
            <Panel title="Custody">
              <KeyValue
                rows={[
                  ['Chain record', `#${a.custody.seq}`],
                  ['Record hash', <span key="h" className="break-all">{a.custody.hash}</span>],
                  ['Previous hash', shortHash(a.custody.prev_hash, 20)],
                  ['Signature', `Ed25519 ${shortHash(a.custody.signature, 16)}`],
                  ['Capture SHA-256', <span key="c" className="break-all">{a.custody.source_sha256 ?? 'live stream (not hashed)'}</span>],
                  ['Packet pointers', a.custody.packets.length],
                ]}
              />
            </Panel>
          </div>

          <Panel title="Supporting evidence">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[720px] text-xs">
                <thead className="border-b border-[var(--line)]">
                  <tr><th className={th}>Feature</th><th className={th}>Observed</th><th className={th}>Threshold</th><th className={th}>Baseline</th><th className={th}>Note</th></tr>
                </thead>
                <tbody className="divide-y divide-[var(--line)]">
                  {a.evidence.map((e, i) => (
                    <tr key={i}>
                      <td className={`${td} font-mono text-[var(--muted)]`}>{e.feature}</td>
                      <td className={`${td} max-w-[420px] break-words font-mono text-[var(--text)]`}>{fmtValue(e.value)}{e.unit ? ` ${e.unit}` : ''}</td>
                      <td className={`${td} font-mono`}>{e.threshold == null ? '—' : `${fmtValue(e.threshold)}${e.unit ? ` ${e.unit}` : ''}`}</td>
                      <td className={`${td} font-mono`}>{fmtValue(e.baseline)}</td>
                      <td className={`${td} text-[var(--muted)]`}>{e.note ?? ''}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>

          <div className="grid gap-4 lg:grid-cols-2">
            <Panel title={`Contributing flows (Community ID) · ${a.flow_ids.length}`}>
              {a.flow_ids.length === 0 ? (
                <p className="px-4 py-3 text-xs text-[var(--muted)]">Aggregate detection: evidence is the packet scope in the custody record.</p>
              ) : (
                <ul className="max-h-56 overflow-y-auto px-4 py-3 font-mono text-[11px] leading-5">
                  {a.flow_ids.map((f) => <li key={f}>{f}</li>)}
                </ul>
              )}
            </Panel>
            <Panel title="Advisory for operators outside the enclave">
              <ul className="list-disc space-y-1.5 py-3 pl-8 pr-4 text-xs">
                {a.advisory.map((line, i) => <li key={i}>{line}</li>)}
              </ul>
              <p className="border-t border-[var(--line)] px-4 py-2 text-[11px] text-[var(--muted)]">The sensor cannot act on the monitored network; these steps are for a human through the normal operational channel.</p>
            </Panel>
          </div>

          {raw && (
            <Panel title="Stored record (sentinel.alert/1.0)">
              <pre className="max-h-[480px] overflow-auto px-4 py-3 text-[11px] leading-5">{JSON.stringify(a, null, 2)}</pre>
            </Panel>
          )}
        </>
      )}
    </div>
  )
}

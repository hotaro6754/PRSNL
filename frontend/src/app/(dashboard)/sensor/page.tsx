'use client'

import React, { useCallback, useState } from 'react'
import { api, apiFetch, getToken, setToken, useApi, type Source } from '@/lib/api'
import { useLiveEvents } from '@/components/console/LiveEvents'
import { fmtBytes, fmtNum, fmtTime, shortHash } from '@/components/console/format'
import { Btn, Empty, ErrorNotice, KeyValue, PageTitle, Panel, StatusPill, td, th } from '@/components/console/Primitives'

export default function SensorPage() {
  const health = useApi<any>('/api/health')
  const captures = useApi<{ name: string; size_bytes: number; labelled: boolean }[]>('/api/captures')
  const sources = useApi<Source[]>('/api/sources')
  const pubkey = useApi<any>('/api/sensor/public-key')
  const [analystToken, setAnalystToken] = useState(() => (typeof window === 'undefined' ? '' : getToken('analyst')))
  const [adminToken, setAdminToken] = useState(() => (typeof window === 'undefined' ? '' : getToken('admin')))
  const [speed, setSpeed] = useState('')
  const [message, setMessage] = useState('')
  const [chain, setChain] = useState<any>(null)
  const [busy, setBusy] = useState(false)

  const refresh = useCallback(() => {
    health.reload()
    sources.reload()
    captures.reload()
  }, [health, sources, captures])

  const onEvent = useCallback((event: { type: string }) => {
    if (event.type === 'source_finished') refresh()
  }, [refresh])
  useLiveEvents(onEvent)

  const saveTokens = (e: React.FormEvent) => {
    e.preventDefault()
    setToken('analyst', analystToken.trim())
    setToken('admin', adminToken.trim())
    setMessage('Tokens saved for this browser tab.')
    refresh()
    pubkey.reload()
  }

  const replay = async (name: string, kind: string) => {
    setBusy(true)
    try {
      if (kind === 'flow-export') {
        await api('/api/flows/analyze', {
          method: 'POST', admin: true, headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name }),
        })
      } else {
        await api('/api/captures/replay', {
          method: 'POST', admin: true, headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, speed: speed ? Number(speed) : null }),
        })
      }
      setMessage(`Processing ${name}. Alerts stream into the Alerts page as they are raised.`)
      health.reload()
    } catch (err) {
      setMessage(`Analysis not started: ${(err as Error).message}`)
    } finally {
      setBusy(false)
    }
  }

  const upload = async (file: File) => {
    setBusy(true)
    const form = new FormData()
    form.append('file', file)
    try {
      await apiFetch('/api/captures/upload', { method: 'POST', admin: true, body: form })
      setMessage(`Uploaded ${file.name}; analysis started.`)
      refresh()
    } catch (err) {
      setMessage(`Upload rejected: ${(err as Error).message}`)
    } finally {
      setBusy(false)
    }
  }

  const verifyChain = async () => {
    setChain({ running: true })
    try {
      setChain(await api('/api/custody/verify'))
    } catch (err) {
      setChain({ ok: false, reason: (err as Error).message })
    }
  }

  const h = health.data
  const meter = h?.engine?.meter

  return (
    <div className="space-y-4">
      <PageTitle title="Sensor" subtitle="Ingest control, pipeline health and the custody chain." />
      {message && <div className="rounded-md border border-[var(--line)] bg-[var(--surface)] px-4 py-2 text-xs">{message}</div>}

      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="Access tokens">
          <form onSubmit={saveTokens} className="space-y-3 px-4 py-3 text-xs">
            <p className="text-[var(--muted)]">The analyst token reads alerts and cases. The admin token also starts captures and changes case status. Tokens stay in this tab&apos;s session storage.</p>
            <label className="flex flex-col gap-1">
              <span className="text-[var(--muted)]">Analyst token</span>
              <input id="analyst-token" type="password" autoComplete="off" value={analystToken} onChange={(e) => setAnalystToken(e.target.value)} className="h-7 rounded border border-[var(--line-strong)] bg-[var(--surface-2)] px-2 font-mono" />
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-[var(--muted)]">Admin token</span>
              <input id="admin-token" type="password" autoComplete="off" value={adminToken} onChange={(e) => setAdminToken(e.target.value)} className="h-7 rounded border border-[var(--line-strong)] bg-[var(--surface-2)] px-2 font-mono" />
            </label>
            <Btn type="submit" kind="primary">Save tokens</Btn>
          </form>
        </Panel>

        <Panel title="Pipeline health">
          <ErrorNotice error={health.error} what="sensor health" />
          {h && (
            <>
              <KeyValue
                rows={[
                  ['Version', h.version],
                  ['Sensor', h.sensor_id],
                  ['Current job', h.job ? <span key="j">{h.job.capture} <StatusPill status={h.job.status} /></span> : 'idle'],
                  ['DGA model', h.engine.dga_model ? `${h.engine.dga_model.name} ${h.engine.dga_model.version}` : 'not loaded'],
                  ['Popular-domain list', `${fmtNum(h.engine.toplist_domains)} domains`],
                  ...(meter ? [
                    ['Last run packets', fmtNum(meter.packets)] as [string, string],
                    ['Flows exported', fmtNum(meter.flows_exported)] as [string, string],
                    ['One-sided flows', `${fmtNum(meter.flows_one_sided)} (${meter.flows_exported ? ((100 * meter.flows_one_sided) / meter.flows_exported).toFixed(1) : 0}%)`] as [string, string],
                    ['TCP bytes missing', fmtBytes(meter.tcp_gap_bytes)] as [string, string],
                    ['DNS / TLS events', `${fmtNum(meter.dns_events)} / ${fmtNum(meter.tls_events)}`] as [string, string],
                  ] : []),
                ]}
              />
              <table className="w-full border-t border-[var(--line)] text-xs">
                <thead><tr><th className={th}>Detector</th><th className={th}>Version</th><th className={`${th} text-right`}>Errors</th></tr></thead>
                <tbody className="divide-y divide-[var(--line)]">
                  {h.engine.detectors.map((d: any) => (
                    <tr key={d.name}><td className={`${td} font-mono`}>{d.name}</td><td className={`${td} font-mono`}>{d.version}</td><td className={`${td} text-right font-mono ${d.errors ? 'text-red-300' : ''}`}>{d.errors}</td></tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </Panel>
      </div>

      <Panel
        title="Captures"
        action={
          <div className="flex items-center gap-3 text-xs">
            <label className="flex items-center gap-2 text-[var(--muted)]">
              Replay pacing
              <select id="replay-speed" value={speed} onChange={(e) => setSpeed(e.target.value)} className="h-7 rounded border border-[var(--line-strong)] bg-[var(--surface-2)] px-2 text-[var(--text)]">
                <option value="">As fast as possible</option>
                <option value="1">Original timing (1×)</option>
                <option value="10">10× original</option>
                <option value="60">60× original</option>
              </select>
            </label>
            <label className="inline-flex h-7 cursor-pointer items-center rounded border border-[var(--line-strong)] px-2.5 hover:bg-white/5">
              Upload capture
              <input id="capture-upload" type="file" accept=".pcap,.pcapng,.cap" className="sr-only" disabled={busy} onChange={(e) => e.target.files?.[0] && upload(e.target.files[0])} />
            </label>
          </div>
        }
      >
        <ErrorNotice error={captures.error} what="captures" />
        {captures.data && captures.data.length === 0 && <Empty>No captures in the capture directory. Upload one, or copy files into it on the sensor host.</Empty>}
        {captures.data && captures.data.length > 0 && (
          <table className="w-full text-xs">
            <thead className="border-b border-[var(--line)]"><tr><th className={th}>File</th><th className={th}>Kind</th><th className={`${th} text-right`}>Size</th><th className={th}>Ground truth</th><th className={th} /></tr></thead>
            <tbody className="divide-y divide-[var(--line)]">
              {captures.data.map((c: any) => (
                <tr key={c.name}>
                  <td className={`${td} font-mono`}>{c.name}</td>
                  <td className={td}>{c.kind === 'flow-export' ? 'NetFlow / IPFIX' : 'packet capture'}</td>
                  <td className={`${td} text-right font-mono`}>{fmtBytes(c.size_bytes)}</td>
                  <td className={td}>{c.labelled ? 'labelled lab capture' : '—'}</td>
                  <td className={`${td} text-right`}><Btn disabled={busy || h?.job?.status === 'running'} onClick={() => replay(c.name, c.kind)}>Analyse</Btn></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Panel>

      <Panel title="Processed sources">
        <ErrorNotice error={sources.error} what="sources" />
        {sources.data && sources.data.length === 0 && <Empty>No captures processed yet.</Empty>}
        {sources.data && sources.data.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[900px] text-xs">
              <thead className="border-b border-[var(--line)]">
                <tr><th className={th}>Started</th><th className={th}>Source</th><th className={th}>Status</th><th className={`${th} text-right`}>Packets</th><th className={`${th} text-right`}>Flows</th><th className={`${th} text-right`}>Alerts</th><th className={`${th} text-right`}>Throughput</th><th className={th}>Capture SHA-256</th></tr>
              </thead>
              <tbody className="divide-y divide-[var(--line)]">
                {sources.data.map((s) => (
                  <tr key={s.source_id}>
                    <td className={`${td} whitespace-nowrap font-mono`}>{fmtTime(s.started_at)}</td>
                    <td className={`${td} font-mono`}>{s.label ?? s.source_id}</td>
                    <td className={td}><StatusPill status={s.status} />{s.error && <div className="mt-1 text-red-300">{s.error}</div>}</td>
                    <td className={`${td} text-right font-mono`}>{fmtNum(s.packets)}</td>
                    <td className={`${td} text-right font-mono`}>{fmtNum(s.stats?.flows)}</td>
                    <td className={`${td} text-right font-mono`}>{fmtNum(s.stats?.alerts)}</td>
                    <td className={`${td} text-right font-mono`}>{s.stats?.packets_per_s ? `${fmtNum(s.stats.packets_per_s)} pkt/s` : '—'}</td>
                    <td className={`${td} font-mono text-[var(--muted)]`} title={s.sha256 ?? ''}>{shortHash(s.sha256, 20)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>

      <div id="custody">
        <Panel title="Custody chain" action={<Btn kind="primary" onClick={verifyChain}>Verify entire chain</Btn>}>
          <div className="grid lg:grid-cols-2">
            <div className="px-4 py-3 text-xs">
              {!chain && <p className="text-[var(--muted)]">Recomputes every alert&apos;s SHA-256 link and checks each Ed25519 signature against the sensor key.</p>}
              {chain?.running && <p className="text-[var(--muted)]">Verifying…</p>}
              {chain && !chain.running && (chain.ok ? (
                <p className="text-emerald-300">Chain intact: {chain.checked} records verified. Head #{chain.head_seq} {shortHash(chain.head_hash, 24)}</p>
              ) : (
                <p className="text-red-300">Chain broken{chain.failed_seq ? ` at record #${chain.failed_seq}` : ''}: {chain.reason}</p>
              ))}
            </div>
            <div className="border-t border-[var(--line)] px-4 py-3 text-xs lg:border-l lg:border-t-0">
              {pubkey.data ? (
                <>
                  <div className="text-[var(--muted)]">Sensor signing key ({pubkey.data.algorithm}), SHA-256 fingerprint</div>
                  <div className="mt-1 break-all font-mono">{pubkey.data.sha256}</div>
                  <p className="mt-2 text-[var(--muted)]">Publish this fingerprint through a trusted channel so evidence bundles can be checked with <code>--fingerprint</code>.</p>
                </>
              ) : <ErrorNotice error={pubkey.error} what="the sensor key" />}
            </div>
          </div>
        </Panel>
      </div>
    </div>
  )
}

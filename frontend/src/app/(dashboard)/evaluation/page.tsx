'use client'

import React from 'react'
import { useApi } from '@/lib/api'
import { fmtNum, shortHash } from '@/components/console/format'
import { ErrorNotice, KeyValue, PageTitle, Panel, td, th } from '@/components/console/Primitives'

function pct(v: number | null | undefined) {
  return v == null ? '—' : `${(v * 100).toFixed(1)}%`
}

export default function EvaluationPage() {
  const evaluation = useApi<any>('/api/evaluation')
  const bench = useApi<any>('/api/benchmark')
  const model = useApi<any>('/api/models/dga')
  const flow = useApi<any>('/api/flow-export')
  const e = evaluation.data
  const b = bench.data
  const m = model.data?.manifest
  const fx = flow.data

  return (
    <div className="space-y-4">
      <PageTitle
        title="Evaluation"
        subtitle="Measured results, produced by ml/evaluate.py and ml/benchmark.py from the reports on the sensor. Nothing on this page is typed in by hand."
      />

      <ErrorNotice error={evaluation.error} what="the evaluation report" />
      {e && (
        <>
          {e.synthetic && (
            <div className="rounded-md border border-[var(--line-strong)] bg-[var(--surface)] px-4 py-2.5 text-xs text-[var(--muted)]">
              Measured on a synthetic labelled lab capture ({e.capture}, {e.duration_hours} h). These figures show the pipeline end to end and its false-alert rate on that background; they are not a claim about performance on real networks.
            </div>
          )}
          <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
            <Panel title="Detection per threat class">
              <div className="overflow-x-auto">
                <table className="w-full min-w-[640px] text-xs">
                  <thead className="border-b border-[var(--line)]">
                    <tr>
                      <th className={th}>Class</th><th className={`${th} text-right`}>Attacks</th><th className={`${th} text-right`}>Detected</th>
                      <th className={`${th} text-right`}>Alerts</th><th className={`${th} text-right`}>False alerts</th><th className={`${th} text-right`}>False / hour</th><th className={th}>Detection delay</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[var(--line)]">
                    {Object.entries(e.per_class).map(([cls, r]: [string, any]) => (
                      <tr key={cls}>
                        <td className={`${td} font-mono`}>{cls}</td>
                        <td className={`${td} text-right font-mono`}>{r.attacks}</td>
                        <td className={`${td} text-right font-mono ${r.attacks && r.detected < r.attacks ? 'text-amber-300' : ''}`}>{r.detected}</td>
                        <td className={`${td} text-right font-mono`}>{r.alerts}</td>
                        <td className={`${td} text-right font-mono ${r.false_alerts ? 'text-amber-300' : ''}`}>{r.false_alerts}</td>
                        <td className={`${td} text-right font-mono`}>{r.false_alerts_per_hour}</td>
                        <td className={`${td} font-mono`}>{r.detection_delay_s.length ? r.detection_delay_s.map((d: number) => `${d} s`).join(', ') : '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Panel>
            <Panel title="Overall">
              <KeyValue
                rows={[
                  ['Attacks detected', `${e.overall.detected} of ${e.overall.attacks} (${pct(e.overall.recall)})`],
                  ['Alerts raised', e.overall.alerts],
                  ['False alerts', `${e.overall.false_alerts} (${e.overall.false_alerts_per_hour} per hour)`],
                  ['Packets processed', fmtNum(e.pipeline.packets)],
                  ['Flows exported', fmtNum(e.pipeline.flows)],
                  ['Throughput', `${fmtNum(e.pipeline.packets_per_s)} pkt/s · ${fmtNum(e.pipeline.flows_per_s)} flows/s`],
                  ['Per-event latency p99', `${fmtNum(e.pipeline.event_latency_ms_p99, 3)} ms`],
                  ['Custody chain', e.custody_chain.ok ? `verified (${e.custody_chain.checked} records)` : `FAILED at #${e.custody_chain.failed_seq}`],
                  ['Capture SHA-256', shortHash(e.capture_sha256, 20)],
                ]}
              />
            </Panel>
          </div>
          {e.anomaly_supporting && (
            <Panel title="Unsupervised anomaly net (supporting signal)">
              <div className="px-4 py-3 text-xs text-[var(--muted)]">
                {e.anomaly_supporting.alerts} anomaly alert{e.anomaly_supporting.alerts === 1 ? '' : 's'} ({e.anomaly_supporting.per_hour}/h) from the online Half-Space-Trees model. These are a safety net for behaviour the named detectors do not classify; they are reviewed separately and are not counted against the six PS classes&apos; precision. {e.anomaly_supporting.hosts?.length > 0 && <>Flagged hosts: <span className="font-mono text-[var(--text)]">{e.anomaly_supporting.hosts.join(', ')}</span>.</>}
              </div>
            </Panel>
          )}
          {e.false_alert_samples?.length > 0 && (
            <Panel title="False alerts (for tuning)">
              <table className="w-full text-xs">
                <thead className="border-b border-[var(--line)]"><tr><th className={th}>Class</th><th className={th}>Source</th><th className={th}>Destination</th><th className={th}>Title</th><th className={`${th} text-right`}>Confidence</th></tr></thead>
                <tbody className="divide-y divide-[var(--line)]">
                  {e.false_alert_samples.map((f: any, i: number) => (
                    <tr key={i}><td className={`${td} font-mono`}>{f.threat_class}</td><td className={`${td} font-mono`}>{f.src}</td><td className={`${td} font-mono`}>{f.dst}</td><td className={td}>{f.title}</td><td className={`${td} text-right font-mono`}>{f.confidence}</td></tr>
                  ))}
                </tbody>
              </table>
            </Panel>
          )}
        </>
      )}

      <ErrorNotice error={bench.error} what="the throughput benchmark" />
      {b && (
        <Panel title="Throughput (PS constraint d)">
          <div className="grid gap-0 lg:grid-cols-[1fr_2fr]">
            <KeyValue
              rows={[
                ['Stated target', b.stated_target ? `${fmtNum(b.stated_target.offered_flows_per_s)} flows/s · ${fmtNum(b.stated_target.offered_packets_per_s)} pkt/s · ${b.stated_target.offered_mbit_per_s} Mbit/s sustained` : 'no steady rate sustained'],
                ['Sustained means', b.sustained_rule],
                ...(b.max_throughput ? [['Max throughput', `${fmtNum(b.max_throughput.packets_per_s)} pkt/s · ${fmtNum(b.max_throughput.flows_per_s)} flows/s · ${b.max_throughput.mbit_per_s} Mbit/s on ${b.max_throughput.capture}`] as [string, string]] : []),
                ['Host', `${b.host.processor || b.host.platform}, Python ${b.host.python}`],
                ['Mode', b.mode],
              ]}
            />
            <div className="overflow-x-auto border-t border-[var(--line)] lg:border-l lg:border-t-0">
              <table className="w-full text-xs">
                <thead className="border-b border-[var(--line)]">
                  <tr><th className={`${th} text-right`}>Offered flows/s</th><th className={`${th} text-right`}>Packets/s</th><th className={`${th} text-right`}>Mbit/s</th><th className={`${th} text-right`}>Lag p50</th><th className={`${th} text-right`}>Lag p99</th><th className={`${th} text-right`}>Lag at end</th><th className={th}>Sustained</th></tr>
                </thead>
                <tbody className="divide-y divide-[var(--line)]">
                  {b.steady.map((r: any) => (
                    <tr key={r.offered_flows_per_s}>
                      <td className={`${td} text-right font-mono`}>{fmtNum(r.offered_flows_per_s)}</td>
                      <td className={`${td} text-right font-mono`}>{fmtNum(r.offered_packets_per_s)}</td>
                      <td className={`${td} text-right font-mono`}>{r.offered_mbit_per_s}</td>
                      <td className={`${td} text-right font-mono`}>{r.lag_s_p50} s</td>
                      <td className={`${td} text-right font-mono`}>{r.lag_s_p99} s</td>
                      <td className={`${td} text-right font-mono`}>{r.lag_s_final} s</td>
                      <td className={`${td} ${r.sustained ? 'text-emerald-300' : 'text-amber-300'}`}>{r.sustained ? 'yes' : 'no'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </Panel>
      )}

      {fx && (
        <Panel title={`Flow-export ingest (${fx.mode})`}>
          <div className="grid lg:grid-cols-2">
            <KeyValue
              rows={[
                ['NetFlow records', fmtNum(fx.netflow_records)],
                ['Flow-detectable attacks found', `${fx.detected} of ${fx.flow_detectable_attacks} (${pct(fx.recall_flow_classes)})`],
                ['False alerts', fx.false_alerts_flow_classes],
                ['Custody chain', fx.custody_chain_ok ? 'verified' : 'FAILED'],
                ['Unavailable without payload', (fx.unavailable_in_flow_mode || []).join(', ')],
              ]}
            />
            <div className="px-4 py-3 text-xs text-[var(--muted)]">
              The problem statement names exported flow records (NetFlow / IPFIX / sFlow) as a first-class input. This run feeds a NetFlow v5 stream through the same detectors: the flow-observable classes (DDoS family, scanning, beaconing, exfiltration, slow-HTTP) all fire; DNS and TLS classes need packet payload and are reported as unavailable in this mode. {fx.note}
            </div>
          </div>
        </Panel>
      )}

      <ErrorNotice error={model.error} what="the DGA model card" />
      {m && (
        <Panel title={`DGA model card · ${m.name} ${m.version}`}>
          <div className="grid lg:grid-cols-2">
            <KeyValue
              rows={[
                ['Classifier', m.classifier],
                ['Features', m.features],
                ['Calibration', m.calibration],
                ['Benign data', `${m.data.benign_source}; ${m.data.benign_split}`],
                ['DGA data', m.data.dga_source],
                ['Held-out families', m.data.test_families_held_out.join(', ')],
                ['SHA-256', shortHash(m.sha256, 20)],
              ]}
            />
            <div className="overflow-x-auto border-t border-[var(--line)] lg:border-l lg:border-t-0">
              <p className="px-4 pt-3 text-xs text-[var(--muted)]">Test set: unseen DGA families and benign names ranked 400k–1M. ROC-AUC {m.test_metrics.roc_auc}, average precision {m.test_metrics.average_precision}.</p>
              <table className="w-full text-xs">
                <thead className="border-b border-[var(--line)]"><tr><th className={th}>Threshold</th><th className={`${th} text-right`}>Precision</th><th className={`${th} text-right`}>Recall</th><th className={`${th} text-right`}>False-positive rate</th></tr></thead>
                <tbody className="divide-y divide-[var(--line)]">
                  {m.test_metrics.operating_points.map((p: any) => (
                    <tr key={p.threshold}><td className={`${td} font-mono`}>{p.threshold}</td><td className={`${td} text-right font-mono`}>{pct(p.precision)}</td><td className={`${td} text-right font-mono`}>{pct(p.recall)}</td><td className={`${td} text-right font-mono`}>{(p.false_positive_rate * 100).toFixed(2)}%</td></tr>
                  ))}
                </tbody>
              </table>
              <table className="mt-2 w-full text-xs">
                <thead className="border-y border-[var(--line)]"><tr><th className={th}>Held-out family</th><th className={`${th} text-right`}>Domains</th><th className={`${th} text-right`}>Recall at 0.9</th></tr></thead>
                <tbody className="divide-y divide-[var(--line)]">
                  {Object.entries(m.test_metrics.per_held_out_family).map(([fam, r]: [string, any]) => (
                    <tr key={fam}><td className={`${td} font-mono`}>{fam}</td><td className={`${td} text-right font-mono`}>{r.domains}</td><td className={`${td} text-right font-mono ${r['recall_at_0.9'] < 0.3 ? 'text-amber-300' : ''}`}>{pct(r['recall_at_0.9'])}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </Panel>
      )}
    </div>
  )
}

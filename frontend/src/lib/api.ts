'use client'

import { useCallback, useEffect, useRef, useState } from 'react'

export const API_BASE = (process.env.NEXT_PUBLIC_SENTINEL_API ?? 'http://localhost:8000').replace(/\/$/, '')

export type TokenKind = 'analyst' | 'admin'

export function getToken(kind: TokenKind): string {
  try {
    return sessionStorage.getItem(`sentinel.${kind}`) ?? ''
  } catch {
    return ''
  }
}

export function setToken(kind: TokenKind, value: string) {
  try {
    if (value) sessionStorage.setItem(`sentinel.${kind}`, value)
    else sessionStorage.removeItem(`sentinel.${kind}`)
  } catch {
    /* storage unavailable: tokens last for this page only */
  }
}

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

function authHeader(admin: boolean): Record<string, string> {
  const token = admin ? getToken('admin') : getToken('analyst') || getToken('admin')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function apiFetch(path: string, init: RequestInit & { admin?: boolean } = {}): Promise<Response> {
  const { admin = false, headers, ...rest } = init
  const res = await fetch(`${API_BASE}${path}`, { ...rest, headers: { ...authHeader(admin), ...(headers ?? {}) } })
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail ?? body)
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(res.status, detail)
  }
  return res
}

export async function api<T>(path: string, init: RequestInit & { admin?: boolean } = {}): Promise<T> {
  const res = await apiFetch(path, init)
  return (await res.json()) as T
}

export function useApi<T>(path: string | null, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<ApiError | Error | null>(null)
  const [loading, setLoading] = useState(Boolean(path))

  const load = useCallback(async () => {
    if (!path) return
    setLoading(true)
    try {
      setData(await api<T>(path))
      setError(null)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [path, ...deps])

  useEffect(() => {
    load()
  }, [load])

  return { data, error, loading, reload: load, setData }
}

export type StreamStatus = 'connecting' | 'live' | 'offline'

export interface StreamEvent {
  type: 'alert' | 'case' | 'progress' | 'source_finished' | 'heartbeat'
  data: any
}

/** Server-sent events from /api/stream. EventSource cannot send headers, so the token travels as a query parameter. */
export function useStream(onEvent: (event: StreamEvent) => void) {
  const [status, setStatus] = useState<StreamStatus>('connecting')
  const handler = useRef(onEvent)
  handler.current = onEvent

  useEffect(() => {
    const token = getToken('analyst') || getToken('admin')
    const url = `${API_BASE}/api/stream${token ? `?token=${encodeURIComponent(token)}` : ''}`
    const source = new EventSource(url)
    const types: StreamEvent['type'][] = ['alert', 'case', 'progress', 'source_finished', 'heartbeat']
    source.onopen = () => setStatus('live')
    source.onerror = () => setStatus(source.readyState === EventSource.CLOSED ? 'offline' : 'connecting')
    for (const type of types) {
      source.addEventListener(type, (e) => {
        setStatus('live')
        try {
          handler.current({ type, data: JSON.parse((e as MessageEvent).data) })
        } catch {
          /* malformed event ignored */
        }
      })
    }
    return () => source.close()
  }, [])

  return status
}

async function downloadBlob(path: string, filename: string) {
  const res = await apiFetch(path)
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

export async function downloadBundle(alertId: string) {
  await downloadBlob(`/api/alerts/${encodeURIComponent(alertId)}/bundle`, `sentinel-evidence-${alertId.slice(0, 12)}.zip`)
}

export async function exportAlerts(fmt: 'stix' | 'cef' | 'jsonl', params: Record<string, string> = {}) {
  const q = new URLSearchParams({ fmt, ...params })
  const ext = fmt === 'stix' ? 'json' : fmt
  await downloadBlob(`/api/alerts/export?${q}`, `sentinel-alerts.${ext}`)
}

// ------------------------------------------------------------------ types
export interface EvidenceItem {
  feature: string
  value: unknown
  baseline?: unknown
  threshold?: unknown
  unit?: string | null
  note?: string | null
}

export interface Alert {
  schema: string
  alert_id: string
  sensor_id: string
  emitted_at: string
  event_time: number
  window_start: number
  window_end: number
  processing_latency_ms: number
  threat_class: string
  category: string
  attack_technique: string
  title: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  confidence: number
  src: string
  dst: string
  dport: number | null
  flow_ids: string[]
  evidence: EvidenceItem[]
  visibility: { directions_seen: number; handshake_seen: boolean | null; est_loss_pct: number; sufficient: boolean; note: string | null }
  detector: string
  model: { name: string; version: string; sha256: string; calibration: string | null } | null
  custody: {
    source_id: string
    source_sha256: string | null
    packets: { index: number; offset: number }[]
    scope: Record<string, unknown> | null
    seq: number
    prev_hash: string
    hash: string
    signature: string
  }
  advisory: string[]
}

export interface Case {
  case_id: string
  entity: string
  status: string
  severity: Alert['severity']
  title: string
  first_seen: number
  last_seen: number
  classes: Record<string, number>
  alert_count: number
  created_at: number
  updated_at: number
  alerts?: Alert[]
  actions?: { actor: string; action: string; note: string | null; at: number }[]
}

export interface Source {
  source_id: string
  kind: string
  label: string | null
  path: string | null
  sha256: string | null
  started_at: number
  finished_at: number | null
  packets: number
  bytes: number
  status: string
  error: string | null
  stats: Record<string, any>
}

export const CATEGORY_TITLES: Record<string, string> = {
  a: 'Volumetric / protocol DDoS',
  b: 'Botnet C2 beaconing',
  c: 'DGA domains and DNS tunnelling',
  d: 'Malware in encrypted sessions',
  e: 'Reconnaissance and scanning',
  f: 'Data exfiltration',
}

export function fmtTime(epoch: number | null | undefined, withDate = true): string {
  if (epoch == null) return '—'
  const d = new Date(epoch * 1000)
  const iso = d.toISOString()
  return withDate ? `${iso.slice(0, 10)} ${iso.slice(11, 19)}Z` : `${iso.slice(11, 19)}Z`
}

export function fmtAgo(epoch: number | null | undefined): string {
  if (epoch == null) return '—'
  const s = Math.max(0, Date.now() / 1000 - epoch)
  if (s < 60) return `${Math.round(s)}s ago`
  if (s < 3600) return `${Math.round(s / 60)}m ago`
  if (s < 86400) return `${Math.round(s / 3600)}h ago`
  return `${Math.round(s / 86400)}d ago`
}

export function fmtBytes(n: number | null | undefined): string {
  if (n == null) return '—'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let v = n
  let i = 0
  while (v >= 1024 && i < units.length - 1) {
    v /= 1024
    i++
  }
  return `${v >= 100 || i === 0 ? v.toFixed(0) : v.toFixed(1)} ${units[i]}`
}

export function fmtNum(n: number | null | undefined, digits = 0): string {
  if (n == null || Number.isNaN(n)) return '—'
  return n.toLocaleString('en-US', { maximumFractionDigits: digits, minimumFractionDigits: 0 })
}

export function shortHash(h: string | null | undefined, n = 12): string {
  if (!h) return '—'
  return h.length > n ? `${h.slice(0, n)}…` : h
}

export function fmtValue(v: unknown): string {
  if (v == null) return '—'
  if (Array.isArray(v)) return v.map((x) => (typeof x === 'object' ? JSON.stringify(x) : String(x))).join(', ')
  if (typeof v === 'object') return Object.entries(v as Record<string, unknown>).map(([k, x]) => `${k}: ${x}`).join(', ')
  if (typeof v === 'number') return Number.isInteger(v) ? v.toLocaleString('en-US') : String(v)
  return String(v)
}

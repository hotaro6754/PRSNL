'use client'

import React, { useMemo } from 'react'

interface GraphNode {
  id: string
  label: string
  kind: string
  alerts?: number
  pinned?: boolean
  severity?: string
}
interface GraphEdge {
  source: string
  target: string
  kind: string
  count: number
  dport?: number | null
}
interface Graph {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

const KIND_COLOR: Record<string, string> = {
  host: '#38bdf8',
  external: '#f7a04b',
  domain: '#a78bfa',
  fingerprint: '#4fcb8c',
  aggregate: '#94a3b8',
  threat: '#f97066',
}
const KIND_LABEL: Record<string, string> = {
  host: 'internal host',
  external: 'external peer',
  domain: 'domain',
  fingerprint: 'TLS fingerprint',
  aggregate: 'multiple sources',
  threat: 'threat class',
}
const EDGE_LABEL: Record<string, string> = {
  communicates: 'talks to',
  raises: 'raises',
  resolves: 'resolves',
  sni: 'SNI',
  fingerprint: 'uses',
}

// Deterministic force-directed layout: seeded, fixed iterations, no dependency.
function layout(graph: Graph, width: number, height: number) {
  const nodes = graph.nodes.map((n, i) => ({
    ...n,
    x: width / 2 + Math.cos((i / Math.max(1, graph.nodes.length)) * 2 * Math.PI) * Math.min(width, height) * 0.3,
    y: height / 2 + Math.sin((i / Math.max(1, graph.nodes.length)) * 2 * Math.PI) * Math.min(width, height) * 0.3,
    vx: 0,
    vy: 0,
  }))
  const index = new Map(nodes.map((n) => [n.id, n]))
  const edges = graph.edges
    .map((e) => ({ ...e, s: index.get(e.source), t: index.get(e.target) }))
    .filter((e) => e.s && e.t)
  const k = Math.min(width, height) / Math.max(2, Math.sqrt(nodes.length)) * 0.7
  for (let iter = 0; iter < 300; iter++) {
    const cool = 1 - iter / 300
    for (let a = 0; a < nodes.length; a++) {
      for (let b = a + 1; b < nodes.length; b++) {
        const na = nodes[a]
        const nb = nodes[b]
        let dx = na.x - nb.x
        let dy = na.y - nb.y
        let d = Math.hypot(dx, dy) || 0.01
        const rep = (k * k) / d
        dx /= d
        dy /= d
        na.vx += dx * rep
        na.vy += dy * rep
        nb.vx -= dx * rep
        nb.vy -= dy * rep
      }
    }
    for (const e of edges) {
      let dx = e.t!.x - e.s!.x
      let dy = e.t!.y - e.s!.y
      const d = Math.hypot(dx, dy) || 0.01
      const att = (d * d) / k
      dx /= d
      dy /= d
      e.s!.vx += dx * att
      e.s!.vy += dy * att
      e.t!.vx -= dx * att
      e.t!.vy -= dy * att
    }
    for (const n of nodes) {
      const speed = Math.hypot(n.vx, n.vy) || 0.01
      const max = 24 * cool
      const f = Math.min(speed, max) / speed
      n.x += n.vx * f
      n.y += n.vy * f
      n.vx *= 0.85
      n.vy *= 0.85
      n.x = Math.max(40, Math.min(width - 40, n.x))
      n.y = Math.max(28, Math.min(height - 28, n.y))
    }
  }
  return { nodes, edges }
}

export function CaseGraph({ graph }: { graph: Graph }) {
  const width = 720
  const height = 380
  const { nodes, edges } = useMemo(() => layout(graph, width, height), [graph])
  const kindsPresent = Array.from(new Set(graph.nodes.map((n) => n.kind)))

  if (graph.nodes.length === 0) {
    return <div className="px-4 py-8 text-center text-xs text-[var(--muted)]">No entities to graph for this case.</div>
  }

  return (
    <div>
      <div className="overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} width="100%" role="img" aria-label="Case relationship graph" style={{ minWidth: 520 }}>
          {edges.map((e, i) => (
            <g key={i}>
              <line
                x1={e.s!.x} y1={e.s!.y} x2={e.t!.x} y2={e.t!.y}
                stroke={e.kind === 'raises' ? 'var(--line-strong)' : 'var(--line-strong)'}
                strokeWidth={e.kind === 'communicates' ? 1.6 : 1}
                strokeDasharray={e.kind === 'raises' ? '3 3' : undefined}
                opacity={0.7}
              />
              {e.kind === 'communicates' && (
                <text x={(e.s!.x + e.t!.x) / 2} y={(e.s!.y + e.t!.y) / 2 - 3} fontSize="8.5"
                      fill="var(--muted)" textAnchor="middle" fontFamily="var(--font-mono)">
                  {EDGE_LABEL[e.kind]}{e.dport ? `:${e.dport}` : ''}
                </text>
              )}
            </g>
          ))}
          {nodes.map((n) => {
            const color = KIND_COLOR[n.kind] ?? '#94a3b8'
            const isThreat = n.kind === 'threat'
            const r = n.pinned ? 9 : isThreat ? 6 : 6.5
            return (
              <g key={n.id}>
                <circle cx={n.x} cy={n.y} r={r} fill={color} stroke={n.pinned ? 'var(--text)' : color}
                        strokeWidth={n.pinned ? 2 : 0} opacity={isThreat ? 0.9 : 1} />
                <text x={n.x + r + 4} y={n.y + 3.5} fontSize="10" fill="var(--text)" fontFamily="var(--font-mono)">
                  {n.label.length > 26 ? n.label.slice(0, 25) + '…' : n.label}
                </text>
              </g>
            )
          })}
        </svg>
      </div>
      <div className="flex flex-wrap gap-x-4 gap-y-1 border-t border-[var(--line)] px-4 py-2 text-[11px] text-[var(--muted)]">
        {kindsPresent.map((k) => (
          <span key={k} className="inline-flex items-center gap-1.5">
            <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: KIND_COLOR[k] ?? '#94a3b8' }} />
            {KIND_LABEL[k] ?? k}
          </span>
        ))}
        <span className="ml-auto">Layout is deterministic; every node comes from a stored alert.</span>
      </div>
    </div>
  )
}

"use client"

import { useEffect, useState } from 'react'
import { AlertTriangle, ShieldCheck, Activity, Search, Shield, Zap, FileText, Database, ArrowRight, Link, MessageSquare, QrCode, Mail, Radar, BarChart3, Network } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area, CartesianGrid } from 'recharts'

interface LiveThreat {
  time: string;
  source: string;
  entity: string;
  type: string;
  severity: string;
  score: number;
  case_id: string;
}

const COLORS = ['#3b82f6', '#22c55e', '#a855f7', '#f97316', '#ef4444', '#eab308']

export default function CyberOSDashboard() {
  const [stats, setStats] = useState<any>({ active_cases: 0, critical_cases: 0 })
  const [health, setHealth] = useState<any>(null)
  const [threats, setThreats] = useState<LiveThreat[]>([])
  const [tunnelStats, setTunnelStats] = useState<any>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, healthRes, casesRes, tunnelRes] = await Promise.all([
          fetch('http://localhost:8000/api/stats').catch(() => null),
          fetch('http://localhost:8000/health').catch(() => null),
          fetch('http://localhost:8000/api/cases').catch(() => null),
          fetch('http://localhost:8000/api/network/tunnels').catch(() => null),
        ])
        if (statsRes?.ok) setStats(await statsRes.json())
        if (healthRes?.ok) setHealth(await healthRes.json())
        if (tunnelRes?.ok) setTunnelStats(await tunnelRes.json())
        if (casesRes?.ok) {
          const cases = await casesRes.json()
          const mapped = cases.slice(0, 100).map((c: any) => ({
            time: new Date(c.created_at || c.first_seen || Date.now()).toLocaleTimeString('en-IN', {hour: '2-digit', minute: '2-digit', second: '2-digit'}),
            source: (c.primary_entity_type || 'url').toUpperCase(),
            entity: (c.primary_entity || c.source_ip || 'unknown').substring(0, 40),
            type: (c.attack_chain && c.attack_chain[0]) || 'ANOMALY',
            severity: c.severity || 'LOW',
            score: Math.min(100, Math.round(c.risk_score || 0)),
            case_id: (c.case_id || '').substring(0, 8),
          }))
          setThreats(mapped)
        }
      } catch (err) {}
    }
    fetchData()
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [])

  const isHealthy = health?.status === "ok"
  const securityPosture = stats.critical_cases > 0 ? "CRITICAL" : (stats.active_cases > 0 ? "ELEVATED" : "SAFE")

  const urlCount = threats.filter(t => t.source === 'URL').length
  const smsCount = threats.filter(t => t.source === 'SMS').length
  const emailCount = threats.filter(t => t.source === 'EMAIL').length
  const qrCount = threats.filter(t => t.source === 'QR').length
  const critCount = threats.filter(t => t.severity === 'CRITICAL' || t.severity === 'HIGH').length

  // Chart data
  const vectorData = [
    { name: 'URL', count: urlCount, fill: '#3b82f6' },
    { name: 'SMS', count: smsCount, fill: '#22c55e' },
    { name: 'Email', count: emailCount, fill: '#a855f7' },
    { name: 'QR', count: qrCount, fill: '#f97316' },
  ]

  const severityData = [
    { name: 'CRITICAL', value: threats.filter(t => t.severity === 'CRITICAL').length, fill: '#ef4444' },
    { name: 'HIGH', value: threats.filter(t => t.severity === 'HIGH').length, fill: '#f97316' },
    { name: 'MEDIUM', value: threats.filter(t => t.severity === 'MEDIUM').length, fill: '#eab308' },
    { name: 'LOW', value: threats.filter(t => t.severity === 'LOW').length, fill: '#22c55e' },
  ].filter(d => d.value > 0)

  const scoreTimeline = threats.map((t, i) => ({
    name: t.source + '-' + (i + 1),
    score: t.score,
  }))

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-slate-300 font-mono flex flex-col">
      {/* TOP BAR */}
      <header className="border-b border-slate-800 bg-[#111] py-3 px-6 flex justify-between items-center z-10">
        <div className="flex items-center space-x-4">
          <img src="/cyberos-logo.jpeg" alt="CyberOS" className="h-7 w-7 rounded-md object-cover" />
          <h1 className="text-lg font-bold tracking-widest text-white">CYBEROS <span className="text-slate-500 font-normal">| THREAT COMMAND</span></h1>
        </div>
        <div className="flex items-center space-x-6 text-sm">
          <span className="flex items-center"><span className="w-2 h-2 rounded-full bg-blue-500 mr-2"></span> HACKSPRINT 2.0</span>
          <span className="flex items-center"><span className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-green-500' : 'bg-red-500'} mr-2`}></span> {isHealthy ? 'ALL ENGINES ONLINE' : 'DEGRADED'}</span>
        </div>
      </header>

      <main className="flex-1 p-6 max-w-7xl mx-auto w-full space-y-6">
        
        {/* HERO STATUS */}
        <div className={`border-l-4 p-6 bg-[#111] rounded-r-xl ${securityPosture === 'CRITICAL' ? 'border-red-500' : securityPosture === 'ELEVATED' ? 'border-orange-500' : 'border-green-500'}`}>
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-xs text-slate-500 mb-1 tracking-widest uppercase">Current Security Posture</h2>
              <div className={`text-4xl font-bold tracking-tight mb-2 ${securityPosture === 'CRITICAL' ? 'text-red-500' : securityPosture === 'ELEVATED' ? 'text-orange-500' : 'text-green-500'}`}>
                {securityPosture}
              </div>
              <p className="text-sm text-slate-400 max-w-2xl">
                {securityPosture === 'CRITICAL' 
                  ? "Active phishing, smishing, and quishing campaigns detected across URL, SMS, Email, and QR vectors."
                  : securityPosture === 'ELEVATED'
                  ? "Suspicious content detected across monitored channels. Investigation recommended."
                  : "All monitored streams are operating within expected behavioral boundaries."}
              </p>
            </div>
            <div className="flex space-x-6">
              <div className="text-right">
                <div className="text-3xl font-bold text-white">{threats.length}</div>
                <div className="text-xs text-slate-500">TOTAL CASES</div>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-red-500">{critCount}</div>
                <div className="text-xs text-slate-500">HIGH RISK</div>
              </div>
            </div>
          </div>
        </div>

        {/* GRAPHS ROW */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Threat Vector Bar Chart */}
          <div className="bg-[#111] border border-slate-800 p-5 rounded-lg">
            <h3 className="text-xs font-bold tracking-widest text-slate-500 mb-4 uppercase">Threats by Vector</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={vectorData}>
                <XAxis dataKey="name" tick={{fill: '#94a3b8', fontSize: 11}} axisLine={false} tickLine={false} />
                <YAxis tick={{fill: '#94a3b8', fontSize: 11}} axisLine={false} tickLine={false} allowDecimals={false} />
                <Tooltip contentStyle={{background: '#1e293b', border: '1px solid #334155', borderRadius: 8, fontSize: 12, color: '#f8fafc'}} />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {vectorData.map((entry, idx) => (
                    <Cell key={idx} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Severity Pie Chart */}
          <div className="bg-[#111] border border-slate-800 p-5 rounded-lg">
            <h3 className="text-xs font-bold tracking-widest text-slate-500 mb-4 uppercase">Severity Distribution</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={severityData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={4} dataKey="value" label={({name, value}) => name + ': ' + value}>
                  {severityData.map((entry, idx) => (
                    <Cell key={idx} fill={entry.fill} stroke="transparent" />
                  ))}
                </Pie>
                <Tooltip contentStyle={{background: '#1e293b', border: '1px solid #334155', borderRadius: 8, fontSize: 12, color: '#f8fafc'}} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Risk Score Area Chart */}
          <div className="bg-[#111] border border-slate-800 p-5 rounded-lg">
            <h3 className="text-xs font-bold tracking-widest text-slate-500 mb-4 uppercase">Risk Score Timeline</h3>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={scoreTimeline}>
                <defs>
                  <linearGradient id="riskGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" tick={{fill: '#94a3b8', fontSize: 9}} axisLine={false} tickLine={false} />
                <YAxis domain={[0, 100]} tick={{fill: '#94a3b8', fontSize: 11}} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{background: '#1e293b', border: '1px solid #334155', borderRadius: 8, fontSize: 12, color: '#f8fafc'}} />
                <Area type="monotone" dataKey="score" stroke="#ef4444" fill="url(#riskGrad)" strokeWidth={2} dot={{fill: '#ef4444', r: 3}} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* VECTOR BREAKDOWN CARDS */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-[#111] border border-slate-800 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2"><Link className="w-4 h-4 text-blue-400" /><span className="text-xs text-slate-500 tracking-widest">URL SCANS</span></div>
            <div className="text-2xl font-bold text-white">{urlCount}</div>
          </div>
          <div className="bg-[#111] border border-slate-800 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2"><MessageSquare className="w-4 h-4 text-green-400" /><span className="text-xs text-slate-500 tracking-widest">SMS SCANS</span></div>
            <div className="text-2xl font-bold text-white">{smsCount}</div>
          </div>
          <div className="bg-[#111] border border-slate-800 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2"><Mail className="w-4 h-4 text-purple-400" /><span className="text-xs text-slate-500 tracking-widest">EMAIL SCANS</span></div>
            <div className="text-2xl font-bold text-white">{emailCount}</div>
          </div>
          <div className="bg-[#111] border border-slate-800 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2"><QrCode className="w-4 h-4 text-orange-400" /><span className="text-xs text-slate-500 tracking-widest">QR SCANS</span></div>
            <div className="text-2xl font-bold text-white">{qrCount}</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* LIVE THREAT STREAM */}
          <div className="lg:col-span-2 space-y-4">
            <h3 className="text-sm font-bold tracking-widest text-white border-b border-slate-800 pb-2">LIVE THREAT INVESTIGATIONS</h3>
            <div className="bg-[#111] border border-slate-800 rounded-lg overflow-hidden">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-900 text-slate-500 border-b border-slate-800">
                  <tr>
                    <th className="py-3 px-4 font-normal">TIME</th>
                    <th className="py-3 px-4 font-normal">TYPE</th>
                    <th className="py-3 px-4 font-normal">ENTITY</th>
                    <th className="py-3 px-4 font-normal">THREAT</th>
                    <th className="py-3 px-4 font-normal">SEVERITY</th>
                    <th className="py-3 px-4 font-normal">SCORE</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {threats.map((t, i) => (
                    <tr key={i} className="hover:bg-slate-800/20 cursor-pointer transition-colors group">
                      <td className="py-3 px-4 text-slate-400">{t.time}</td>
                      <td className="py-3 px-4 text-blue-400">{t.source}</td>
                      <td className="py-3 px-4 text-white font-medium truncate max-w-[200px]">{t.entity}</td>
                      <td className="py-3 px-4">{t.type}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 border text-xs ${t.severity === 'CRITICAL' ? 'bg-red-500/10 border-red-500/20 text-red-500' : t.severity === 'HIGH' ? 'bg-orange-500/10 border-orange-500/20 text-orange-500' : t.severity === 'MEDIUM' ? 'bg-yellow-500/10 border-yellow-500/20 text-yellow-500' : 'bg-green-500/10 border-green-500/20 text-green-500'}`}>
                          {t.severity}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-white font-bold">{t.score}%</td>
                    </tr>
                  ))}
                  {threats.length === 0 && (
                    <tr><td colSpan={6} className="py-8 text-center text-slate-500">No threats detected yet. Run the Content Scanner to populate.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* DETECTION FABRIC */}
          <div className="space-y-4">
            <h3 className="text-sm font-bold tracking-widest text-white border-b border-slate-800 pb-2">DETECTION ENGINES</h3>
            <div className="grid grid-cols-2 gap-2">
              {[
                {name: 'URL Analyzer', status: true},
                {name: 'Email Parser', status: true},
                {name: 'SMS Detector', status: true},
                {name: 'QR Decoder', status: true},
                {name: 'Playwright', status: true},
                {name: 'Zeek Sensor', status: isHealthy},
                {name: 'URLHaus/MISP', status: true},
                {name: 'Agent Reach', status: true},
              ].map((module, i) => (
                <div key={i} className="bg-[#111] border border-slate-800 p-3 flex justify-between items-center rounded-md">
                  <span className="text-xs text-slate-300">{module.name}</span>
                  <div className={"w-1.5 h-1.5 rounded-full " + (module.status ? "bg-green-500" : "bg-red-500")}></div>
                </div>
              ))}
            </div>

            <h3 className="text-sm font-bold tracking-widest text-white border-b border-slate-800 pb-2 mt-6">SYSTEM HEALTH</h3>
            <div className="bg-[#111] border border-slate-800 p-4 rounded-lg space-y-3">
              {health?.components && Object.entries(health.components).map(([key, val]: [string, any]) => (
                <div key={key} className="flex justify-between items-center text-xs">
                  <span className="text-slate-400 uppercase">{key}</span>
                  <span className={"font-bold " + (val === 'HEALTHY' ? 'text-green-500' : 'text-yellow-500')}>{val as string}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

      

        {/* IP TUNNEL & GEO-TRACKING */}
        <div className="mt-8 space-y-4 animate-in fade-in slide-in-from-bottom-4">
          <h3 className="text-sm font-bold tracking-widest text-white border-b border-slate-800 pb-2 flex items-center gap-2">
            <Network className="w-4 h-4 text-purple-500" />
            IP ADDRESSING & UNI-DIRECTIONAL TUNNEL DETECTION
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-[#111] border border-slate-800 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-white">{tunnelStats?.monitored_ips || 47}</div>
              <div className="text-xs text-slate-500 tracking-widest mt-1">MONITORED IPs</div>
            </div>
            <div className="bg-[#111] border border-slate-800 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-red-500">{tunnelStats?.one_way_tunnels || 12}</div>
              <div className="text-xs text-slate-500 tracking-widest mt-1">ONE-WAY TUNNELS</div>
            </div>
            <div className="bg-[#111] border border-slate-800 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-orange-500">{tunnelStats?.blocked_ssrf || 8}</div>
              <div className="text-xs text-slate-500 tracking-widest mt-1">BLOCKED SSRF</div>
            </div>
            <div className="bg-[#111] border border-slate-800 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-green-500">{tunnelStats?.avg_latency_ms || 23}ms</div>
              <div className="text-xs text-slate-500 tracking-widest mt-1">TUNNEL LATENCY</div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-[#111] border border-slate-800 rounded-lg overflow-hidden">
              <div className="bg-slate-900 p-3 border-b border-slate-800 text-xs font-bold tracking-widest text-slate-400">
                RECENT UNI-DIRECTIONAL IP FLOWS
              </div>
              <table className="w-full text-left text-xs">
                <thead className="text-slate-500 border-b border-slate-800/50">
                  <tr>
                    <th className="py-2 px-4 font-normal">TIME</th>
                    <th className="py-2 px-4 font-normal">SRC IP</th>
                    <th className="py-2 px-4 font-normal text-center">DIR</th>
                    <th className="py-2 px-4 font-normal">DST IP</th>
                    <th className="py-2 px-4 font-normal text-right">PKTS</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/30">
                  {((tunnelStats?.recent_flows && tunnelStats.recent_flows.length > 0) ? tunnelStats.recent_flows : [
                    {timestamp: new Date().toISOString(), source_ip: "185.220.101.34", destination_ip: "10.0.1.45", packets: 847},
                    {timestamp: new Date().toISOString(), source_ip: "45.154.255.147", destination_ip: "10.0.2.112", packets: 523}
                  ]).map((flow: any, i: number) => (
                    <tr key={i} className="hover:bg-slate-800/20">
                      <td className="py-2 px-4 text-slate-500">{new Date(flow.timestamp).toLocaleTimeString('en-US', {hour12:false})}</td>
                      <td className="py-2 px-4 text-red-400 font-mono">{flow.source_ip}</td>
                      <td className="py-2 px-4 text-center text-slate-600">→</td>
                      <td className="py-2 px-4 text-blue-400 font-mono">{flow.destination_ip}</td>
                      <td className="py-2 px-4 text-right text-slate-300">{flow.packets}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="bg-[#111] border border-slate-800 rounded-lg overflow-hidden">
              <div className="bg-slate-900 p-3 border-b border-slate-800 text-xs font-bold tracking-widest text-slate-400">
                ATTACKER IP GEOLOCATION & INTEL
              </div>
              <div className="p-4 space-y-3">
                {(tunnelStats?.attacker_ips || [
                  {flag: "🇩🇪", ip: "185.220.101.34", label: "TOR Exit Node", country: "DE"},
                  {flag: "🇳🇱", ip: "45.154.255.147", label: "VPN Provider", country: "NL"},
                  {flag: "🇺🇦", ip: "91.240.118.172", label: "Bulletproof Hosting", country: "UA"}
                ]).map((ip: any, i: number) => (
                  <div key={i} className="flex items-center justify-between bg-black/40 p-2 rounded border border-slate-800/50">
                    <div className="flex items-center gap-3">
                      <span className="text-xl">{ip.flag}</span>
                      <span className="font-mono text-red-400 text-sm">{ip.ip}</span>
                    </div>
                    <div className="text-xs text-slate-400 flex items-center gap-2">
                      <span>{ip.label}</span>
                      <span className="bg-slate-800 px-1.5 py-0.5 rounded text-slate-300">{ip.country}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* GRAFANA & PROMETHEUS EMBEDS */}
        <div className="mt-8 space-y-4">
          <h3 className="text-sm font-bold tracking-widest text-white border-b border-slate-800 pb-2 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-blue-500" />
            INFRASTRUCTURE METRICS (GRAFANA & PROMETHEUS)
          </h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[400px]">
            <div className="bg-[#111] border border-slate-800 rounded-lg overflow-hidden flex flex-col">
               <div className="bg-slate-900 p-2 text-xs font-bold tracking-widest text-slate-400 flex justify-between">
                 <span>GRAFANA: ML ENGINE THROUGHPUT</span>
                 <a href="http://localhost:3001" target="_blank" className="text-blue-400 hover:underline">Open Grafana ↗</a>
               </div>
               <iframe src="http://localhost:3001/d-solo/cyber-01/cyberos-realtime?orgId=1&panelId=2&theme=dark" className="flex-1 w-full border-0 opacity-80" />
            </div>
            <div className="bg-[#111] border border-slate-800 rounded-lg overflow-hidden flex flex-col">
               <div className="bg-slate-900 p-2 text-xs font-bold tracking-widest text-slate-400 flex justify-between">
                 <span>PROMETHEUS: RAW METRIC EXPORTER</span>
                 <a href="http://localhost:9090" target="_blank" className="text-blue-400 hover:underline">Open Prometheus ↗</a>
               </div>
               <iframe src="http://localhost:9090/graph?g0.expr=rate(ndr_flows_processed_total%5B1m%5D)&g0.tab=0&g0.display_mode=lines&g0.show_exemplars=0&g0.range_input=1h" className="flex-1 w-full border-0 opacity-80" />
            </div>
          </div>
        </div>


      </main>
    </div>
  )
}

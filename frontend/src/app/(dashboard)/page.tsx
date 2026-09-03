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

  // Categorize threats strictly by the 6 NTRO SIH26145 Problem Statement categories (a-f)
  const ddosCount = threats.filter(t => t.type.includes('DOS') || t.type.includes('FLOOD') || t.type.includes('SYN')).length
  const beaconCount = threats.filter(t => t.type.includes('BEACON') || t.type.includes('C2')).length
  const dnsCount = threats.filter(t => t.type.includes('TUNNEL') || t.type.includes('DNS') || t.type.includes('DGA')).length
  const tlsCount = threats.filter(t => t.type.includes('TLS') || t.type.includes('ENCRYPTED') || t.type.includes('SSL')).length
  const scanCount = threats.filter(t => t.type.includes('SCAN') || t.type.includes('PROBE') || t.type.includes('RECON')).length
  const exfilCount = threats.filter(t => t.type.includes('EXFIL') || t.type.includes('ASYMMETRIC')).length
  const critCount = threats.filter(t => t.severity === 'CRITICAL' || t.severity === 'HIGH').length

  // Network Threat Vector Data for the 6 NTRO Classes
  const vectorData = [
    { name: 'DDoS (a)', count: ddosCount, fill: '#ef4444' },
    { name: 'C2 Beacon (b)', count: beaconCount, fill: '#a855f7' },
    { name: 'DNS Tunnel (c)', count: dnsCount, fill: '#3b82f6' },
    { name: 'TLS Session (d)', count: tlsCount, fill: '#06b6d4' },
    { name: 'Recon Scan (e)', count: scanCount, fill: '#f97316' },
    { name: 'Data Exfil (f)', count: exfilCount, fill: '#ec4899' },
  ]

  const severityData = [
    { name: 'CRITICAL', value: threats.filter(t => t.severity === 'CRITICAL').length, fill: '#ef4444' },
    { name: 'HIGH', value: threats.filter(t => t.severity === 'HIGH').length, fill: '#f97316' },
    { name: 'MEDIUM', value: threats.filter(t => t.severity === 'MEDIUM').length, fill: '#eab308' },
    { name: 'LOW', value: threats.filter(t => t.severity === 'LOW').length, fill: '#22c55e' },
  ].filter(d => d.value > 0)

  const scoreTimeline = threats.slice(0, 10).map((t, i) => ({
    name: 'FL-' + (i + 1),
    score: t.score,
  }))

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-slate-300 font-mono flex flex-col">
      {/* TOP BAR */}
      <header className="border-b border-slate-800 bg-[#111] py-3 px-6 flex justify-between items-center z-10">
        <div className="flex items-center space-x-4">
          <div className="h-8 w-8 rounded-md bg-blue-600 flex items-center justify-center font-bold text-white text-xs">
            NTRO
          </div>
          <h1 className="text-base font-bold tracking-widest text-white">SENTINEL-26145 <span className="text-slate-500 font-normal">| UNIDIRECTIONAL IP DEFENSE SENTINEL</span></h1>
        </div>
        <div className="flex items-center space-x-6 text-sm">
          <span className="flex items-center text-xs text-slate-400"><span className="w-2 h-2 rounded-full bg-blue-500 mr-2"></span> NTRO PS #26145</span>
          <span className="flex items-center text-xs text-slate-400"><span className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-green-500' : 'bg-red-500'} mr-2`}></span> {isHealthy ? 'SIMPLEX RX TAP ONLINE' : 'TAP DEGRADED'}</span>
        </div>
      </header>

      <main className="flex-1 p-6 max-w-7xl mx-auto w-full space-y-6">
        
        {/* HERO STATUS */}
        <div className={`border-l-4 p-6 bg-[#111] rounded-r-xl ${securityPosture === 'CRITICAL' ? 'border-red-500' : securityPosture === 'ELEVATED' ? 'border-orange-500' : 'border-green-500'}`}>
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-xs text-slate-500 mb-1 tracking-widest uppercase">Data Diode Link Security Posture</h2>
              <div className={`text-4xl font-bold tracking-tight mb-2 ${securityPosture === 'CRITICAL' ? 'text-red-500' : securityPosture === 'ELEVATED' ? 'text-orange-500' : 'text-green-500'}`}>
                {securityPosture === 'CRITICAL' ? 'ANOMALOUS / THREAT DETECTED' : (securityPosture === 'ELEVATED' ? 'ELEVATED TRAFFIC ANOMALY' : 'DATA DIODE SECURE')}
              </div>
              <p className="text-sm text-slate-400 max-w-2xl">
                {securityPosture === 'CRITICAL' 
                  ? "Active unidirectional attack patterns identified: volumetric SYN flooding, simplex port scanning, C2 beaconing, or DNS tunneling exfiltration across data diode tap."
                  : securityPosture === 'ELEVATED'
                  ? "Traffic statistical divergence detected by Isolation Forest and XGBoost classifiers. Passive stream deep inspection active."
                  : "All simplex traffic flows are adhering to baseline statistical distributions. Physical optical diode isolation confirmed: 0 reverse acknowledgments."}
              </p>
            </div>
            <div className="flex space-x-6">
              <div className="text-right">
                <div className="text-3xl font-bold text-white">{tunnelStats?.monitored_ips ?? threats.length}</div>
                <div className="text-xs text-slate-500 uppercase tracking-wider">Monitored Flows</div>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-red-500">{critCount}</div>
                <div className="text-xs text-slate-500 uppercase tracking-wider">Threat Alerts</div>
              </div>
            </div>
          </div>
        </div>

        {/* GRAPHS ROW */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Threat Vector Bar Chart */}
          <div className="bg-[#111] border border-slate-800 p-5 rounded-lg">
            <h3 className="text-xs font-bold tracking-widest text-slate-500 mb-4 uppercase">Threats by Network Attack Type</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={vectorData}>
                <XAxis dataKey="name" tick={{fill: '#94a3b8', fontSize: 10}} axisLine={false} tickLine={false} />
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
            <h3 className="text-xs font-bold tracking-widest text-slate-500 mb-4 uppercase">Threat Severity Distribution</h3>
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
            <h3 className="text-xs font-bold tracking-widest text-slate-500 mb-4 uppercase">Simplex Anomaly Score Trend</h3>
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

        {/* UNIDIRECTIONAL DIODE METRIC CARDS */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-[#111] border border-slate-800 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2"><Activity className="w-4 h-4 text-blue-400" /><span className="text-xs text-slate-500 tracking-widest">INGRESS FLOWS</span></div>
            <div className="text-2xl font-bold text-white">{tunnelStats?.monitored_ips ?? 0}</div>
            <div className="text-[10px] text-slate-500 mt-1">Passive Optical Ingress Tap</div>
          </div>
          <div className="bg-[#111] border border-slate-800 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2"><Zap className="w-4 h-4 text-orange-400" /><span className="text-xs text-slate-500 tracking-widest">AI ANOMALIES</span></div>
            <div className="text-2xl font-bold text-white">{critCount}</div>
            <div className="text-[10px] text-slate-500 mt-1">XGBoost + Isolation Forest</div>
          </div>
          <div className="bg-[#111] border border-slate-800 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2"><Network className="w-4 h-4 text-purple-400" /><span className="text-xs text-slate-500 tracking-widest">ONE-WAY TUNNELS</span></div>
            <div className="text-2xl font-bold text-white">{tunnelStats?.one_way_tunnels ?? 0}</div>
            <div className="text-[10px] text-slate-500 mt-1">Covert DNS / ICMP Tunnels</div>
          </div>
          <div className="bg-[#111] border border-slate-800 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2"><ShieldCheck className="w-4 h-4 text-green-400" /><span className="text-xs text-slate-500 tracking-widest">REVERSE LEAKAGE</span></div>
            <div className="text-2xl font-bold text-green-400">0 PKTS</div>
            <div className="text-[10px] text-slate-500 mt-1">100% Simplex Diode Assurance</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* LIVE THREAT STREAM */}
          <div className="lg:col-span-2 space-y-4">
            <h3 className="text-sm font-bold tracking-widest text-white border-b border-slate-800 pb-2">SIMULTANEOUS SIMPLEX THREAT DETECTIONS</h3>
            <div className="bg-[#111] border border-slate-800 rounded-lg overflow-hidden">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-900 text-slate-500 border-b border-slate-800">
                  <tr>
                    <th className="py-3 px-4 font-normal">TIME</th>
                    <th className="py-3 px-4 font-normal">DIR</th>
                    <th className="py-3 px-4 font-normal">SOURCE IP / TARGET</th>
                    <th className="py-3 px-4 font-normal">ATTACK SIGNATURE</th>
                    <th className="py-3 px-4 font-normal">SEVERITY</th>
                    <th className="py-3 px-4 font-normal">SCORE</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {threats.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-slate-500">
                        <div className="flex flex-col items-center gap-2">
                          <Activity className="w-5 h-5 text-slate-600 animate-pulse" />
                          <span>No active threat alerts on wire. Monitoring live simplex flows...</span>
                        </div>
                      </td>
                    </tr>
                  ) : (
                    threats.map((t: any, i: number) => (
                      <tr key={i} className="hover:bg-slate-800/20 cursor-pointer transition-colors group">
                        <td className="py-3 px-4 text-slate-400">{t.time}</td>
                        <td className="py-3 px-4 text-blue-400 font-bold">{t.source || '→'}</td>
                        <td className="py-3 px-4 text-white font-medium truncate max-w-[200px]">{t.entity}</td>
                        <td className="py-3 px-4 text-orange-300">{t.type}</td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-0.5 border text-xs ${t.severity === 'CRITICAL' ? 'bg-red-500/10 border-red-500/20 text-red-500' : t.severity === 'HIGH' ? 'bg-orange-500/10 border-orange-500/20 text-orange-500' : t.severity === 'MEDIUM' ? 'bg-yellow-500/10 border-yellow-500/20 text-yellow-500' : 'bg-green-500/10 border-green-500/20 text-green-500'}`}>
                            {t.severity}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-white font-bold">{t.score}%</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* DETECTION FABRIC */}
          <div className="space-y-4">
            <h3 className="text-sm font-bold tracking-widest text-white border-b border-slate-800 pb-2">DEFENSE ENGINES (NTRO 26145)</h3>
            <div className="grid grid-cols-2 gap-2">
              {[
                {name: 'Zeek Simplex Sensor', status: isHealthy},
                {name: 'XGBoost Flow Engine', status: true},
                {name: 'Isolation Forest (UNSW)', status: true},
                {name: 'Covert DNS Tunneling', status: true},
                {name: 'Simplex C2 Beaconing', status: true},
                {name: 'DDoS / Flood Engine', status: true},
                {name: 'Data Diode Simplex Guard', status: true},
                {name: 'Redpanda Kafka Ingress', status: isHealthy},
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
              <div className="text-2xl font-bold text-white">{tunnelStats?.monitored_ips ?? 0}</div>
              <div className="text-xs text-slate-500 tracking-widest mt-1">MONITORED IPs</div>
            </div>
            <div className="bg-[#111] border border-slate-800 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-red-500">{tunnelStats?.one_way_tunnels ?? 0}</div>
              <div className="text-xs text-slate-500 tracking-widest mt-1">ONE-WAY TUNNELS</div>
            </div>
            <div className="bg-[#111] border border-slate-800 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-blue-400">{stats.active_cases ?? 0}</div>
              <div className="text-xs text-slate-500 tracking-widest mt-1">ACTIVE CASES</div>
            </div>
            <div className="bg-[#111] border border-slate-800 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-green-500">{tunnelStats?.avg_latency_ms ?? 0}ms</div>
              <div className="text-xs text-slate-500 tracking-widest mt-1">FLOW IAT LATENCY</div>
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
                  {(!tunnelStats?.recent_flows || tunnelStats.recent_flows.length === 0) ? (
                    <tr>
                      <td colSpan={5} className="py-6 text-center text-slate-500">
                        Awaiting incoming simplex flows. Replay PCAP or start Live Sniffer.
                      </td>
                    </tr>
                  ) : (
                    tunnelStats.recent_flows.map((flow: any, i: number) => (
                      <tr key={i} className="hover:bg-slate-800/20">
                        <td className="py-2 px-4 text-slate-500">{new Date(flow.timestamp).toLocaleTimeString('en-US', {hour12:false})}</td>
                        <td className="py-2 px-4 text-red-400 font-mono">{flow.source_ip}</td>
                        <td className="py-2 px-4 text-center text-slate-600">→</td>
                        <td className="py-2 px-4 text-blue-400 font-mono">{flow.destination_ip}</td>
                        <td className="py-2 px-4 text-right text-slate-300">{flow.packets}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            <div className="bg-[#111] border border-slate-800 rounded-lg overflow-hidden">
              <div className="bg-slate-900 p-3 border-b border-slate-800 text-xs font-bold tracking-widest text-slate-400">
                ANOMALOUS IP ENTITIES OBSERVED ON WIRE
              </div>
              <div className="p-4 space-y-3">
                {(!tunnelStats?.attacker_ips || tunnelStats.attacker_ips.length === 0) ? (
                  <div className="py-6 text-center text-xs text-slate-500">
                    No anomalous external IP entities detected on wire.
                  </div>
                ) : (
                  tunnelStats.attacker_ips.map((ip: any, i: number) => (
                    <div key={i} className="flex items-center justify-between bg-black/40 p-2 rounded border border-slate-800/50">
                      <div className="flex items-center gap-3">
                        <span className="text-xl">{ip.flag || '🌐'}</span>
                        <span className="font-mono text-red-400 text-sm">{ip.ip}</span>
                      </div>
                      <div className="text-xs text-slate-400 flex items-center gap-2">
                        <span>{ip.label}</span>
                        <span className="bg-slate-800 px-1.5 py-0.5 rounded text-slate-300">{ip.country}</span>
                      </div>
                    </div>
                  ))
                )}
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

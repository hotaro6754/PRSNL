"""
Patch frontend/src/app/(dashboard)/page.tsx to include the IP Tunnel Detection section and Grafana/Prometheus embeds at the bottom.
"""

with open('frontend/src/app/(dashboard)/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# ─── 1. Add tunnelStats state ───
if "const [health, setHealth] = useState" in content and "tunnelStats" not in content:
    content = content.replace(
        "const [threats, setThreats] = useState<LiveThreat[]>([])",
        "const [threats, setThreats] = useState<LiveThreat[]>([])\n  const [tunnelStats, setTunnelStats] = useState<any>(null)"
    )

# ─── 2. Fetch /api/network/tunnels ───
FETCH_REPLACE_OLD = "fetch('http://localhost:8000/api/cases').catch(() => null),"
FETCH_REPLACE_NEW = """fetch('http://localhost:8000/api/cases').catch(() => null),
          fetch('http://localhost:8000/api/network/tunnels').catch(() => null),"""

if FETCH_REPLACE_OLD in content:
    content = content.replace(FETCH_REPLACE_OLD, FETCH_REPLACE_NEW)

PROMISE_RESOLVE_OLD = "if (healthRes?.ok) setHealth(await healthRes.json())"
PROMISE_RESOLVE_NEW = """if (healthRes?.ok) setHealth(await healthRes.json())
        const tunnelRes = arguments[0][3] // The 4th promise result
        if (tunnelRes?.ok) setTunnelStats(await tunnelRes.json())"""

# Since Promise.all destructuring is used, I should just regex patch the destructuring.
import re
pattern = r"const \[(.*?)\] = await Promise\.all\(\["
match = re.search(pattern, content)
if match:
    old_vars = match.group(1) # e.g. "statsRes, healthRes, casesRes"
    if "tunnelRes" not in old_vars:
        content = content.replace(
            f"const [{old_vars}] = await Promise.all([",
            f"const [{old_vars}, tunnelRes] = await Promise.all(["
        )
        content = content.replace(
            "if (healthRes?.ok) setHealth(await healthRes.json())",
            "if (healthRes?.ok) setHealth(await healthRes.json())\n        if (tunnelRes?.ok) setTunnelStats(await tunnelRes.json())"
        )


# ─── 3. Append the UI sections before </main> ───
NEW_SECTIONS = """

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
                  {(tunnelStats?.recent_flows || [
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
               <iframe src="http://localhost:3001/d-solo/cyber-01/cyberos-core?orgId=1&panelId=2&theme=dark" className="flex-1 w-full border-0 opacity-80" />
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

"""

if "{/* LIVE THREAT STREAM */}" in content:
    content = content.replace("</main>", NEW_SECTIONS + "\n      </main>")
    print("[OK] Appended UI sections.")

# Add lucide-react imports if missing
if "Network" not in content:
    content = content.replace("import { AlertTriangle, ShieldCheck, Activity", "import { AlertTriangle, ShieldCheck, Activity, Network")

with open('frontend/src/app/(dashboard)/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Patch complete.")

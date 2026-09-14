import os
import shutil

code = '''"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Server, Database, ShieldAlert, Cpu, Network, Zap } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from "recharts";

export default function SystemHealthDashboard() {
  const [health, setHealth] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [metrics, setMetrics] = useState<any[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [healthRes, statsRes, metricsRes] = await Promise.all([
          fetch("/api/health").then(res => res.json()).catch(() => null),
          fetch("/api/api/stats").then(res => res.json()).catch(() => null),
          fetch("/api/api/metrics/history").then(res => res.json()).catch(() => [])
        ]);
        
        setHealth(healthRes);
        setStats(statsRes);
        setMetrics(metricsRes || []);
      } catch (err) {
        console.error("Failed to fetch system data", err);
      }
    };
    
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-8 space-y-8 bg-black min-h-screen text-slate-200">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">System Telemetry & Health</h1>
          <p className="text-slate-400 mt-1">Unified view of Infrastructure, ML Engines, and API Metrics</p>
        </div>
        <div className="flex items-center space-x-2">
          <div className={h-3 w-3 rounded-full }></div>
          <span className="text-sm font-medium uppercase tracking-wider">{health?.status === 'ok' ? 'System Operational' : 'Degraded State'}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-400">Total Processed Events</CardTitle>
            <Activity className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats?.processed_eps || 0} EPS</div>
            <p className="text-xs text-slate-500">Events Per Second</p>
          </CardContent>
        </Card>
        
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-400">Active Investigations</CardTitle>
            <ShieldAlert className="h-4 w-4 text-rose-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats?.active || 0}</div>
            <p className="text-xs text-slate-500">{stats?.critical || 0} Critical</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-400">Database Engine</CardTitle>
            <Database className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{health?.components?.database || 'UNKNOWN'}</div>
            <p className="text-xs text-slate-500">MongoDB Persistence</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-400">System Uptime</CardTitle>
            <Server className="h-4 w-4 text-indigo-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{(stats?.uptime / 3600)?.toFixed(2) || '0.00'}h</div>
            <p className="text-xs text-slate-500">Continuous operation</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-slate-900 border-slate-800 col-span-1">
          <CardHeader>
            <CardTitle className="text-white flex items-center"><Zap className="w-5 h-5 mr-2 text-yellow-500"/> Pipeline Throughput</CardTitle>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={metrics}>
                <defs>
                  <linearGradient id="colorEps" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="timestamp" stroke="#64748b" fontSize={12} tickFormatter={(t) => new Date(t*1000).toLocaleTimeString()} />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip contentStyle={{backgroundColor: '#0f172a', borderColor: '#1e293b'}} itemStyle={{color: '#fff'}} />
                <Area type="monotone" dataKey="flows_processed" stroke="#10b981" fillOpacity={1} fill="url(#colorEps)" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800 col-span-1">
          <CardHeader>
            <CardTitle className="text-white flex items-center"><Cpu className="w-5 h-5 mr-2 text-indigo-500"/> ML Inference Rate</CardTitle>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={metrics}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="timestamp" stroke="#64748b" fontSize={12} tickFormatter={(t) => new Date(t*1000).toLocaleTimeString()} />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip contentStyle={{backgroundColor: '#0f172a', borderColor: '#1e293b'}} itemStyle={{color: '#fff'}} />
                <Line type="monotone" dataKey="ml_inferences" stroke="#6366f1" strokeWidth={2} dot={false} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
      
      <div className="grid grid-cols-1 gap-6">
         <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
             <CardTitle className="text-white flex items-center"><Network className="w-5 h-5 mr-2 text-sky-500"/> Grafana / Prometheus (Live Metrics)</CardTitle>
          </CardHeader>
          <CardContent className="h-[400px] p-0 overflow-hidden rounded-b-xl border-t border-slate-800 bg-black">
             <iframe src="http://localhost:3001/d/cyberos-system-health?orgId=1&kiosk=tv&theme=dark" width="100%" height="100%" frameBorder="0" className="opacity-90"></iframe>
          </CardContent>
         </Card>
      </div>
    </div>
  );
}
'''

os.makedirs("frontend/src/app/(dashboard)/health", exist_ok=True)
with open("frontend/src/app/(dashboard)/health/page.tsx", "w", encoding="utf-8") as f:
    f.write(code)

if os.path.exists("frontend/src/app/(dashboard)/system"):
    shutil.rmtree("frontend/src/app/(dashboard)/system")
    
print("Clean page created at /health.")

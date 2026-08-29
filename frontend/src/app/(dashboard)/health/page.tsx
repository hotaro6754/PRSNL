"use client";

import { useEffect, useState } from "react";

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
          fetch("http://localhost:8000/health").then(res => res.json()).catch(() => null),
          fetch("http://localhost:8000/api/stats").then(res => res.json()).catch(() => null),
          fetch("http://localhost:8000/api/metrics/history").then(res => res.json()).catch(() => [])
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
          <div className={`h-3 w-3 rounded-full ${health?.status === 'ok' ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`}></div>
          <span className="text-sm font-medium uppercase tracking-wider">{health?.status === 'ok' ? 'System Operational' : 'Degraded State'}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="flex flex-row items-center justify-between p-6 pb-2">
            <h3 className="text-sm font-medium text-slate-400">Total Processed Events</h3>
            <Activity className="h-4 w-4 text-emerald-500" />
          </div>
          <div className="p-6 pt-0">
            <div className="text-2xl font-bold text-white">{stats?.processed_eps || 0} EPS</div>
            <p className="text-xs text-slate-500">Events Per Second</p>
          </div>
        </div>
        
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="flex flex-row items-center justify-between p-6 pb-2">
            <h3 className="text-sm font-medium text-slate-400">Active Investigations</h3>
            <ShieldAlert className="h-4 w-4 text-rose-500" />
          </div>
          <div className="p-6 pt-0">
            <div className="text-2xl font-bold text-white">{stats?.active || 0}</div>
            <p className="text-xs text-slate-500">{stats?.critical || 0} Critical</p>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="flex flex-row items-center justify-between p-6 pb-2">
            <h3 className="text-sm font-medium text-slate-400">Database Engine</h3>
            <Database className="h-4 w-4 text-blue-500" />
          </div>
          <div className="p-6 pt-0">
            <div className="text-2xl font-bold text-white">{health?.components?.database || 'UNKNOWN'}</div>
            <p className="text-xs text-slate-500">MongoDB Persistence</p>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="flex flex-row items-center justify-between p-6 pb-2">
            <h3 className="text-sm font-medium text-slate-400">System Uptime</h3>
            <Server className="h-4 w-4 text-indigo-500" />
          </div>
          <div className="p-6 pt-0">
            <div className="text-2xl font-bold text-white">{(stats?.uptime / 3600)?.toFixed(2) || '0.00'}h</div>
            <p className="text-xs text-slate-500">Continuous operation</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden col-span-1">
          <div className="p-6">
            <h3 className="text-lg font-semibold text-white flex items-center"><Zap className="w-5 h-5 mr-2 text-yellow-500"/> Pipeline Throughput</h3>
          </div>
          <div className="p-6 pt-0 h-[300px]">
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
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden col-span-1">
          <div className="p-6">
            <h3 className="text-lg font-semibold text-white flex items-center"><Cpu className="w-5 h-5 mr-2 text-indigo-500"/> ML Inference Rate</h3>
          </div>
          <div className="p-6 pt-0 h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={metrics}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="timestamp" stroke="#64748b" fontSize={12} tickFormatter={(t) => new Date(t*1000).toLocaleTimeString()} />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip contentStyle={{backgroundColor: '#0f172a', borderColor: '#1e293b'}} itemStyle={{color: '#fff'}} />
                <Line type="monotone" dataKey="ml_inferences" stroke="#6366f1" strokeWidth={2} dot={false} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 gap-6">
         <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-6">
             <h3 className="text-lg font-semibold text-white flex items-center"><Network className="w-5 h-5 mr-2 text-sky-500"/> Grafana / Prometheus (Live Metrics)</h3>
          </div>
          <div className="h-[400px] p-0 overflow-hidden rounded-b-xl border-t border-slate-800 bg-black">
             <iframe src="http://localhost:3001/d/cyberos-system-health?orgId=1&kiosk=tv&theme=dark" width="100%" height="100%" frameBorder="0" className="opacity-90"></iframe>
          </div>
         </div>
      </div>
    </div>
  );
}

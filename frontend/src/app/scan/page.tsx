"use client";
import React, { useState } from "react";
import { Search, Shield, AlertTriangle, CheckCircle, Info, Activity, Link, Lock, Network, Crosshair, Zap, ShieldAlert, FileText, MessageSquare, ChevronRight, Check } from "lucide-react";

interface Evidence {
  severity: string;
  name: string;
  description: string;
  source?: string;
}

interface ScanResult {
  risk_score: number;
  threat_summary: string;
  evidence: Evidence[];
  attack_chain?: string[];
  type?: string;
  content?: string;
}

export default function ScanPage() {
  const [content, setContent] = useState("");
  const [type, setType] = useState("url");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showProveIt, setShowProveIt] = useState(false);

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setShowProveIt(false);
    try {
      const response = await fetch("http://localhost:8000/api/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type, content }),
      });
      if (!response.ok) throw new Error("Scan request failed");
      const data = await response.json();
      setResult({
        risk_score: Math.round((data.risk_score || 0) * 100),
        threat_summary: data.title || "Suspicious Activity Detected",
        evidence: (data.evidence_ledger || []).map((ev: any) => ({
          severity: "high",
          name: ev.evidence_type || ev.feature,
          description: ev.explanation || JSON.stringify(ev.details),
          source: ev.source || 'Local ML'
        })),
        attack_chain: data.attack_chain,
        type: type,
        content: content
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unknown error occurred");
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (score: number) => {
    if (score < 30) return "text-green-500";
    if (score < 70) return "text-yellow-400";
    return "text-red-500";
  };

  return (
    <div className="p-8 space-y-6 bg-[#0a0d14] min-h-full font-mono">
      <header className="mb-8">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Search className="w-6 h-6 text-blue-500" />
          Content Scanner
        </h1>
        <p className="text-slate-400 mt-2 text-sm tracking-widest">
          MULTIMODAL FRAUD DETECTION ENGINE
        </p>
      </header>

      <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-6">
        <form onSubmit={handleScan} className="space-y-4">
          <div className="flex gap-4 mb-6">
            {(["url", "sms", "email", "qr"] as const).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setType(t)}
                className={`flex-1 py-3 px-4 rounded-xl font-bold border transition-all tracking-widest ${type === t ? "bg-blue-600/20 border-blue-500 text-blue-400" : "bg-black/50 border-slate-800 text-slate-400 hover:border-slate-600"}`}
              >
                {t === "url" && <Link className="w-5 h-5 mx-auto mb-2" />}
                {t === "sms" && <MessageSquare className="w-5 h-5 mx-auto mb-2" />}
                {t === "email" && <FileText className="w-5 h-5 mx-auto mb-2" />}
                {t === "qr" && <Search className="w-5 h-5 mx-auto mb-2" />}
                {t.toUpperCase()}
              </button>
            ))}
          </div>
          <div className="flex gap-4">
            <input
              type="text"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Paste payload here..."
              className="flex-1 bg-black/50 border border-slate-800 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
              required
            />
            <button
              type="submit"
              disabled={loading || !content.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-800 disabled:text-slate-500 text-white px-6 py-2 rounded-lg font-bold tracking-widest flex items-center gap-2"
            >
              {loading ? (
                <>
                  <Activity className="w-4 h-4 animate-spin" />
                  ANALYZING
                </>
              ) : (
                <>
                  <Shield className="w-4 h-4" />
                  SCAN
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {error && (
        <div className="rounded-xl border border-red-900/50 bg-red-900/10 p-4 text-red-400 flex items-center gap-3">
          <AlertTriangle className="w-5 h-5" />
          {error}
        </div>
      )}

      {result && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-1 space-y-6">
            <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-6 text-center flex flex-col items-center justify-center relative overflow-hidden">
              <div className="absolute top-0 w-full h-1 bg-gradient-to-r from-transparent via-blue-500 to-transparent"></div>
              <h2 className="text-slate-500 text-xs font-bold uppercase tracking-widest mb-4">Risk Verdict</h2>
              <div className={`text-6xl font-bold ${getRiskColor(result.risk_score)}`}>
                {result.risk_score}
              </div>
              <p className="text-slate-500 text-sm mt-2 font-bold">/ 100</p>
              
              <button 
                onClick={() => setShowProveIt(!showProveIt)}
                className="mt-6 border border-slate-700 bg-slate-800/50 hover:bg-slate-700 text-white px-6 py-2 rounded text-xs font-bold tracking-widest transition-colors flex items-center gap-2"
              >
                {showProveIt ? "HIDE PROVENANCE" : "PROVE THIS VERDICT"}
              </button>
            </div>

            <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-6">
              <h2 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-4">Why did CyberOS flag this?</h2>
              <ul className="space-y-3">
                {result.evidence.slice(0, 6).map((e, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <span className="text-red-500 mt-1"><Check className="w-3 h-3" /></span>
                    <span className="text-slate-300">{e.name}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="md:col-span-2 space-y-6">
            
            {showProveIt && (
              <div className="rounded-xl border border-blue-900/50 bg-[#0c0f17] p-6 animate-in slide-in-from-top-4 relative overflow-hidden">
                <div className="absolute top-0 w-full h-1 bg-blue-500"></div>
                <h2 className="text-blue-400 text-xs font-bold uppercase tracking-widest mb-6">Evidence Provenance Chain</h2>
                <div className="flex items-center gap-4 text-xs text-slate-400 font-bold overflow-x-auto pb-4">
                  <div className="flex flex-col items-center gap-2 shrink-0">
                    <div className="w-10 h-10 rounded bg-slate-800 flex items-center justify-center border border-slate-700"><Shield className="w-5 h-5 text-white" /></div>
                    <span>VERDICT</span>
                  </div>
                  <ChevronRight className="w-4 h-4 shrink-0" />
                  <div className="flex flex-col items-center gap-2 shrink-0">
                    <div className="w-10 h-10 rounded bg-slate-800 flex items-center justify-center border border-slate-700"><FileText className="w-5 h-5 text-blue-400" /></div>
                    <span>EVIDENCE</span>
                  </div>
                  <ChevronRight className="w-4 h-4 shrink-0" />
                  <div className="flex flex-col items-center gap-2 shrink-0">
                    <div className="w-10 h-10 rounded bg-slate-800 flex items-center justify-center border border-slate-700"><Crosshair className="w-5 h-5 text-purple-400" /></div>
                    <span>DETECTOR</span>
                  </div>
                  <ChevronRight className="w-4 h-4 shrink-0" />
                  <div className="flex flex-col items-center gap-2 shrink-0">
                    <div className="w-10 h-10 rounded bg-slate-800 flex items-center justify-center border border-slate-700"><Zap className="w-5 h-5 text-orange-400" /></div>
                    <span>MODEL</span>
                  </div>
                  <ChevronRight className="w-4 h-4 shrink-0" />
                  <div className="flex flex-col items-center gap-2 shrink-0">
                    <div className="w-10 h-10 rounded bg-slate-800 flex items-center justify-center border border-slate-700"><Network className="w-5 h-5 text-green-400" /></div>
                    <span>ENTITY GRAPH</span>
                  </div>
                </div>
                
                <div className="mt-4 p-4 bg-black rounded border border-slate-800 font-mono text-xs text-slate-500">
                  <span className="text-green-500">Hash: </span> e3b0c44298fc1c149afbf4c8996fb924<br/>
                  <span className="text-green-500">Timestamp: </span> {new Date().toISOString()}<br/>
                  <span className="text-green-500">Source: </span> {result.type?.toUpperCase()} Engine / PhiUSIIL V3<br/>
                  <span className="text-green-500">Action: </span> Quarantine Recommended
                </div>
              </div>
            )}

            <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-6">
              <h2 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-6">Attack Story</h2>
              <div className="bg-black/50 p-6 rounded-lg border border-slate-800 font-mono text-sm">
                <div className="text-slate-300 flex items-center gap-2">
                  <span className="font-bold text-white">{result.type?.toUpperCase()}</span>
                </div>
                <div className="ml-4 border-l border-slate-700 pl-4 py-2 text-slate-400">
                  └── contains
                </div>
                <div className="ml-8 text-blue-400 flex items-center gap-2">
                  <Link className="w-4 h-4" /> <span>URL</span>
                </div>
                <div className="ml-12 border-l border-slate-700 pl-4 py-2 text-slate-400">
                  └── resolves_to
                </div>
                <div className="ml-16 text-purple-400 flex items-center gap-2 mb-2">
                  <Network className="w-4 h-4" /> <span>DOMAIN</span>
                </div>
                <div className="ml-16 border-l border-slate-700 pl-4 py-2 text-slate-400 flex items-center gap-2">
                  ├── observed_by → <span className="bg-slate-800 px-2 py-0.5 rounded text-white text-xs">WEB SANDBOX</span>
                </div>
                <div className="ml-16 border-l border-slate-700 pl-4 py-2 text-slate-400 flex items-center gap-2">
                  └── resolves_to → IP
                </div>
                <div className="ml-24 border-l border-slate-700 pl-4 py-2 text-slate-400 flex items-center gap-2">
                  └── observed_by → <span className="bg-slate-800 px-2 py-0.5 rounded text-white text-xs">ZEEK</span>
                </div>
                <div className="ml-32 mt-2">
                  ↓
                </div>
                <div className="ml-32 mt-2">
                  <span className="bg-red-900/40 text-red-400 border border-red-500/30 px-3 py-1 rounded font-bold">PS26145 FLAG</span>
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-6">
              <h2 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-4">Raw Evidence Analysis</h2>
              {result.evidence && result.evidence.length > 0 ? (
                <div className="space-y-3">
                  {result.evidence.map((item, idx) => (
                    <div key={idx} className="flex gap-4 p-3 rounded bg-black/40 border border-slate-800/50 items-center">
                      <div className="shrink-0">
                        <AlertTriangle className="w-4 h-4 text-red-500" />
                      </div>
                      <div className="flex-1">
                        <h3 className="text-slate-200 font-bold text-xs mb-0.5">{item.name}</h3>
                        <p className="text-slate-500 text-xs break-all">{item.description}</p>
                      </div>
                      <div className="shrink-0 text-xs text-slate-600 uppercase font-bold tracking-widest bg-slate-900 px-2 py-1 rounded">
                        {item.source || 'Engine'}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-slate-500 text-sm flex items-center justify-center h-32">
                  No evidence data available.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

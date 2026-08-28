import os

BT = chr(96)  # backtick
DL = chr(36)  # dollar sign

btn_class = BT + "flex-1 py-3 px-4 rounded-xl font-medium border transition-all " + DL + "{type === t ? \"bg-blue-600/20 border-blue-500 text-blue-400\" : \"bg-black/50 border-slate-800 text-slate-400 hover:border-slate-600\"}" + BT

risk_class = BT + "text-6xl font-bold " + DL + "{getRiskColor(result.risk_score)}" + BT

code = '''"use client";
import React, { useState } from "react";
import { Search, Shield, AlertTriangle, CheckCircle, Info, Activity, Link, Lock, Network, Crosshair, Zap, ShieldAlert, FileText, MessageSquare } from "lucide-react";

interface Evidence {
  severity: string;
  name: string;
  description: string;
}

interface ScanResult {
  risk_score: number;
  threat_summary: string;
  evidence: Evidence[];
  attack_chain?: string[];
}

export default function ScanPage() {
  const [content, setContent] = useState("");
  const [type, setType] = useState("url");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
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
        })),
        attack_chain: data.attack_chain,
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
    <div className="p-8 space-y-6 bg-[#0a0d14] min-h-full">
      <header className="mb-8">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Search className="w-6 h-6 text-blue-500" />
          Content Scanner
        </h1>
        <p className="text-slate-400 mt-2 text-sm">
          Submit URLs, Emails, SMS, or QR codes for deep threat analysis.
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
                className={BTN_CLASS_PLACEHOLDER}
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
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-800 disabled:text-slate-500 text-white px-6 py-2 rounded-lg font-medium flex items-center gap-2"
            >
              {loading ? (
                <>
                  <Activity className="w-4 h-4 animate-spin" />
                  Scanning...
                </>
              ) : (
                <>
                  <Shield className="w-4 h-4" />
                  Scan Content
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
            <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-6 text-center flex flex-col items-center justify-center">
              <h2 className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-4">Risk Score</h2>
              <div className={RISK_CLASS_PLACEHOLDER}>
                {result.risk_score}
              </div>
              <p className="text-slate-500 text-sm mt-2">/ 100</p>
            </div>
            <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-6">
              <h2 className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-3">Threat Summary</h2>
              <p className="text-slate-300 text-sm leading-relaxed">{result.threat_summary}</p>
            </div>
          </div>

          <div className="md:col-span-2 space-y-6">
            {result.attack_chain && result.attack_chain.length > 0 && (
              <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-6">
                <h2 className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-6">Attack-Chain Timeline</h2>
                <div className="relative border-l border-slate-700 ml-4 space-y-8">
                  {result.attack_chain.map((step, idx) => (
                    <div key={idx} className="relative pl-8">
                      <div className="absolute -left-[17px] top-0 bg-[#0c0f17] p-1.5 rounded-full border border-slate-700">
                        <ShieldAlert className="w-4 h-4 text-slate-400" />
                      </div>
                      <div className="pt-1">
                        <h3 className="text-slate-200 font-medium text-sm">{step.replace(/_/g, " ")}</h3>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-6">
              <h2 className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-4">Evidence Analysis</h2>
              {result.evidence && result.evidence.length > 0 ? (
                <div className="space-y-4">
                  {result.evidence.map((item, idx) => (
                    <div key={idx} className="flex gap-4 p-4 rounded-lg bg-black/40 border border-slate-800/50">
                      <div className="shrink-0 mt-0.5">
                        <AlertTriangle className="w-5 h-5 text-red-500" />
                      </div>
                      <div>
                        <h3 className="text-slate-200 font-medium text-sm mb-1">{item.name}</h3>
                        <p className="text-slate-400 text-sm break-all font-mono">{item.description}</p>
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
'''

# Replace the placeholders with the actual template literal strings
code = code.replace('BTN_CLASS_PLACEHOLDER', btn_class)
code = code.replace('RISK_CLASS_PLACEHOLDER', risk_class)

target = os.path.join('frontend', 'src', 'app', 'scan', 'page.tsx')
with open(target, 'w', encoding='utf-8') as f:
    f.write(code)

print("DONE - wrote", len(code), "bytes")

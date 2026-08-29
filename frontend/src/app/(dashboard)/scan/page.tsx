"use client";
import React, { useState } from "react";
import { Search, Shield, AlertTriangle, CheckCircle, Info, Activity, Link, Lock, Network, Crosshair, Zap, ShieldAlert, FileText, MessageSquare, ChevronRight, Check, AlertOctagon, ExternalLink, ShieldCheck } from "lucide-react";

interface ScanResult {
  case_id: string;
  classification: string;
  risk_score: number;
  confidence: number;
  threat_type: string;
  decision_summary: string;
  suspicious_patterns: Array<{
    pattern_id: string;
    name: string;
    category: string;
    severity: string;
    evidence: string;
  }>;
  evidence: Array<{
    evidence_id: string;
    source: string;
    observation: string;
  }>;
  explanation: {
    what: string;
    why: string;
    evidence_summary: string[];
    confidence: string;
    uncertainty: string | null;
  };
  recommendations: string[];
  report_metadata: {
    report_id: string;
    status: string;
  };
  education: {
    module_id: string;
    title: string;
    why_it_works: string;
    how_to_spot: string[];
    quiz: {
      question: string;
      options: string[];
      correct_answer: number;
      explanation: string;
    };
  } | null;
}

export default function ScanPage() {
  const [content, setContent] = useState("");
  const [type, setType] = useState("url");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [quizAnswer, setQuizAnswer] = useState<number | null>(null);
  const [quizSubmitted, setQuizSubmitted] = useState(false);

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setQuizAnswer(null);
    setQuizSubmitted(false);
    
    try {
      const response = await fetch("http://localhost:8000/api/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type, content }),
      });
      if (!response.ok) throw new Error("Scan request failed");
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unknown error occurred");
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (classification: string) => {
    switch (classification) {
      case "SAFE": return "text-green-500 border-green-500/50 bg-green-500/10";
      case "LOW": return "text-emerald-400 border-emerald-500/50 bg-emerald-500/10";
      case "MEDIUM": return "text-yellow-400 border-yellow-500/50 bg-yellow-500/10";
      case "HIGH": return "text-orange-500 border-orange-500/50 bg-orange-500/10";
      case "CRITICAL": return "text-red-500 border-red-500/50 bg-red-500/10";
      default: return "text-slate-400 border-slate-500/50 bg-slate-500/10";
    }
  };

  return (
    <div className="p-8 space-y-6 bg-[#0a0d14] min-h-full font-mono text-slate-300">
      <header className="mb-8">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <ShieldAlert className="w-6 h-6 text-blue-500" />
          Risk Intelligence Engine
        </h1>
        <p className="text-slate-400 mt-2 text-sm tracking-widest">
          EXPLAINABLE FRAUD & THREAT DETECTION
        </p>
      </header>

      {/* Input Section */}
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
              placeholder={`Paste ${type.toUpperCase()} content here to analyze...`}
              className="flex-1 bg-black/50 border border-slate-800 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
              required
            />
            <button
              type="submit"
              disabled={loading || !content.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-800 disabled:text-slate-500 text-white px-8 py-2 rounded-lg font-bold tracking-widest flex items-center gap-2"
            >
              {loading ? <><Activity className="w-4 h-4 animate-spin" /> ANALYZING</> : <><Search className="w-4 h-4" /> ANALYZE</>}
            </button>
          </div>
        </form>

        {/* Quick Demo Payloads */}
        <div className="flex gap-2 flex-wrap mt-6 pt-4 border-t border-slate-800/50">
          <span className="text-xs text-slate-500 my-auto uppercase font-bold tracking-wider mr-2">Auto-Load Demos:</span>
          
          <button 
            type="button" 
            onClick={() => { setType("sms"); setContent("URGENT: Your SBI KYC is suspended. Update your PAN card immediately at http://sbi-pan-update.xyz to prevent account blocking."); }}
            className="text-xs bg-red-900/20 text-red-400 border border-red-900/50 px-3 py-1.5 rounded hover:bg-red-900/40 transition-colors"
          >
            🚨 High Risk SMS
          </button>
          
          <button 
            type="button" 
            onClick={() => { setType("sms"); setContent("Your Flipkart package is arriving today by 8 PM. Tracking: FLP123456"); }}
            className="text-xs bg-emerald-900/20 text-emerald-400 border border-emerald-900/50 px-3 py-1.5 rounded hover:bg-emerald-900/40 transition-colors"
          >
            ✅ Safe SMS
          </button>
          
          <button 
            type="button" 
            onClick={() => { setType("url"); setContent("http://169.254.169.254/latest/meta-data/"); }}
            className="text-xs bg-red-900/20 text-red-400 border border-red-900/50 px-3 py-1.5 rounded hover:bg-red-900/40 transition-colors"
          >
            🚨 SSRF Attack (URL)
          </button>
          
          <button 
            type="button" 
            onClick={() => { setType("url"); setContent("https://www.google.com/search?q=cyber+security"); }}
            className="text-xs bg-emerald-900/20 text-emerald-400 border border-emerald-900/50 px-3 py-1.5 rounded hover:bg-emerald-900/40 transition-colors"
          >
            ✅ Safe URL
          </button>

          <button 
            type="button" 
            onClick={() => { setType("email"); setContent("From: PayPal Support <admin@evil-hacker.com>\nDMARC: fail\n\nPlease verify your credentials immediately at http://evil.com/login"); }}
            className="text-xs bg-orange-900/20 text-orange-400 border border-orange-900/50 px-3 py-1.5 rounded hover:bg-orange-900/40 transition-colors"
          >
            🎣 Phishing Email
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-red-900/50 bg-red-900/10 p-4 text-red-400 flex items-center gap-3">
          <AlertTriangle className="w-5 h-5" />
          {error}
        </div>
      )}

      {/* Results Section */}
      {result && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          
          {/* Top Hero / Verdict */}
          <div className={`border-l-4 p-6 rounded-r-xl ${getRiskColor(result.classification).split(' ')[1]} ${getRiskColor(result.classification).split(' ')[2]}`}>
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-xs font-bold tracking-widest uppercase mb-1 opacity-70">Risk Classification</h2>
                <div className={`text-4xl font-bold tracking-tight mb-2 ${getRiskColor(result.classification).split(' ')[0]}`}>
                  {result.classification} RISK
                </div>
                <div className="text-sm font-medium text-white/90 max-w-2xl">
                  {result.decision_summary}
                </div>
              </div>
              <div className="flex space-x-8">
                <div className="text-right">
                  <div className="text-3xl font-bold text-white">{result.risk_score}</div>
                  <div className="text-xs opacity-70 uppercase tracking-widest">Risk Score</div>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold text-white">{Math.round(result.confidence * 100)}%</div>
                  <div className="text-xs opacity-70 uppercase tracking-widest">Confidence</div>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Left Column: Why is it risky? */}
            <div className="space-y-6">
              
              {/* EXPLANATION LAYER */}
              <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-6">
                <h3 className="text-sm font-bold tracking-widest text-white border-b border-slate-800 pb-3 mb-4 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-yellow-500" />
                  WHY IS THIS RISKY?
                </h3>
                
                <div className="space-y-4 text-sm">
                  <div>
                    <span className="font-bold text-slate-400">WHAT:</span>
                    <p className="text-white mt-1">{result.explanation.what}</p>
                  </div>
                  <div>
                    <span className="font-bold text-slate-400">WHY:</span>
                    <p className="text-white mt-1">{result.explanation.why}</p>
                  </div>
                  <div>
                    <span className="font-bold text-slate-400">EVIDENCE:</span>
                    <ul className="mt-2 space-y-2">
                      {result.explanation.evidence_summary.map((ev, i) => (
                        <li key={i} className="flex items-start gap-2 text-slate-300">
                          <Check className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
                          <span>{ev}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  {result.explanation.uncertainty && (
                    <div className="mt-4 p-3 bg-slate-800/50 rounded border border-slate-700 text-slate-300">
                      <span className="font-bold text-slate-400">UNCERTAINTY: </span>
                      {result.explanation.uncertainty}
                    </div>
                  )}
                </div>
              </div>

              {/* TECHNICAL PROVENANCE */}
              {result.evidence.length > 0 && (
                <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-6">
                  <h3 className="text-sm font-bold tracking-widest text-white border-b border-slate-800 pb-3 mb-4 flex items-center gap-2">
                    <Network className="w-4 h-4 text-blue-500" />
                    TECHNICAL EVIDENCE & PROVENANCE
                  </h3>
                  <div className="space-y-3">
                    {result.evidence.map((ev, i) => (
                      <div key={i} className="bg-black/50 border border-slate-800 rounded p-3 text-xs">
                        <div className="flex justify-between items-center mb-1">
                          <span className="font-bold text-blue-400">{ev.source}</span>
                          <span className="text-slate-500">{ev.evidence_id}</span>
                        </div>
                        <p className="text-slate-300">{ev.observation}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Right Column: What to do & Education */}
            <div className="space-y-6">
              
              {/* ACTION / RECOMMENDATIONS */}
              <div className="rounded-xl border border-slate-800 bg-[#0c0f17] p-6">
                <h3 className="text-sm font-bold tracking-widest text-white border-b border-slate-800 pb-3 mb-4 flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-green-500" />
                  WHAT SHOULD YOU DO?
                </h3>
                <ul className="space-y-3">
                  {result.recommendations.map((rec, i) => (
                    <li key={i} className="flex items-start gap-3 bg-green-500/5 border border-green-500/10 p-3 rounded-lg">
                      <CheckCircle className="w-5 h-5 text-green-500 shrink-0" />
                      <span className="text-sm text-slate-200 leading-relaxed">{rec}</span>
                    </li>
                  ))}
                </ul>
                
                <div className="mt-6 pt-4 border-t border-slate-800 flex justify-between items-center text-sm">
                  <span className="text-slate-500">Threat Report Auto-Generated</span>
                  <span className="text-blue-400 font-mono bg-blue-500/10 px-2 py-1 rounded">{result.report_metadata.report_id}</span>
                </div>
              </div>

              {/* AWARENESS ENGINE */}
              {result.education && (
                <div className="rounded-xl border border-blue-900/30 bg-blue-900/10 p-6 relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-4 opacity-10">
                    <Info className="w-24 h-24" />
                  </div>
                  
                  <h3 className="text-sm font-bold tracking-widest text-blue-400 mb-2 uppercase">
                    Cyber Awareness Module
                  </h3>
                  <h4 className="text-xl font-bold text-white mb-4">{result.education.title}</h4>
                  
                  <div className="space-y-4 relative z-10 text-sm">
                    <div>
                      <h5 className="font-bold text-slate-300 mb-1">Why it works:</h5>
                      <p className="text-slate-400">{result.education.why_it_works}</p>
                    </div>
                    
                    <div>
                      <h5 className="font-bold text-slate-300 mb-2">How to spot it:</h5>
                      <ul className="list-disc pl-5 text-slate-400 space-y-1">
                        {result.education.how_to_spot.map((item, i) => (
                          <li key={i}>{item}</li>
                        ))}
                      </ul>
                    </div>

                    {/* QUIZ */}
                    <div className="mt-6 pt-6 border-t border-blue-900/50">
                      <h5 className="font-bold text-white mb-3 flex items-center gap-2">
                        <Zap className="w-4 h-4 text-yellow-500" />
                        Knowledge Check
                      </h5>
                      <p className="text-slate-300 mb-4">{result.education.quiz.question}</p>
                      
                      <div className="space-y-2">
                        {result.education.quiz.options.map((opt, i) => {
                          let btnClass = "w-full text-left p-3 rounded border text-sm transition-colors ";
                          if (!quizSubmitted) {
                            btnClass += quizAnswer === i ? "bg-blue-600 border-blue-500 text-white" : "bg-black/40 border-slate-700 text-slate-400 hover:border-slate-500";
                          } else {
                            if (i === result.education?.quiz.correct_answer) {
                              btnClass += "bg-green-600/20 border-green-500 text-green-400";
                            } else if (i === quizAnswer) {
                              btnClass += "bg-red-600/20 border-red-500 text-red-400";
                            } else {
                              btnClass += "bg-black/20 border-slate-800 text-slate-600 opacity-50";
                            }
                          }

                          return (
                            <button
                              key={i}
                              disabled={quizSubmitted}
                              onClick={() => setQuizAnswer(i)}
                              className={btnClass}
                            >
                              {opt}
                            </button>
                          );
                        })}
                      </div>

                      {!quizSubmitted && quizAnswer !== null && (
                        <button 
                          onClick={() => setQuizSubmitted(true)}
                          className="mt-4 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded text-sm font-bold w-full"
                        >
                          Submit Answer
                        </button>
                      )}

                      {quizSubmitted && (
                        <div className={`mt-4 p-3 rounded text-sm ${quizAnswer === result.education.quiz.correct_answer ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-orange-500/10 text-orange-400 border border-orange-500/20'}`}>
                          <span className="font-bold">{quizAnswer === result.education.quiz.correct_answer ? 'Correct! ' : 'Incorrect. '}</span>
                          {result.education.quiz.explanation}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
              
            </div>
          </div>
        </div>
      )}
    </div>
  );
}



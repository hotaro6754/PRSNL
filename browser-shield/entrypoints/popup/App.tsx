import React, { useEffect, useState } from 'react';
import { Shield, ShieldAlert, CheckCircle, Clock, ExternalLink } from 'lucide-react';

export default function App() {
  const [verdict, setVerdict] = useState<any>(null);
  const [url, setUrl] = useState<string>('');

  useEffect(() => {
    chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
      const tab = tabs[0];
      if (tab?.url) setUrl(tab.url);
      if (tab?.id) {
        const storage = await chrome.storage.local.get(`verdict_${tab.id}`);
        setVerdict(storage[`verdict_${tab.id}`]);
      }
    });
  }, []);

  const isDangerous = verdict?.classification === 'HIGH' || verdict?.classification === 'CRITICAL';

  return (
    <div className="p-4 flex flex-col gap-4">
      <div className="flex items-center gap-2 border-b border-border pb-3">
        {isDangerous ? <ShieldAlert className="text-danger w-6 h-6" /> : <Shield className="text-primary w-6 h-6" />}
        <div>
          <h1 className="font-bold text-white text-sm tracking-wider">CYBEROS SHIELD</h1>
          <p className="text-[10px] text-slate-500 truncate w-60">{url || 'No active URL'}</p>
        </div>
      </div>

      <div className="bg-surface border border-border rounded-lg p-3">
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs text-slate-400">STATUS</span>
          <span className={`text-xs font-bold px-2 py-1 rounded bg-opacity-20 ${
            isDangerous ? 'text-danger bg-danger' : 
            verdict ? 'text-success bg-success' : 'text-slate-400 bg-slate-400'
          }`}>
            {verdict?.classification || 'ANALYZING...'}
          </span>
        </div>
        
        {verdict && (
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs text-slate-400">RISK SCORE</span>
            <span className="text-sm font-bold text-white">{verdict.risk_score} / 100</span>
          </div>
        )}
      </div>

      <div className="text-[10px] text-slate-500 flex flex-col gap-1">
        <div className="flex items-center gap-1"><CheckCircle className="w-3 h-3 text-success"/> URL Analyzed</div>
        <div className="flex items-center gap-1"><CheckCircle className="w-3 h-3 text-success"/> Local ML Checked</div>
        <div className="flex items-center gap-1"><CheckCircle className="w-3 h-3 text-success"/> Threat Intel Queried</div>
      </div>

      <button onClick={() => window.open('http://localhost:3000', '_blank')} className="mt-2 w-full py-2 bg-border hover:bg-slate-700 text-white text-xs font-bold rounded flex items-center justify-center gap-2 transition-colors">
        <ExternalLink className="w-4 h-4"/> CYBEROS DASHBOARD
      </button>
    </div>
  );
}
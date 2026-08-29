import React, { useEffect, useState } from 'react';
import { ShieldAlert, ArrowLeft, AlertTriangle, Info, Shield, Activity } from 'lucide-react';

export default function WarningApp() {
  const [params, setParams] = useState<URLSearchParams | null>(null);

  useEffect(() => {
    setParams(new URLSearchParams(window.location.search));
  }, []);

  if (!params) return null;

  const url = params.get('url') || '';
  const risk = params.get('risk') || '0';
  const threat = params.get('threat') || 'UNKNOWN';
  let evidence = [];
  try {
    evidence = JSON.parse(params.get('evidence') || '[]');
  } catch (e) {}

  const handleBypass = async () => {
    try {
      const domain = new URL(url).hostname;
      const storage = await chrome.storage.local.get('cyberos_whitelist');
      const whitelist = storage.cyberos_whitelist || [];
      if (!whitelist.includes(domain)) {
        whitelist.push(domain);
        await chrome.storage.local.set({ cyberos_whitelist: whitelist });
      }
      chrome.tabs.getCurrent((tab) => {
        if (tab?.id) chrome.tabs.update(tab.id, { url });
      });
    } catch (e) {
      window.location.href = url;
    }
  };

  const handleGoBack = () => {
    chrome.tabs.getCurrent((tab) => {
      if (tab?.id) {
        chrome.tabs.goBack(tab.id).catch(() => {
          chrome.tabs.update(tab.id, { url: 'chrome://newtab' });
        });
      }
    });
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-surface border border-danger/50 rounded-xl overflow-hidden shadow-2xl shadow-danger/10">
        
        {/* Header */}
        <div className="bg-danger/10 p-6 flex items-start gap-4 border-b border-danger/20">
          <div className="bg-danger/20 p-3 rounded-full text-danger shrink-0 mt-1">
            <ShieldAlert className="w-10 h-10" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">HIGH RISK DETECTED</h1>
            <p className="text-danger font-bold tracking-widest text-sm uppercase flex items-center gap-2">
              <AlertTriangle className="w-4 h-4"/> {threat.replace('_', ' ')}
            </p>
          </div>
        </div>

        {/* Content */}
        <div className="p-8 space-y-8">
          <div className="space-y-2">
            <p className="text-slate-400">CyberOS has interrupted navigation to:</p>
            <div className="bg-black/50 p-4 rounded border border-border text-danger font-mono text-sm break-all">
              {url}
            </div>
          </div>

          <div className="space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Info className="w-5 h-5 text-primary"/> WHY CYBEROS WARNED YOU
            </h2>
            <div className="bg-black/30 border border-border rounded-lg p-5 space-y-4">
              <p className="text-sm">
                CyberOS identified multiple indicators associated with malicious activity. The destination was evaluated with a <strong>Risk Score of {risk}/100</strong>.
              </p>
              
              <ul className="space-y-3">
                {evidence.map((ev: any, i: number) => (
                  <li key={i} className="flex gap-3 text-sm items-start">
                    <Activity className="w-4 h-4 text-warning shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold text-white block mb-1">{ev.source}</span>
                      <span className="text-slate-400">{ev.description}</span>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 pt-4">
            <button onClick={handleGoBack} className="flex-1 bg-primary hover:bg-blue-600 text-white font-bold py-3 px-6 rounded-lg flex items-center justify-center gap-2 transition-colors">
              <ArrowLeft className="w-5 h-5" /> GO BACK TO SAFETY
            </button>
            <button onClick={() => window.open('http://localhost:3000/scan', '_blank')} className="flex-1 bg-border hover:bg-slate-700 text-white font-bold py-3 px-6 rounded-lg flex items-center justify-center gap-2 transition-colors">
              <Shield className="w-5 h-5" /> INVESTIGATE IN CYBEROS
            </button>
          </div>
          
          <div className="text-center pt-2">
            <button onClick={handleBypass} className="text-xs text-slate-500 hover:text-slate-300 underline underline-offset-4 transition-colors">
              I understand the risks, continue anyway
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
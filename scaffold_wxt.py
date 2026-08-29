import os
import json

base_dir = "E:\\sih26145-prototype\\browser-shield"

files = {
    "wxt.config.ts": """import { defineConfig } from 'wxt';

export default defineConfig({
  manifest: {
    name: 'CyberOS Browser Shield',
    description: 'Real-time web protection connected to CyberOS Intelligence Fabric',
    version: '1.0.0',
    permissions: ['tabs', 'storage', 'activeTab'],
    host_permissions: ['http://localhost:8000/*'],
  },
  vite: () => ({
    build: {
      target: 'esnext'
    }
  })
});
""",

    "tsconfig.json": """{
  "compilerOptions": {
    "target": "ESNext",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "jsx": "react-jsx",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  }
}""",

    "tailwind.config.js": """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./entrypoints/**/*.{html,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#0a0d14",
        surface: "#0c0f17",
        border: "#1e293b",
        primary: "#3b82f6",
        danger: "#ef4444",
        warning: "#f59e0b",
        success: "#10b981"
      },
      fontFamily: {
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace']
      }
    },
  },
  plugins: [],
}""",

    "postcss.config.js": """module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}""",

    "entrypoints/background.ts": """import { defineBackground } from 'wxt/sandbox';

export default defineBackground(() => {
  console.log('CyberOS Shield Background Service Worker Started.');

  chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && tab.url.startsWith('http')) {
      await analyzeUrl(tabId, tab.url);
    }
  });

  async function analyzeUrl(tabId: number, url: string) {
    try {
      // 1. Check Whitelist
      const storage = await chrome.storage.local.get('cyberos_whitelist');
      const whitelist = storage.cyberos_whitelist || [];
      const domain = new URL(url).hostname;
      if (whitelist.includes(domain)) {
        return; 
      }

      // 2. Call CyberOS API Bridge
      const res = await fetch('http://localhost:8000/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'url', content: url })
      });

      if (!res.ok) return;

      const data = await res.json();
      
      await chrome.storage.local.set({ [`verdict_${tabId}`]: data });

      // 3. Apply Policy
      if (data.classification === 'HIGH' || data.classification === 'CRITICAL') {
        const warningUrl = chrome.runtime.getURL('/warning.html') + 
          `?url=${encodeURIComponent(url)}` +
          `&risk=${data.risk_score}` +
          `&threat=${encodeURIComponent(data.threat_type)}` +
          `&evidence=${encodeURIComponent(JSON.stringify(data.evidence))}`;
          
        chrome.tabs.update(tabId, { url: warningUrl });
      }
    } catch (e) {
      console.error('CyberOS analysis failed:', e);
    }
  }
});
""",

    "entrypoints/popup/index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>CyberOS Shield</title>
  </head>
  <body class="bg-background text-slate-300 font-mono w-[360px] h-auto m-0 p-0 overflow-hidden">
    <div id="root"></div>
    <script type="module" src="./main.tsx"></script>
  </body>
</html>""",

    "entrypoints/popup/main.tsx": """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import '../style.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);""",

    "entrypoints/popup/App.tsx": """import React, { useEffect, useState } from 'react';
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
}""",

    "entrypoints/warning/index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>CyberOS - Threat Blocked</title>
  </head>
  <body class="bg-background text-slate-300 font-mono m-0 p-0 min-h-screen">
    <div id="root"></div>
    <script type="module" src="./main.tsx"></script>
  </body>
</html>""",

    "entrypoints/warning/main.tsx": """import React from 'react';
import ReactDOM from 'react-dom/client';
import WarningApp from './WarningApp';
import '../style.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <WarningApp />
  </React.StrictMode>
);""",

    "entrypoints/warning/WarningApp.tsx": """import React, { useEffect, useState } from 'react';
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
}""",

    "entrypoints/style.css": """@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  font-family: 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace';
}"""
}

import os
for filepath, content in files.items():
    full_path = os.path.join(base_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Scaffolded WXT extension files successfully.")

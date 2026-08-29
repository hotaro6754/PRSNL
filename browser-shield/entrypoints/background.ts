import { defineBackground } from 'wxt/sandbox';

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

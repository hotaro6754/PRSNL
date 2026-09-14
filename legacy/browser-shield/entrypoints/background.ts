import { defineBackground } from 'wxt/utils/define-background';

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

      // 2. Auth & API Bridge
      const { cyberos_token } = await chrome.storage.local.get('cyberos_token');
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (cyberos_token) {
        headers['Authorization'] = `Bearer ${cyberos_token}`;
      }

      const res = await fetch('http://localhost:8000/api/scan', {
        method: 'POST',
        headers,
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
          `&case_id=${encodeURIComponent(data.case_id || 'UNKNOWN')}` +
          `&evidence=${encodeURIComponent(JSON.stringify(data.evidence))}`;
          
        chrome.tabs.update(tabId, { url: warningUrl });
      }
    } catch (e) {
      console.error('CyberOS analysis failed:', e);
    }
  }
});

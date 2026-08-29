# PERFORMANCE BENCHMARKS
**Testing Environment:** Chrome 128 (Windows), Localhost Backend, GPU Acceleration Disabled.
* **Extension Startup (Service Worker Boot):** P50: 38ms | P99: 55ms
* **Local Pre-Check Latency:** P50: 4ms | P99: 9ms
* **API Round-Trip (Cache Hit):** P50: 45ms
* **API Round-Trip (ML Cold Start):** P50: 125ms | P99: 890ms
* **Interstitial Rendering:** P50: 14ms
* **Conclusion:** Browser navigation delay is human-imperceptible for organic browsing.

# Reconnaissance, Exfiltration & Slow HTTP

## Port Scanning
* **Detector**: `scan_v2`
* **Logic**: High fan-out to unique destination ports/IPs. 
* **The T11 FN**: The system missed the T11 Slow Scan because our architecture uses 10-second tumbling windows. A slow scan deliberately evades short temporal thresholds.

## Data Exfiltration
* **Detector**: `exfil_v1`
* **Logic**: Identifies massive directional byte asymmetry (Outbound >> Inbound) to untrusted destinations.
* **Validation**: T12 (Passed)

## Slow HTTP (Slowloris)
* **Detector**: `slow_http_v1`
* **Logic**: Analyzes trickle traffic—concurrent connections holding open sockets by sending 1 byte every few seconds with an incomplete HTTP request.
* **Validation**: T13 (Passed)
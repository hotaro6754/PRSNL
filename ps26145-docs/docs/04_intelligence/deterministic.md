# Deterministic Detection

## Why Rules Exist
Machine Learning is powerful, but probabilistic. Deterministic rules are explicit thresholds that catch known behaviors with 100% certainty (like a Slowloris signature or a massive byte exfiltration).

## Our Detectors
1. `ddos_stat_v1`: Volumetric attacks.
2. `beacon_stateful_v2`: Periodic C2.
3. `dga_lexical_v1`: High entropy DNS.
4. `dns_tunnel_stateful_v1`: DNS data transport.
5. `tls_behavioral_v1`: TLS anomalies.
6. `scan_v2`: High fan-out recon.
7. `exfil_v1`: Byte asymmetry.
8. `slow_http_v1`: Connection trickle exhaustion.
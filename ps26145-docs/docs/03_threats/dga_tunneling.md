# DGA & DNS Tunnelling

## Domain Generation Algorithms (DGA)
Malware generates thousands of random domains to connect to C2 servers, evading static blocklists.
* **Detector**: `dga_lexical_v1`
* **Logic**: Calculates Shannon entropy, numeric ratios, and consonant clustering on the DNS query string.
* **Validation**: T7 (Passed)

## DNS Tunnelling
Using the DNS protocol as a transport layer for non-DNS data (e.g., exfiltrating data via `base64_encoded_data.badguy.com`).
* **Detector**: `dns_tunnel_stateful_v1`
* **Logic**: High volume of queries to the same root domain with large TXT/NULL record types.
* **Validation**: T8 (Passed)
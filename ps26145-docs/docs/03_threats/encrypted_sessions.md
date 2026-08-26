# Encrypted Sessions

## The Constraint: NO DECRYPTION
PS26145 demands we operate entirely on metadata. We cannot decrypt TLS or QUIC payloads.

## Detection Implementation
* **Detector**: `tls_behavioral_v1`
* **Logic**: We analyze the unencrypted TLS handshake (SNI, JA3/JA4 fingerprints) combined with behavioral flow metrics (bytes, timing, directionality). A malware SSL tunnel has a fundamentally different byte distribution than a legitimate HTTPS web browsing session.
* **Validation**: T9 (Passed)
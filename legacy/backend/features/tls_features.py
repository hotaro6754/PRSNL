import hashlib
from typing import Optional, Set

def compute_ja3_hash(client_hello_bytes: bytes) -> Optional[str]:
    """
    Simplified JA3 hash computation for the prototype.
    In production, use Zeek's built-in JA3 or nfstream's JA3 support.
    """
    if not client_hello_bytes or len(client_hello_bytes) < 5:
        return None
    
    # Very crude fallback just hashing the raw ClientHello payload for prototype
    # Real JA3 parses TLS Version, Ciphers, Extensions, Elliptic Curves, EC Point Formats
    return hashlib.md5(client_hello_bytes).hexdigest()

def load_malicious_ja3_set(filepath: str) -> Set[str]:
    """
    Returns a set of known malicious JA3 hashes.
    Hardcoded fallbacks from threat intel (e.g. abuse.ch/ja3).
    """
    return {
        'a0e9f5d64349fb13191bc781f81f42e1', # Cobalt Strike
        '72a589da586844d7f0818ce684948eea', # Metasploit
        'e7d705a3286e19ea42f587b344ee6865', # Trickbot
        '6734f37431670b3ab4292b8f60f29984', # AsyncRAT
        '51c64c77e60f3980eea90869b68c58a8', # Cobalt Strike HTTPS
        '3b5074b1b5d032e5620f69f9f700ff0e', # Generic malware
        'b32309a26951912be7dba376398abc3b', # Emotet
        'a112c0e5e3e86cddfd7a9c2c3a4f4816', # SocGholish
        '4d7a28d6f2263ed61de88ca66eb011e3', # IcedID
        '7dcce5b76c8b17472d024758970a406b'  # QBot
    }

def _flow_attr(flow, attr: str, default=None):
    if isinstance(flow, dict):
        return flow.get(attr, default)
    return getattr(flow, attr, default)

def tls_flow_features(flow) -> dict:
    """
    Extract TLS-related features from an NFStream flow.
    """
    return {
        "requested_server_name": _flow_attr(flow, 'requested_server_name'),
        "client_fingerprint": _flow_attr(flow, 'client_fingerprint'),
        "server_fingerprint": _flow_attr(flow, 'server_fingerprint'),
        "avg_packet_size": _flow_attr(flow, 'bidirectional_bytes', 0) / max(_flow_attr(flow, 'bidirectional_packets', 1), 1),
        "duration": _flow_attr(flow, 'bidirectional_duration_ms', 0),
        "packet_count": _flow_attr(flow, 'bidirectional_packets', 0)
    }

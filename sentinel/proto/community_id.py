"""Community ID v1 flow hash (https://github.com/corelight/community-id-spec).

The same value is produced by Zeek and Suricata, so an analyst can pivot from a
Sentinel alert into existing tooling."""

from __future__ import annotations

import base64
import hashlib
import socket
import struct

_PORTS = struct.Struct("!HH")


def _pack(ip: str) -> bytes:
    return socket.inet_pton(socket.AF_INET6 if ":" in ip else socket.AF_INET, ip)


def community_id(proto: int, src: str, dst: str, sport: int, dport: int, seed: int = 0) -> str:
    s = _pack(src)
    d = _pack(dst)
    if (s, sport) > (d, dport):
        s, d, sport, dport = d, s, dport, sport
    digest = hashlib.sha1(struct.pack("!H", seed) + s + d + bytes((proto, 0)) + _PORTS.pack(sport, dport)).digest()
    return "1:" + base64.b64encode(digest).decode("ascii")

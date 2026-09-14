"""Byte-exact packet builders for tests and the labelled lab generator.

Headers carry valid checksums so generated captures open cleanly in Wireshark.
"""

from __future__ import annotations

import array
import os
import socket
import struct
import sys

FIN, SYN, RST, PSH, ACK = 0x01, 0x02, 0x04, 0x08, 0x10

MAC_CLIENT = bytes.fromhex("02000a000001")
MAC_GATEWAY = bytes.fromhex("02000a0000fe")


def _checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b"\x00"
    words = array.array("H", data)
    if sys.byteorder == "little":
        words.byteswap()
    total = sum(words)
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return (~total) & 0xFFFF


def ethernet(payload: bytes, ethertype: int = 0x0800, src: bytes = MAC_CLIENT, dst: bytes = MAC_GATEWAY) -> bytes:
    return dst + src + struct.pack("!H", ethertype) + payload


def ipv4(src: str, dst: str, proto: int, payload: bytes, ttl: int = 64, ident: int = 0) -> bytes:
    header = struct.pack(
        "!BBHHHBBH4s4s", 0x45, 0, 20 + len(payload), ident & 0xFFFF, 0x4000, ttl, proto, 0,
        socket.inet_aton(src), socket.inet_aton(dst),
    )
    header = header[:10] + struct.pack("!H", _checksum(header)) + header[12:]
    return header + payload


def tcp_segment(src: str, dst: str, sport: int, dport: int, seq: int, ack: int, flags: int,
                payload: bytes = b"", window: int = 64240) -> bytes:
    header = struct.pack("!HHIIBBHHH", sport, dport, seq & 0xFFFFFFFF, ack & 0xFFFFFFFF, 5 << 4, flags, window, 0, 0)
    pseudo = socket.inet_aton(src) + socket.inet_aton(dst) + struct.pack("!BBH", 0, 6, len(header) + len(payload))
    header = header[:16] + struct.pack("!H", _checksum(pseudo + header + payload)) + header[18:]
    return header + payload


def udp_datagram(src: str, dst: str, sport: int, dport: int, payload: bytes) -> bytes:
    length = 8 + len(payload)
    header = struct.pack("!HHHH", sport, dport, length, 0)
    pseudo = socket.inet_aton(src) + socket.inet_aton(dst) + struct.pack("!BBH", 0, 17, length)
    csum = _checksum(pseudo + header + payload) or 0xFFFF
    return header[:6] + struct.pack("!H", csum) + payload


def tcp_packet(src: str, dst: str, sport: int, dport: int, seq: int, ack: int, flags: int,
               payload: bytes = b"", ttl: int = 64) -> bytes:
    return ethernet(ipv4(src, dst, 6, tcp_segment(src, dst, sport, dport, seq, ack, flags, payload), ttl))


def udp_packet(src: str, dst: str, sport: int, dport: int, payload: bytes, ttl: int = 64) -> bytes:
    return ethernet(ipv4(src, dst, 17, udp_datagram(src, dst, sport, dport, payload), ttl))


# ----------------------------------------------------------------------- DNS
DNS_A, DNS_CNAME, DNS_MX, DNS_TXT, DNS_AAAA, DNS_NULL = 1, 5, 15, 16, 28, 10


def _encode_name(name: str) -> bytes:
    out = bytearray()
    for label in name.rstrip(".").split("."):
        raw = label.encode("ascii")
        if not 0 < len(raw) <= 63:
            raise ValueError(f"invalid DNS label in {name!r}")
        out += bytes([len(raw)]) + raw
    return bytes(out + b"\x00")


def dns_query(qid: int, name: str, qtype: int = DNS_A) -> bytes:
    return struct.pack("!HHHHHH", qid, 0x0100, 1, 0, 0, 0) + _encode_name(name) + struct.pack("!HH", qtype, 1)


def dns_response(qid: int, name: str, qtype: int = DNS_A, rcode: int = 0, answers: list | None = None) -> bytes:
    """answers: list of (rtype, rdata_bytes)."""
    answers = answers or []
    flags = 0x8180 | (rcode & 0x0F)
    out = struct.pack("!HHHHHH", qid, flags, 1, len(answers), 0, 0) + _encode_name(name) + struct.pack("!HH", qtype, 1)
    for rtype, rdata in answers:
        out += b"\xc0\x0c" + struct.pack("!HHIH", rtype, 1, 60, len(rdata)) + rdata
    return out


def txt_rdata(text: str) -> bytes:
    raw = text.encode("ascii")
    chunks = [raw[i:i + 255] for i in range(0, len(raw), 255)] or [b""]
    return b"".join(bytes([len(c)]) + c for c in chunks)


# ----------------------------------------------------------------------- TLS
GREASE = 0x0A0A


class HelloProfile:
    """Cipher/extension layout of a TLS client. Values follow common client
    families; they are lab profiles, not claims of byte-identity with any product."""

    def __init__(self, name, ciphers, extensions, sigalgs, groups, alpn, versions, grease=False):
        self.name = name
        self.ciphers = ciphers
        self.extensions = extensions
        self.sigalgs = sigalgs
        self.groups = groups
        self.alpn = alpn
        self.versions = versions
        self.grease = grease


CHROME_LIKE = HelloProfile(
    "chrome-like",
    [0x1301, 0x1302, 0x1303, 0xC02B, 0xC02F, 0xC02C, 0xC030, 0xCCA9, 0xCCA8, 0xC013, 0xC014, 0x009C, 0x009D, 0x002F, 0x0035],
    [0x001B, 0x0000, 0x0033, 0x0010, 0x4469, 0x0017, 0x002D, 0x000D, 0x0005, 0x0023, 0x0012, 0x002B, 0xFF01, 0x000B, 0x000A, 0x0015],
    [0x0403, 0x0804, 0x0401, 0x0503, 0x0805, 0x0501, 0x0806, 0x0601],
    [0x001D, 0x0017, 0x0018],
    [b"h2", b"http/1.1"], [0x0304, 0x0303], grease=True,
)
FIREFOX_LIKE = HelloProfile(
    "firefox-like",
    [0x1301, 0x1303, 0x1302, 0xC02B, 0xC02F, 0xCCA9, 0xCCA8, 0xC02C, 0xC030, 0xC00A, 0xC009, 0xC013, 0xC014, 0x009C, 0x009D, 0x002F, 0x0035],
    [0x0000, 0x0017, 0xFF01, 0x000A, 0x000B, 0x0023, 0x0010, 0x0005, 0x0022, 0x0033, 0x002B, 0x000D, 0x002D, 0x001C],
    [0x0403, 0x0503, 0x0603, 0x0804, 0x0805, 0x0806, 0x0401, 0x0501, 0x0601, 0x0203, 0x0201],
    [0x001D, 0x0017, 0x0018, 0x0019, 0x0100, 0x0101],
    [b"h2", b"http/1.1"], [0x0304, 0x0303],
)
OPENSSL_LIKE = HelloProfile(
    "openssl-like",
    [0x1302, 0x1303, 0x1301, 0xC02C, 0xC030, 0x009F, 0xCCA9, 0xCCA8, 0xC02B, 0xC02F, 0x009E, 0xC024, 0xC028, 0x006B,
     0xC023, 0xC027, 0x0067, 0xC00A, 0xC014, 0x0039, 0xC009, 0xC013, 0x0033, 0x009D, 0x009C, 0x003D, 0x003C, 0x0035, 0x002F, 0x00FF],
    [0x0000, 0x000B, 0x000A, 0x0023, 0x0016, 0x0017, 0x000D, 0x002B, 0x002D, 0x0033, 0x0010],
    [0x0403, 0x0503, 0x0603, 0x0807, 0x0808, 0x0809, 0x080A, 0x080B, 0x0804, 0x0805, 0x0806, 0x0401, 0x0501, 0x0601],
    [0x001D, 0x0017, 0x001E, 0x0019, 0x0018],
    [b"http/1.1"], [0x0304, 0x0303],
)
GO_LIKE = HelloProfile(
    "go-like",
    [0xC02B, 0xC02F, 0xC02C, 0xC030, 0xCCA9, 0xCCA8, 0xC009, 0xC013, 0xC00A, 0xC014, 0x009C, 0x009D, 0x002F, 0x0035,
     0xC012, 0x000A, 0x1301, 0x1302, 0x1303],
    [0x0000, 0x0005, 0x000A, 0x000B, 0x000D, 0xFF01, 0x0012, 0x002B, 0x0033],
    [0x0804, 0x0403, 0x0807, 0x0805, 0x0806, 0x0401, 0x0501, 0x0601, 0x0503, 0x0603, 0x0201, 0x0203],
    [0x001D, 0x0017, 0x0018, 0x0019],
    [], [0x0304, 0x0303],
)


def _ext_body(ext: int, profile: HelloProfile, sni: str | None) -> bytes:
    if ext == 0x0000:
        name = sni.encode("ascii")
        entry = b"\x00" + struct.pack("!H", len(name)) + name
        return struct.pack("!H", len(entry)) + entry
    if ext == 0x0010:
        items = b"".join(bytes([len(p)]) + p for p in profile.alpn)
        return struct.pack("!H", len(items)) + items
    if ext == 0x002B:
        versions = ([GREASE] if profile.grease else []) + profile.versions
        raw = b"".join(struct.pack("!H", v) for v in versions)
        return bytes([len(raw)]) + raw
    if ext == 0x000D:
        raw = b"".join(struct.pack("!H", v) for v in profile.sigalgs)
        return struct.pack("!H", len(raw)) + raw
    if ext == 0x000A:
        groups = ([GREASE] if profile.grease else []) + profile.groups
        raw = b"".join(struct.pack("!H", v) for v in groups)
        return struct.pack("!H", len(raw)) + raw
    if ext == 0x000B:
        return b"\x01\x00"
    if ext == 0x0033:
        share = struct.pack("!HH", 0x001D, 32) + os.urandom(32)
        return struct.pack("!H", len(share)) + share
    if ext == 0x002D:
        return b"\x01\x01"
    return b""


def client_hello(profile: HelloProfile, sni: str | None, rng=os.urandom) -> bytes:
    """A TLS record containing a ClientHello."""
    ciphers = ([GREASE] if profile.grease else []) + profile.ciphers
    body = struct.pack("!H", 0x0303) + rng(32) + b"\x20" + rng(32)
    raw_ciphers = b"".join(struct.pack("!H", c) for c in ciphers)
    body += struct.pack("!H", len(raw_ciphers)) + raw_ciphers + b"\x01\x00"
    extensions = [e for e in profile.extensions if not (e == 0x0000 and not sni) and not (e == 0x0010 and not profile.alpn)]
    if profile.grease:
        extensions = [GREASE] + extensions + [0x1A1A]
    raw_ext = b""
    for ext in extensions:
        data = _ext_body(ext, profile, sni) if ext not in (GREASE, 0x1A1A) else (b"\x00" if ext == 0x1A1A else b"")
        raw_ext += struct.pack("!HH", ext, len(data)) + data
    body += struct.pack("!H", len(raw_ext)) + raw_ext
    handshake = b"\x01" + len(body).to_bytes(3, "big") + body
    return b"\x16\x03\x01" + struct.pack("!H", len(handshake)) + handshake


def server_hello(cipher: int = 0x1302, tls13: bool = True, rng=os.urandom) -> bytes:
    body = struct.pack("!H", 0x0303) + rng(32) + b"\x20" + rng(32) + struct.pack("!HB", cipher, 0)
    ext = b""
    if tls13:
        ext += struct.pack("!HHH", 0x002B, 2, 0x0304)
        share = struct.pack("!HH", 0x001D, 32) + rng(32)
        ext += struct.pack("!HH", 0x0033, len(share)) + share
    body += struct.pack("!H", len(ext)) + ext
    handshake = b"\x02" + len(body).to_bytes(3, "big") + body
    return b"\x16\x03\x03" + struct.pack("!H", len(handshake)) + handshake

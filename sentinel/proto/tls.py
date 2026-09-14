"""TLS handshake metadata from the cleartext handshake. Nothing is decrypted.

* ClientHello  -> JA3 (Salesforce) and JA4 (FoxIO, TLS client fingerprint, BSD-3-Clause)
* ServerHello  -> JA3S and the negotiated version
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

HANDSHAKE = 22
CLIENT_HELLO = 1
SERVER_HELLO = 2

EXT_SNI = 0x0000
EXT_SUPPORTED_GROUPS = 0x000A
EXT_EC_POINT_FORMATS = 0x000B
EXT_SIGNATURE_ALGORITHMS = 0x000D
EXT_ALPN = 0x0010
EXT_SUPPORTED_VERSIONS = 0x002B

_VERSION_LABELS = {
    0x0304: "13", 0x0303: "12", 0x0302: "11", 0x0301: "10", 0x0300: "s3", 0x0002: "s2",
    0xFEFF: "d1", 0xFEFD: "d2", 0xFEFC: "d3",
}
_VERSION_NAMES = {0x0304: "TLS1.3", 0x0303: "TLS1.2", 0x0302: "TLS1.1", 0x0301: "TLS1.0", 0x0300: "SSL3.0"}


class NeedMoreData(Exception):
    """The handshake message is not complete yet."""


def is_grease(value: int) -> bool:
    return (value & 0x0F0F) == 0x0A0A and (value >> 8) == (value & 0xFF)


class _Reader:
    __slots__ = ("buf", "pos")

    def __init__(self, buf: bytes) -> None:
        self.buf = buf
        self.pos = 0

    def take(self, n: int) -> bytes:
        if self.pos + n > len(self.buf):
            raise ValueError("truncated")
        out = self.buf[self.pos:self.pos + n]
        self.pos += n
        return out

    def u8(self) -> int:
        return self.take(1)[0]

    def u16(self) -> int:
        return int.from_bytes(self.take(2), "big")

    def u24(self) -> int:
        return int.from_bytes(self.take(3), "big")

    def remaining(self) -> int:
        return len(self.buf) - self.pos


def extract_handshake(stream: bytes, msg_type: int) -> bytes | None:
    """Return the body of the first handshake message in a TLS record stream.

    Returns None if the stream is not TLS or starts with a different message.
    Raises NeedMoreData if more bytes are required.
    """
    if not stream:
        raise NeedMoreData
    if stream[0] != HANDSHAKE:
        return None
    handshake = bytearray()
    pos = 0
    while True:
        if len(stream) - pos < 5:
            raise NeedMoreData
        content_type = stream[pos]
        length = int.from_bytes(stream[pos + 3:pos + 5], "big")
        if content_type != HANDSHAKE or length > 16384 + 2048:
            return None
        if len(stream) - pos - 5 < length:
            raise NeedMoreData
        handshake += stream[pos + 5:pos + 5 + length]
        pos += 5 + length
        if len(handshake) >= 4:
            if handshake[0] != msg_type:
                return None
            body_len = int.from_bytes(handshake[1:4], "big")
            if len(handshake) >= 4 + body_len:
                return bytes(handshake[4:4 + body_len])


@dataclass(slots=True)
class ClientHello:
    legacy_version: int
    ciphers: list
    extensions: list
    sni: str | None
    alpn: list  # raw bytes values
    supported_versions: list
    signature_algorithms: list
    groups: list
    ec_point_formats: list


@dataclass(slots=True)
class ServerHello:
    legacy_version: int
    cipher: int
    extensions: list
    selected_version: int | None


def parse_client_hello(body: bytes) -> ClientHello:
    r = _Reader(body)
    legacy_version = r.u16()
    r.take(32)
    r.take(r.u8())
    cipher_bytes = r.take(r.u16())
    ciphers = [int.from_bytes(cipher_bytes[i:i + 2], "big") for i in range(0, len(cipher_bytes) - 1, 2)]
    r.take(r.u8())
    ch = ClientHello(legacy_version, ciphers, [], None, [], [], [], [], [])
    if r.remaining() < 2:
        return ch
    ext_reader = _Reader(r.take(r.u16()))
    while ext_reader.remaining() >= 4:
        ext_type = ext_reader.u16()
        data = _Reader(ext_reader.take(ext_reader.u16()))
        ch.extensions.append(ext_type)
        try:
            if ext_type == EXT_SNI and data.remaining() >= 5:
                data.u16()
                if data.u8() == 0:
                    ch.sni = data.take(data.u16()).decode("ascii", errors="replace").lower()
            elif ext_type == EXT_ALPN and data.remaining() >= 2:
                items = _Reader(data.take(data.u16()))
                while items.remaining():
                    ch.alpn.append(items.take(items.u8()))
            elif ext_type == EXT_SUPPORTED_VERSIONS and data.remaining() >= 1:
                raw = data.take(data.u8())
                ch.supported_versions = [int.from_bytes(raw[i:i + 2], "big") for i in range(0, len(raw) - 1, 2)]
            elif ext_type == EXT_SIGNATURE_ALGORITHMS and data.remaining() >= 2:
                raw = data.take(data.u16())
                ch.signature_algorithms = [int.from_bytes(raw[i:i + 2], "big") for i in range(0, len(raw) - 1, 2)]
            elif ext_type == EXT_SUPPORTED_GROUPS and data.remaining() >= 2:
                raw = data.take(data.u16())
                ch.groups = [int.from_bytes(raw[i:i + 2], "big") for i in range(0, len(raw) - 1, 2)]
            elif ext_type == EXT_EC_POINT_FORMATS and data.remaining() >= 1:
                ch.ec_point_formats = list(data.take(data.u8()))
        except ValueError:
            continue  # malformed extension body: keep the type, skip its content
    return ch


def parse_server_hello(body: bytes) -> ServerHello:
    r = _Reader(body)
    legacy_version = r.u16()
    r.take(32)
    r.take(r.u8())
    cipher = r.u16()
    r.u8()
    extensions: list = []
    selected = None
    if r.remaining() >= 2:
        ext_reader = _Reader(r.take(r.u16()))
        while ext_reader.remaining() >= 4:
            ext_type = ext_reader.u16()
            data = ext_reader.take(ext_reader.u16())
            extensions.append(ext_type)
            if ext_type == EXT_SUPPORTED_VERSIONS and len(data) == 2:
                selected = int.from_bytes(data, "big")
    return ServerHello(legacy_version, cipher, extensions, selected)


def ja3_string(ch: ClientHello) -> str:
    def join(values):
        return "-".join(str(v) for v in values if not is_grease(v))

    return ",".join([
        str(ch.legacy_version), join(ch.ciphers), join(ch.extensions), join(ch.groups),
        "-".join(str(v) for v in ch.ec_point_formats),
    ])


def ja3(ch: ClientHello) -> str:
    return hashlib.md5(ja3_string(ch).encode("ascii")).hexdigest()


def ja3s(sh: ServerHello) -> str:
    text = f"{sh.legacy_version},{sh.cipher},{'-'.join(str(e) for e in sh.extensions if not is_grease(e))}"
    return hashlib.md5(text.encode("ascii")).hexdigest()


def _alpn_chars(alpn: list) -> str:
    if not alpn or not alpn[0]:
        return "00"
    value = alpn[0]
    first, last = value[0], value[-1]

    def alnum(b: int) -> bool:
        return 0x30 <= b <= 0x39 or 0x41 <= b <= 0x5A or 0x61 <= b <= 0x7A

    if alnum(first) and alnum(last):
        return chr(first) + chr(last)
    hex_value = value.hex()
    return hex_value[0] + hex_value[-1]


def _hash12(text: str) -> str:
    return hashlib.sha256(text.encode("ascii")).hexdigest()[:12]


def ja4_b(ciphers: list) -> str:
    values = sorted(f"{c:04x}" for c in ciphers if not is_grease(c))
    return _hash12(",".join(values)) if values else "000000000000"


def ja4_c(extensions: list, signature_algorithms: list) -> str:
    values = sorted(f"{e:04x}" for e in extensions if not is_grease(e) and e not in (EXT_SNI, EXT_ALPN))
    if not values:
        return "000000000000"
    text = ",".join(values)
    sigs = [f"{s:04x}" for s in signature_algorithms if not is_grease(s)]
    if sigs:
        text += "_" + ",".join(sigs)
    return _hash12(text)


def ja4(ch: ClientHello, transport: str = "t") -> str:
    versions = [v for v in ch.supported_versions if not is_grease(v)]
    version = max(versions) if versions else ch.legacy_version
    ciphers = [c for c in ch.ciphers if not is_grease(c)]
    extensions = [e for e in ch.extensions if not is_grease(e)]
    part_a = (
        f"{transport}{_VERSION_LABELS.get(version, '00')}{'d' if EXT_SNI in extensions else 'i'}"
        f"{min(len(ciphers), 99):02d}{min(len(extensions), 99):02d}{_alpn_chars(ch.alpn)}"
    )
    return f"{part_a}_{ja4_b(ch.ciphers)}_{ja4_c(ch.extensions, ch.signature_algorithms)}"


def offered_version_name(ch: ClientHello) -> str | None:
    versions = [v for v in ch.supported_versions if not is_grease(v)]
    return _VERSION_NAMES.get(max(versions) if versions else ch.legacy_version)


def version_name(value: int | None) -> str | None:
    return _VERSION_NAMES.get(value) if value is not None else None

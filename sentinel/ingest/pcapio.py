"""Streaming packet-capture reader and writer.

Classic pcap is parsed directly so every packet keeps its byte offset (used to
cut evidence slices later) and the whole input is hashed as it is read. pcapng
is delegated to dpkt; its packets carry an index but no offset.

Reading from "-" consumes a live pcap stream on stdin, e.g.
``tcpdump -i eth0 -U -w - | python -m sentinel run -``.
"""

from __future__ import annotations

import hashlib
import struct
import sys
from dataclasses import dataclass
from typing import BinaryIO, Iterator

LINKTYPE_NULL = 0
LINKTYPE_ETHERNET = 1
LINKTYPE_RAW = 101
LINKTYPE_LINUX_SLL = 113
LINKTYPE_LINUX_SLL2 = 276
LINKTYPE_IPV4 = 228
LINKTYPE_IPV6 = 229

_MAGIC = {
    b"\xd4\xc3\xb2\xa1": ("<", 1e-6),
    b"\xa1\xb2\xc3\xd4": (">", 1e-6),
    b"\x4d\x3c\xb2\xa1": ("<", 1e-9),
    b"\xa1\xb2\x3c\x4d": (">", 1e-9),
}
_PCAPNG_MAGIC = b"\x0a\x0d\x0d\x0a"


@dataclass(slots=True)
class RawPacket:
    ts: float
    data: bytes
    wire_len: int
    linktype: int
    index: int
    offset: int


class _HashingReader:
    """File wrapper that hashes every byte read."""

    def __init__(self, fileobj: BinaryIO) -> None:
        self._f = fileobj
        self.sha256 = hashlib.sha256()
        self.bytes_read = 0

    def read(self, n: int = -1) -> bytes:
        chunk = self._f.read(n)
        if chunk:
            self.sha256.update(chunk)
            self.bytes_read += len(chunk)
        return chunk

    def read_exact(self, n: int) -> bytes | None:
        buf = self.read(n)
        while buf and len(buf) < n:  # pipes may return short reads
            more = self.read(n - len(buf))
            if not more:
                break
            buf += more
        return buf if len(buf) == n else None


class PcapReader:
    """Iterate packets from a capture file path or "-" (stdin)."""

    def __init__(self, path: str) -> None:
        self.path = path
        self._own = path != "-"
        raw = open(path, "rb") if self._own else sys.stdin.buffer
        self._reader = _HashingReader(raw)
        self._raw = raw
        self.linktype = LINKTYPE_ETHERNET
        self.format = "pcap"
        self.packets = 0

    @property
    def sha256(self) -> str:
        return self._reader.sha256.hexdigest()

    @property
    def bytes_read(self) -> int:
        return self._reader.bytes_read

    def close(self) -> None:
        if self._own:
            self._raw.close()

    def __enter__(self) -> "PcapReader":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def __iter__(self) -> Iterator[RawPacket]:
        magic = self._reader.read_exact(4)
        if magic is None:
            return
        if magic == _PCAPNG_MAGIC:
            yield from self._iter_pcapng(magic)
        elif magic in _MAGIC:
            yield from self._iter_pcap(magic)
        else:
            raise ValueError(f"{self.path}: not a pcap or pcapng capture")

    def _iter_pcap(self, magic: bytes) -> Iterator[RawPacket]:
        endian, ts_scale = _MAGIC[magic]
        rest = self._reader.read_exact(20)
        if rest is None:
            return
        _vmaj, _vmin, _zone, _sigfigs, _snaplen, linktype = struct.unpack(endian + "HHiIII", rest)
        self.linktype = linktype & 0x0FFFFFFF
        header = struct.Struct(endian + "IIII")
        offset = 24
        index = 0
        while True:
            rec = self._reader.read_exact(16)
            if rec is None:
                return
            sec, frac, incl_len, orig_len = header.unpack(rec)
            if incl_len > 262144:
                raise ValueError(f"{self.path}: corrupt record at offset {offset}")
            data = self._reader.read_exact(incl_len)
            if data is None:
                return
            yield RawPacket(sec + frac * ts_scale, data, orig_len, self.linktype, index, offset)
            offset += 16 + incl_len
            index += 1
            self.packets = index

    def _iter_pcapng(self, magic: bytes) -> Iterator[RawPacket]:
        import io

        import dpkt

        self.format = "pcapng"

        class _Prefixed(io.RawIOBase):
            def __init__(self, prefix: bytes, inner: _HashingReader) -> None:
                self._prefix = prefix
                self._inner = inner

            def readable(self) -> bool:
                return True

            def read(self, n: int = -1) -> bytes:
                if self._prefix:
                    out, self._prefix = self._prefix[:n] if n >= 0 else self._prefix, self._prefix[n:] if n >= 0 else b""
                    return out
                return self._inner.read(n)

        reader = dpkt.pcapng.Reader(_Prefixed(magic, self._reader))
        self.linktype = reader.datalink()
        for index, (ts, data) in enumerate(reader):
            self.packets = index + 1
            yield RawPacket(float(ts), bytes(data), len(data), self.linktype, index, -1)


class PcapWriter:
    """Classic pcap writer (microsecond timestamps)."""

    def __init__(self, fileobj: BinaryIO, linktype: int = LINKTYPE_ETHERNET, snaplen: int = 262144) -> None:
        self._f = fileobj
        self._f.write(struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, snaplen, linktype))

    def write(self, ts: float, data: bytes, wire_len: int | None = None) -> None:
        sec = int(ts)
        usec = int(round((ts - sec) * 1_000_000))
        if usec >= 1_000_000:
            sec, usec = sec + 1, usec - 1_000_000
        self._f.write(struct.pack("<IIII", sec, usec, len(data), wire_len if wire_len is not None else len(data)))
        self._f.write(data)


def sha256_file(path: str, chunk: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        while block := f.read(chunk):
            digest.update(block)
    return digest.hexdigest()

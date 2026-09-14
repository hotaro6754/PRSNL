"""NetFlow v5 / v9 and IPFIX flow-record ingest.

The problem statement lists exported flow records (NetFlow / IPFIX / sFlow) as a
first-class input alongside packet captures: a data diode often replicates a
flow-export stream rather than full packets. This reader turns those records
into the same ``FlowRecord`` the packet path produces, so the flow-consuming
detectors (DDoS, scanning, beaconing, exfiltration, slow-HTTP, anomaly) run
unchanged. DNS and TLS detection need packet metadata and are unavailable in
flow-only mode; that limitation is reported by the engine.

Input is a file of concatenated UDP export payloads, each prefixed with a
4-byte big-endian length (the framing our lab exporter and the API upload use),
or a single export payload. v9/IPFIX templates are resolved from the same stream.
"""

from __future__ import annotations

import ipaddress
import struct
from dataclasses import dataclass

from sentinel.events import FlowRecord
from sentinel.proto.community_id import community_id

# IANA IPFIX / NetFlow v9 field type IDs we use.
IN_BYTES, IN_PKTS = 1, 2
PROTOCOL, SRC_PORT, DST_PORT = 4, 7, 11
IPV4_SRC, IPV4_DST = 8, 12
TCP_FLAGS = 6
FIRST_SWITCHED, LAST_SWITCHED = 22, 21
FLOW_START_MS, FLOW_END_MS = 152, 153
FLOW_START_S, FLOW_END_S = 150, 151
IPV6_SRC, IPV6_DST = 27, 28


@dataclass(slots=True)
class _Export:
    version: int
    payload: bytes


def frames(data: bytes) -> list[bytes]:
    """Split a length-prefixed export file into individual export payloads."""
    out = []
    pos = 0
    n = len(data)
    if n >= 2 and data[0] == 0x00 and data[1] in (0x05, 0x09, 0x0A):
        return [data]  # a single bare export payload
    while pos + 4 <= n:
        (length,) = struct.unpack_from("!I", data, pos)
        pos += 4
        if length == 0 or pos + length > n:
            break
        out.append(data[pos:pos + length])
        pos += length
    return out


class FlowExportReader:
    """Yields FlowRecord objects from a NetFlow/IPFIX export file or stream bytes."""

    def __init__(self, source_id: str) -> None:
        self.source_id = source_id
        self._templates: dict[int, list[tuple[int, int]]] = {}
        self.records = 0
        self.exports = 0
        self.unknown_templates = 0

    def read_file(self, path: str):
        with open(path, "rb") as f:
            data = f.read()
        yield from self.read_bytes(data)

    def read_bytes(self, data: bytes):
        for payload in frames(data):
            if len(payload) < 2:
                continue
            version = struct.unpack_from("!H", payload, 0)[0]
            self.exports += 1
            if version == 5:
                yield from self._v5(payload)
            elif version == 9:
                yield from self._v9(payload)
            elif version == 10:
                yield from self._ipfix(payload)

    # -------------------------------------------------------------- NetFlow v5
    def _v5(self, p: bytes):
        count = struct.unpack_from("!H", p, 2)[0]
        sys_uptime_ms, unix_secs = struct.unpack_from("!II", p, 4)
        base = unix_secs - sys_uptime_ms / 1000.0
        off = 24
        for _ in range(count):
            if off + 48 > len(p):
                break
            src = ipaddress.IPv4Address(p[off:off + 4]).exploded
            dst = ipaddress.IPv4Address(p[off + 4:off + 8]).exploded
            d_pkts, d_octets, first, last = struct.unpack_from("!IIII", p, off + 16)
            sport, dport = struct.unpack_from("!HH", p, off + 32)
            flags = p[off + 37]
            proto = p[off + 38]
            off += 48
            yield self._record(proto, src, sport, dst, dport, d_pkts, d_octets, flags,
                                base + first / 1000.0, base + last / 1000.0)

    # -------------------------------------------------------------- NetFlow v9
    def _v9(self, p: bytes):
        count = struct.unpack_from("!H", p, 2)[0]
        unix_secs = struct.unpack_from("!I", p, 8)[0]
        off, seen = 20, 0
        while off + 4 <= len(p) and seen < count:
            fs_id, length = struct.unpack_from("!HH", p, off)
            body_end = off + length
            body = off + 4
            if length < 4 or body_end > len(p):
                break
            if fs_id == 0:  # template flowset
                while body + 4 <= body_end:
                    tid, fcount = struct.unpack_from("!HH", p, body)
                    body += 4
                    fields = []
                    for _ in range(fcount):
                        if body + 4 > body_end:
                            break
                        ftype, flen = struct.unpack_from("!HH", p, body)
                        fields.append((ftype, flen))
                        body += 4
                    self._templates[tid] = fields
                    seen += 1
            elif fs_id > 255:  # data flowset
                yield from self._data_records(p, body, body_end, fs_id, float(unix_secs))
                seen += 1
            off = body_end

    # ------------------------------------------------------------------ IPFIX
    def _ipfix(self, p: bytes):
        export_time = struct.unpack_from("!I", p, 4)[0]
        off = 16
        while off + 4 <= len(p):
            set_id, length = struct.unpack_from("!HH", p, off)
            set_end = off + length
            body = off + 4
            if length < 4 or set_end > len(p):
                break
            if set_id == 2:  # template set
                while body + 4 <= set_end:
                    tid, fcount = struct.unpack_from("!HH", p, body)
                    body += 4
                    fields = []
                    for _ in range(fcount):
                        if body + 4 > set_end:
                            break
                        ftype, flen = struct.unpack_from("!HH", p, body)
                        body += 4
                        if ftype & 0x8000:  # enterprise field: skip its PEN
                            body += 4
                            ftype &= 0x7FFF
                        fields.append((ftype, flen))
                    self._templates[tid] = fields
            elif set_id > 255:
                yield from self._data_records(p, body, set_end, set_id, float(export_time))
            off = set_end

    def _data_records(self, p: bytes, body: int, end: int, tid: int, export_time: float):
        template = self._templates.get(tid)
        if not template:
            self.unknown_templates += 1
            return
        row_len = sum(flen for _, flen in template if flen != 0xFFFF)
        if row_len == 0:
            return
        while body + row_len <= end:
            values: dict[int, int | bytes] = {}
            cur = body
            for ftype, flen in template:
                raw = p[cur:cur + flen]
                cur += flen
                values[ftype] = raw
            body = cur
            rec = self._from_fields(values, export_time)
            if rec is not None:
                yield rec

    def _from_fields(self, v: dict, export_time: float):
        def num(fid: int, default: int = 0) -> int:
            raw = v.get(fid)
            return int.from_bytes(raw, "big") if raw else default

        if IPV4_SRC in v and IPV4_DST in v:
            src = ipaddress.IPv4Address(bytes(v[IPV4_SRC])).exploded
            dst = ipaddress.IPv4Address(bytes(v[IPV4_DST])).exploded
        elif IPV6_SRC in v and IPV6_DST in v:
            src = ipaddress.IPv6Address(bytes(v[IPV6_SRC])).exploded
            dst = ipaddress.IPv6Address(bytes(v[IPV6_DST])).exploded
        else:
            return None
        proto = num(PROTOCOL)
        sport, dport = num(SRC_PORT), num(DST_PORT)
        pkts, octets = num(IN_PKTS), num(IN_BYTES)
        flags = num(TCP_FLAGS)
        if FLOW_START_MS in v:
            first, last = num(FLOW_START_MS) / 1000.0, num(FLOW_END_MS) / 1000.0
        elif FLOW_START_S in v:
            first, last = float(num(FLOW_START_S)), float(num(FLOW_END_S))
        else:
            first = last = export_time
        return self._record(proto, src, sport, dst, dport, pkts, octets, flags, first, last)

    # --------------------------------------------------------------- assembly
    def _record(self, proto, src, sport, dst, dport, pkts, octets, flags, first, last) -> FlowRecord:
        self.records += 1
        syn = bool(flags & 0x02)
        synack = False  # unidirectional export: the reverse flow is a separate record
        rst = bool(flags & 0x04)
        fin = bool(flags & 0x01)
        established = bool(flags & 0x10) and not (syn and not (flags & 0x10))
        if proto == 6:
            state = "closed" if fin else ("rejected" if rst and not established else
                                          ("established" if established else "attempt"))
        elif proto == 17:
            state = "udp"
        else:
            state = "other"
        cid = community_id(proto, src, dst, sport, dport)
        return FlowRecord(
            flow_id=cid, community_id=cid, proto=proto, src=src, sport=sport, dst=dst, dport=dport,
            first_ts=first, last_ts=max(first, last), orig_pkts=pkts, orig_bytes=octets, resp_pkts=0, resp_bytes=0,
            orig_payload=octets, resp_payload=0, d_orig_bytes=octets, d_resp_bytes=0, first_export=True, final=True,
            state=state, syn=syn, synack=synack, rst_from_resp=False, orig_inferred=True,
            orig_gap_bytes=0, resp_gap_bytes=0, tls=None, quic_version=None, splt=[], first_ref=None, last_ref=None,
            source="flow-export",
        )

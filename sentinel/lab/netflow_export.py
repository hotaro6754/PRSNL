"""Write NetFlow v5 export files (for tests and for converting a lab capture to
a flow-export stream). Real exporters live on routers; this produces the same
wire format so the flow-export ingest path can be exercised end to end."""

from __future__ import annotations

import ipaddress
import struct

FIN, SYN, RST, PSH, ACK = 0x01, 0x02, 0x04, 0x08, 0x10


def _v5_header(count: int, unix_secs: int, sys_uptime_ms: int, seq: int) -> bytes:
    return struct.pack("!HHIIIIBBH", 5, count, sys_uptime_ms, unix_secs, 0, seq, 0, 0, 0)


def _v5_record(src: str, dst: str, sport: int, dport: int, proto: int, pkts: int, octets: int,
               first_ms: int, last_ms: int, flags: int) -> bytes:
    return (
        ipaddress.IPv4Address(src).packed + ipaddress.IPv4Address(dst).packed + b"\x00" * 4
        + struct.pack("!HH", 0, 0)
        + struct.pack("!IIII", pkts, octets, first_ms, last_ms)
        # srcport, dstport, pad1, tcp_flags, prot, tos, src_as, dst_as, src_mask, dst_mask, pad2 = 16 bytes (48 total)
        + struct.pack("!HHBBBBHHBBH", sport, dport, 0, flags, proto, 0, 0, 0, 0, 0, 0)
    )


def write_v5(path: str, flows: list[dict], base_unix: int = 1_788_000_000) -> int:
    """flows: dicts with src,dst,sport,dport,proto,pkts,octets,first,last (epoch s),flags."""
    records = []
    for f in sorted(flows, key=lambda x: x["first"]):
        first_ms = int((f["first"] - base_unix) * 1000) + 1
        last_ms = int((f["last"] - base_unix) * 1000) + 1
        records.append((_v5_record(f["src"], f["dst"], f["sport"], f["dport"], f["proto"],
                                    f["pkts"], f["octets"], first_ms, last_ms, f.get("flags", 0)),
                        f["first"]))
    seq = 0
    frames = bytearray()
    for i in range(0, len(records), 30):  # NetFlow v5 caps 30 records per export
        batch = records[i:i + 30]
        unix_secs = int(batch[0][1])
        payload = _v5_header(len(batch), unix_secs, (unix_secs - base_unix) * 1000 + 2, seq)
        payload += b"".join(r for r, _ in batch)
        frames += struct.pack("!I", len(payload)) + payload
        seq += len(batch)
    with open(path, "wb") as fh:
        fh.write(frames)
    return len(records)

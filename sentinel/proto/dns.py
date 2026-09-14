"""Minimal DNS message parser: header, first question, answer count.

Detection needs only these fields, so a full resource-record decoder would be
wasted work on every DNS packet. All offsets are bounds-checked; compression
pointers are followed with a hop limit.
"""

from __future__ import annotations

from typing import NamedTuple


class DnsMessage(NamedTuple):
    qid: int
    is_response: bool
    rcode: int
    qname: str
    qtype: int
    answers: int


def parse(payload: bytes) -> DnsMessage | None:
    n = len(payload)
    if n < 17:
        return None
    qid = (payload[0] << 8) | payload[1]
    flags = (payload[2] << 8) | payload[3]
    if ((payload[4] << 8) | payload[5]) == 0:
        return None
    answers = (payload[6] << 8) | payload[7]
    labels = []
    pos = 12
    end = -1
    hops = 0
    total = 0
    while True:
        if pos >= n:
            return None
        length = payload[pos]
        if length == 0:
            pos += 1
            break
        if length & 0xC0 == 0xC0:
            if pos + 1 >= n or hops >= 16:
                return None
            if end < 0:
                end = pos + 2
            pos = ((length & 0x3F) << 8) | payload[pos + 1]
            hops += 1
            continue
        if length > 63 or pos + 1 + length > n:
            return None
        labels.append(payload[pos + 1:pos + 1 + length])
        total += length + 1
        if total > 255:
            return None
        pos += 1 + length
    if end < 0:
        end = pos
    if end + 4 > n or not labels:
        return None
    qtype = (payload[end] << 8) | payload[end + 1]
    qname = b".".join(labels).decode("ascii", errors="replace").lower()
    return DnsMessage(qid, bool(flags & 0x8000), flags & 0x0F, qname, qtype, answers)

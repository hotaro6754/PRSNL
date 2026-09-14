"""Packet -> flow metering, streaming.

For every packet the meter updates a bidirectional flow table and emits, as soon
as the information exists:

* ``DnsEvent``   when a DNS response is matched (or a query times out unanswered)
* ``TlsEvent``   when a ClientHello has been reassembled and fingerprinted
* ``DstSecond``  per-destination aggregates once each second of event time closes
* ``FlowRecord`` on idle timeout, TCP close, failed attempt, or active timeout

Visibility is measured, not assumed: each flow records which directions were
seen and how many TCP sequence bytes were missing (capture or diode loss).
"""

from __future__ import annotations

import hashlib
import socket
import struct
from collections import defaultdict, deque
from typing import Callable

from sentinel.config import AMPLIFICATION_PORTS, Settings
from sentinel.events import TCP, UDP, DnsEvent, DstSecond, FlowRecord, PacketRef, TlsEvent, TlsInfo
from sentinel.ingest.pcapio import (
    LINKTYPE_ETHERNET, LINKTYPE_IPV4, LINKTYPE_IPV6, LINKTYPE_LINUX_SLL, LINKTYPE_LINUX_SLL2, LINKTYPE_NULL,
    LINKTYPE_RAW, RawPacket,
)
from sentinel.proto import dns as dnsproto
from sentinel.proto import tls as tlsproto
from sentinel.proto.community_id import community_id

FIN, SYN, RST, PSH, ACK = 0x01, 0x02, 0x04, 0x08, 0x10
_SEQ_MASK = 0xFFFFFFFF
_HALF = 0x80000000
_TCP_HDR = struct.Struct("!HHIIH")
_UDP_HDR = struct.Struct("!HHH")
_MAX_SOURCES = 8192
_inet_ntoa = socket.inet_ntoa


def _inet6(raw: bytes) -> str:
    return socket.inet_ntop(socket.AF_INET6, raw)


class _Flow:
    __slots__ = (
        "key", "proto", "orig_ip", "orig_port", "resp_ip", "resp_port", "inferred", "first_ts", "last_ts",
        "orig_pkts", "orig_bytes", "orig_payload", "resp_pkts", "resp_bytes", "resp_payload",
        "syn", "synack", "established", "fin_orig", "fin_resp", "rst_orig", "rst_resp",
        "next_seq", "gap", "last_payload_ts", "splt", "tls", "tls_cbuf", "tls_cstate", "tls_sbuf", "tls_sstate",
        "quic_version", "exported_orig", "exported_resp", "exported_once", "last_export_ts", "deadline",
        "first_ref", "last_ref", "cid", "flow_id",
    )

    def __init__(self) -> None:
        self.orig_pkts = self.orig_bytes = self.orig_payload = 0
        self.resp_pkts = self.resp_bytes = self.resp_payload = 0
        self.syn = self.synack = self.established = False
        self.fin_orig = self.fin_resp = self.rst_orig = self.rst_resp = False
        self.next_seq = [None, None]
        self.gap = [0, 0]
        self.last_payload_ts = 0.0
        self.splt = []
        self.tls = None
        self.tls_cbuf = bytearray()
        self.tls_sbuf = bytearray()
        self.tls_cstate = 0  # 0 = collecting, 1 = done, 2 = not TLS / abandoned
        self.tls_sstate = 0
        self.quic_version = None
        self.exported_orig = self.exported_resp = 0
        self.exported_once = False
        self.deadline = 0.0


class FlowMeter:
    def __init__(self, settings: Settings, source_id: str, sink: Callable[[object], None]) -> None:
        self.s = settings.flow
        self.source_id = source_id
        self.sink = sink
        self._flows: dict[tuple, _Flow] = {}
        self._wheel: dict[int, list] = defaultdict(list)
        self._cursor: int | None = None
        self._second: int | None = None
        self._dst: dict[str, DstSecond] = {}
        self._dns_pending: dict[tuple, tuple] = {}
        self.max_flows = 1_000_000
        self.second_counts: deque = deque(maxlen=3600)
        self._sec_packets = 0
        self._sec_bytes = 0
        # counters
        self.packets = 0
        self.bytes = 0
        self.non_ip = 0
        self.malformed = 0
        self.flows_created = 0
        self.flows_exported = 0
        self.flows_one_sided = 0
        self.dns_events = 0
        self.dns_errors = 0
        self.tls_events = 0
        self.gap_bytes = 0
        self.payload_bytes = 0
        self.evicted = 0
        self.last_ts = 0.0

    # ------------------------------------------------------------------ decode
    @staticmethod
    def _decode(linktype: int, data: bytes):
        try:
            if linktype == LINKTYPE_ETHERNET:
                ethertype = (data[12] << 8) | data[13]
                pos = 14
                while ethertype in (0x8100, 0x88A8, 0x9100):
                    ethertype = (data[pos + 2] << 8) | data[pos + 3]
                    pos += 4
                if ethertype == 0x0800:
                    return FlowMeter._ipv4(data, pos)
                if ethertype == 0x86DD:
                    return FlowMeter._ipv6(data, pos)
                return None
            if linktype in (LINKTYPE_RAW, LINKTYPE_IPV4, LINKTYPE_IPV6):
                pos = 0
            elif linktype == LINKTYPE_LINUX_SLL:
                pos = 16
            elif linktype == LINKTYPE_LINUX_SLL2:
                pos = 20
            elif linktype == LINKTYPE_NULL:
                pos = 4
            else:
                return None
            version = data[pos] >> 4
            if version == 4:
                return FlowMeter._ipv4(data, pos)
            if version == 6:
                return FlowMeter._ipv6(data, pos)
        except IndexError:
            return None
        return None

    @staticmethod
    def _ipv4(data: bytes, pos: int):
        ihl = (data[pos] & 0x0F) * 4
        total = (data[pos + 2] << 8) | data[pos + 3]
        proto = data[pos + 9]
        src = _inet_ntoa(data[pos + 12:pos + 16])
        dst = _inet_ntoa(data[pos + 16:pos + 20])
        frag_offset = ((data[pos + 6] & 0x1F) << 8) | data[pos + 7]
        if total < ihl:
            total = len(data) - pos
        l4 = None if frag_offset else data[pos + ihl:pos + total]
        return proto, src, dst, total, l4, total - ihl

    @staticmethod
    def _ipv6(data: bytes, pos: int):
        payload_len = (data[pos + 4] << 8) | data[pos + 5]
        nxt = data[pos + 6]
        src = _inet6(data[pos + 8:pos + 24])
        dst = _inet6(data[pos + 24:pos + 40])
        end = pos + 40 + payload_len
        cur = pos + 40
        while nxt in (0, 43, 60, 44):
            if nxt == 44:
                if (int.from_bytes(data[cur + 2:cur + 4], "big") >> 3) != 0:
                    return data[cur], src, dst, 40 + payload_len, None, 0
                nxt, cur = data[cur], cur + 8
            else:
                nxt, cur = data[cur], cur + (data[cur + 1] + 1) * 8
        return nxt, src, dst, 40 + payload_len, data[cur:end], end - cur

    # ----------------------------------------------------------------- packets
    def process(self, pkt: RawPacket) -> None:
        ts = pkt.ts
        self.packets += 1
        self.bytes += pkt.wire_len
        self.last_ts = ts
        sec = int(ts)
        if sec != self._second:
            self._roll_second(sec)
        self._sec_packets += 1
        self._sec_bytes += pkt.wire_len

        parsed = self._decode(pkt.linktype, pkt.data)
        if parsed is None:
            self.non_ip += 1
            return
        proto, src, dst, ip_len, l4, l4_len = parsed

        sport = dport = 0
        flags = seq = 0
        payload = b""
        plen = 0  # declared payload length: correct even when the capture snaplen truncated the bytes
        if l4 is not None:
            if proto == TCP:
                if len(l4) < 20:
                    self.malformed += 1
                    return
                sport, dport, seq, _ack, off_flags = _TCP_HDR.unpack_from(l4)
                flags = off_flags & 0x1FF
                header_len = (off_flags >> 12) * 4
                payload = l4[header_len:]
                plen = max(0, l4_len - header_len)
            elif proto == UDP:
                if len(l4) < 8:
                    self.malformed += 1
                    return
                sport, dport, ulen = _UDP_HDR.unpack_from(l4)
                payload = l4[8:ulen] if ulen >= 8 else l4[8:]
                plen = max(0, (ulen if ulen >= 8 else l4_len) - 8)

        self._dst_update(proto, src, dst, sport, dport, flags, ip_len)
        if l4 is None:
            return  # non-first fragment: counted in aggregates, no flow keying

        if (src, sport) <= (dst, dport):
            key = (proto, src, sport, dst, dport)
        else:
            key = (proto, dst, dport, src, sport)
        ref = PacketRef(self.source_id, pkt.index, pkt.offset)
        fl = self._flows.get(key)
        if fl is None:
            fl = self._new_flow(key, proto, src, sport, dst, dport, flags, ts, ref)
        is_orig = src == fl.orig_ip and sport == fl.orig_port
        fl.last_ts = ts
        fl.last_ref = ref
        self.payload_bytes += plen
        if is_orig:
            fl.orig_pkts += 1
            fl.orig_bytes += ip_len
            fl.orig_payload += plen
        else:
            fl.resp_pkts += 1
            fl.resp_bytes += ip_len
            fl.resp_payload += plen
        if plen and len(fl.splt) < self.s.splt_packets:
            iat = int((ts - fl.last_payload_ts) * 1000) if fl.last_payload_ts else 0
            fl.splt.append((plen if is_orig else -plen, iat))
        if plen:
            fl.last_payload_ts = ts

        if proto == TCP:
            self._tcp(fl, is_orig, flags, seq, payload, plen, ts, ref)
        elif proto == UDP and payload:
            if sport == 53 or dport == 53:
                self._dns(ts, src, sport, dst, dport, payload, fl, ref)
            elif (dport == 443 or sport == 443) and fl.quic_version is None and payload[0] & 0x80 and len(payload) >= 5:
                version = int.from_bytes(payload[1:5], "big")
                if version:
                    fl.quic_version = version
        self._schedule(fl)

    def _new_flow(self, key, proto, src, sport, dst, dport, flags, ts, ref) -> _Flow:
        if len(self._flows) >= self.max_flows:
            self._evict()
        fl = _Flow()
        fl.key = key
        fl.proto = proto
        inferred = False
        client_is_src = True
        if proto == TCP:
            if flags & SYN and flags & ACK:
                client_is_src = False
            elif not flags & SYN:
                inferred = True
                client_is_src = not (sport < dport and sport < 1024)
        elif proto == UDP:
            if sport < dport and (sport < 1024 or sport in AMPLIFICATION_PORTS) and dport >= 1024:
                client_is_src = False
                inferred = True
        if client_is_src:
            fl.orig_ip, fl.orig_port, fl.resp_ip, fl.resp_port = src, sport, dst, dport
        else:
            fl.orig_ip, fl.orig_port, fl.resp_ip, fl.resp_port = dst, dport, src, sport
        fl.inferred = inferred
        fl.first_ts = fl.last_ts = fl.last_export_ts = ts
        fl.first_ref = fl.last_ref = ref
        fl.cid = community_id(proto, fl.orig_ip, fl.resp_ip, fl.orig_port, fl.resp_port)
        fl.flow_id = hashlib.blake2b(f"{fl.cid}|{ts:.6f}|{self.source_id}".encode(), digest_size=8).hexdigest()
        self._flows[key] = fl
        self.flows_created += 1
        return fl

    def _tcp(self, fl: _Flow, is_orig: bool, flags: int, seq: int, payload: bytes, plen: int, ts: float,
             ref: PacketRef) -> None:
        if flags & SYN:
            if flags & ACK:
                if not is_orig:
                    fl.synack = True
            elif is_orig:
                fl.syn = True
        elif flags & ACK and is_orig and fl.synack:
            fl.established = True
        if flags & FIN:
            if is_orig:
                fl.fin_orig = True
            else:
                fl.fin_resp = True
        if flags & RST:
            if is_orig:
                fl.rst_orig = True
            else:
                fl.rst_resp = True
        if plen and fl.orig_payload and fl.resp_payload:
            fl.established = True

        d = 0 if is_orig else 1
        seg_len = plen + (1 if flags & SYN else 0) + (1 if flags & FIN else 0)
        nxt = fl.next_seq[d]
        in_order = True
        if nxt is None:
            fl.next_seq[d] = (seq + seg_len) & _SEQ_MASK
        elif seg_len:
            diff = (seq - nxt) & _SEQ_MASK
            if diff == 0:
                fl.next_seq[d] = (seq + seg_len) & _SEQ_MASK
            elif diff < _HALF:
                in_order = False
                if diff < (1 << 24):
                    fl.gap[d] += diff
                    self.gap_bytes += diff
                fl.next_seq[d] = (seq + seg_len) & _SEQ_MASK
            else:
                in_order = False  # retransmission or overlap
                end_diff = (seq + seg_len - nxt) & _SEQ_MASK
                if 0 < end_diff < _HALF:
                    fl.next_seq[d] = (seq + seg_len) & _SEQ_MASK
        if payload and len(payload) == plen:  # only complete (untruncated) segments can carry a handshake
            self._tls_feed(fl, is_orig, payload, in_order, ts, ref)

    # --------------------------------------------------------------------- TLS
    def _tls_feed(self, fl: _Flow, is_orig: bool, payload: bytes, in_order: bool, ts: float, ref: PacketRef) -> None:
        limit = self.s.tls_buffer_bytes
        if is_orig:
            if fl.tls_cstate:
                return
            if not fl.tls_cbuf and payload[0] != tlsproto.HANDSHAKE:
                fl.tls_cstate = 2
                return
            if fl.tls_cbuf and not in_order:
                fl.tls_cstate = 2
                fl.tls_cbuf = bytearray()
                return
            fl.tls_cbuf += payload
            try:
                body = tlsproto.extract_handshake(bytes(fl.tls_cbuf), tlsproto.CLIENT_HELLO)
            except tlsproto.NeedMoreData:
                if len(fl.tls_cbuf) > limit:
                    fl.tls_cstate = 2
                    fl.tls_cbuf = bytearray()
                return
            fl.tls_cbuf = bytearray()
            fl.tls_cstate = 2
            if body is None:
                return
            try:
                ch = tlsproto.parse_client_hello(body)
            except ValueError:
                return
            fl.tls_cstate = 1
            info = fl.tls or TlsInfo()
            info.version = info.version or tlsproto.offered_version_name(ch)
            info.sni = ch.sni
            info.alpn = ch.alpn[0].decode("ascii", errors="replace") if ch.alpn else None
            info.ja3_string = tlsproto.ja3_string(ch)
            info.ja3 = tlsproto.ja3(ch)
            info.ja4 = tlsproto.ja4(ch, "t")
            fl.tls = info
            self.tls_events += 1
            self.sink(TlsEvent(ts, fl.orig_ip, fl.orig_port, fl.resp_ip, fl.resp_port, fl.flow_id, info,
                               community_id=fl.cid, ref=ref))
        else:
            if fl.tls_sstate:
                return
            if not fl.tls_sbuf and payload[0] != tlsproto.HANDSHAKE:
                fl.tls_sstate = 2
                return
            if fl.tls_sbuf and not in_order:
                fl.tls_sstate = 2
                fl.tls_sbuf = bytearray()
                return
            fl.tls_sbuf += payload
            try:
                body = tlsproto.extract_handshake(bytes(fl.tls_sbuf), tlsproto.SERVER_HELLO)
            except tlsproto.NeedMoreData:
                if len(fl.tls_sbuf) > limit:
                    fl.tls_sstate = 2
                    fl.tls_sbuf = bytearray()
                return
            fl.tls_sbuf = bytearray()
            fl.tls_sstate = 2
            if body is None:
                return
            try:
                sh = tlsproto.parse_server_hello(body)
            except ValueError:
                return
            fl.tls_sstate = 1
            info = fl.tls or TlsInfo()
            info.ja3s = tlsproto.ja3s(sh)
            info.version = tlsproto.version_name(sh.selected_version or sh.legacy_version) or info.version
            info.server_hello_seen = True
            fl.tls = info

    # --------------------------------------------------------------------- DNS
    def _dns(self, ts, src, sport, dst, dport, payload, fl: _Flow, ref: PacketRef) -> None:
        msg = dnsproto.parse(payload)
        if msg is None:
            self.dns_errors += 1
            return
        name = msg.qname
        if not msg.is_response:
            key = (src, sport, dst, msg.qid, name)
            if key not in self._dns_pending:
                self._dns_pending[key] = (ts, name, msg.qtype, fl.flow_id, ref, fl.cid)
            return
        pending = self._dns_pending.pop((dst, dport, src, msg.qid, name), None)
        if pending:
            qts, _, qtype, flow_id, qref, cid = pending
            event = DnsEvent(qts, dst, src, name, qtype, msg.rcode, msg.answers, True, flow_id,
                             community_id=cid, ref=qref)
        else:  # only the response direction was visible
            event = DnsEvent(ts, dst, src, name, msg.qtype, msg.rcode, msg.answers, True, fl.flow_id,
                             community_id=fl.cid, ref=ref)
        self.dns_events += 1
        self.sink(event)

    def _expire_dns(self, now: float) -> None:
        wait = self.s.dns_response_wait_s
        pending = self._dns_pending
        while pending:
            key = next(iter(pending))
            qts, name, qtype, flow_id, ref, cid = pending[key]
            if qts + wait > now:
                break
            del pending[key]
            self.dns_events += 1
            self.sink(DnsEvent(qts, key[0], key[2], name, qtype, None, 0, False, flow_id, community_id=cid, ref=ref))

    # --------------------------------------------------- per-destination seconds
    def _dst_update(self, proto, src, dst, sport, dport, flags, ip_len) -> None:
        table = self._dst
        st = table.get(dst)
        if st is None:
            st = table[dst] = DstSecond(self._second or 0, dst)
        st.packets += 1
        st.bytes += ip_len
        if len(st.sources) < _MAX_SOURCES:
            st.sources[src] = st.sources.get(src, 0) + 1
        elif src in st.sources:
            st.sources[src] += 1
        else:
            st.sources_truncated = True
        if proto == TCP:
            if flags & SYN:
                if flags & ACK:
                    back = table.get(src)
                    if back is None:
                        back = table[src] = DstSecond(self._second or 0, src)
                    back.synack_sent += 1
                else:
                    st.tcp_syn += 1
        elif proto == UDP:
            st.udp_packets += 1
            sender = table.get(src)
            if sender is None:
                sender = table[src] = DstSecond(self._second or 0, src)
            sender.udp_sent += 1
            if sport in AMPLIFICATION_PORTS and dport not in AMPLIFICATION_PORTS:
                st.amp_bytes += ip_len
                st.amp_packets += 1
                if len(st.amp_sources) < _MAX_SOURCES:
                    st.amp_sources.add(src)
            elif dport in AMPLIFICATION_PORTS and sport >= 1024:
                sender.amp_requests_sent += 1

    def _roll_second(self, sec: int) -> None:
        if self._second is not None:
            self.second_counts.append((self._second, self._sec_packets, self._sec_bytes))
            minimum = self.s.dst_stats_min_packets
            for st in self._dst.values():
                if st.packets >= minimum or st.synack_sent >= minimum or st.amp_requests_sent >= minimum:
                    st.ts = self._second
                    self.sink(st)
        self._dst = {}
        self._sec_packets = self._sec_bytes = 0
        self._second = sec
        self._expire_dns(sec)
        self.advance(sec)

    # ------------------------------------------------------------------ timers
    def _schedule(self, fl: _Flow) -> None:
        deadline = self._deadline(fl)
        if fl.deadline == 0.0 or int(deadline) != int(fl.deadline):
            self._wheel[int(deadline)].append(fl.key)
        fl.deadline = deadline

    def _idle_deadline(self, fl: _Flow) -> float:
        s = self.s
        if fl.proto == TCP:
            if (fl.fin_orig and fl.fin_resp) or fl.rst_orig or fl.rst_resp:
                return fl.last_ts + s.tcp_closed_linger_s
            if not fl.established and fl.resp_pkts == 0:
                return fl.last_ts + s.tcp_attempt_s
            return fl.last_ts + s.tcp_idle_s
        return fl.last_ts + s.udp_idle_s

    def _deadline(self, fl: _Flow) -> float:
        return min(self._idle_deadline(fl), fl.last_export_ts + self.s.active_timeout_s)

    def advance(self, now: float) -> None:
        target = int(now)
        if self._cursor is None:
            self._cursor = target
            return
        if target - self._cursor > 600:
            buckets = sorted(k for k in self._wheel if k < target)
        else:
            buckets = range(self._cursor, target)
        for sec in buckets:
            keys = self._wheel.pop(sec, None)
            if keys:
                self._fire(sec, keys, now)
        self._cursor = max(self._cursor, target)

    def _fire(self, sec: int, keys: list, now: float) -> None:
        for key in keys:
            fl = self._flows.get(key)
            if fl is None or int(fl.deadline) != sec:
                continue
            if self._idle_deadline(fl) <= now:
                del self._flows[key]
                self._export(fl, final=True)
            else:
                self._export(fl, final=False)
                fl.last_export_ts = now
                fl.deadline = 0.0
                self._schedule(fl)

    def _evict(self) -> None:
        target = max(1, len(self._flows) // 10)
        evicted = 0
        for sec in sorted(self._wheel):
            for key in self._wheel.pop(sec):
                fl = self._flows.pop(key, None)
                if fl is not None:
                    self._export(fl, final=True)
                    evicted += 1
            if evicted >= target:
                break
        self.evicted += evicted

    # ------------------------------------------------------------------ export
    def _export(self, fl: _Flow, final: bool) -> None:
        if fl.proto == TCP:
            if fl.rst_resp and not fl.established:
                state = "rejected"
            elif not fl.established and fl.resp_pkts == 0:
                state = "attempt"
            elif (fl.fin_orig and fl.fin_resp) or fl.rst_orig or fl.rst_resp:
                state = "closed"
            else:
                state = "established" if fl.established else "other"
        elif fl.proto == UDP:
            state = "udp"
        else:
            state = "other"
        record = FlowRecord(
            flow_id=fl.flow_id, community_id=fl.cid, proto=fl.proto,
            src=fl.orig_ip, sport=fl.orig_port, dst=fl.resp_ip, dport=fl.resp_port,
            first_ts=fl.first_ts, last_ts=fl.last_ts,
            orig_pkts=fl.orig_pkts, orig_bytes=fl.orig_bytes, resp_pkts=fl.resp_pkts, resp_bytes=fl.resp_bytes,
            orig_payload=fl.orig_payload, resp_payload=fl.resp_payload,
            d_orig_bytes=fl.orig_bytes - fl.exported_orig, d_resp_bytes=fl.resp_bytes - fl.exported_resp,
            first_export=not fl.exported_once, final=final, state=state,
            syn=fl.syn, synack=fl.synack, rst_from_resp=fl.rst_resp, orig_inferred=fl.inferred,
            orig_gap_bytes=fl.gap[0], resp_gap_bytes=fl.gap[1], tls=fl.tls, quic_version=fl.quic_version,
            splt=list(fl.splt), first_ref=fl.first_ref, last_ref=fl.last_ref,
        )
        fl.exported_orig = fl.orig_bytes
        fl.exported_resp = fl.resp_bytes
        fl.exported_once = True
        self.flows_exported += 1
        if final and record.directions_seen == 1:
            self.flows_one_sided += 1
        self.sink(record)

    def flush(self) -> None:
        """End of input: close the open second, answer-less DNS, and every flow."""
        if self._second is not None:
            self._roll_second(self._second + 1)
        self._expire_dns(float("inf"))
        for fl in sorted(self._flows.values(), key=lambda f: f.first_ts):
            self._export(fl, final=True)
        self._flows.clear()
        self._wheel.clear()

    def stats(self) -> dict:
        return {
            "packets": self.packets, "bytes": self.bytes, "non_ip": self.non_ip, "malformed": self.malformed,
            "flows_active": len(self._flows), "flows_created": self.flows_created,
            "flows_exported": self.flows_exported, "flows_one_sided": self.flows_one_sided,
            "dns_events": self.dns_events, "dns_errors": self.dns_errors, "tls_events": self.tls_events,
            "tcp_gap_bytes": self.gap_bytes, "payload_bytes": self.payload_bytes, "evicted": self.evicted,
            "last_packet_ts": self.last_ts,
        }

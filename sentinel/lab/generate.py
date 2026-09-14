"""Labelled lab traffic generator.

Writes a classic pcap of an enterprise gateway link (both directions, as a
passive tap or diode feed would copy it) plus a ground-truth JSON manifest
listing every injected attack with its class, entities and time window.

Background traffic: DNS lookups of popular domains, HTTPS browsing with
browser-like TLS fingerprints, API polling, NTP, large downloads, a sanctioned
nightly backup upload, and a fleet-wide update-check service that is
periodic by design (a realistic beaconing false-positive trap).

Attacks: spoofed SYN flood, DNS/NTP reflection flood, jittered TLS beacon from
an implant with a rare client fingerprint, DGA lookups from an unseen malware
family, DNS tunnelling over TXT, SYN port scan, and slow bulk exfiltration.

This is SYNTHETIC data. Detection numbers measured on it show the pipeline
works end to end and bound its false-alert behaviour on this background; they
are not a substitute for evaluation on real captures.

    python -m sentinel.lab.generate --out lab/capture.pcap --hours 2
"""

from __future__ import annotations

import argparse
import base64
import csv
import heapq
import ipaddress
import json
import random
import struct
from pathlib import Path

from sentinel.ingest.pcapio import PcapWriter
from sentinel.lab import packets as P

SNAPLEN_BULK = 128  # bulk data packets are stored header-only, like `tcpdump -s 128`
ROOT = Path(__file__).resolve().parents[2]


class Timeline:
    """Collects (ts, frame, wire_len) from many generators and writes them in order."""

    def __init__(self) -> None:
        self._heap: list = []
        self._n = 0

    def add(self, ts: float, frame: bytes, truncate: bool = False) -> None:
        wire = len(frame)
        data = frame[:SNAPLEN_BULK] if truncate else frame
        heapq.heappush(self._heap, (ts, self._n, data, wire))
        self._n += 1

    def __len__(self) -> int:
        return self._n

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            writer = PcapWriter(f)
            while self._heap:
                ts, _, data, wire = heapq.heappop(self._heap)
                writer.write(ts, data, wire)


class Lab:
    def __init__(self, seed: int, start: float, hours: float) -> None:
        self.rng = random.Random(seed)
        self.t0 = start
        self.duration = hours * 3600
        self.tl = Timeline()
        self.truth: list[dict] = []
        self.ports = {}
        self.clients = [f"10.20.{1 + i // 200}.{10 + i % 200}" for i in range(60)]
        self.resolver = "10.20.0.53"
        self.popular = self._load_popular()
        self.cdn = {d: f"{self.rng.choice([23, 104, 142, 151, 172])}.{self.rng.randint(1, 250)}."
                       f"{self.rng.randint(1, 250)}.{self.rng.randint(2, 250)}" for d in self.popular}

    def _load_popular(self) -> list[str]:
        from sentinel.intel.toplist import TopList

        tl = TopList.load()
        names = list(tl._ranks)[:3000] if len(tl) else ["example.com", "example.org", "example.net"]
        return [n for n in names if n.count(".") == 1][:1500]

    def sport(self, host: str) -> int:
        port = self.ports.get(host, self.rng.randint(32768, 50000)) + 1
        if port > 60999:
            port = 32768
        self.ports[host] = port
        return port

    # ------------------------------------------------------------ primitives
    def dns(self, ts: float, client: str, name: str, qtype: int = P.DNS_A, rcode: int = 0, answer: str | None = None,
            txt: str | None = None, rtt: float = 0.004) -> None:
        qid = self.rng.randint(1, 65535)
        port = self.sport(client)
        self.tl.add(ts, P.udp_packet(client, self.resolver, port, 53, P.dns_query(qid, name, qtype)))
        answers = []
        if rcode == 0:
            if qtype == P.DNS_TXT:
                answers = [(P.DNS_TXT, P.txt_rdata(txt or "ok"))]
            elif answer:
                answers = [(P.DNS_A, ipaddress.ip_address(answer).packed)]
        self.tl.add(ts + rtt, P.udp_packet(self.resolver, client, 53, port, P.dns_response(qid, name, qtype, rcode, answers)))

    def tcp_session(self, ts: float, client: str, server: str, dport: int, requests: list[tuple[int, int]],
                    hello: bytes | None = None, rtt: float = 0.02, gap: float = 0.05, server_hello: bool = True,
                    close: bool = True) -> float:
        """requests: list of (client_bytes, server_bytes). Returns end time."""
        sp = self.sport(client)
        cseq, sseq = self.rng.randint(1, 2 ** 31), self.rng.randint(1, 2 ** 31)
        add = self.tl.add
        add(ts, P.tcp_packet(client, server, sp, dport, cseq, 0, P.SYN))
        add(ts + rtt, P.tcp_packet(server, client, dport, sp, sseq, cseq + 1, P.SYN | P.ACK))
        t = ts + rtt + 0.0005
        cseq += 1
        sseq += 1
        add(t, P.tcp_packet(client, server, sp, dport, cseq, sseq, P.ACK))
        if hello is not None:
            t += 0.001
            add(t, P.tcp_packet(client, server, sp, dport, cseq, sseq, P.PSH | P.ACK, hello))
            cseq += len(hello)
            if server_hello:
                sh = P.server_hello(rng=self.rng.randbytes)
                t += rtt
                add(t, P.tcp_packet(server, client, dport, sp, sseq, cseq, P.PSH | P.ACK, sh))
                sseq += len(sh)
        for c_bytes, s_bytes in requests:
            t += gap
            cseq, t = self._bulk(t, client, server, sp, dport, cseq, sseq, c_bytes, 0.00008)
            t += rtt
            sseq, t = self._bulk(t, server, client, dport, sp, sseq, cseq, s_bytes, 0.00008)
        if close:
            t += 0.01
            add(t, P.tcp_packet(client, server, sp, dport, cseq, sseq, P.FIN | P.ACK))
            add(t + rtt, P.tcp_packet(server, client, dport, sp, sseq, cseq + 1, P.FIN | P.ACK))
            add(t + rtt + 0.0005, P.tcp_packet(client, server, sp, dport, cseq + 1, sseq + 1, P.ACK))
            t += rtt
        return t

    def _bulk(self, t, src, dst, sport, dport, seq, ack, nbytes, pace):
        mss = 1400
        while nbytes > 0:
            size = min(mss, nbytes)
            frame = P.tcp_packet(src, dst, sport, dport, seq, ack, P.ACK, b"\x17" * size)
            self.tl.add(t, frame, truncate=size > 200)
            seq += size
            nbytes -= size
            t += pace
        return seq, t

    def label(self, cls: str, t0: float, t1: float, src: str | None = None, dst: str | None = None, **extra) -> None:
        self.truth.append({"threat_class": cls, "src": src, "dst": dst, "t0": round(t0, 3), "t1": round(t1, 3), **extra})

    # ------------------------------------------------------------ background
    def background(self) -> None:
        rng = self.rng
        profiles = [P.CHROME_LIKE, P.FIREFOX_LIKE]
        end = self.t0 + self.duration
        for i, host in enumerate(self.clients):
            profile = profiles[i % 2]
            t = self.t0 + rng.uniform(0, 30)
            while t < end:
                domain = rng.choice(self.popular[:400]) if rng.random() < 0.7 else rng.choice(self.popular)
                server = self.cdn[domain]
                sub = rng.choice(["www.", "", "static.", "api.", "cdn."])
                self.dns(t, host, sub + domain, answer=server)
                if rng.random() < 0.3:
                    self.dns(t + 0.001, host, sub + domain, P.DNS_AAAA)
                reqs = [(rng.randint(300, 1800), rng.randint(2000, 120000)) for _ in range(rng.randint(1, 4))]
                self.tcp_session(t + 0.01, host, server, 443, reqs, hello=P.client_hello(profile, sub + domain, rng.randbytes),
                                 rtt=rng.uniform(0.01, 0.08))
                t += rng.expovariate(1 / 45.0)
            # NTP every ~17 minutes
            nt = self.t0 + rng.uniform(0, 600)
            while nt < end:
                sp = 123
                self.tl.add(nt, P.udp_packet(host, "10.20.0.1", sp, 123, b"\xe3" + b"\x00" * 47))
                self.tl.add(nt + 0.001, P.udp_packet("10.20.0.1", host, 123, sp, b"\x24" + b"\x00" * 47))
                nt += 1024 + rng.uniform(-5, 5)

        # fleet update-check service: every host polls every 30 min (periodic by design)
        update_ip = "13.107.4.50"
        for host in self.clients:
            t = self.t0 + rng.uniform(0, 1800)
            while t < end:
                self.dns(t, host, "update.microsoft.com", answer=update_ip)
                self.tcp_session(t + 0.01, host, update_ip, 443, [(420, 1350)],
                                 hello=P.client_hello(P.CHROME_LIKE, "update.microsoft.com", rng.randbytes))
                t += 1800 + rng.uniform(-20, 20)

        # large downloads (inbound heavy)
        for _ in range(int(self.duration / 600)):
            host = rng.choice(self.clients)
            t = self.t0 + rng.uniform(0, self.duration - 300)
            self.tcp_session(t, host, self.cdn["github.com"] if "github.com" in self.cdn else "140.82.112.3", 443,
                             [(900, rng.randint(40, 200) * 1_000_000)],
                             hello=P.client_hello(P.CHROME_LIKE, "objects.githubusercontent.com", rng.randbytes))

        # sanctioned backup upload: large outbound, destination allow-listed in the lab settings
        backup_host, backup_dst = self.clients[5], "203.0.113.200"
        t = self.t0 + 1200
        self.tcp_session(t, backup_host, backup_dst, 443, [(160_000_000, 40_000)],
                         hello=P.client_hello(P.OPENSSL_LIKE, "backup.corp-offsite.example", rng.randbytes))

        # internal monitoring poller: wide, successful fan-out
        poller = "10.20.0.5"
        t = self.t0 + 300
        while t < end:
            for k in range(40):
                self.tcp_session(t + k * 0.05, poller, f"10.20.1.{10 + k}", 9100, [(120, 3000)], rtt=0.001)
            t += 300

    # --------------------------------------------------------------- attacks
    def syn_flood(self, at: float, seconds: int = 12, rate: int = 3000) -> None:
        target, rng = "10.20.0.80", self.rng
        answered = 0
        for s in range(seconds):
            for k in range(rate):
                ts = at + s + k / rate
                src = f"{rng.randint(11, 223)}.{rng.randint(0, 255)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}"
                sp = rng.randint(1024, 65535)
                seq = rng.randint(1, 2 ** 31)
                self.tl.add(ts, P.tcp_packet(src, target, sp, 443, seq, 0, P.SYN, ttl=rng.randint(40, 250)))
                if k % 25 == 0:  # the target's backlog still answers a few
                    self.tl.add(ts + 0.0002, P.tcp_packet(target, src, 443, sp, rng.randint(1, 2 ** 31), seq + 1,
                                                          P.SYN | P.ACK))
                    answered += 1
        self.label("ddos.syn_flood", at, at + seconds, dst=target, spoofed=True, rate_pps=rate)

    def amplification(self, at: float, seconds: int = 10) -> None:
        target, rng = "10.20.0.53", self.rng
        reflectors = [f"{rng.randint(11, 223)}.{rng.randint(0, 255)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}"
                      for _ in range(400)]
        for s in range(seconds):
            for k in range(1500):
                ts = at + s + k / 1500
                refl = reflectors[k % len(reflectors)]
                if k % 3:
                    payload = P.dns_response(rng.randint(1, 65535), "isc.org", 255, 0,
                                             [(P.DNS_TXT, P.txt_rdata("v" * 600)), (P.DNS_TXT, P.txt_rdata("k" * 600))])
                    self.tl.add(ts, P.udp_packet(refl, target, 53, rng.randint(1024, 65535), payload), truncate=True)
                else:
                    payload = b"\x17\x00\x03\x2a" + b"\x00" * 436
                    self.tl.add(ts, P.udp_packet(refl, target, 123, rng.randint(1024, 65535), payload), truncate=True)
        self.label("ddos.udp_amplification", at, at + seconds, dst=target, reflectors=len(reflectors))

    def beacon(self, at: float, until: float, interval: float = 60.0, jitter: float = 0.15) -> None:
        host, c2, rng = "10.20.5.23", "185.225.17.91", self.rng
        t = at
        first = True
        while t < until:
            hello = P.client_hello(P.GO_LIKE, None, rng.randbytes)
            self.tcp_session(t, host, c2, 443, [(rng.randint(310, 330), rng.randint(90, 140))], hello=hello, rtt=0.09)
            if first:
                first = False
            t += interval * (1 + rng.uniform(-jitter, jitter))
        self.label("c2.beaconing", at, until, src=host, dst=c2, interval_s=interval, jitter=jitter)
        self.label("tls.suspicious_session", at, until, src=host, dst=c2, note="rare Go-like fingerprint, no SNI")

    def dga(self, at: float, family: str = "necurs", count: int = 30) -> None:
        host, rng = "10.20.7.41", self.rng
        domains = []
        with open(ROOT / "ml" / "data" / "dga_domains.csv", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["family"] == family:
                    domains.append(row["domain"])
        rng.shuffle(domains)
        t = at
        for i, d in enumerate(domains[:count]):
            resolved = i == count - 1
            self.dns(t, host, d, rcode=0 if resolved else 3, answer="45.153.160.2" if resolved else None)
            t += rng.uniform(0.5, 3.0)
        self.label("dns.dga", at, t, src=host, family=family, domains=count)

    def dns_tunnel(self, at: float, queries: int = 400) -> None:
        host, domain, rng = "10.20.8.12", "cdn-sync-telemetry.xyz", self.rng
        t = at
        for i in range(queries):
            chunk = base64.b32encode(rng.randbytes(35)).decode().rstrip("=").lower()
            name = f"{chunk[:56]}.{i:04x}.t.{domain}"
            self.dns(t, host, name, P.DNS_TXT, txt=base64.b64encode(rng.randbytes(90)).decode(), rtt=0.03)
            t += rng.uniform(0.05, 0.4)
        self.label("dns.tunnel", at, t, src=host, dst=domain, queries=queries)

    def port_scan(self, at: float) -> None:
        scanner, target, rng = "10.20.9.99", "10.20.0.10", self.rng
        open_ports = {22, 80, 443, 3306}
        ports = rng.sample(range(1, 10000), 1000)
        t = at
        for port in ports:
            sp = rng.randint(40000, 60000)
            seq = rng.randint(1, 2 ** 31)
            self.tl.add(t, P.tcp_packet(scanner, target, sp, port, seq, 0, P.SYN))
            if port in open_ports:
                self.tl.add(t + 0.0004, P.tcp_packet(target, scanner, port, sp, 7, seq + 1, P.SYN | P.ACK))
                self.tl.add(t + 0.0008, P.tcp_packet(scanner, target, sp, port, seq + 1, 0, P.RST))
            else:
                self.tl.add(t + 0.0004, P.tcp_packet(target, scanner, port, sp, 0, seq + 1, P.RST | P.ACK))
            t += 0.004
        self.label("recon.scan", at, t, src=scanner, dst=target, ports=len(ports))

    def slowloris(self, at: float, connections: int = 60, duration: float = 90.0) -> None:
        # Many concurrent connections from a few sources to one web server, each held open
        # for a long time while sending only a trickle of header bytes and never completing.
        attackers = ["10.20.11.5", "10.20.11.6"]
        target, rng = "10.20.0.90", self.rng
        for k in range(connections):
            src = attackers[k % len(attackers)]
            sp = self.sport(src)
            cseq, sseq = rng.randint(1, 2 ** 31), rng.randint(1, 2 ** 31)
            self.tl.add(at + k * 0.05, P.tcp_packet(src, target, sp, 80, cseq, 0, P.SYN))
            self.tl.add(at + k * 0.05 + 0.01, P.tcp_packet(target, src, 80, sp, sseq, cseq + 1, P.SYN | P.ACK))
            cseq += 1
            sseq += 1
            self.tl.add(at + k * 0.05 + 0.011, P.tcp_packet(src, target, sp, 80, cseq, sseq, P.ACK))
            # trickle a few header bytes every ~15 s for the whole hold time
            t = at + k * 0.05 + 1.0
            while t < at + duration:
                chunk = b"X-a: b\r\n"
                self.tl.add(t, P.tcp_packet(src, target, sp, 80, cseq, sseq, P.PSH | P.ACK, chunk))
                cseq += len(chunk)
                t += 15.0
        self.label("ddos.slow_http", at, at + duration, dst=target, connections=connections, sources=len(attackers))

    def exfil(self, at: float) -> None:
        host, dst, rng = "10.20.6.77", "91.215.85.14", self.rng
        t = at
        for _ in range(6):  # six uploads of 30 MB over ~5 minutes
            t = self.tcp_session(t, host, dst, 443, [(30_000_000, 2000)],
                                 hello=P.client_hello(P.OPENSSL_LIKE, "files.sharestore-drop.top", rng.randbytes)) + 20
        self.label("exfil.volume", at, t, src=host, dst=dst, bytes=180_000_000)
        # the uploads use a TLS client shared by almost no other host toward an unranked drop domain
        self.label("tls.suspicious_session", at, t, src=host, dst=dst, note="exfiltration channel")


def build(out: Path, hours: float, seed: int, start: float) -> dict:
    lab = Lab(seed, start, hours)
    lab.background()
    d = lab.duration
    lab.beacon(lab.t0 + 600, lab.t0 + d - 60)
    lab.syn_flood(lab.t0 + 0.30 * d)
    lab.amplification(lab.t0 + 0.45 * d)
    lab.dga(lab.t0 + 0.20 * d)
    lab.dns_tunnel(lab.t0 + 0.55 * d)
    lab.port_scan(lab.t0 + 0.65 * d)
    lab.slowloris(lab.t0 + 0.70 * d)
    lab.exfil(lab.t0 + 0.80 * d)
    lab.tl.write(out)
    manifest = {
        "format": "sentinel.lab-truth/1.0",
        "capture": out.name,
        "seed": seed,
        "start": lab.t0,
        "end": lab.t0 + d,
        "duration_hours": hours,
        "packets": len(lab.tl),
        "internal_nets": ["10.20.0.0/16"],
        "allow_destinations": ["203.0.113.200"],
        "benign_background": ["dns", "https-browsing", "ntp", "update-polling", "downloads", "backup-upload",
                              "monitoring-poller"],
        "attacks": lab.truth,
        "synthetic": True,
    }
    out.with_suffix(".truth.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="lab/captures/lab.pcap")
    ap.add_argument("--hours", type=float, default=2.0)
    ap.add_argument("--seed", type=int, default=26145)
    ap.add_argument("--start", type=float, default=1_788_000_000.0)
    args = ap.parse_args()
    manifest = build(Path(args.out), args.hours, args.seed, args.start)
    print(f"wrote {args.out}: {manifest['packets']} packets, {len(manifest['attacks'])} labelled attacks")


if __name__ == "__main__":
    main()

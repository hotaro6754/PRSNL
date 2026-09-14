"""Streaming pipeline: capture -> flow meter -> detectors -> signed alert store -> cases.

Two ingest modes share the same detectors, store, correlation and custody:
  * run_capture:      packet capture (file or live pcap stream) -> full flow meter
  * run_flow_export:  NetFlow v5/v9 or IPFIX records -> FlowRecord directly
Flow-export mode has no packet payload, so DNS and TLS detection are unavailable
in it; every other detector runs unchanged.
"""

from __future__ import annotations

import bisect
import logging
import threading
import time
import uuid
from collections import defaultdict
from pathlib import Path

from sentinel.archive import FlowArchiveWriter
from sentinel.cases import CaseCorrelator
from sentinel.config import Settings
from sentinel.detect.anomaly import AnomalyDetector
from sentinel.detect.base import Context, Detector
from sentinel.detect.beacon import BeaconDetector
from sentinel.detect.ddos import DDoSDetector
from sentinel.detect.dga_model import DgaModel
from sentinel.detect.dns import DnsDetector
from sentinel.detect.exfil import ExfilDetector
from sentinel.detect.scan import ScanDetector
from sentinel.detect.slowhttp import SlowHttpDetector
from sentinel.detect.tls import TlsDetector
from sentinel.events import TCP, UDP, DnsEvent, DstSecond, FlowRecord, TlsEvent
from sentinel.config import AMPLIFICATION_PORTS
from sentinel.ingest.flowmeter import FlowMeter
from sentinel.ingest.netflow import FlowExportReader
from sentinel.ingest.pcapio import PcapReader, sha256_file
from sentinel.intel.toplist import TopList, load_ja3_blocklist
from sentinel.store import Store

log = logging.getLogger("sentinel.engine")

DEFAULT_DGA_MODEL = Path(__file__).resolve().parent.parent / "models" / "dga" / "dga_char_ngram_lr.npz"

_DISPATCH = {FlowRecord: "on_flow", DnsEvent: "on_dns", TlsEvent: "on_tls", DstSecond: "on_dst_second"}
_LATENCY_SAMPLE = 8  # record event latency for one event in eight


class LatencyTracker:
    """Keeps a bounded sorted sample of processing latencies (ms)."""

    def __init__(self, size: int = 20000) -> None:
        self.size = size
        self.samples: list[float] = []
        self.count = 0

    def add(self, value: float) -> None:
        self.count += 1
        if len(self.samples) < self.size:
            bisect.insort(self.samples, value)
        elif self.count % 7 == 0:  # thin sampling once full
            self.samples.pop(len(self.samples) // 2)
            bisect.insort(self.samples, value)

    def percentile(self, p: float) -> float | None:
        if not self.samples:
            return None
        return self.samples[min(len(self.samples) - 1, int(p / 100 * len(self.samples)))]


class FlowDstAggregator:
    """Rebuilds per-destination one-second aggregates from flow records so the DDoS
    detector runs in flow-export mode. A flow's packets/bytes are attributed to its
    start second (flow exporters do not give per-second detail)."""

    def __init__(self, sink) -> None:
        self.sink = sink
        self._second: int | None = None
        self._dst: dict[str, DstSecond] = {}

    def add(self, rec: FlowRecord) -> None:
        sec = int(rec.first_ts)
        if self._second is None:
            self._second = sec
        elif sec != self._second:
            self._flush()
            self._second = sec
        st = self._dst.get(rec.dst)
        if st is None:
            st = self._dst[rec.dst] = DstSecond(sec, rec.dst)
        st.packets += rec.orig_pkts
        st.bytes += rec.orig_bytes
        st.sources[rec.src] = st.sources.get(rec.src, 0) + rec.orig_pkts
        if rec.proto == TCP and rec.syn and rec.state in ("attempt", "rejected"):
            st.tcp_syn += rec.orig_pkts
        elif rec.proto == UDP:
            st.udp_packets += rec.orig_pkts
            if rec.sport in AMPLIFICATION_PORTS and rec.dport not in AMPLIFICATION_PORTS:
                st.amp_bytes += rec.orig_bytes
                st.amp_packets += rec.orig_pkts
                st.amp_sources.add(rec.src)

    def _flush(self) -> None:
        for st in self._dst.values():
            self.sink(st)
        self._dst = {}

    def flush(self) -> None:
        self._flush()


class Engine:
    def __init__(self, settings: Settings, store: Store, dga_model_path: str | Path | None = None,
                 detectors: list[Detector] | None = None) -> None:
        self.settings = settings
        self.store = store
        self.ctx = Context(settings)
        self.toplist = TopList.load()
        model_path = Path(dga_model_path) if dga_model_path else DEFAULT_DGA_MODEL
        self.dga_model = DgaModel.load(model_path) if model_path.exists() else None
        if self.dga_model is None:
            log.warning("DGA model not found at %s: DGA scoring disabled", model_path)
        if detectors is None:
            detectors = [
                DDoSDetector(settings.ddos),
                ScanDetector(settings.scan),
                BeaconDetector(settings.beacon),
                DnsDetector(settings.dns, self.dga_model, self.toplist),
                TlsDetector(settings.tls, self.toplist, load_ja3_blocklist()),
                ExfilDetector(settings.exfil),
                SlowHttpDetector(settings.slowhttp),
            ]
            if settings.anomaly.enabled:
                detectors.append(AnomalyDetector(settings.anomaly))
        self.detectors = detectors
        # Only call detector methods that are actually implemented (base-class methods are no-ops).
        self._routes = {
            event_type: [(d, getattr(d, method)) for d in self.detectors
                         if getattr(type(d), method) is not getattr(Detector, method)]
            for event_type, method in _DISPATCH.items()
        }
        self._route_keys = {event_type: method[3:] for event_type, method in _DISPATCH.items()}
        self._handled = 0
        self.correlator = CaseCorrelator(store)
        self.source_sha256: str | None = None
        self.events = {"flow": 0, "dns": 0, "tls": 0, "dst_second": 0}
        self.alerts_emitted = 0
        self.detector_errors: dict[str, int] = {}
        self.alert_latency = LatencyTracker()
        self.event_latency = LatencyTracker()
        self.meter: FlowMeter | None = None
        self.running_source: str | None = None
        self._archive: FlowArchiveWriter | None = None
        self._lock = threading.RLock()

    # ------------------------------------------------------------ event sink
    def handle(self, event) -> None:
        start = time.perf_counter()
        event_type = type(event)
        routes = self._routes.get(event_type)
        if routes is None:
            return
        self.events[self._route_keys[event_type]] += 1
        if event_type is FlowRecord:
            self.ctx.now = event.last_ts
            if self._archive is not None:
                self._archive.write(event)
        ctx = self.ctx
        for detector, fn in routes:
            try:
                produced = fn(event, ctx)
            except Exception:
                self.detector_errors[detector.name] = self.detector_errors.get(detector.name, 0) + 1
                log.exception("detector %s failed on %s", detector.name, event_type.__name__)
                continue
            for alert in produced:
                self._emit(alert, start)
        self._handled += 1
        if self._handled % _LATENCY_SAMPLE == 0:
            self.event_latency.add((time.perf_counter() - start) * 1000)

    def _emit(self, alert, start: float) -> None:
        alert.sensor_id = self.settings.sensor_id
        if alert.custody is not None:
            alert.custody.source_sha256 = self.source_sha256
        alert.processing_latency_ms = round((time.perf_counter() - start) * 1000, 3)
        doc = self.store.append_alert(alert)
        self.alerts_emitted += 1
        self.alert_latency.add(alert.processing_latency_ms)
        try:
            self.correlator.ingest(doc)
        except Exception:
            log.exception("case correlation failed for alert %s", doc["alert_id"])

    def _open_archive(self, source_id: str) -> None:
        if self.settings.archive.enabled:
            try:
                self._archive = FlowArchiveWriter(self.settings.data_dir, source_id,
                                                  self.settings.archive.max_flows_per_source)
            except OSError as exc:
                log.warning("flow archive disabled: %s", exc)
                self._archive = None

    def _close_archive(self) -> None:
        if self._archive is not None:
            self._archive.close()
            self._archive = None

    # --------------------------------------------------------------- capture
    def run_capture(self, path: str, label: str | None = None, source_id: str | None = None,
                    realtime: float | None = None, live: bool = False, progress=None) -> dict:
        """Process a packet capture (file, or "-" for a live pcap stream on stdin).

        realtime: replay speed multiplier (1.0 = original pacing); None = as fast as possible.
        """
        source_id = source_id or uuid.uuid4().hex[:16]
        with self._lock:
            self.ctx.source_id = source_id
            self.source_sha256 = sha256_file(path) if path != "-" else None
            self.running_source = source_id
            self.store.add_source(source_id, "live" if live or path == "-" else "pcap", label, path)
            self._open_archive(source_id)
            meter = self.meter = FlowMeter(self.settings, source_id, self.handle)
        reader = PcapReader(path)
        stop_ticker = threading.Event()
        if live or path == "-":
            threading.Thread(target=self._tick_live, args=(meter, stop_ticker), daemon=True).start()
        wall_start = time.perf_counter()
        first_ts = None
        alerts_before = self.alerts_emitted
        status, error = "completed", None
        try:
            for pkt in reader:
                if realtime:
                    if first_ts is None:
                        first_ts = pkt.ts
                    ahead = (pkt.ts - first_ts) / realtime - (time.perf_counter() - wall_start)
                    if ahead > 0.002:
                        time.sleep(min(ahead, 1.0))
                with self._lock:
                    meter.process(pkt)
                if progress is not None and meter.packets % 20000 == 0:
                    progress(self._summary(meter, reader, wall_start, alerts_before))
            with self._lock:
                meter.flush()
        except Exception as exc:
            status, error = "failed", f"{type(exc).__name__}: {exc}"
            log.exception("capture %s failed", path)
        finally:
            stop_ticker.set()
            reader.close()
            self._close_archive()
        summary = self._summary(meter, reader, wall_start, alerts_before)
        summary["status"] = status
        summary["mode"] = "packet"
        if error:
            summary["error"] = error
        self.store.finish_source(source_id, status, self.source_sha256 or reader.sha256, meter.packets, meter.bytes,
                                 summary, error)
        self.running_source = None
        return summary

    # ----------------------------------------------------------- flow export
    def run_flow_export(self, path: str, label: str | None = None, source_id: str | None = None,
                        progress=None) -> dict:
        """Process a NetFlow v5/v9 or IPFIX export file into the same detectors."""
        source_id = source_id or uuid.uuid4().hex[:16]
        with self._lock:
            self.ctx.source_id = source_id
            self.source_sha256 = sha256_file(path)
            self.running_source = source_id
            self.store.add_source(source_id, "flow-export", label, path)
            self._open_archive(source_id)
        reader = FlowExportReader(source_id)
        aggregator = FlowDstAggregator(self.handle)
        wall_start = time.perf_counter()
        alerts_before = self.alerts_emitted
        total_bytes = 0
        status, error = "completed", None
        try:
            records = sorted(reader.read_file(path), key=lambda r: r.first_ts)
            for rec in records:
                total_bytes += rec.orig_bytes
                with self._lock:
                    aggregator.add(rec)
                    self.handle(rec)
            with self._lock:
                aggregator.flush()
        except Exception as exc:
            status, error = "failed", f"{type(exc).__name__}: {exc}"
            log.exception("flow export %s failed", path)
        finally:
            self._close_archive()
        elapsed = max(1e-9, time.perf_counter() - wall_start)
        summary = {
            "source_id": source_id, "status": status, "mode": "flow-export",
            "elapsed_s": round(elapsed, 3), "packets": 0, "bytes": total_bytes,
            "flows": reader.records, "exports": reader.exports, "unknown_templates": reader.unknown_templates,
            "flows_per_s": round(reader.records / elapsed, 1),
            "mbit_per_s": round(total_bytes * 8 / elapsed / 1e6, 2),
            "alerts": self.alerts_emitted - alerts_before,
            "event_latency_ms_p99": self.event_latency.percentile(99),
            "detector_errors": dict(self.detector_errors), "capture_sha256": self.source_sha256,
            "note": "flow-export mode: DNS and TLS detection unavailable (no packet payload)",
        }
        if error:
            summary["error"] = error
        self.store.finish_source(source_id, status, self.source_sha256, 0, total_bytes, summary, error)
        self.running_source = None
        return summary

    def _tick_live(self, meter: FlowMeter, stop: threading.Event) -> None:
        """On a quiet live link, timers must still fire on wall-clock time."""
        while not stop.wait(1.0):
            with self._lock:
                if meter.last_ts:
                    meter.advance(max(meter.last_ts, time.time()))

    def _summary(self, meter: FlowMeter, reader: PcapReader, wall_start: float, alerts_before: int) -> dict:
        elapsed = max(1e-9, time.perf_counter() - wall_start)
        stats = meter.stats()
        return {
            "source_id": meter.source_id,
            "elapsed_s": round(elapsed, 3),
            "packets": stats["packets"],
            "bytes": stats["bytes"],
            "flows": stats["flows_exported"],
            "packets_per_s": round(stats["packets"] / elapsed, 1),
            "flows_per_s": round(stats["flows_exported"] / elapsed, 1),
            "mbit_per_s": round(stats["bytes"] * 8 / elapsed / 1e6, 2),
            "alerts": self.alerts_emitted - alerts_before,
            "alert_latency_ms_p50": self.alert_latency.percentile(50),
            "alert_latency_ms_p99": self.alert_latency.percentile(99),
            "event_latency_ms_p50": self.event_latency.percentile(50),
            "event_latency_ms_p99": self.event_latency.percentile(99),
            "events": dict(self.events),
            "detector_errors": dict(self.detector_errors),
            "meter": stats,
            "capture_sha256": self.source_sha256 or reader.sha256,
        }

    def health(self) -> dict:
        return {
            "detectors": [{"name": d.name, "version": d.version, "errors": self.detector_errors.get(d.name, 0)}
                          for d in self.detectors],
            "dga_model": self.dga_model.ref().model_dump() if self.dga_model else None,
            "toplist_domains": len(self.toplist),
            "running_source": self.running_source,
            "meter": self.meter.stats() if self.meter else None,
        }

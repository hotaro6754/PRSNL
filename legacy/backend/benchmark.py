import time
import psutil
import os
import sys
import numpy as np
from pathlib import Path
from backend.ingestion.scapy_adapter import ScapyAdapter
from backend.correlation import CorrelationEngine
from backend.detectors.ddos import DDoSDetector
from backend.detectors.scan import PortScanDetector
from backend.detectors.beacon import BeaconingDetector
from backend.detectors.dga import DGADetector
from backend.detectors.dns_tunnel import DNSTunnelDetector
from backend.detectors.tls import TLSSessionDetector

def run_benchmark(pcap_files, iterations=1):
    print("=" * 60)
    print("M11 - THROUGHPUT & LATENCY BENCHMARK")
    print("=" * 60)
    
    process = psutil.Process(os.getpid())
    start_memory = process.memory_info().rss / (1024 * 1024)
    
    detectors = [
        DDoSDetector(),
        PortScanDetector(),
        BeaconingDetector(),
        DGADetector(),
        DNSTunnelDetector(),
        TLSSessionDetector()
    ]
    
    correlation_engine = CorrelationEngine(max_cases=1000, max_alerts_per_case=50)
    
    latencies = []
    total_flows = 0
    total_alerts = 0
    
    start_time = time.time()
    cpu_measurements = []
    memory_measurements = []
    
    for i in range(iterations):
        for pcap_file in pcap_files:
            if not Path(pcap_file).exists():
                print(f"Skipping {pcap_file} - Not found.")
                continue
                
            adapter = ScapyAdapter()
            for flow in adapter.consume(pcap_file):
                flow_start_t = time.perf_counter()
                
                for detector in detectors:
                    alerts = detector.add_flow(flow)
                    for alert in alerts:
                        total_alerts += 1
                        correlation_engine.ingest_alert(alert)
                
                flow_end_t = time.perf_counter()
                latencies.append((flow_end_t - flow_start_t) * 1000) # ms
                total_flows += 1
                
                if total_flows % 100 == 0:
                    cpu_measurements.append(psutil.cpu_percent(interval=None))
                    memory_measurements.append(process.memory_info().rss / (1024 * 1024))
            
            # Flush detectors
            for detector in detectors:
                alerts = detector.flush()
                for alert in alerts:
                    total_alerts += 1
                    correlation_engine.ingest_alert(alert)
                    
    end_time = time.time()
    
    total_time = end_time - start_time
    flows_per_sec = total_flows / total_time if total_time > 0 else 0
    
    p50 = np.percentile(latencies, 50) if latencies else 0
    p95 = np.percentile(latencies, 95) if latencies else 0
    p99 = np.percentile(latencies, 99) if latencies else 0
    
    avg_cpu = np.mean(cpu_measurements) if cpu_measurements else psutil.cpu_percent()
    peak_mem = np.max(memory_measurements) if memory_measurements else (process.memory_info().rss / (1024 * 1024))
    
    print(f"Dataset      : {', '.join([Path(p).name for p in pcap_files])} (x{iterations})")
    print(f"Total Flows  : {total_flows}")
    print(f"Duration     : {total_time:.2f} seconds")
    print(f"Throughput   : {flows_per_sec:.2f} flows/sec")
    print("-" * 60)
    print(f"Latency P50  : {p50:.4f} ms")
    print(f"Latency P95  : {p95:.4f} ms")
    print(f"Latency P99  : {p99:.4f} ms")
    print("-" * 60)
    print(f"Alerts       : {total_alerts}")
    print(f"Cases        : {len(correlation_engine.get_all_cases())}")
    print(f"Avg CPU      : {avg_cpu:.1f}%")
    print(f"Peak RAM     : {peak_mem:.2f} MB")
    print(f"Delta RAM    : {peak_mem - start_memory:.2f} MB")
    print("=" * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--workload", type=str, default="medium", choices=["small", "medium", "large", "stress"])
    args = parser.parse_args()
    
    small_files = ["data/pcaps/real_port_scan.pcap", "data/pcaps/encrypted_c2.pcap"]
    medium_files = small_files + ["data/pcaps/benign_transfer.pcap", "data/pcaps/udp_flood.pcap"]
    
    if args.workload == "small":
        run_benchmark(small_files, iterations=1)
    elif args.workload == "medium":
        run_benchmark(medium_files, iterations=5)
    elif args.workload == "large":
        run_benchmark(medium_files, iterations=25)
    elif args.workload == "stress":
        run_benchmark(medium_files, iterations=100)

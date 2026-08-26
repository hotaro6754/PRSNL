import argparse
import time
import json
import os
from datetime import datetime
import requests
import subprocess
import yaml

API_BASE = "http://localhost:8000"

def parse_duration(duration_str):
    if duration_str.endswith('h'):
        return int(duration_str[:-1]) * 3600
    elif duration_str.endswith('m'):
        return int(duration_str[:-1]) * 60
    elif duration_str.endswith('s'):
        return int(duration_str[:-1])
    return int(duration_str)

def collect_metrics(elapsed):
    try:
        stats = requests.get(f"{API_BASE}/api/stats", timeout=2).json()
        health = requests.get(f"{API_BASE}/health", timeout=2).json()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "elapsed_seconds": elapsed,
            "flows_per_second": stats.get("flows_per_sec", 0.0),
            "alerts_per_min": stats.get("alerts_per_min", 0.0),
            "total_active_cases": stats.get("total_active_cases", 0),
            "backend_health": health.get("status", "unknown"),
            "mongo_status": health.get("components", {}).get("mongodb", {}).get("status", "unknown"),
            "kafka_status": health.get("components", {}).get("redpanda", {}).get("status", "unknown")
        }
    except Exception as e:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "elapsed_seconds": elapsed,
            "error": str(e)
        }

def run_action(action):
    print(f"[{datetime.utcnow().isoformat()}] INJECTING: {action}")
    if action == "simulate_port_scan":
        requests.post(f"{API_BASE}/api/simulate/port_scan")
    elif action == "simulate_dga":
        requests.post(f"{API_BASE}/api/simulate/dga")
    elif action == "simulate_brute_force":
        requests.post(f"{API_BASE}/api/simulate/brute_force")
    elif action == "restart_ml_worker":
        subprocess.run(["docker", "compose", "restart", "sih26145-ml-worker"])

def generate_report(run_dir, target_duration, actual_duration, metrics):
    status = "PASS" if actual_duration >= target_duration else "INCOMPLETE"
    
    report = f"""# PS26145_CONTINUOUS_RELIABILITY_MASTER_REPORT

## 1. Test Information
- **Target Duration:** {target_duration} seconds
- **Actual Duration:** {actual_duration} seconds
- **Status:** {status}
- **Run Directory:** {run_dir}

## 2. Summary Scorecard
- Final Elapsed Time: {actual_duration}s
- Telemetry Samples: {len(metrics)}

## 3. Data Integrity & Discrepancies
- *Physical NIC Drop Metrics Unavailable* (Running on Docker/WSL2)
"""
    with open(os.path.join(run_dir, "report.md"), "w") as f:
        f.write(report)
        
    print(f"\n==================================================")
    print(f" TARGET DURATION : {target_duration}s")
    print(f" ACTUAL DURATION : {actual_duration}s")
    print(f" STATUS          : {status}")
    print(f"==================================================")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=str, required=True, help="e.g. 1h, 90m, 60s")
    parser.add_argument("--sample-interval", type=int, default=10, help="seconds")
    args = parser.parse_args()

    target_duration = parse_duration(args.duration)
    sample_interval = args.sample_interval

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = f"endurance_runs/{run_id}"
    os.makedirs(run_dir, exist_ok=True)
    
    metrics_file = open(os.path.join(run_dir, "metrics.jsonl"), "w")

    print(f"Starting Endurance Run: {run_id}")
    print(f"Target Duration: {target_duration}s")
    
    start_time = time.time()
    last_sample_time = 0
    metrics_log = []

    try:
        while True:
            current_time = time.time()
            elapsed = int(current_time - start_time)
            
            if elapsed >= target_duration:
                break
                
            if current_time - last_sample_time >= sample_interval:
                m = collect_metrics(elapsed)
                metrics_log.append(m)
                metrics_file.write(json.dumps(m) + "\\n")
                metrics_file.flush()
                print(f"[{elapsed}s] {m}")
                last_sample_time = current_time
                
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\\nRun aborted by user.")
        
    finally:
        actual_duration = int(time.time() - start_time)
        metrics_file.close()
        generate_report(run_dir, target_duration, actual_duration, metrics_log)

if __name__ == "__main__":
    main()

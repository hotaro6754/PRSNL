import time
import argparse
import asyncio
import uuid
import sys
import psutil
from collections import deque
from backend.contracts.observation import NetworkObservation

def generate_mock_observations(count: int, rate: int) -> list:
    """Generates synthetic NetworkObservations in memory for benchmarking."""
    print(f"Generating {count} mock observations in memory...")
    obs_list = []
    base_ts = int(time.time() * 1000)
    for i in range(count):
        obs = NetworkObservation(
            observation_id=str(uuid.uuid4()),
            timestamp=base_ts + i,
            sensor_id="benchmark_sensor",
            source_ip="192.168.1.100",
            destination_ip="10.0.0.1",
            source_port=50000 + (i % 10000),
            destination_port=443,
            protocol=6,
            flow_id=f"flow_{i}",
            first_seen=base_ts + i,
            last_seen=base_ts + i + 100,
            duration=0.1,
            packets=10,
            bytes=1500,
            src2dst_bytes=500,
            dst2src_bytes=1000,
            bidirectional_bytes=1500,
            bidirectional_packets=10
        )
        obs_list.append(obs)
    return obs_list

def run_streaming_benchmark(rate: int, duration_sec: int):
    try:
        from backend.streaming.kafka_adapter import KafkaObservationProducer
        producer = KafkaObservationProducer(bootstrap_servers="localhost:9092")
        if not producer.enabled:
            print("Kafka not available. Benchmark requires confluent_kafka and a running Redpanda/Kafka broker.")
            return
    except ImportError:
        print("confluent_kafka not installed.")
        return

    total_obs = rate * duration_sec
    observations = generate_mock_observations(total_obs, rate)
    
    print("=" * 60)
    print(f"P1 - STREAMING THROUGHPUT BENCHMARK (Target: {rate} flows/sec)")
    print("=" * 60)

    start_time = time.perf_counter()
    sent = 0
    
    # We send in bursts to simulate realistic batched ingress, bounded by the target rate
    batch_size = max(1, rate // 10)
    
    for i in range(0, total_obs, batch_size):
        batch = observations[i:i+batch_size]
        
        batch_start = time.perf_counter()
        for obs in batch:
            producer.produce(obs)
            sent += 1
            
        elapsed = time.perf_counter() - batch_start
        # Sleep to pace the sending to the target rate
        expected_time = len(batch) / rate
        if elapsed < expected_time:
            time.sleep(expected_time - elapsed)

    producer.flush()
    end_time = time.perf_counter()
    
    actual_duration = end_time - start_time
    actual_rate = sent / actual_duration
    
    print(f"Target Rate    : {rate} flows/sec")
    print(f"Actual Sent    : {sent}")
    print(f"Total Time     : {actual_duration:.2f} seconds")
    print(f"Actual Rate    : {actual_rate:.2f} flows/sec")
    
    if actual_rate < rate * 0.9:
        print(f"WARNING: System could not sustain target rate. Bottleneck reached.")
    else:
        print(f"SUCCESS: System sustained {rate} flows/sec through Kafka.")
        
    print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=int, default=1000, help="Target flows per second")
    parser.add_argument("--duration", type=int, default=10, help="Duration in seconds")
    args = parser.parse_args()
    
    run_streaming_benchmark(args.rate, args.duration)

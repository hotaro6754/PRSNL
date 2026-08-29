import os
import json
import time
import logging
from confluent_kafka import Consumer, Producer, KafkaException, KafkaError
from backend.ml.router import ModelRouter
from backend.ml.registry import ModelRegistry
from backend.ml.resolver import ModelResolver
from backend.schemas import MLPrediction
from backend.detectors.ddos import DDoSDetector
from backend.detectors.beacon import BeaconingDetector
from backend.detectors.dga import DGADetector
from backend.detectors.scan import PortScanDetector
from backend.detectors.brute_force import BruteForceDetector
from backend.detectors.tls_anomaly import TLSAnomalyDetector
from backend.detectors.exfil import ExfiltrationDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092")
TOPIC_FEATURES = "ml-feature-vectors"
TOPIC_PREDICTIONS = "ml-predictions"

class InferenceWorker:
    def __init__(self):
        self.registry = ModelRegistry()
        self.resolver = ModelResolver(self.registry, model_dir="models")
        self.router = ModelRouter(resolver=self.resolver)
        self.detectors = [
            DDoSDetector(),
            BeaconingDetector(),
            DGADetector(),
            PortScanDetector(),
            BruteForceDetector(),
            TLSAnomalyDetector(),
            ExfiltrationDetector()
        ]
        self.consumer = Consumer({
            'bootstrap.servers': KAFKA_BROKERS,
            'group.id': 'ml-inference-group',
            'auto.offset.reset': 'latest',
            'enable.auto.commit': False
        })
        self.producer = Producer({
            'bootstrap.servers': KAFKA_BROKERS,
            'client.id': 'ml-inference-worker'
        })
        
    def _delivery_report(self, err, msg):
        if err:
            logger.error(f"Failed to deliver prediction: {err}")

    def run(self):
        self.consumer.subscribe([TOPIC_FEATURES])
        logger.info(f"ML Inference Worker started. Listening on {TOPIC_FEATURES}")
        
        while True:
            msg = self.consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                logger.error(f"Kafka error: {msg.error()}")
                continue
                
            try:
                start_time = time.perf_counter()
                
                # Payload contains feature vector and observation context
                payload = json.loads(msg.value().decode('utf-8'))
                features = payload.get("features", {})
                context = payload.get("context", {})
                
                if not features:
                    continue
                    
                # The router actually requires NetworkObservation for context
                # For the worker, we can just pass the raw dict or reconstruct it
                from backend.schemas import NetworkObservation, FeatureVector
                obs = NetworkObservation(**context)
                
                try:
                    fv = FeatureVector(**features)
                except Exception as e:
                    logger.error(f"Failed to parse FeatureVector: {e}")
                    continue
                
                # Execute inference
                prediction = self.router.evaluate(fv, obs)
                
                latency_ms = (time.perf_counter() - start_time) * 1000
                
                if prediction:
                    prediction.inference_latency_ms = latency_ms
                    
                    self.producer.produce(
                        topic=TOPIC_PREDICTIONS,
                        key=obs.source_ip,
                        value=prediction.model_dump_json(),
                        on_delivery=self._delivery_report
                    )
                    self.producer.poll(0)
                    
                self.consumer.commit(asynchronous=True)
                
            except Exception as e:
                logger.error(f"Inference error: {e}", exc_info=True)

if __name__ == "__main__":
    worker = InferenceWorker()
    worker.run()

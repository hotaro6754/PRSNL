import json
import logging
import os
import time
from typing import Iterator, Optional
from confluent_kafka import Producer, Consumer, KafkaError, KafkaException

from backend.schemas import NetworkObservation

logger = logging.getLogger(__name__)

KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092")
TOPIC_OBSERVATIONS = os.getenv("KAFKA_TOPIC", "network-observations")
TOPIC_DLQ = f"{TOPIC_OBSERVATIONS}-dlq"
CONSUMER_GROUP = os.getenv("KAFKA_GROUP", "sih26145-ndr-group")

class KafkaObservationProducer:
    """Produces NetworkObservation messages to Kafka/Redpanda."""
    
    def __init__(self, brokers: str = KAFKA_BROKERS):
        self.brokers = brokers
        self.producer = Producer({
            'bootstrap.servers': self.brokers,
            'client.id': 'ndr-zeek-ingestor',
            'linger.ms': 5,
            'compression.type': 'lz4'
        })

    def _delivery_report(self, err, msg):
        if err is not None:
            logger.error(f"Kafka message delivery failed: {err}")
        else:
            pass # Delivered

    def publish(self, observation: NetworkObservation):
        try:
            self.producer.produce(
                topic=TOPIC_OBSERVATIONS,
                key=observation.source_ip,
                value=observation.model_dump_json(),
                on_delivery=self._delivery_report
            )
            self.producer.poll(0)
        except BufferError:
            logger.error("Kafka local producer queue is full. Waiting...")
            self.producer.poll(1)
            self.publish(observation)
            
    def flush(self):
        self.producer.flush()


class KafkaObservationConsumer:
    """Consumes NetworkObservation messages from Kafka/Redpanda."""
    
    def __init__(self, brokers: str = KAFKA_BROKERS, group_id: str = CONSUMER_GROUP):
        self.brokers = brokers
        self.group_id = group_id
        
        # Test if enabled (since in our lab environment Kafka might not be reachable)
        self.enabled = True
        
        self.consumer = Consumer({
            'bootstrap.servers': self.brokers,
            'group.id': self.group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,
        })
        
        self.dlq_producer = Producer({'bootstrap.servers': self.brokers})

    def _send_to_dlq(self, msg_value: bytes, error_reason: str):
        try:
            self.dlq_producer.produce(
                topic=TOPIC_DLQ,
                value=msg_value,
                headers={"error": error_reason.encode()}
            )
            self.dlq_producer.poll(0)
        except Exception as e:
            logger.error(f"Failed to write to DLQ: {e}")

    def consume(self) -> Iterator[NetworkObservation]:
        try:
            self.consumer.subscribe([TOPIC_OBSERVATIONS])
            logger.info(f"Subscribed to Kafka topic: {TOPIC_OBSERVATIONS}")
            
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                        logger.warning("Topic not available yet. Retrying...")
                        time.sleep(2)
                        continue
                    else:
                        raise KafkaException(msg.error())
                
                try:
                    data = json.loads(msg.value().decode('utf-8'))
                    obs = NetworkObservation(**data)
                    yield obs
                    self.consumer.commit(asynchronous=True)
                except Exception as e:
                    logger.error(f"Malformed message in Kafka: {e}")
                    self._send_to_dlq(msg.value(), str(e))
                    self.consumer.commit(asynchronous=True)
                    
        except KafkaException as e:
            logger.error(f"Kafka consumer error: {e}")
            self.enabled = False
        finally:
            self.consumer.close()

from abc import ABC, abstractmethod
from typing import Iterator
from backend.contracts.observation import NetworkObservation

class BaseIngestionAdapter(ABC):
    """
    Base contract for all passive telemetry ingestion sources.
    Adapters (Scapy, Zeek, Kafka, eBPF) must implement this and yield NetworkObservations.
    """
    
    @abstractmethod
    def consume(self, source: str) -> Iterator[NetworkObservation]:
        """
        Consume from a source (e.g. PCAP file, Kafka topic) and yield canonical NetworkObservations.
        """
        pass

# ENTERPRISE DEPLOYMENT

The Enterprise CyberOS stack is fully containerized using Docker Compose for simple on-premise or cloud deployments.

## Services
* rontend: Next.js Node application.
* ackend: Uvicorn FastAPI.
* ml-worker: Python Kafka Consumer utilizing XGBoost/Scikit-Learn.
* zeek: Network traffic observation.
* edpanda: High-throughput Kafka event bus.
* mongodb: Primary persistence layer.
* edis: Caching and Rate Limiting.

## Scaling
The architecture allows the ackend and ml-worker to scale horizontally. MongoDB provides document resilience, and Redpanda manages backpressure during traffic spikes.

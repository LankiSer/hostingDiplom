# Production Readiness

## Infrastructure Baseline

- PostgreSQL with persistent volume and healthchecks
- Redis with persistent volume and healthchecks
- Kafka in KRaft mode with healthchecks
- MinIO for object-like storage and deployment artifacts
- Private Docker Registry for pushed images
- Kafka UI for local event inspection

## Backend Conventions

- DTOs and response schemas stay in `schemas`
- Orchestration and retries stay in `services`
- File system and future object storage adapters stay isolated from HTTP handlers
- Kafka topic naming uses a topic prefix such as `platform.local`

## Deploy Service Expectations

- Detect runtime before build when possible
- Persist uploaded source or source references in a storage layer
- Retry I/O operations with bounded attempts and backoff
- Emit deployment lifecycle events for observability and audit trails

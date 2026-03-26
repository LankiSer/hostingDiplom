# Backend Services

Every platform capability is isolated in its own FastAPI service.

## Services

- `gateway-service`
- `auth-service`
- `user-service`
- `project-service`
- `deploy-service`
- `domain-service`
- `billing-service`
- `observability-service`

## Shared Conventions

- Each service is independently deployable.
- Each service contains `Dockerfile`, `pyproject.toml`, `.env.example`, and `src/main.py`.
- Each service exposes `/health` and `/api/v1/info`.
- Shared environment names stay consistent across services.
- DTO contracts live in `src/schemas/`, not in `main.py`.
- HTTP routers live in `src/api/`, while use-cases live in `src/services/`.
- Domain entities and repository abstractions are kept separate for DDD-friendly growth.
- Retry policy, event publishing, and file storage should live outside route handlers.
- Kafka topic naming should be prefixed per environment, for example `platform.local`.

## Growth Path

As each service grows, extend `src` with:

- `api/`
- `core/`
- `domain/`
- `repositories/`
- `services/`
- `schemas/`
- `events/`
- `tests/`

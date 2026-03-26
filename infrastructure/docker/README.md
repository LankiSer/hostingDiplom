# Docker Platform

Use Docker Compose for the first production-oriented platform baseline.

## Start

```bash
docker compose up -d
```

## Included Services

- `frontend`
- `nginx`
- `postgres`
- `redis`
- `kafka`
- `kafka-ui`
- `minio`
- `registry`
- `gateway-service`
- `auth-service`
- `user-service`
- `project-service`
- `deploy-service`
- `domain-service`
- `billing-service`
- `observability-service`

## Notes

- Frontend is served on `:3000`.
- Nginx exposes `dashboard.gcloude.ru`, `api.gcloude.ru`, and `*.apps.gcloude.ru`.
- Kafka UI is available on `:8080`.
- MinIO API is available on `:9000`, console on `:9001`.
- Local image registry is available on `:5000`.
- Docker Desktop or another running Docker daemon is required.

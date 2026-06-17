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

## Production (kostricyn.ru)

See [docs/deploy-kostricyn.ru.md](../../docs/deploy-kostricyn.ru.md) for DNS, SSL, and nginx reload on a VPS.

Quick start on server:

```bash
cd infrastructure/docker
cp .env.production.example .env.production
cd ../scripts
chmod +x *.sh
./deploy-production.sh
./issue-ssl.sh
```
- Nginx exposes `dashboard.gcloude.ru`, `api.gcloude.ru`, and `*.apps.gcloude.ru`.
- Kafka UI is available on `:8080`.
- MinIO API is available on `:9000`, console on `:9001`.
- Local image registry is available on `:5000`.
- Docker Desktop or another running Docker daemon is required.

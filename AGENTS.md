# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Scope and current state

- Monorepo for a Docker-first PaaS MVP: Nuxt frontend, FastAPI backend services, and infra assets for Docker Compose now and Kubernetes later.
- Existing `AGENTS.md` has been updated with validated commands and architecture details from source and docs.
- No `WARP.md`, `CLAUDE.md`, `.cursorrules`, `.cursor/rules`, or `.github/copilot-instructions.md` are present in this repository.

## Common commands

### Full platform locally (primary workflow)

Run from `infrastructure/docker`:

- Start full stack: `docker compose up -d`
- Rebuild and start selected core services: `docker compose up -d --build nginx frontend gateway-service auth-service postgres redis kafka`
- Stop stack: `docker compose down`
- Follow logs: `docker compose logs -f --tail=100 gateway-service auth-service nginx`

Local hostnames and entry points are documented in `docs/local-development.md`.

### Frontend (`frontend`)

- Install deps: `npm install`
- Dev server: `npm run dev`
- Build: `npm run build`
- Preview build: `npm run preview`
- Static generate (if needed): `npm run generate`

### Backend services (`backend/<service>`)

All services run with `uvicorn src.main:app --host 0.0.0.0 --port 8000`.

Per-service dependency install patterns used in Dockerfiles:

- `gateway-service`: `pip install -r requirements.txt`
- Other services: `pip install fastapi "uvicorn[standard]"` (plus `pydantic-settings` for `auth-service`)
- `tldraw-sync-service`: `pip install fastapi "uvicorn[standard]"` (plus `websockets`, `aiofiles`, `sqlalchemy`)

### Tests and linting

- No repo-level lint script is currently defined.
- No test suite is currently checked in.
- If adding pytest tests to backend services:
  - run all tests: `pytest`
  - run one test: `pytest tests/test_<module>.py::test_<name>`

## High-level architecture

### System shape

- `frontend/app`: Nuxt UI split by route pages (`pages`), feature modules (`common`), and shared app-level hooks/helpers (`shared`).
- `backend/*-service/src`: FastAPI services following a consistent layered layout (`api`, `core`, `domain`, `repositories`, `services`, `schemas`, `events`).
- `infrastructure/docker/docker-compose.yml`: authoritative local runtime topology and service wiring.

### Request and routing flow

- Nginx is the single ingress in the local stack.
- Frontend uses same-origin `/api` by default; `NUXT_PUBLIC_API_BASE_URL` can override base URL (`frontend/nuxt.config.ts`).
- Frontend auth state is cookie-based (`platform_session` via `frontend/app/middleware/auth.ts` and `frontend/app/middleware/guest.ts`).
- API wrapper `frontend/app/shared/app/hooks/use-platform-api.ts` injects `x-platform-email`, `x-platform-name`, and `x-platform-role` headers used by gateway RBAC-protected endpoints.

### Backend responsibilities (important for changes)

- `gateway-service` is the functional platform BFF and control plane entrypoint:
  - mounts platform, hosting, billing, and proxy routers;
  - proxies `/api/v1/auth/*` to `auth-service`;
  - initializes and migrates core Postgres tables at startup (`src/core/database.py`);
  - manages per-app nginx config generation/reload for hosted workloads.
- `gateway-service` owns durable platform entities in Postgres (`projects`, `applications`, `deployments`, `invoices`, `team_members`, `audit_logs`, `team_call_*`).
- `deploy-service` currently provides runtime detection + source-reference persistence + event publication flow, but repository/storage are still MVP-style scaffolding (static deployment IDs and file-backed source reference writes).
- Other services expose contract-shaped endpoints and service layers but are comparatively thin versus gateway in current implementation.

## Key docs and files to read before major edits

- `docs/local-development.md`
- `docs/architecture/overview.md`
- `docs/architecture/deploy-flow.md`
- `docs/architecture/api-contracts.md`
- `docs/architecture/production-readiness.md`
- `docs/architecture/adr/001-docker-first-kubernetes-later.md`
- `infrastructure/docker/docker-compose.yml`
- `backend/gateway-service/src/main.py`
- `backend/gateway-service/src/core/database.py`
- `frontend/app/shared/app/hooks/use-platform-api.ts`

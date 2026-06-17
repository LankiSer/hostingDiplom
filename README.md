# PaaS Monorepo

Monorepo for a microservice hosting platform with:

- `frontend` on Nuxt 4 + TypeScript;
- `backend` with FastAPI microservices;
- `infrastructure` for Docker Compose, Nginx, and Kubernetes;
- `docs` for architecture decisions and API conventions;
- `packages` for shared contracts and reusable tooling.

## Directories

- `frontend` — dashboard and operator UI.
- `backend` — platform microservices.
- `infrastructure` — local and production deployment assets.
- `docs` — architecture and decisions.
- `packages` — shared contracts and future SDK packages.

## Delivery Strategy

1. Build the MVP on Docker Compose.
2. Support Node.js and Python user workloads first.
3. Add billing and 1C integration for legal entities.
4. Move runtime orchestration to Kubernetes after MVP stabilizes.

## 1C Integration (file exchange)

Billing invoices can be exported to JSON and imported into 1C without a web server.
See `docs/onec-file-import.md` for the external processing setup.

## Production (VPS)

From the repo root on the server (e.g. `/opt/hosting`):

```bash
# После копирования с Windows — запускайте через bash:
bash setup.sh

# Или если уже Unix-формат:
chmod +x setup.sh && ./setup.sh
```

See `docs/deploy-kostricyn.ru.md` for DNS, SSL, and Git deploy details.

## Local Demo

Use `nginx` as the single local entry point and map `dashboard.gcloude.local`,
`api.gcloude.local`, `crm.apps.gcloude.local`, and `bot.apps.gcloude.local` in
your `hosts` file. Local instructions are documented in `docs/local-development.md`.

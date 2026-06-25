---
inclusion: always
---

# Monorepo Standards

- Keep `frontend`, `backend`, `infrastructure`, `docs`, and `packages` cleanly separated.
- Prefer MVP-friendly decisions first, but leave an explicit path to Kubernetes scale-out.
- Do not mix business logic with infra adapters or transport code.
- Keep naming explicit: `*-service` for backend services, `common/shared` for frontend modules.
- Add docs or ADR updates when introducing an architectural decision.

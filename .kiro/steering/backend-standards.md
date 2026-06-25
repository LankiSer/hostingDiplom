---
inclusion: fileMatch
fileMatchPattern: ['backend/**/*.py']
---

# Backend Standards

- Use one uniform structure for all services: API, config, domain, repositories, services, schemas, events, tests.
- Keep each microservice independently deployable with its own `Dockerfile`, `pyproject.toml`, and `.env.example`.
- Use FastAPI for HTTP boundaries and keep business logic isolated from HTTP handlers.
- Expose `/health` and `/api/v1/info` in every service.
- Keep service names explicit and aligned with product capability, for example `deploy-service`.

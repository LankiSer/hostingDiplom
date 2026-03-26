# API Contracts

## Auth Service

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/register-organization`

## User Service

- `GET /api/v1/users`
- `POST /api/v1/users`

## Project Service

- `GET /api/v1/projects`
- `POST /api/v1/projects`
- `POST /api/v1/microservices`

## Deploy Service

- `POST /api/v1/deployments/detect-runtime`
- `POST /api/v1/deployments`
- `GET /api/v1/deployments/{deployment_id}`

## Domain Service

- `POST /api/v1/domains/assign`
- `GET /api/v1/domains/{service_name}/ssl`
- `GET /api/v1/domains/wildcard`

## Billing Service

- `POST /api/v1/invoices`
- `GET /api/v1/invoices/{invoice_id}`

## Observability Service

- `GET /api/v1/events`
- `GET /api/v1/logs/{service_name}`

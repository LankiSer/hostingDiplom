# Architecture Overview

## Product Goal

The platform hosts customer microservices behind managed subdomains with SSL,
deployment automation, billing, and observability.

## Main Layers

- `frontend` provides one Nuxt dashboard for operators and customers.
- `backend` provides platform APIs and internal orchestration services.
- `infrastructure` contains local Docker and production Kubernetes assets.

## MVP Services

- `gateway-service`
- `auth-service`
- `user-service`
- `project-service`
- `deploy-service`
- `domain-service`
- `billing-service`
- `observability-service`

## Runtime Strategy

MVP uses Docker Compose for local orchestration and Docker-based user service
deployment. The second phase moves runtime orchestration to Kubernetes with
Ingress, `cert-manager`, registry-backed images, and autoscaling.

## Critical Flow

1. Organization authenticates in the dashboard.
2. User creates a project and a microservice.
3. Deploy service builds a Node.js or Python image.
4. Domain service assigns a subdomain and SSL strategy.
5. Observability stores deployment status and logs.
6. Billing issues an invoice and syncs it with 1C.

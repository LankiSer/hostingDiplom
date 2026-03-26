# ADR 001: Docker First, Kubernetes Later

## Status

Accepted.

## Context

The platform needs to support fast delivery of an MVP for hosting customer
microservices with managed subdomains, SSL, and billing. Kubernetes is a valid
target architecture, but it increases initial infrastructure complexity.

## Decision

We start with Docker Compose and Docker-based deployment for the MVP. After the
critical flow is stable, we introduce Kubernetes for scaling, ingress, and
runtime orchestration.

## Consequences

- Faster MVP delivery.
- Easier local development for all platform services.
- Clear migration path to registry-backed Kubernetes deployments.
- Some runtime logic will be rewritten later in `deploy-service`.

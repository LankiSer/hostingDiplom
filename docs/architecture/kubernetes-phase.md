# Kubernetes Phase

## Trigger for Migration

Move to Kubernetes when you need replica scaling, safer rollouts, isolated
customer workloads, or multiple worker nodes.

## Required Components

- NGINX Ingress Controller
- `cert-manager`
- `metrics-server`
- container registry
- HPA for hosted customer services

## Migration Order

1. Build and push images to a private registry.
2. Deploy platform services into the `platform` namespace.
3. Switch domain routing from host Nginx rules to Kubernetes Ingress.
4. Issue wildcard and service TLS certificates through `cert-manager`.
5. Enable autoscaling for customer workloads with HPA.

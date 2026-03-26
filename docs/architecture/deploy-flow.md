# Deploy Flow

## MVP Flow

1. `auth-service` authenticates the organization.
2. `project-service` creates the project and target microservice record.
3. `deploy-service` receives runtime and repository metadata.
4. `deploy-service` builds a Node.js or Python container image.
5. `domain-service` assigns `*.apps.gcloude.ru` routing metadata.
6. `observability-service` stores deployment and domain events.
7. `billing-service` issues an invoice and syncs it with 1C.

## Runtime Detection

- If the uploaded code contains `package.json`, treat it as Node.js.
- If it contains `requirements.txt` or `pyproject.toml`, treat it as Python.

## Output of a Successful Deploy

- deployment id
- target runtime
- assigned subdomain
- SSL strategy
- event trail for logs and auditing

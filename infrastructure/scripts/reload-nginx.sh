#!/usr/bin/env bash
# Hot reload nginx inside Docker (after new app subdomain config is written).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_DIR="$(cd "$SCRIPT_DIR/../docker" && pwd)"

cd "$COMPOSE_DIR"

if [[ -f .env.production ]]; then
  # shellcheck disable=SC1091
  source .env.production
fi

compose_args=( -f docker-compose.yml -f docker-compose.prod.yml )
if [[ "${HOST_NGINX_MODE:-false}" == "true" ]] || { command -v ss >/dev/null 2>&1 && ss -H -tln "sport = :80" 2>/dev/null | grep -q .; }; then
  compose_args+=( -f docker-compose.host-nginx.yml )
else
  compose_args+=( -f docker-compose.publish.yml )
fi
compose_args+=( --env-file .env.production )

if docker compose version >/dev/null 2>&1; then
  NGINX_CONTAINER="$(docker compose "${compose_args[@]}" ps -q nginx 2>/dev/null || true)"
elif command -v docker-compose >/dev/null 2>&1; then
  NGINX_CONTAINER="$(docker-compose "${compose_args[@]}" ps -q nginx 2>/dev/null || true)"
else
  NGINX_CONTAINER=""
fi
if [[ -z "$NGINX_CONTAINER" ]]; then
  NGINX_CONTAINER="$(docker ps -q -f 'name=nginx' | head -1)"
fi

if [[ -z "$NGINX_CONTAINER" ]]; then
  echo "nginx container not found" >&2
  exit 1
fi

echo "Testing nginx config..."
docker exec "$NGINX_CONTAINER" nginx -t

echo "Reloading nginx..."
docker exec "$NGINX_CONTAINER" nginx -s reload

echo "Done."

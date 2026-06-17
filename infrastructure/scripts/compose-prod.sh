#!/usr/bin/env bash
# Production docker compose wrapper (selects host-nginx vs publish port overlay).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_DIR="$(cd "$SCRIPT_DIR/../docker" && pwd)"

tcp_port_busy() {
  local port="$1"
  if command -v ss >/dev/null 2>&1; then
    ss -H -tln "sport = :${port}" 2>/dev/null | grep -q .
  elif command -v netstat >/dev/null 2>&1; then
    netstat -tln 2>/dev/null | grep -q ":${port} "
  else
    return 1
  fi
}

cd "$COMPOSE_DIR"

args=( -f docker-compose.yml -f docker-compose.prod.yml )
if [[ -f .env.production ]]; then
  # shellcheck disable=SC1091
  source .env.production
fi
if [[ "${HOST_NGINX_MODE:-false}" == "true" ]] || tcp_port_busy 80; then
  args+=( -f docker-compose.host-nginx.yml )
else
  args+=( -f docker-compose.publish.yml )
fi
args+=( --env-file .env.production )

if docker compose version >/dev/null 2>&1; then
  exec docker compose "${args[@]}" "$@"
elif command -v docker-compose >/dev/null 2>&1; then
  exec docker-compose "${args[@]}" "$@"
fi

echo "docker compose not found" >&2
exit 1

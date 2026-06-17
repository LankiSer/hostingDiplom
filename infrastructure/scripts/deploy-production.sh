#!/usr/bin/env bash
# Full production deploy on a Linux VPS.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
COMPOSE_DIR="$REPO_ROOT/infrastructure/docker"

cd "$COMPOSE_DIR"

if [[ ! -f .env.production ]]; then
  cp .env.production.example .env.production
  echo "Created .env.production — edit passwords and CERTBOT_EMAIL, then re-run."
  exit 1
fi

# shellcheck disable=SC1091
source .env.production

echo "==> Building and starting platform (including auth-service)..."
"$SCRIPT_DIR/compose-prod.sh" up -d --build \
  nginx frontend gateway-service auth-service postgres redis kafka

echo ""
echo "Stack is up (HTTP mode if NGINX_CONFIG=nginx.http.conf)."
echo "Next: run infrastructure/scripts/issue-ssl.sh for free SSL + HTTPS nginx."

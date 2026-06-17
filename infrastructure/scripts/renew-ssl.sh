#!/usr/bin/env bash
# Renew Let's Encrypt certificates and reload nginx (add to cron: 0 3 * * *).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_DIR="$(cd "$SCRIPT_DIR/../docker" && pwd)"

cd "$COMPOSE_DIR"

docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.production \
  --profile certbot run --rm certbot renew --quiet

"$SCRIPT_DIR/reload-nginx.sh"
echo "Certificates renewed."

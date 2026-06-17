#!/usr/bin/env bash
# Manually issue SSL for one app subdomain (if auto-issue failed).
# Usage: ./issue-app-ssl.sh myweb
set -euo pipefail

SLUG="${1:?Usage: $0 <app-slug>}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_DIR="$(cd "$SCRIPT_DIR/../docker" && pwd)"
cd "$COMPOSE_DIR"

# shellcheck disable=SC1091
source .env.production

DOMAIN="${BASE_DOMAIN:-kostricyn.ru}"
HOSTNAME="${SLUG}.apps.${DOMAIN}"
EMAIL="${CERTBOT_EMAIL:-admin@${DOMAIN}}"

echo "Issuing certificate for ${HOSTNAME}..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.production \
  --profile certbot run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  --email "$EMAIL" \
  --agree-tos --no-eff-email --non-interactive \
  -d "$HOSTNAME" \
  --cert-name "$HOSTNAME"

echo "Reload nginx and redeploy app from cabinet to apply HTTPS config, or run reload-nginx.sh"
"$SCRIPT_DIR/reload-nginx.sh"

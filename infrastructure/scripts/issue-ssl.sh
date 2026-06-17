#!/usr/bin/env bash
# Issue Let's Encrypt for platform (app + api). Each app subdomain gets its own cert on deploy.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_DIR="$(cd "$SCRIPT_DIR/../docker" && pwd)"

cd "$COMPOSE_DIR"

if [[ ! -f .env.production ]]; then
  echo "Create .env.production from .env.production.example first." >&2
  exit 1
fi

# shellcheck disable=SC1091
source .env.production

EMAIL="${CERTBOT_EMAIL:-admin@${BASE_DOMAIN}}"
DOMAIN="${BASE_DOMAIN:-kostricyn.ru}"

echo "==> Step 1: HTTP nginx"
export NGINX_CONFIG=nginx.http.conf
export NGINX_SSL_ENABLED=false
export SSL_AUTO_ISSUE=false
"$SCRIPT_DIR/compose-prod.sh" up -d nginx frontend gateway-service auth-service postgres redis kafka

echo "==> Step 2: SSL for app.${DOMAIN} and api.${DOMAIN}"
"$SCRIPT_DIR/compose-prod.sh" \
  --profile certbot run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  --email "$EMAIL" \
  --agree-tos --no-eff-email \
  -d "app.${DOMAIN}" \
  -d "api.${DOMAIN}" \
  --cert-name "${DOMAIN}"

echo "==> Step 3: Enable HTTPS nginx + auto SSL per app on deploy"
if grep -q '^NGINX_CONFIG=' .env.production; then
  sed -i.bak 's/^NGINX_CONFIG=.*/NGINX_CONFIG=nginx.https.conf/' .env.production
else
  echo 'NGINX_CONFIG=nginx.https.conf' >> .env.production
fi
if grep -q '^NGINX_SSL_ENABLED=' .env.production; then
  sed -i.bak 's/^NGINX_SSL_ENABLED=.*/NGINX_SSL_ENABLED=true/' .env.production
else
  echo 'NGINX_SSL_ENABLED=true' >> .env.production
fi
if grep -q '^SSL_AUTO_ISSUE=' .env.production; then
  sed -i.bak 's/^SSL_AUTO_ISSUE=.*/SSL_AUTO_ISSUE=true/' .env.production
else
  echo 'SSL_AUTO_ISSUE=true' >> .env.production
fi

"$SCRIPT_DIR/compose-prod.sh" up -d nginx gateway-service
"$SCRIPT_DIR/reload-nginx.sh"

echo ""
echo "Platform SSL ready."
echo "  Cabinet:  https://app.${DOMAIN}"
echo "  API:      https://api.${DOMAIN}"
echo ""
echo "For each deployed app (e.g. myweb.apps.${DOMAIN}):"
echo "  1. Add DNS A-record: myweb.apps.${DOMAIN} -> server IP"
echo "  2. Deploy from cabinet — certbot runs automatically"
echo "  3. nginx reloads with https://myweb.apps.${DOMAIN}"

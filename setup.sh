#!/usr/bin/env bash
#
# gcloude platform — установка и запуск с корня репозитория.
#
# Скопировали папку с Windows (zip/scp)? Запускайте так:
#   cd /opt/hosting
#   bash setup.sh
#
#   cd /opt/hosting
#   chmod +x setup.sh
#   ./setup.sh              # первый запуск: env + сборка + HTTP (+ SSL если DNS готов)
#
# Переменные (опционально):
#   BASE_DOMAIN=kostricyn.ru ./setup.sh
#
# Если файл приехал с CRLF (Windows), скрипт сам поправит переводы строк.
if grep -q $'\r' "${BASH_SOURCE[0]}" 2>/dev/null; then
  sed -i 's/\r$//' "${BASH_SOURCE[0]}" 2>/dev/null || true
  exec /usr/bin/env bash "${BASH_SOURCE[0]}" "$@"
fi

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_DIR="$ROOT_DIR/infrastructure/docker"
SCRIPTS_DIR="$ROOT_DIR/infrastructure/scripts"
ENV_FILE="$COMPOSE_DIR/.env.production"
ENV_EXAMPLE="$COMPOSE_DIR/.env.production.example"
DEFAULT_CERTBOT_EMAIL="kostricyn50@mail.ru"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}==>${NC} $*"; }
warn()  { echo -e "${YELLOW}!!${NC} $*"; }
error() { echo -e "${RED}ERROR:${NC} $*" >&2; }

compose() {
  local args=( -f docker-compose.yml -f docker-compose.prod.yml )
  cd "$COMPOSE_DIR"
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
    docker compose "${args[@]}" "$@"
  elif command -v docker-compose >/dev/null 2>&1; then
    docker-compose "${args[@]}" "$@"
  else
    error "docker compose не найден. Перезапустите: bash setup.sh"
    exit 1
  fi
}

has_compose() {
  docker compose version >/dev/null 2>&1 || command -v docker-compose >/dev/null 2>&1
}

ensure_system_packages() {
  if ! command -v apt-get >/dev/null 2>&1; then
    warn "apt-get не найден — пропускаю установку пакетов (не Debian/Ubuntu?)"
    return 0
  fi
  info "Обновление apt и базовые пакеты (curl, git)..."
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq
  apt-get install -y -qq curl ca-certificates gnupg lsb-release git
}

install_compose_plugin() {
  local arch_name plugin_dir="/usr/local/lib/docker/cli-plugins"
  case "$(uname -m)" in
    x86_64|amd64) arch_name="x86_64" ;;
    aarch64|arm64) arch_name="aarch64" ;;
    *) arch_name="x86_64" ;;
  esac
  mkdir -p "$plugin_dir"
  info "Скачиваю Docker Compose plugin..."
  curl -fsSL "https://github.com/docker/compose/releases/download/v2.29.7/docker-compose-linux-${arch_name}" \
    -o "${plugin_dir}/docker-compose"
  chmod +x "${plugin_dir}/docker-compose"
}

ensure_docker() {
  if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1 && has_compose; then
    info "Docker уже установлен: $(docker --version)"
    return 0
  fi

  if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
    error "Для автоматической установки Docker нужен root:"
    error "  sudo bash setup.sh"
    exit 1
  fi

  info "Docker не найден — устанавливаю автоматически..."
  ensure_system_packages

  if curl -fsSL https://get.docker.com -o /tmp/get-docker.sh; then
    info "Запуск официального установщика Docker..."
    sh /tmp/get-docker.sh
    rm -f /tmp/get-docker.sh
  else
    warn "get.docker.com недоступен — пробую apt install docker.io..."
    apt-get install -y docker.io
  fi

  if ! has_compose; then
    install_compose_plugin
  fi

  if command -v systemctl >/dev/null 2>&1; then
    systemctl enable docker >/dev/null 2>&1 || true
    systemctl start docker >/dev/null 2>&1 || true
  else
    service docker start >/dev/null 2>&1 || true
  fi

  sleep 2

  if ! command -v docker >/dev/null 2>&1 || ! docker info >/dev/null 2>&1; then
    error "Docker установлен, но daemon не отвечает."
    error "Проверьте: systemctl status docker && journalctl -u docker --no-pager -n 30"
    exit 1
  fi

  if ! has_compose; then
    error "Docker Compose не найден после установки."
    exit 1
  fi

  info "Готово: $(docker --version), $(docker compose version 2>/dev/null || docker-compose --version)"
}

require_root_layout() {
  if [[ ! -d "$COMPOSE_DIR" ]] || [[ ! -f "$COMPOSE_DIR/docker-compose.yml" ]]; then
    error "Запускайте из корня репозитория (где лежат frontend/, backend/, infrastructure/)."
    error "Ожидался каталог: $COMPOSE_DIR"
    exit 1
  fi
}

fix_crlf_in_file() {
  local file="$1"
  if [[ -f "$file" ]] && grep -q $'\r' "$file" 2>/dev/null; then
    sed -i 's/\r$//' "$file"
    return 0
  fi
  return 1
}

fix_windows_transfer() {
  info "Проверка файлов после переноса с Windows (CRLF → LF)..."
  local count=0

  while IFS= read -r -d '' file; do
    if fix_crlf_in_file "$file"; then
      count=$((count + 1))
    fi
    chmod +x "$file" 2>/dev/null || true
  done < <(find "$ROOT_DIR" -type f -name '*.sh' \
    ! -path '*/node_modules/*' \
    ! -path '*/.git/*' \
    ! -path '*/.output/*' \
    -print0 2>/dev/null)

  for env_file in "$ENV_FILE" "$ENV_EXAMPLE"; do
    if fix_crlf_in_file "$env_file"; then
      count=$((count + 1))
    fi
  done

  if [[ $count -gt 0 ]]; then
    info "Исправлено файлов: $count"
  else
    info "Переводы строк в порядке (Unix LF)"
  fi
}

random_secret() {
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -hex 16
  else
    date +%s | sha256sum | head -c 32
  fi
}

set_env_var() {
  local key="$1"
  local value="$2"
  local file="$ENV_FILE"
  if grep -q "^${key}=" "$file" 2>/dev/null; then
    sed -i.bak "s|^${key}=.*|${key}=${value}|" "$file"
  else
    echo "${key}=${value}" >> "$file"
  fi
}

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

publish_host_port() {
  local publish="${1:-80}"
  if [[ "$publish" == *:* ]]; then
    echo "${publish##*:}"
  else
    echo "$publish"
  fi
}

configure_port_coexistence() {
  # shellcheck disable=SC1091
  source "$ENV_FILE"

  local changed=false
  local http_pub="${PLATFORM_HTTP_PUBLISH:-80}"
  local https_pub="${PLATFORM_HTTPS_PUBLISH:-443}"
  local http_host_port https_host_port

  http_host_port="$(publish_host_port "$http_pub")"
  https_host_port="$(publish_host_port "$https_pub")"

  if tcp_port_busy "$http_host_port" && [[ "$http_pub" == "80" || "$http_pub" == "0.0.0.0:80" ]]; then
    warn "Порт 80 занят (внешний nginx?) — platform nginx будет на 127.0.0.1:8080"
    set_env_var "PLATFORM_HTTP_PUBLISH" "127.0.0.1:8080"
    set_env_var "HOST_NGINX_MODE" "true"
    changed=true
  fi

  if tcp_port_busy "$https_host_port" && [[ "$https_pub" == "443" || "$https_pub" == "0.0.0.0:443" ]]; then
    warn "Порт 443 занят — platform nginx HTTPS будет на 127.0.0.1:8443"
    set_env_var "PLATFORM_HTTPS_PUBLISH" "127.0.0.1:8443"
    set_env_var "HOST_NGINX_MODE" "true"
    changed=true
  fi

  if [[ "$changed" == true ]]; then
    # shellcheck disable=SC1091
    source "$ENV_FILE"
    warn "Проксируйте app/api/apps.* с внешнего nginx → platform (bash setup.sh host-nginx)"
  fi
}

platform_local_url() {
  # shellcheck disable=SC1091
  source "$ENV_FILE"
  local pub="${PLATFORM_HTTP_PUBLISH:-80}"
  if [[ "$pub" == *:* ]]; then
    echo "http://${pub}"
  else
    echo "http://127.0.0.1:${pub}"
  fi
}

platform_http_port() {
  # shellcheck disable=SC1091
  source "$ENV_FILE"
  publish_host_port "${PLATFORM_HTTP_PUBLISH:-8080}"
}

platform_https_port() {
  # shellcheck disable=SC1091
  source "$ENV_FILE"
  publish_host_port "${PLATFORM_HTTPS_PUBLISH:-8443}"
}

host_cert_exists() {
  local domain="$1"
  # shellcheck disable=SC1091
  source "$ENV_FILE"
  local le="${LETSENCRYPT_HOST:-$ROOT_DIR/runtime/letsencrypt}"
  [[ -f "${le}/live/${domain}/fullchain.pem" && -f "${le}/live/${domain}/privkey.pem" ]]
}

install_host_nginx_for_ssl() {
  local domain="$1"
  local with_https="${2:-auto}"
  # shellcheck disable=SC1091
  source "$ENV_FILE"

  local webroot="${CERTBOT_WEBROOT_HOST:-$ROOT_DIR/runtime/certbot-webroot}"
  local le="${LETSENCRYPT_HOST:-$ROOT_DIR/runtime/letsencrypt}"
  local port https_port
  port="$(platform_http_port)"
  https_port="$(platform_https_port)"
  local domain_escaped="${domain//./\\.}"
  local generated_dir="$ROOT_DIR/infrastructure/nginx/generated"
  local generated="$generated_dir/gcloude-host-${domain}.conf"
  local target="/etc/nginx/sites-available/gcloude-${domain}.conf"
  local enabled="/etc/nginx/sites-enabled/gcloude-${domain}.conf"

  if [[ "$with_https" == "auto" ]]; then
    if host_cert_exists "$domain"; then
      with_https=true
    else
      with_https=false
    fi
  fi

  mkdir -p "$generated_dir"

  cat > "$generated" <<NGINX
# gcloude platform — внешний nginx (ACME + HTTPS + прокси в Docker)
# Generated by setup.sh — re-run: bash setup.sh host-nginx

server {
    listen 80;
    server_name app.${domain} api.${domain};

    location /.well-known/acme-challenge/ {
        root ${webroot};
        default_type text/plain;
        try_files \$uri =404;
    }

    location / {
NGINX

  if [[ "$with_https" == "true" ]]; then
    cat >> "$generated" <<NGINX
        return 301 https://\$host\$request_uri;
NGINX
  else
    cat >> "$generated" <<NGINX
        proxy_pass http://127.0.0.1:${port};
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
NGINX
  fi

  cat >> "$generated" <<NGINX
    }
}

server {
    listen 80;
    server_name ~^.+\.apps\.${domain_escaped}\$;

    location /.well-known/acme-challenge/ {
        root ${webroot};
        default_type text/plain;
        try_files \$uri =404;
    }

    location / {
        proxy_pass http://127.0.0.1:${port};
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
NGINX

  if [[ "$with_https" == "true" ]]; then
    cat >> "$generated" <<NGINX

server {
    listen 443 ssl;
    http2 on;
    server_name app.${domain};

    ssl_certificate     ${le}/live/${domain}/fullchain.pem;
    ssl_certificate_key ${le}/live/${domain}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://127.0.0.1:${port};
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}

server {
    listen 443 ssl;
    http2 on;
    server_name api.${domain};

    ssl_certificate     ${le}/live/${domain}/fullchain.pem;
    ssl_certificate_key ${le}/live/${domain}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://127.0.0.1:${port};
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}

# Приложения (*.apps): TLS на platform nginx (127.0.0.1:${https_port})
server {
    listen 443 ssl;
    http2 on;
    server_name ~^.+\.apps\.${domain_escaped}\$;

    ssl_certificate     ${le}/live/${domain}/fullchain.pem;
    ssl_certificate_key ${le}/live/${domain}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass https://127.0.0.1:${https_port};
        proxy_ssl_server_name on;
        proxy_ssl_verify off;
        proxy_ssl_name \$host;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
NGINX
  fi

  if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
    warn "Нужен root для /etc/nginx — шаблон сохранён: $generated"
    return 1
  fi

  if ! command -v nginx >/dev/null 2>&1; then
    warn "nginx на хосте не найден — шаблон: $generated"
    return 1
  fi

  cp "$generated" "$target"
  ln -sf "$target" "$enabled"
  info "Конфиг внешнего nginx: $target"

  if nginx -t; then
    systemctl reload nginx 2>/dev/null || service nginx reload 2>/dev/null || nginx -s reload
    info "Внешний nginx перезагружен"
  else
    error "nginx -t не прошёл — проверьте $target"
    return 1
  fi
}

ensure_runtime_dirs() {
  # shellcheck disable=SC1091
  source "$ENV_FILE"
  local webroot="${CERTBOT_WEBROOT_HOST:-$ROOT_DIR/runtime/certbot-webroot}"
  local le="${LETSENCRYPT_HOST:-$ROOT_DIR/runtime/letsencrypt}"
  mkdir -p "${webroot}/.well-known/acme-challenge" "$le"
  chmod 755 "$webroot" "${webroot}/.well-known" "${webroot}/.well-known/acme-challenge" 2>/dev/null || true
}

verify_platform_nginx() {
  # shellcheck disable=SC1091
  source "$ENV_FILE"
  local domain="${BASE_DOMAIN:-kostricyn.ru}"
  local port=8080
  local cid published i

  if [[ "${HOST_NGINX_MODE:-false}" != "true" ]] && ! tcp_port_busy 80; then
    port="$(publish_host_port "${PLATFORM_HTTP_PUBLISH:-80}")"
  fi

  for i in 1 2 3 4 5; do
    cid="$(compose ps -q nginx 2>/dev/null | head -1 || true)"
    if [[ -n "$cid" ]]; then
      published="$(docker port "$cid" 80 2>/dev/null | head -1 || true)"
      if [[ -n "$published" ]]; then
        break
      fi
    fi
    if [[ "$i" -eq 1 ]]; then
      warn "Docker nginx не проброшен на хост — пересоздаю с docker-compose.host-nginx.yml"
      set_env_var "HOST_NGINX_MODE" "true"
      set_env_var "PLATFORM_HTTP_PUBLISH" "127.0.0.1:8080"
      set_env_var "PLATFORM_HTTPS_PUBLISH" "127.0.0.1:8443"
      # shellcheck disable=SC1091
      source "$ENV_FILE"
      compose up -d --force-recreate --no-deps nginx
    fi
    sleep 2
  done

  published="$(docker port "${cid:-none}" 80 2>/dev/null | head -1 || true)"
  if [[ -z "$published" ]]; then
    error "nginx всё ещё без проброса порта. Проверьте:"
    error "  cd $COMPOSE_DIR && docker compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.host-nginx.yml config | grep -A6 'nginx:'"
    return 1
  fi
  info "Docker nginx: ${published} -> 80/tcp"

  for i in 1 2 3 4 5; do
    if curl -sf --connect-timeout 3 -H "Host: app.${domain}" "http://127.0.0.1:${port}/" -o /dev/null; then
      info "Platform nginx OK на 127.0.0.1:${port}"
      return 0
    fi
    sleep 2
  done

  warn "Platform nginx не отвечает на 127.0.0.1:${port}"
  compose logs --tail=30 nginx 2>/dev/null || true
  return 1
}

verify_acme_http() {
  local domain="$1"
  # shellcheck disable=SC1091
  source "$ENV_FILE"
  local webroot="${CERTBOT_WEBROOT_HOST:-$ROOT_DIR/runtime/certbot-webroot}"
  local token="gcloude-setup-test"
  local content="acme-ok"
  local host code body

  mkdir -p "${webroot}/.well-known/acme-challenge"
  echo -n "$content" > "${webroot}/.well-known/acme-challenge/${token}"

  for host in "app.${domain}" "api.${domain}"; do
    code="$(curl -s -o /tmp/gcloude-acme-test -w '%{http_code}' --connect-timeout 8 "http://${host}/.well-known/acme-challenge/${token}" 2>/dev/null || echo "000")"
    body="$(tr -d '\r\n' < /tmp/gcloude-acme-test 2>/dev/null || true)"
    if [[ "$code" != "200" ]] || [[ "$body" != "$content" ]]; then
      warn "ACME probe ${host} → HTTP ${code} (нужен 200 и тело '${content}')"
      rm -f "${webroot}/.well-known/acme-challenge/${token}" /tmp/gcloude-acme-test
      return 1
    fi
    info "ACME probe ${host} → OK"
  done

  rm -f "${webroot}/.well-known/acme-challenge/${token}" /tmp/gcloude-acme-test
  return 0
}

prepare_ssl_host_nginx() {
  local domain="$1"
  # shellcheck disable=SC1091
  source "$ENV_FILE"

  ensure_runtime_dirs

  if tcp_port_busy 80; then
    set_env_var "HOST_NGINX_MODE" "true"
    # shellcheck disable=SC1091
    source "$ENV_FILE"
    info "Порт 80 занят — настраиваю внешний nginx для ACME + прокси на platform..."
    install_host_nginx_for_ssl "$domain"
    verify_acme_http "$domain"
    return $?
  fi

  return 0
}

init_env() {
  if [[ ! -f "$ENV_FILE" ]]; then
    info "Создаю $ENV_FILE из примера..."
    cp "$ENV_EXAMPLE" "$ENV_FILE"
  fi

  # shellcheck disable=SC1091
  source "$ENV_FILE"

  local changed=false

  if [[ -n "${BASE_DOMAIN:-}" ]] && [[ "${BASE_DOMAIN}" != "kostricyn.ru" ]]; then
    :
  elif [[ -n "${SETUP_BASE_DOMAIN:-}" ]]; then
    set_env_var "BASE_DOMAIN" "$SETUP_BASE_DOMAIN"
    changed=true
  fi

  # shellcheck disable=SC1091
  source "$ENV_FILE"
  local domain="${BASE_DOMAIN:-kostricyn.ru}"

  if [[ "${POSTGRES_PASSWORD:-change-me-strong-password}" == "change-me-strong-password" ]]; then
    set_env_var "POSTGRES_PASSWORD" "$(random_secret)"
    changed=true
    info "Сгенерирован POSTGRES_PASSWORD"
  fi

  if [[ "${MINIO_ROOT_PASSWORD:-change-me-minio-password}" == "change-me-minio-password" ]]; then
    set_env_var "MINIO_ROOT_PASSWORD" "$(random_secret)"
    changed=true
    info "Сгенерирован MINIO_ROOT_PASSWORD"
  fi

  if [[ -z "${CERTBOT_EMAIL:-}" ]] || [[ "${CERTBOT_EMAIL}" == "admin@kostricyn.ru" ]]; then
    if [[ -n "${SETUP_CERTBOT_EMAIL:-}" ]]; then
      set_env_var "CERTBOT_EMAIL" "$SETUP_CERTBOT_EMAIL"
      changed=true
    else
      set_env_var "CERTBOT_EMAIL" "$DEFAULT_CERTBOT_EMAIL"
      changed=true
    fi
  fi

  if ! grep -q "^PLATFORM_HTTP_PUBLISH=" "$ENV_FILE" 2>/dev/null; then
    set_env_var "PLATFORM_HTTP_PUBLISH" "80"
    changed=true
  fi
  if ! grep -q "^PLATFORM_HTTPS_PUBLISH=" "$ENV_FILE" 2>/dev/null; then
    set_env_var "PLATFORM_HTTPS_PUBLISH" "443"
    changed=true
  fi

  if ! grep -q "^CERTBOT_WEBROOT_HOST=" "$ENV_FILE" 2>/dev/null; then
    set_env_var "CERTBOT_WEBROOT_HOST" "$ROOT_DIR/runtime/certbot-webroot"
    changed=true
  fi
  if ! grep -q "^LETSENCRYPT_HOST=" "$ENV_FILE" 2>/dev/null; then
    set_env_var "LETSENCRYPT_HOST" "$ROOT_DIR/runtime/letsencrypt"
    changed=true
  fi

  # shellcheck disable=SC1091
  source "$ENV_FILE"
  configure_port_coexistence
  ensure_runtime_dirs

  if [[ "$changed" == true ]]; then
    info "Конфиг обновлён: $ENV_FILE"
  fi

  export BASE_DOMAIN="${BASE_DOMAIN:-kostricyn.ru}"
  export CERTBOT_EMAIL="${CERTBOT_EMAIL:-$DEFAULT_CERTBOT_EMAIL}"
}

deploy_stack() {
  cd "$COMPOSE_DIR"
  info "Сборка и запуск сервисов (это может занять несколько минут)..."
  compose up -d --build \
    nginx frontend gateway-service auth-service postgres redis kafka

  info "Ожидание postgres..."
  local i
  for i in {1..30}; do
    if compose exec -T postgres pg_isready -U platform -d platform >/dev/null 2>&1; then
      break
    fi
    sleep 2
  done

  info "Проверка gateway..."
  sleep 3
  if compose exec -T gateway-service python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" >/dev/null 2>&1; then
    info "Gateway отвечает OK"
  else
    warn "Gateway пока не отвечает — смотрите: ./setup.sh logs"
  fi

  verify_platform_nginx || warn "Проверьте порты: docker port gcloude-nginx-1 80"
}

cert_exists() {
  local domain="$1"
  cd "$COMPOSE_DIR"
  compose exec -T nginx test -f "/etc/letsencrypt/live/${domain}/fullchain.pem" 2>/dev/null
}

finalize_ssl_nginx_mode() {
  local domain="$1"
  cd "$COMPOSE_DIR"
  # shellcheck disable=SC1091
  source "$ENV_FILE"

  set_env_var "NGINX_SSL_ENABLED" "true"
  set_env_var "SSL_AUTO_ISSUE" "true"

  if [[ "${HOST_NGINX_MODE:-false}" == "true" ]]; then
    info "HOST_NGINX_MODE: SSL на внешнем nginx, platform HTTP на 127.0.0.1:$(platform_http_port)"
    set_env_var "NGINX_CONFIG" "nginx.http.conf"
    # shellcheck disable=SC1091
    source "$ENV_FILE"
    install_host_nginx_for_ssl "$domain" true
    compose up -d --force-recreate nginx gateway-service
    verify_platform_nginx || true
    info "HTTPS: app.${domain} и api.${domain} (внешний nginx → Docker :8080)"
  else
    set_env_var "NGINX_CONFIG" "nginx.https.conf"
    compose up -d nginx gateway-service
    bash "$SCRIPTS_DIR/reload-nginx.sh"
    info "HTTPS включён для app.${domain} и api.${domain}"
  fi
}

setup_ssl() {
  cd "$COMPOSE_DIR"
  # shellcheck disable=SC1091
  source "$ENV_FILE"

  local domain="${BASE_DOMAIN:-kostricyn.ru}"
  local email="${CERTBOT_EMAIL:-$DEFAULT_CERTBOT_EMAIL}"

  ensure_runtime_dirs

  if ! prepare_ssl_host_nginx "$domain"; then
    warn "ACME challenge недоступен с интернета — certbot пропущен."
    warn "Исправьте внешний nginx и выполните: bash setup.sh host-nginx && bash setup.sh ssl"
    warn "Если app/api уже описаны в другом конфиге nginx — добавьте туда:"
    warn "  location /.well-known/acme-challenge/ { root ${CERTBOT_WEBROOT_HOST:-$ROOT_DIR/runtime/certbot-webroot}; }"
    return 1
  fi

  info "Режим HTTP для выпуска сертификата..."
  set_env_var "NGINX_CONFIG" "nginx.http.conf"
  set_env_var "NGINX_SSL_ENABLED" "false"
  set_env_var "SSL_AUTO_ISSUE" "false"
  # shellcheck disable=SC1091
  source "$ENV_FILE"

  compose up -d nginx frontend gateway-service auth-service

  if cert_exists "$domain"; then
    info "Сертификат для ${domain} уже есть — переключаю HTTPS nginx"
  else
    info "Запрос Let's Encrypt для app.${domain} и api.${domain}..."
    if ! compose --profile certbot run --rm certbot certonly \
      --webroot -w /var/www/certbot \
      --email "$email" \
      --agree-tos --no-eff-email \
      -d "app.${domain}" \
      -d "api.${domain}" \
      --cert-name "${domain}"; then
      warn "Certbot не смог выпустить сертификат."
      warn "Проверьте DNS (app.${domain} → IP сервера) и открытый порт 80."
      warn "Платформа работает по HTTP. Повторите позже: ./setup.sh ssl"
      return 1
    fi
  fi

  finalize_ssl_nginx_mode "$domain"
  return 0
}

cmd_host_nginx() {
  require_root_layout
  fix_windows_transfer
  ensure_docker
  init_env
  # shellcheck disable=SC1091
  source "$ENV_FILE"
  local domain="${BASE_DOMAIN:-kostricyn.ru}"
  ensure_runtime_dirs
  install_host_nginx_for_ssl "$domain"
  verify_acme_http "$domain"
}

cmd_install() {
  local with_ssl="${1:-auto}"

  require_root_layout
  fix_windows_transfer
  ensure_docker
  init_env
  deploy_stack

  # shellcheck disable=SC1091
  source "$ENV_FILE"
  local domain="${BASE_DOMAIN:-kostricyn.ru}"

  case "$with_ssl" in
    yes|1|true|--with-ssl)
      setup_ssl || true
      ;;
    no|0|false|--no-ssl)
      warn "SSL пропущен. Позже: ./setup.sh ssl"
      ;;
    auto|*)
      if cert_exists "$domain"; then
        info "Сертификат найден — включаю HTTPS..."
        finalize_ssl_nginx_mode "$domain"
      else
        info "Пробую выпустить SSL (если DNS уже настроен)..."
        if ! setup_ssl; then
          warn "Пока работает HTTP: http://app.${domain}"
          warn "Когда DNS готов: ./setup.sh ssl"
        fi
      fi
      ;;
  esac

  print_summary
}

cmd_update() {
  require_root_layout
  fix_windows_transfer
  ensure_docker
  init_env
  cd "$ROOT_DIR"
  if [[ -d .git ]]; then
    info "git pull..."
    git pull --ff-only || warn "git pull не выполнен — продолжаю с текущими файлами"
  fi
  deploy_stack
  cd "$COMPOSE_DIR"
  # shellcheck disable=SC1091
  source "$ENV_FILE"
  if [[ "${NGINX_CONFIG:-nginx.http.conf}" == "nginx.https.conf" ]]; then
    bash "$SCRIPTS_DIR/reload-nginx.sh" || true
  fi
  print_summary
}

cmd_status() {
  require_root_layout
  ensure_docker
  cd "$COMPOSE_DIR"
  compose ps
  echo ""
  info "Health:"
  # shellcheck disable=SC1091
  source "$ENV_FILE"
  local domain="${BASE_DOMAIN:-kostricyn.ru}"
  local port=8080
  if [[ "${HOST_NGINX_MODE:-false}" != "true" ]] && ! tcp_port_busy 80; then
    port="$(publish_host_port "${PLATFORM_HTTP_PUBLISH:-80}")"
  fi
  if curl -sf --connect-timeout 5 -H "Host: app.${domain}" "http://127.0.0.1:${port}/" >/dev/null 2>&1; then
    echo "  platform nginx OK (127.0.0.1:${port})"
  elif curl -sf --connect-timeout 5 "https://api.${domain}/health" >/dev/null 2>&1; then
    echo "  api.${domain}/health OK"
  elif curl -sf --connect-timeout 5 "https://app.${domain}/" >/dev/null 2>&1; then
    echo "  app.${domain} OK"
  else
    warn "  health недоступен — bash setup.sh ssl  (или: curl -H 'Host: app.${domain}' http://127.0.0.1:${port}/)"
  fi
}

cmd_logs() {
  require_root_layout
  ensure_docker
  cd "$COMPOSE_DIR"
  compose logs -f --tail=100 gateway-service auth-service nginx
}

print_summary() {
  # shellcheck disable=SC1091
  source "$ENV_FILE"
  local domain="${BASE_DOMAIN:-kostricyn.ru}"
  local scheme="http"
  if [[ "${NGINX_CONFIG:-}" == "nginx.https.conf" ]]; then
    scheme="https"
  elif [[ "${HOST_NGINX_MODE:-false}" == "true" ]] && [[ "${NGINX_SSL_ENABLED:-false}" == "true" ]]; then
    scheme="https"
  fi

  echo ""
  echo "============================================"
  echo -e " ${GREEN}gcloude готов${NC}"
  echo "============================================"
  echo "  Кабинет:     ${scheme}://app.${domain}"
  echo "  API:         ${scheme}://api.${domain}"
  echo "  Приложения:  ${scheme}://<slug>.apps.${domain}"
  echo ""
  if [[ "${HOST_NGINX_MODE:-false}" == "true" ]]; then
    echo "  Внешний nginx на 80/443 — platform слушает:"
    echo "    HTTP  → ${PLATFORM_HTTP_PUBLISH:-127.0.0.1:8080}"
    echo "    HTTPS → ${PLATFORM_HTTPS_PUBLISH:-127.0.0.1:8443}"
    echo "    Пример прокси: bash setup.sh host-nginx"
    echo ""
  fi
  echo "  DNS нужен:"
  echo "    app.${domain}  api.${domain}  *.apps.${domain}  →  IP сервера"
  echo ""
  echo "  Команды:"
  echo "    ./setup.sh update   — обновить код и пересобрать"
  echo "    ./setup.sh ssl      — выпустить/обновить SSL кабинета"
  echo "    ./setup.sh status   — статус контейнеров"
  echo "    ./setup.sh logs     — логи"
  echo ""
  echo "  В кабинете: Настройки → Домены"
  echo "    app.${domain} / api.${domain} / apps.${domain}"
  echo "============================================"
}

usage() {
  cat <<EOF
Использование: ./setup.sh [команда] [опции]

Команды:
  (без аргументов)   Первый запуск: env + docker + SSL (если DNS готов)
  install            То же самое
  update             git pull + пересборка
  ssl                Только Let's Encrypt для app + api
  host-nginx         Настроить внешний nginx (ACME + прокси на Docker)
  status             Статус контейнеров
  logs               Логи gateway / auth / nginx
  help               Эта справка

Опции:
  --with-ssl         Обязательно попытаться выпустить SSL
  --no-ssl           Только HTTP, без certbot

Переменные окружения:
  BASE_DOMAIN=kostricyn.ru
  CERTBOT_EMAIL=kostricyn50@mail.ru

Перенос с Windows:
  Распакуйте архив в /opt/hosting и выполните:
  bash setup.sh
  (скрипт сам уберёт CRLF и выставит права на .sh)

Пример:
  cd /opt/hosting && bash setup.sh
EOF
}

main() {
  local cmd="install"
  local ssl_mode="auto"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      install|start|update|rebuild|ssl|https|host-nginx|status|ps|logs|help)
        cmd="$1"
        shift
        ;;
      --with-ssl)
        ssl_mode="yes"
        shift
        ;;
      --no-ssl)
        ssl_mode="no"
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        error "Неизвестный аргумент: $1"
        usage
        exit 1
        ;;
    esac
  done

  case "$cmd" in
    install|start)
      cmd_install "$ssl_mode"
      ;;
    update|rebuild)
      cmd_update
      ;;
    ssl|https)
      require_root_layout
      fix_windows_transfer
      ensure_docker
      init_env
      deploy_stack
      setup_ssl || exit 1
      print_summary
      ;;
    host-nginx)
      cmd_host_nginx
      ;;
    status|ps)
      cmd_status
      ;;
    logs)
      cmd_logs
      ;;
    help|-h|--help)
      usage
      ;;
    *)
      error "Неизвестная команда: $cmd"
      usage
      exit 1
      ;;
  esac
}

main "$@"

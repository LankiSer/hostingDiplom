import logging
import os

logger = logging.getLogger(__name__)

NGINX_CONF_DIR = os.getenv("NGINX_CONF_DIR", "/etc/nginx/platform.d")
APP_DOMAIN = os.getenv("APP_DOMAIN", "apps.localhost")
SSL_ENABLED = os.getenv("NGINX_SSL_ENABLED", "false").lower() in ("1", "true", "yes")
SSL_AUTO_ISSUE = os.getenv("SSL_AUTO_ISSUE", "false").lower() in ("1", "true", "yes")
LETSENCRYPT_LIVE = os.getenv("LETSENCRYPT_LIVE_DIR", "/etc/letsencrypt/live")
PLATFORM_API_UPSTREAM = os.getenv("PLATFORM_API_UPSTREAM", "gateway-service:8000")


def ssl_auto_issue() -> bool:
    return SSL_AUTO_ISSUE


def app_hostname(slug: str) -> str:
    return f"{slug}.{APP_DOMAIN}"


def cert_paths(hostname: str) -> tuple[str, str]:
    return (
        f"{LETSENCRYPT_LIVE}/{hostname}/fullchain.pem",
        f"{LETSENCRYPT_LIVE}/{hostname}/privkey.pem",
    )


def cert_exists(hostname: str) -> bool:
    cert, key = cert_paths(hostname)
    return os.path.isfile(cert) and os.path.isfile(key)


def _scheme(with_ssl: bool) -> str:
    return "https" if with_ssl else "http"


def _api_proxy_block(api_upstream: str, proto: str) -> str:
    return (
        "    location /api/ {\n"
        "        resolver 127.0.0.11 valid=10s;\n"
        f"        set $api_upstream {api_upstream};\n"
        "        proxy_pass http://$api_upstream;\n"
        "        proxy_http_version 1.1;\n"
        "        proxy_set_header Host $host;\n"
        "        proxy_set_header X-Real-IP $remote_addr;\n"
        "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n"
        f"        proxy_set_header X-Forwarded-Proto {proto};\n"
        "        proxy_read_timeout 120s;\n"
        "        proxy_connect_timeout 10s;\n"
        "    }\n"
    )


def _ui_proxy_block(container_name: str, port: int, proto: str) -> str:
    return (
        "    location / {\n"
        "        resolver 127.0.0.11 valid=10s;\n"
        f"        set $upstream {container_name}:{port};\n"
        "        proxy_pass http://$upstream;\n"
        "        proxy_http_version 1.1;\n"
        "        proxy_set_header Host $host;\n"
        "        proxy_set_header X-Real-IP $remote_addr;\n"
        "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n"
        f"        proxy_set_header X-Forwarded-Proto {proto};\n"
        "        proxy_read_timeout 60s;\n"
        "        proxy_connect_timeout 10s;\n"
        "    }\n"
    )


def _acme_block() -> str:
    return (
        "    location /.well-known/acme-challenge/ {\n"
        "        root /var/www/certbot;\n"
        "    }\n"
    )


def _resolve_api_upstream(api_container: str | None, api_port: int) -> str:
    if api_container:
        return f"{api_container}:{api_port}"
    return PLATFORM_API_UPSTREAM


def _locations(
    container_name: str,
    port: int,
    proto: str,
    *,
    proxy_api: bool,
    api_container: str | None,
    api_port: int,
) -> str:
    body = ""
    if proxy_api:
        body += _api_proxy_block(_resolve_api_upstream(api_container, api_port), proto)
    body += _ui_proxy_block(container_name, port, proto)
    return body


def _https_server(
    hostname: str,
    container_name: str,
    port: int,
    *,
    proxy_api: bool,
    api_container: str | None,
    api_port: int,
) -> str:
    cert, key = cert_paths(hostname)
    return (
        f"server {{\n"
        f"    listen 443 ssl;\n"
        f"    http2 on;\n"
        f"    server_name {hostname};\n"
        f"    ssl_certificate     {cert};\n"
        f"    ssl_certificate_key {key};\n\n"
        f"{_locations(container_name, port, 'https', proxy_api=proxy_api, api_container=api_container, api_port=api_port)}"
        f"}}\n"
    )


def _http_server(
    hostname: str,
    container_name: str,
    port: int,
    *,
    redirect_https: bool,
    proxy_api: bool,
    api_container: str | None,
    api_port: int,
) -> str:
    body = _acme_block()
    if redirect_https:
        body += (
            "    location / {\n"
            "        return 301 https://$host$request_uri;\n"
            "    }\n"
        )
    else:
        body += _locations(
            container_name,
            port,
            "http",
            proxy_api=proxy_api,
            api_container=api_container,
            api_port=api_port,
        )
    return (
        f"server {{\n"
        f"    listen 80;\n"
        f"    server_name {hostname};\n"
        f"{body}"
        f"}}\n"
    )


def write_app_config(
    slug: str,
    container_name: str,
    port: int = 3000,
    *,
    with_ssl: bool | None = None,
    proxy_api: bool = False,
    api_container: str | None = None,
    api_port: int = 8000,
) -> bool:
    hostname = app_hostname(slug)
    if with_ssl is None:
        with_ssl = SSL_ENABLED and cert_exists(hostname)

    parts: list[str] = []
    if with_ssl:
        parts.append(
            _https_server(
                hostname,
                container_name,
                port,
                proxy_api=proxy_api,
                api_container=api_container,
                api_port=api_port,
            )
        )
        parts.append(
            _http_server(
                hostname,
                container_name,
                port,
                redirect_https=True,
                proxy_api=proxy_api,
                api_container=api_container,
                api_port=api_port,
            )
        )
    else:
        parts.append(
            _http_server(
                hostname,
                container_name,
                port,
                redirect_https=False,
                proxy_api=proxy_api,
                api_container=api_container,
                api_port=api_port,
            )
        )

    conf = "\n".join(parts)
    try:
        os.makedirs(NGINX_CONF_DIR, exist_ok=True)
        with open(os.path.join(NGINX_CONF_DIR, f"{slug}.conf"), "w") as fh:
            fh.write(conf)
        logger.info("Nginx config written for %s (%s)", slug, _scheme(with_ssl))
        return True
    except Exception as exc:
        logger.error("Failed to write nginx config for %s: %s", slug, exc)
        return False


def remove_app_config(slug: str) -> bool:
    path = os.path.join(NGINX_CONF_DIR, f"{slug}.conf")
    try:
        if os.path.exists(path):
            os.remove(path)
            logger.info("Nginx config removed for %s", slug)
        return True
    except Exception as exc:
        logger.error("Failed to remove nginx config for %s: %s", slug, exc)
        return False


def app_url(slug: str) -> str:
    hostname = app_hostname(slug)
    if SSL_ENABLED and cert_exists(hostname):
        return f"https://{hostname}"
    return f"http://{hostname}"


def setup_app_ssl(
    slug: str,
    container_name: str,
    port: int = 3000,
    *,
    proxy_api: bool = False,
    api_container: str | None = None,
    api_port: int = 8000,
) -> bool:
    from src.services import certbot_service

    hostname = app_hostname(slug)
    if not certbot_service.issue_certificate(hostname):
        logger.warning("SSL certificate not issued for %s", hostname)
        return False
    return write_app_config(
        slug,
        container_name,
        port,
        with_ssl=True,
        proxy_api=proxy_api,
        api_container=api_container,
        api_port=api_port,
    )

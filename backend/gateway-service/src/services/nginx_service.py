import logging
import os

logger = logging.getLogger(__name__)

NGINX_CONF_DIR = os.getenv("NGINX_CONF_DIR", "/etc/nginx/platform.d")
APP_DOMAIN = os.getenv("APP_DOMAIN", "apps.localhost")


def write_app_config(slug: str, container_name: str, port: int = 3000) -> bool:
    conf = (
        f"server {{\n"
        f"    listen 80;\n"
        f"    server_name {slug}.{APP_DOMAIN};\n\n"
        f"    location / {{\n"
        f"        resolver 127.0.0.11 valid=10s;\n"
        f"        set $upstream {container_name}:{port};\n"
        f"        proxy_pass http://$upstream;\n"
        f"        proxy_set_header Host $host;\n"
        f"        proxy_set_header X-Real-IP $remote_addr;\n"
        f"        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n"
        f"        proxy_read_timeout 60s;\n"
        f"        proxy_connect_timeout 10s;\n"
        f"    }}\n"
        f"}}\n"
    )
    try:
        os.makedirs(NGINX_CONF_DIR, exist_ok=True)
        with open(os.path.join(NGINX_CONF_DIR, f"{slug}.conf"), "w") as fh:
            fh.write(conf)
        logger.info("Nginx config written for %s", slug)
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
    return f"http://{slug}.{APP_DOMAIN}"

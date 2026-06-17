import logging
import os

logger = logging.getLogger(__name__)

CERTBOT_EMAIL = os.getenv("CERTBOT_EMAIL", "admin@localhost")
CERTBOT_WEBROOT = os.getenv("CERTBOT_WEBROOT", "/var/www/certbot")
LETSENCRYPT_DIR = os.getenv("LETSENCRYPT_DIR", "/etc/letsencrypt")
CERTBOT_IMAGE = os.getenv("CERTBOT_IMAGE", "certbot/certbot:latest")
# Host bind mounts (production) or named Docker volumes (local dev fallback)
CERTBOT_WEBROOT_HOST = os.getenv("CERTBOT_WEBROOT_HOST", "")
LETSENCRYPT_HOST = os.getenv("LETSENCRYPT_HOST", "")
CERTBOT_WEBROOT_VOLUME = os.getenv("CERTBOT_WEBROOT_VOLUME", "gcloude_certbot_webroot")
LETSENCRYPT_VOLUME = os.getenv("LETSENCRYPT_VOLUME", "gcloude_letsencrypt")


def _certbot_volume_mounts() -> dict:
    if CERTBOT_WEBROOT_HOST and LETSENCRYPT_HOST:
        return {
            CERTBOT_WEBROOT_HOST: {"bind": "/var/www/certbot", "mode": "rw"},
            LETSENCRYPT_HOST: {"bind": "/etc/letsencrypt", "mode": "rw"},
        }
    return {
        CERTBOT_WEBROOT_VOLUME: {"bind": "/var/www/certbot", "mode": "rw"},
        LETSENCRYPT_VOLUME: {"bind": "/etc/letsencrypt", "mode": "rw"},
    }


def issue_certificate(hostname: str) -> bool:
    """Request a dedicated Let's Encrypt certificate for one subdomain (HTTP-01)."""
    if os.path.isfile(f"{LETSENCRYPT_DIR}/live/{hostname}/fullchain.pem"):
        logger.info("Certificate already exists for %s", hostname)
        return True

    try:
        import docker

        client = docker.from_env()
        logger.info("Requesting Let's Encrypt certificate for %s", hostname)
        logs = client.containers.run(
            image=CERTBOT_IMAGE,
            command=[
                "certonly",
                "--webroot",
                "-w",
                "/var/www/certbot",
                "--email",
                CERTBOT_EMAIL,
                "--agree-tos",
                "--no-eff-email",
                "--non-interactive",
                "--keep-until-expiring",
                "-d",
                hostname,
                "--cert-name",
                hostname,
            ],
            volumes=_certbot_volume_mounts(),
            remove=True,
        )
        logger.info("Certbot finished for %s: %s", hostname, logs.decode("utf-8", errors="replace")[:500])
        return os.path.isfile(f"{LETSENCRYPT_DIR}/live/{hostname}/fullchain.pem")
    except Exception as exc:
        logger.error("Certbot failed for %s: %s", hostname, exc)
        return False

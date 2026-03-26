"""
1C:Enterprise HTTP-service client.

Expected 1C HTTP-service root URL: ONEC_URL (e.g. http://host.docker.internal:8090/platform/hs/platform)
The 1C configuration must expose:
    POST /invoices  → create invoice, returns {"id": "...", "number": "...", "date": "..."}
    GET  /invoices/{id} → get invoice status

If 1C is unavailable the client returns None and the caller stores the invoice locally as 'draft'.
"""

import logging
import os

import httpx

logger = logging.getLogger(__name__)

ONEC_URL = os.getenv("ONEC_URL", "")
ONEC_USER = os.getenv("ONEC_USER", "Администратор")
ONEC_PASS = os.getenv("ONEC_PASS", "")
ONEC_TIMEOUT = 10


def _client() -> httpx.Client:
    auth = (ONEC_USER, ONEC_PASS) if ONEC_USER else None
    return httpx.Client(auth=auth, timeout=ONEC_TIMEOUT)


def is_configured() -> bool:
    return bool(ONEC_URL.strip())


def create_invoice(
    company_name: str,
    inn: str,
    amount: float,
    description: str,
) -> dict | None:
    """
    Send invoice to 1C. Returns dict with {id, number, date} or None if 1C is not available.
    """
    if not is_configured():
        logger.info("1C URL not configured — storing invoice locally as draft")
        return None

    payload = {
        "company": company_name,
        "inn": inn,
        "amount": float(amount),
        "description": description,
    }

    try:
        with _client() as client:
            resp = client.post(f"{ONEC_URL}/invoices", json=payload)
            resp.raise_for_status()
            data = resp.json()
            logger.info("1C invoice created: %s", data)
            return data
    except httpx.HTTPStatusError as exc:
        logger.error("1C returned error %s: %s", exc.response.status_code, exc.response.text[:200])
        return None
    except Exception as exc:
        logger.warning("1C unavailable: %s", exc)
        return None


def get_invoice_status(onec_id: str) -> dict | None:
    if not is_configured() or not onec_id:
        return None
    try:
        with _client() as client:
            resp = client.get(f"{ONEC_URL}/invoices/{onec_id}")
            resp.raise_for_status()
            return resp.json()
    except Exception as exc:
        logger.warning("1C status check failed: %s", exc)
        return None

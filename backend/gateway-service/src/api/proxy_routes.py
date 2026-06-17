import logging
import os

import httpx
from fastapi import APIRouter, Request, Response

logger = logging.getLogger(__name__)

router = APIRouter()

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000").rstrip("/")
PROXY_TIMEOUT = float(os.getenv("PROXY_TIMEOUT", "30"))


async def _proxy_request(base_url: str, path: str, request: Request) -> Response:
    url = f"{base_url}{path}"
    if request.url.query:
        url = f"{url}?{request.url.query}"
    body = await request.body()
    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in {"host", "content-length", "connection"}
    }
    try:
        async with httpx.AsyncClient(timeout=PROXY_TIMEOUT) as client:
            upstream = await client.request(
                request.method,
                url,
                content=body,
                headers=headers,
            )
    except httpx.ConnectError as exc:
        logger.error("Upstream unavailable %s: %s", url, exc)
        return Response(
            content='{"detail":"Auth service unavailable. Check auth-service container."}',
            status_code=502,
            media_type="application/json",
        )
    except httpx.HTTPError as exc:
        logger.error("Proxy error %s: %s", url, exc)
        return Response(
            content='{"detail":"Upstream request failed."}',
            status_code=502,
            media_type="application/json",
        )

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers={
            key: value
            for key, value in upstream.headers.items()
            if key.lower() not in {"content-encoding", "transfer-encoding", "connection"}
        },
        media_type=upstream.headers.get("content-type"),
    )


@router.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_auth(path: str, request: Request) -> Response:
    return await _proxy_request(AUTH_SERVICE_URL, f"/api/v1/auth/{path}", request)

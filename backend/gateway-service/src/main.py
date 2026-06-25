import logging

from fastapi import FastAPI

from src.api.app import create_app

logger = logging.getLogger(__name__)


def _init_database(app: FastAPI) -> None:
    try:
        from src.core.database import init_db
        init_db()
        logger.info("Database initialized")
    except Exception as exc:
        logger.warning("Database init skipped: %s", exc)


def _sync_app_nginx_configs() -> None:
    try:
        from src.repositories.hosting_repository import HostingRepository
        from src.services import docker_service, nginx_service

        repo = HostingRepository()
        for app_row in repo.list_apps():
            if not app_row.get("container_name"):
                continue

            proxy_api = app_row.get("app_type") == "frontend"
            api_container: str | None = None
            api_port = 8000
            if proxy_api and app_row.get("project_id"):
                backend = repo.get_app_by_type(str(app_row["project_id"]), "backend")
                if backend and backend.get("container_name") and backend.get("status") == "running":
                    api_container = backend["container_name"]
                    api_port = 8000 if backend.get("runtime") == "python" else 3000

            nginx_service.write_app_config(
                str(app_row["slug"]),
                str(app_row["container_name"]),
                3000,
                proxy_api=proxy_api,
                api_container=api_container,
                api_port=api_port,
            )

        docker_service.reload_nginx()
        logger.info("Application nginx configs synchronized")
    except Exception as exc:
        logger.warning("Application nginx config sync skipped: %s", exc)


app = create_app()


@app.on_event("startup")
def on_startup() -> None:
    _init_database(app)
    _sync_app_nginx_configs()

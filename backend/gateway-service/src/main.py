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


app = create_app()


@app.on_event("startup")
def on_startup() -> None:
    _init_database(app)

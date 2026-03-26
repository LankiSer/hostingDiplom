import logging
import os

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from src.repositories.hosting_repository import HostingRepository
from src.services import docker_service, nginx_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/hosting")
repo = HostingRepository()


class ProjectCreate(BaseModel):
    name: str
    description: str = ""


class AppCreate(BaseModel):
    project_id: str
    name: str
    git_url: str = ""
    runtime: str = "node"


def _deploy_background(app_id: str, slug: str, git_url: str, runtime: str, deployment_id: str) -> None:
    repo.update_deployment(deployment_id, "building")
    repo.update_app(app_id, "building")

    result = docker_service.clone_and_build(slug, git_url, runtime)

    if not result["success"]:
        error = result.get("error", "Unknown error")
        repo.update_deployment(deployment_id, "failed", error)
        repo.update_app(app_id, "error")
        return

    url = nginx_service.app_url(slug)
    nginx_service.write_app_config(slug, result["container_name"])
    docker_service.reload_nginx()

    repo.update_deployment(deployment_id, "running", result.get("build_logs", ""))
    repo.update_app(
        app_id,
        status="running",
        container_id=result["container_id"],
        container_name=result["container_name"],
        url=url,
    )


@router.get("/projects")
def list_projects() -> list[dict]:
    return repo.list_projects()


@router.post("/projects", status_code=201)
def create_project(body: ProjectCreate) -> dict:
    if not body.name.strip():
        raise HTTPException(status_code=400, detail="Name is required")
    return repo.create_project(body.name.strip(), body.description)


@router.get("/projects/{project_id}")
def get_project(project_id: str) -> dict:
    project = repo.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(project_id: str) -> None:
    if not repo.delete_project(project_id):
        raise HTTPException(status_code=404, detail="Project not found")


@router.get("/apps")
def list_apps(project_id: str | None = None) -> list[dict]:
    return repo.list_apps(project_id)


@router.post("/apps", status_code=201)
def create_app(body: AppCreate, background_tasks: BackgroundTasks) -> dict:
    if not body.name.strip():
        raise HTTPException(status_code=400, detail="Name is required")
    if not repo.get_project(body.project_id):
        raise HTTPException(status_code=404, detail="Project not found")

    app = repo.create_app(body.project_id, body.name.strip(), body.git_url, body.runtime)

    if body.git_url.strip():
        deployment = repo.create_deployment(app["id"], body.git_url)
        background_tasks.add_task(
            _deploy_background,
            app["id"],
            app["slug"],
            body.git_url,
            body.runtime,
            deployment["id"],
        )
        return {**app, "deployment_id": deployment["id"]}

    return app


@router.get("/apps/{app_id}")
def get_app(app_id: str) -> dict:
    app = repo.get_app(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    if app.get("container_name"):
        live_status = docker_service.container_status(app["container_name"])
        if live_status != "not_found" and live_status != app["status"]:
            repo.update_app(app_id, live_status, app.get("container_id", ""), app.get("container_name", ""), app.get("url", ""))
            app["status"] = live_status
    return app


@router.get("/apps/{app_id}/logs")
def get_app_logs(app_id: str) -> dict:
    app = repo.get_app(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    logs = docker_service.get_logs(app.get("container_name", "")) if app.get("container_name") else ""
    return {"logs": logs}


@router.post("/apps/{app_id}/stop")
def stop_app(app_id: str) -> dict:
    app = repo.get_app(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    docker_service.stop_container(app.get("container_name", ""))
    repo.update_app(app_id, "stopped", app.get("container_id", ""), app.get("container_name", ""), app.get("url", ""))
    return {"status": "stopped"}


@router.post("/apps/{app_id}/start")
def start_app(app_id: str) -> dict:
    app = repo.get_app(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    docker_service.start_container(app.get("container_name", ""))
    repo.update_app(app_id, "running", app.get("container_id", ""), app.get("container_name", ""), app.get("url", ""))
    return {"status": "running"}


@router.post("/apps/{app_id}/redeploy")
def redeploy_app(app_id: str, background_tasks: BackgroundTasks) -> dict:
    app = repo.get_app(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    if not app.get("git_url"):
        raise HTTPException(status_code=400, detail="No git URL to redeploy from")
    deployment = repo.create_deployment(app_id, app["git_url"])
    background_tasks.add_task(
        _deploy_background,
        app_id,
        app["slug"],
        app["git_url"],
        app["runtime"],
        deployment["id"],
    )
    return {"deployment_id": deployment["id"], "status": "building"}


@router.delete("/apps/{app_id}", status_code=204)
def delete_app(app_id: str) -> None:
    app = repo.get_app(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    if app.get("container_name"):
        docker_service.remove_container(app["container_name"])
        nginx_service.remove_app_config(app["slug"])
        docker_service.reload_nginx()
    repo.delete_app(app_id)


@router.delete("/nginx/{slug}", status_code=204)
def remove_nginx_config(slug: str) -> None:
    nginx_service.remove_app_config(slug)
    docker_service.reload_nginx()


@router.get("/nginx")
def list_nginx_configs() -> list[str]:
    try:
        return [f for f in os.listdir(nginx_service.NGINX_CONF_DIR) if f.endswith(".conf")]
    except Exception:
        return []


@router.get("/apps/{app_id}/deployments")
def list_app_deployments(app_id: str) -> list[dict]:
    return repo.list_deployments(app_id)


@router.get("/deployments")
def list_all_deployments() -> list[dict]:
    return repo.list_deployments()

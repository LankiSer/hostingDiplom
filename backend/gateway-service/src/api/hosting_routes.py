import logging
import os

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from src.repositories.hosting_repository import HostingRepository
from src.services import docker_service, nginx_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/hosting")
repo = HostingRepository()


def _enrich_app(app: dict) -> dict:
    slug = app.get("slug")
    if not slug:
        return app
    hostname = nginx_service.app_hostname(slug)
    app["hostname"] = hostname
    if not app.get("url"):
        app["url"] = nginx_service.app_url(slug)
    return app


class ProjectCreate(BaseModel):
    name: str
    description: str = ""


class AppCreate(BaseModel):
    project_id: str
    name: str
    git_url: str = ""
    runtime: str = "node"
    app_type: str = "custom"
    root_path: str = ""
    branch: str = "main"


class DeployComponentConfig(BaseModel):
    enabled: bool = False
    name: str = ""
    root_path: str = ""
    runtime: str = "node"


class ProjectDeployConfigUpdate(BaseModel):
    git_url: str
    git_branch: str = "main"
    frontend: DeployComponentConfig = Field(default_factory=DeployComponentConfig)
    backend: DeployComponentConfig = Field(
        default_factory=lambda: DeployComponentConfig(name="api", root_path="backend", runtime="python")
    )


def _deploy_background(
    app_id: str,
    slug: str,
    git_url: str,
    runtime: str,
    deployment_id: str,
    branch: str = "main",
    root_path: str = "",
    project_id: str = "",
    app_type: str = "custom",
) -> None:
    repo.update_deployment(deployment_id, "building")
    repo.update_app(app_id, "building")

    result = docker_service.clone_and_build(slug, git_url, runtime, branch=branch, root_path=root_path)

    if not result["success"]:
        error = result.get("error", "Unknown error")
        repo.update_deployment(deployment_id, "failed", error)
        repo.update_app(app_id, "error")
        return

    container_name = result["container_name"]
    port = result.get("port", 3000)

    proxy_api = app_type == "frontend"
    api_container: str | None = None
    api_port = 8000 if runtime == "python" else 3000
    if proxy_api and project_id:
        backend = repo.get_app_by_type(project_id, "backend")
        if backend and backend.get("container_name") and backend.get("status") == "running":
            api_container = backend["container_name"]

    nginx_kwargs = {
        "proxy_api": proxy_api,
        "api_container": api_container,
        "api_port": api_port,
    }

    if nginx_service.ssl_auto_issue():
        nginx_service.write_app_config(slug, container_name, port, with_ssl=False, **nginx_kwargs)
        docker_service.reload_nginx()
        if not nginx_service.setup_app_ssl(slug, container_name, port, **nginx_kwargs):
            logger.warning("Deploy OK but SSL pending for %s — add DNS A-record first", slug)
    else:
        nginx_service.write_app_config(slug, container_name, port, **nginx_kwargs)
    docker_service.reload_nginx()

    if app_type == "backend" and project_id:
        _refresh_frontend_api_proxy(project_id)

    url = nginx_service.app_url(slug)

    repo.update_deployment(deployment_id, "running", result.get("build_logs", ""))
    repo.update_app(
        app_id,
        status="running",
        container_id=result["container_id"],
        container_name=result["container_name"],
        url=url,
    )


def _refresh_frontend_api_proxy(project_id: str) -> None:
    frontend = repo.get_app_by_type(project_id, "frontend")
    backend = repo.get_app_by_type(project_id, "backend")
    if not frontend or not backend:
        return
    if frontend.get("status") != "running" or not frontend.get("container_name"):
        return
    if not backend.get("container_name"):
        return

    slug = frontend["slug"]
    api_port = 8000 if backend.get("runtime") == "python" else 3000
    with_ssl = nginx_service.SSL_ENABLED and nginx_service.cert_exists(nginx_service.app_hostname(slug))
    nginx_service.write_app_config(
        slug,
        frontend["container_name"],
        3000,
        with_ssl=with_ssl,
        proxy_api=True,
        api_container=backend["container_name"],
        api_port=api_port,
    )
    docker_service.reload_nginx()
    logger.info("Updated frontend nginx to proxy /api/ -> %s", backend["container_name"])


def _schedule_deploy(app: dict, git_url: str, background_tasks: BackgroundTasks) -> str:
    deployment = repo.create_deployment(app["id"], git_url)
    background_tasks.add_task(
        _deploy_background,
        app["id"],
        app["slug"],
        git_url,
        app["runtime"],
        deployment["id"],
        app.get("branch") or "main",
        app.get("root_path") or "",
        app.get("project_id") or "",
        app.get("app_type") or "custom",
    )
    return deployment["id"]


def _upsert_stack_app(
    project_id: str,
    app_type: str,
    name: str,
    git_url: str,
    runtime: str,
    root_path: str,
    branch: str,
) -> dict:
    existing = repo.get_app_by_type(project_id, app_type)
    if existing:
        updated = repo.update_app_config(
            existing["id"],
            git_url=git_url,
            runtime=runtime,
            root_path=root_path,
            branch=branch,
            name=name or existing["name"],
        )
        return updated or existing
    return repo.create_app(
        project_id=project_id,
        name=name,
        git_url=git_url,
        runtime=runtime,
        app_type=app_type,
        root_path=root_path,
        branch=branch,
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


@router.put("/projects/{project_id}/deploy-config")
def update_deploy_config(project_id: str, body: ProjectDeployConfigUpdate) -> dict:
    project = repo.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not body.git_url.strip():
        raise HTTPException(status_code=400, detail="git_url is required")

    deploy_config = {
        "frontend": body.frontend.model_dump(),
        "backend": body.backend.model_dump(),
    }
    updated = repo.update_project_deploy_config(
        project_id,
        body.git_url.strip(),
        body.git_branch.strip() or "main",
        deploy_config,
    )
    return updated or project


@router.post("/projects/{project_id}/deploy-stack")
def deploy_stack(project_id: str, background_tasks: BackgroundTasks) -> dict:
    project = repo.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    git_url = (project.get("git_url") or "").strip()
    if not git_url:
        raise HTTPException(status_code=400, detail="Configure git_url in deploy settings first")

    deploy_config = project.get("deploy_config") or {}
    if isinstance(deploy_config, str):
        import json
        deploy_config = json.loads(deploy_config)

    branch = project.get("git_branch") or "main"
    deployments: list[dict] = []

    for app_type, defaults in [
        ("frontend", {"name": "web", "root_path": "frontend", "runtime": "node"}),
        ("backend", {"name": "api", "root_path": "backend", "runtime": "python"}),
    ]:
        component = deploy_config.get(app_type) or {}
        if not component.get("enabled"):
            continue
        app = _upsert_stack_app(
            project_id=project_id,
            app_type=app_type,
            name=component.get("name") or defaults["name"],
            git_url=git_url,
            runtime=component.get("runtime") or defaults["runtime"],
            root_path=component.get("root_path") or defaults["root_path"],
            branch=branch,
        )
        deployment_id = _schedule_deploy(app, git_url, background_tasks)
        deployments.append({"app_id": app["id"], "app_type": app_type, "deployment_id": deployment_id})

    if not deployments:
        raise HTTPException(status_code=400, detail="Enable frontend or backend in deploy settings")

    return {"deployments": deployments, "status": "building"}


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(project_id: str) -> None:
    if not repo.delete_project(project_id):
        raise HTTPException(status_code=404, detail="Project not found")


@router.get("/apps")
def list_apps(project_id: str | None = None) -> list[dict]:
    return [_enrich_app(app) for app in repo.list_apps(project_id)]


@router.post("/apps", status_code=201)
def create_app(body: AppCreate, background_tasks: BackgroundTasks) -> dict:
    if not body.name.strip():
        raise HTTPException(status_code=400, detail="Name is required")
    if not repo.get_project(body.project_id):
        raise HTTPException(status_code=404, detail="Project not found")

    app = repo.create_app(
        body.project_id,
        body.name.strip(),
        body.git_url,
        body.runtime,
        body.app_type,
        body.root_path,
        body.branch,
    )

    if body.git_url.strip():
        deployment_id = _schedule_deploy(app, body.git_url.strip(), background_tasks)
        return _enrich_app({**app, "deployment_id": deployment_id})

    return _enrich_app(app)


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
    return _enrich_app(app)


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
    deployment_id = _schedule_deploy(app, app["git_url"], background_tasks)
    return {"deployment_id": deployment_id, "status": "building"}


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

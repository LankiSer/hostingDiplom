import logging
import os
import shutil
import subprocess

logger = logging.getLogger(__name__)

WORKSPACE = os.getenv("WORKSPACE_DIR", "/workspace")
DOCKER_NETWORK = os.getenv("DOCKER_NETWORK", "platform")


def _get_client():
    try:
        import docker
        return docker.from_env()
    except Exception as exc:
        logger.warning("Docker not available: %s", exc)
        return None


def _generate_dockerfile(runtime: str) -> str:
    if runtime == "node":
        return (
            "FROM node:20-alpine\n"
            "WORKDIR /app\n"
            "COPY . .\n"
            "RUN npm install --production 2>/dev/null || npm install\n"
            "EXPOSE 3000\n"
            'CMD ["npm", "start"]\n'
        )
    return (
        "FROM python:3.11-slim\n"
        "WORKDIR /app\n"
        "COPY . .\n"
        "RUN pip install --no-cache-dir -r requirements.txt\n"
        "EXPOSE 3000\n"
        'CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]\n'
    )


def clone_and_build(slug: str, git_url: str, runtime: str) -> dict:
    client = _get_client()
    if not client:
        return {"success": False, "error": "Docker daemon not reachable"}

    work_dir = f"{WORKSPACE}/{slug}"
    build_logs: list[str] = []

    try:
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)
        os.makedirs(WORKSPACE, exist_ok=True)

        result = subprocess.run(
            ["git", "clone", "--depth", "1", git_url, work_dir],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            return {"success": False, "error": f"git clone failed: {result.stderr[:500]}"}

        dockerfile_path = os.path.join(work_dir, "Dockerfile")
        if not os.path.exists(dockerfile_path):
            with open(dockerfile_path, "w") as fh:
                fh.write(_generate_dockerfile(runtime))

        image_tag = f"platform-userapp-{slug}:latest"
        _stop_old_container(client, slug)

        _, build_iter = client.images.build(
            path=work_dir,
            tag=image_tag,
            rm=True,
            forcerm=True,
        )
        for chunk in build_iter:
            if "stream" in chunk:
                line = chunk["stream"].strip()
                if line:
                    build_logs.append(line)

        container_name = f"userapp-{slug}"
        container = client.containers.run(
            image_tag,
            name=container_name,
            detach=True,
            network=DOCKER_NETWORK,
            environment={"PORT": "3000"},
            restart_policy={"Name": "unless-stopped"},
        )

        return {
            "success": True,
            "container_id": container.id[:12],
            "container_name": container_name,
            "build_logs": "\n".join(build_logs[-30:]),
        }

    except Exception as exc:
        logger.exception("Build failed for %s", slug)
        return {"success": False, "error": str(exc)[:500]}


def get_logs(container_name: str, tail: int = 150) -> str:
    client = _get_client()
    if not client:
        return "Docker daemon not reachable"
    try:
        container = client.containers.get(container_name)
        return container.logs(tail=tail, timestamps=True).decode("utf-8", errors="replace")
    except Exception as exc:
        return f"Error: {exc}"


def container_status(container_name: str) -> str:
    client = _get_client()
    if not client:
        return "unknown"
    try:
        container = client.containers.get(container_name)
        return container.status
    except Exception:
        return "not_found"


def stop_container(container_name: str) -> bool:
    client = _get_client()
    if not client:
        return False
    try:
        client.containers.get(container_name).stop(timeout=10)
        return True
    except Exception as exc:
        logger.warning("Stop failed for %s: %s", container_name, exc)
        return False


def start_container(container_name: str) -> bool:
    client = _get_client()
    if not client:
        return False
    try:
        client.containers.get(container_name).start()
        return True
    except Exception as exc:
        logger.warning("Start failed for %s: %s", container_name, exc)
        return False


def remove_container(container_name: str) -> bool:
    client = _get_client()
    if not client:
        return False
    try:
        container = client.containers.get(container_name)
        container.stop(timeout=5)
        container.remove(force=True)
        return True
    except Exception as exc:
        logger.warning("Remove failed for %s: %s", container_name, exc)
        return False


def reload_nginx() -> bool:
    client = _get_client()
    if not client:
        return False
    try:
        for container in client.containers.list():
            if "nginx" in container.name and "userapp" not in container.name:
                container.exec_run("nginx -s reload")
                logger.info("Nginx reloaded via container %s", container.name)
                return True
    except Exception as exc:
        logger.warning("Nginx reload failed: %s", exc)
    return False


def _stop_old_container(client, slug: str) -> None:
    try:
        old = client.containers.get(f"userapp-{slug}")
        old.stop(timeout=5)
        old.remove(force=True)
    except Exception:
        pass

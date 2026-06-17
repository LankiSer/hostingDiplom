import json
import re

from src.core.database import get_connection, serialize_row


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9-]", "-", name.lower().strip())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug[:40]


class HostingRepository:
    # ------------------------------------------------------------------ projects

    def list_projects(self) -> list[dict]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT p.*,
                           COUNT(a.id) AS app_count
                    FROM projects p
                    LEFT JOIN applications a ON a.project_id = p.id
                    GROUP BY p.id
                    ORDER BY p.created_at DESC
                """)
                return [serialize_row(r) for r in cur.fetchall()]

    def create_project(self, name: str, description: str = "") -> dict:
        slug = _slugify(name)
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO projects (name, slug, description) VALUES (%s, %s, %s) RETURNING *",
                    (name, slug, description),
                )
                conn.commit()
                return serialize_row(cur.fetchone())

    def get_project(self, project_id: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT p.*, COUNT(a.id) AS app_count FROM projects p "
                    "LEFT JOIN applications a ON a.project_id = p.id "
                    "WHERE p.id = %s GROUP BY p.id",
                    (project_id,),
                )
                return serialize_row(cur.fetchone())

    def delete_project(self, project_id: str) -> bool:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM projects WHERE id = %s", (project_id,))
                conn.commit()
                return cur.rowcount > 0

    # ---------------------------------------------------------------- applications

    def list_apps(self, project_id: str | None = None) -> list[dict]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                if project_id:
                    cur.execute(
                        "SELECT a.*, p.name AS project_name FROM applications a "
                        "JOIN projects p ON p.id = a.project_id "
                        "WHERE a.project_id = %s ORDER BY a.created_at DESC",
                        (project_id,),
                    )
                else:
                    cur.execute(
                        "SELECT a.*, p.name AS project_name FROM applications a "
                        "JOIN projects p ON p.id = a.project_id "
                        "ORDER BY a.created_at DESC"
                    )
                return [serialize_row(r) for r in cur.fetchall()]

    def create_app(
        self,
        project_id: str,
        name: str,
        git_url: str = "",
        runtime: str = "node",
        app_type: str = "custom",
        root_path: str = "",
        branch: str = "main",
    ) -> dict:
        slug = _slugify(name)
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO applications
                       (project_id, name, slug, git_url, runtime, app_type, root_path, branch)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                    (project_id, name, slug, git_url, runtime, app_type, root_path, branch),
                )
                conn.commit()
                return serialize_row(cur.fetchone())

    def get_app_by_type(self, project_id: str, app_type: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM applications WHERE project_id = %s AND app_type = %s LIMIT 1",
                    (project_id, app_type),
                )
                return serialize_row(cur.fetchone())

    def update_app_config(
        self,
        app_id: str,
        *,
        git_url: str | None = None,
        runtime: str | None = None,
        root_path: str | None = None,
        branch: str | None = None,
        name: str | None = None,
    ) -> dict | None:
        fields: list[str] = []
        values: list[object] = []
        if git_url is not None:
            fields.append("git_url = %s")
            values.append(git_url)
        if runtime is not None:
            fields.append("runtime = %s")
            values.append(runtime)
        if root_path is not None:
            fields.append("root_path = %s")
            values.append(root_path)
        if branch is not None:
            fields.append("branch = %s")
            values.append(branch)
        if name is not None:
            fields.append("name = %s")
            values.append(name)
        if not fields:
            return self.get_app(app_id)
        values.append(app_id)
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"UPDATE applications SET {', '.join(fields)} WHERE id = %s RETURNING *",
                    values,
                )
                conn.commit()
                return serialize_row(cur.fetchone())

    def update_project_deploy_config(
        self,
        project_id: str,
        git_url: str,
        git_branch: str,
        deploy_config: dict,
    ) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """UPDATE projects
                       SET git_url = %s, git_branch = %s, deploy_config = %s::jsonb
                       WHERE id = %s RETURNING *""",
                    (git_url, git_branch, json.dumps(deploy_config), project_id),
                )
                conn.commit()
                row = cur.fetchone()
                return serialize_row(row)

    def get_app(self, app_id: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT a.*, p.name AS project_name FROM applications a "
                    "JOIN projects p ON p.id = a.project_id "
                    "WHERE a.id = %s",
                    (app_id,),
                )
                return serialize_row(cur.fetchone())

    def update_app(
        self,
        app_id: str,
        status: str,
        container_id: str = "",
        container_name: str = "",
        url: str = "",
    ) -> None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """UPDATE applications
                       SET status = %s, container_id = %s, container_name = %s, url = %s
                       WHERE id = %s""",
                    (status, container_id, container_name, url, app_id),
                )
                conn.commit()

    def delete_app(self, app_id: str) -> bool:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM applications WHERE id = %s", (app_id,))
                conn.commit()
                return cur.rowcount > 0

    # --------------------------------------------------------------- deployments

    def create_deployment(self, app_id: str, git_url: str) -> dict:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO deployments (app_id, git_url) VALUES (%s, %s) RETURNING *",
                    (app_id, git_url),
                )
                conn.commit()
                return serialize_row(cur.fetchone())

    def update_deployment(self, deployment_id: str, status: str, logs: str = "") -> None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE deployments SET status = %s, logs = %s WHERE id = %s",
                    (status, logs, deployment_id),
                )
                conn.commit()

    def list_deployments(self, app_id: str | None = None) -> list[dict]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                if app_id:
                    cur.execute(
                        "SELECT * FROM deployments WHERE app_id = %s ORDER BY created_at DESC",
                        (app_id,),
                    )
                else:
                    cur.execute("SELECT * FROM deployments ORDER BY created_at DESC LIMIT 50")
                return [serialize_row(r) for r in cur.fetchall()]

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
    ) -> dict:
        slug = _slugify(name)
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO applications (project_id, name, slug, git_url, runtime)
                       VALUES (%s, %s, %s, %s, %s) RETURNING *""",
                    (project_id, name, slug, git_url, runtime),
                )
                conn.commit()
                return serialize_row(cur.fetchone())

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

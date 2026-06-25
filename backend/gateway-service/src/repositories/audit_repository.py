import json
from typing import Any

from src.core.database import get_connection, serialize_row
from src.core.rbac import CurrentUser


class AuditRepository:
    def record(
        self,
        *,
        actor: CurrentUser | None,
        action: str,
        resource_type: str = "",
        resource_id: str = "",
        message: str = "",
        metadata: dict[str, Any] | None = None,
        ip: str = "",
    ) -> dict[str, object] | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO audit_logs
                      (actor_email, actor_role, action, resource_type, resource_id, message, metadata, ip)
                    VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                    RETURNING *
                    """,
                    (
                        actor.email if actor else "",
                        actor.role if actor else "",
                        action,
                        resource_type,
                        resource_id,
                        message,
                        json.dumps(metadata or {}, ensure_ascii=False),
                        ip,
                    ),
                )
                conn.commit()
                return serialize_row(cur.fetchone())

    def list(self, limit: int = 80, resource_type: str = "") -> list[dict[str, object]]:
        limit = max(1, min(limit, 200))
        with get_connection() as conn:
            with conn.cursor() as cur:
                if resource_type:
                    cur.execute(
                        """
                        SELECT * FROM audit_logs
                        WHERE resource_type = %s
                        ORDER BY created_at DESC
                        LIMIT %s
                        """,
                        (resource_type, limit),
                    )
                else:
                    cur.execute(
                        "SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT %s",
                        (limit,),
                    )
                return [serialize_row(row) for row in cur.fetchall()]

    def stats(self) -> dict[str, int]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                      COUNT(*) FILTER (WHERE created_at > now() - interval '24 hours') AS last_24h,
                      COUNT(*) FILTER (WHERE action LIKE 'team.%') AS team_events,
                      COUNT(*) FILTER (WHERE action LIKE 'hosting.%') AS hosting_events,
                      COUNT(*) FILTER (WHERE action LIKE 'billing.%') AS billing_events
                    FROM audit_logs
                    """
                )
                row = serialize_row(cur.fetchone()) or {}
                return {key: int(row.get(key) or 0) for key in ("last_24h", "team_events", "hosting_events", "billing_events")}

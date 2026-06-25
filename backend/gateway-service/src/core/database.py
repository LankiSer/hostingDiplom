import datetime
import os
import uuid

import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("POSTGRES_URL", "postgresql://platform:platform@postgres:5432/platform")


def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def _ensure_column(cur, table: str, column: str, definition: str) -> None:
    cur.execute(
        """
        SELECT 1 FROM information_schema.columns
        WHERE table_name = %s AND column_name = %s
        """,
        (table, column),
    )
    if not cur.fetchone():
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def serialize_row(row: dict | None) -> dict | None:
    if row is None:
        return None
    result = {}
    for key, value in dict(row).items():
        if isinstance(value, uuid.UUID):
            result[key] = str(value)
        elif isinstance(value, (datetime.datetime, datetime.date)):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result


def init_db() -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(100) NOT NULL,
                    slug VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT DEFAULT '',
                    git_url TEXT DEFAULT '',
                    git_branch VARCHAR(100) DEFAULT 'main',
                    deploy_config JSONB DEFAULT '{}',
                    created_at TIMESTAMPTZ DEFAULT now()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
                    name VARCHAR(100) NOT NULL,
                    slug VARCHAR(100) NOT NULL UNIQUE,
                    runtime VARCHAR(20) DEFAULT 'node',
                    app_type VARCHAR(20) DEFAULT 'custom',
                    git_url TEXT DEFAULT '',
                    root_path TEXT DEFAULT '',
                    branch VARCHAR(100) DEFAULT 'main',
                    container_id VARCHAR(100) DEFAULT '',
                    container_name VARCHAR(100) DEFAULT '',
                    status VARCHAR(20) DEFAULT 'idle',
                    url TEXT DEFAULT '',
                    created_at TIMESTAMPTZ DEFAULT now()
                )
            """)
            _ensure_column(cur, "projects", "git_url", "TEXT DEFAULT ''")
            _ensure_column(cur, "projects", "git_branch", "VARCHAR(100) DEFAULT 'main'")
            _ensure_column(cur, "projects", "deploy_config", "JSONB DEFAULT '{}'")
            _ensure_column(cur, "applications", "app_type", "VARCHAR(20) DEFAULT 'custom'")
            _ensure_column(cur, "applications", "root_path", "TEXT DEFAULT ''")
            _ensure_column(cur, "applications", "branch", "VARCHAR(100) DEFAULT 'main'")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS deployments (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    app_id UUID REFERENCES applications(id) ON DELETE CASCADE,
                    status VARCHAR(20) DEFAULT 'pending',
                    logs TEXT DEFAULT '',
                    git_url TEXT DEFAULT '',
                    created_at TIMESTAMPTZ DEFAULT now()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    company_name VARCHAR(200) NOT NULL,
                    inn VARCHAR(12) NOT NULL DEFAULT '',
                    description TEXT DEFAULT '',
                    amount NUMERIC(12,2) NOT NULL,
                    status VARCHAR(20) DEFAULT 'draft',
                    onec_id VARCHAR(100) DEFAULT '',
                    onec_number VARCHAR(50) DEFAULT '',
                    created_at TIMESTAMPTZ DEFAULT now()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS team_members (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(120) NOT NULL,
                    email VARCHAR(200) NOT NULL UNIQUE,
                    role VARCHAR(20) NOT NULL DEFAULT 'ops',
                    status VARCHAR(20) NOT NULL DEFAULT 'invited',
                    projects INTEGER NOT NULL DEFAULT 0,
                    invite_token VARCHAR(80) DEFAULT '',
                    invite_expires_at TIMESTAMPTZ,
                    invited_at TIMESTAMPTZ DEFAULT now(),
                    activated_at TIMESTAMPTZ,
                    last_seen_at TIMESTAMPTZ,
                    created_by VARCHAR(200) DEFAULT '',
                    created_at TIMESTAMPTZ DEFAULT now()
                )
            """)
            _ensure_column(cur, "team_members", "invite_token", "VARCHAR(80) DEFAULT ''")
            _ensure_column(cur, "team_members", "invite_expires_at", "TIMESTAMPTZ")
            _ensure_column(cur, "team_members", "invited_at", "TIMESTAMPTZ DEFAULT now()")
            _ensure_column(cur, "team_members", "activated_at", "TIMESTAMPTZ")
            _ensure_column(cur, "team_members", "last_seen_at", "TIMESTAMPTZ")
            _ensure_column(cur, "team_members", "created_by", "VARCHAR(200) DEFAULT ''")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    actor_email VARCHAR(200) NOT NULL DEFAULT '',
                    actor_role VARCHAR(40) NOT NULL DEFAULT '',
                    action VARCHAR(120) NOT NULL,
                    resource_type VARCHAR(80) NOT NULL DEFAULT '',
                    resource_id VARCHAR(120) NOT NULL DEFAULT '',
                    message TEXT NOT NULL DEFAULT '',
                    metadata JSONB DEFAULT '{}',
                    ip VARCHAR(80) NOT NULL DEFAULT '',
                    created_at TIMESTAMPTZ DEFAULT now()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS team_call_sessions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title VARCHAR(160) NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'active',
                    created_by VARCHAR(200) NOT NULL DEFAULT '',
                    tldraw_room VARCHAR(160) NOT NULL DEFAULT '',
                    tldraw_url TEXT NOT NULL DEFAULT '',
                    started_at TIMESTAMPTZ DEFAULT now(),
                    ended_at TIMESTAMPTZ,
                    created_at TIMESTAMPTZ DEFAULT now()
                )
            """)
            _ensure_column(cur, "team_call_sessions", "tldraw_room", "VARCHAR(160) NOT NULL DEFAULT ''")
            _ensure_column(cur, "team_call_sessions", "tldraw_url", "TEXT NOT NULL DEFAULT ''")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS team_call_messages (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    session_id UUID REFERENCES team_call_sessions(id) ON DELETE CASCADE,
                    author_email VARCHAR(200) NOT NULL DEFAULT '',
                    author_name VARCHAR(120) NOT NULL DEFAULT '',
                    kind VARCHAR(30) NOT NULL DEFAULT 'chat',
                    body TEXT NOT NULL DEFAULT '',
                    created_at TIMESTAMPTZ DEFAULT now()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    email VARCHAR(200) NOT NULL UNIQUE,
                    name VARCHAR(120) NOT NULL DEFAULT '',
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT now()
                )
            """)
        conn.commit()
    finally:
        conn.close()

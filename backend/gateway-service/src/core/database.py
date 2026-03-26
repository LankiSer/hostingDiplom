import datetime
import os
import uuid

import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("POSTGRES_URL", "postgresql://platform:platform@postgres:5432/platform")


def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


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
                    git_url TEXT DEFAULT '',
                    container_id VARCHAR(100) DEFAULT '',
                    container_name VARCHAR(100) DEFAULT '',
                    status VARCHAR(20) DEFAULT 'idle',
                    url TEXT DEFAULT '',
                    created_at TIMESTAMPTZ DEFAULT now()
                )
            """)
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
        conn.commit()
    finally:
        conn.close()

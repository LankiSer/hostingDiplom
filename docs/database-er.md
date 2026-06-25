# ER-диаграмма базы данных платформы

Схема создаётся при старте `gateway-service` через `init_db()` (`backend/gateway-service/src/core/database.py`). Отдельных SQL-миграций нет — новые колонки добавляются через `_ensure_column()`.

## Диаграмма сущностей

```mermaid
erDiagram
    projects ||--o{ applications : "has"
    applications ||--o{ deployments : "has"
    team_call_sessions ||--o{ team_call_messages : "has"

    projects {
        uuid id PK
        varchar name
        varchar slug UK
        text description
        text git_url
        varchar git_branch
        jsonb deploy_config
        timestamptz created_at
    }

    applications {
        uuid id PK
        uuid project_id FK
        varchar name
        varchar slug UK
        varchar runtime
        varchar app_type
        text git_url
        text root_path
        varchar branch
        varchar container_id
        varchar container_name
        varchar status
        text url
        timestamptz created_at
    }

    deployments {
        uuid id PK
        uuid app_id FK
        varchar status
        text logs
        text git_url
        timestamptz created_at
    }

    invoices {
        uuid id PK
        varchar company_name
        varchar inn
        text description
        numeric amount
        varchar status
        varchar onec_id
        varchar onec_number
        timestamptz created_at
    }

    team_members {
        uuid id PK
        varchar name
        varchar email UK
        varchar role
        varchar status
        int projects
        varchar invite_token
        timestamptz invite_expires_at
        timestamptz invited_at
        timestamptz activated_at
        timestamptz last_seen_at
        varchar created_by
        timestamptz created_at
    }

    audit_logs {
        uuid id PK
        varchar actor_email
        varchar actor_role
        varchar action
        varchar resource_type
        varchar resource_id
        text message
        jsonb metadata
        varchar ip
        timestamptz created_at
    }

    team_call_sessions {
        uuid id PK
        varchar title
        varchar status
        varchar created_by
        varchar tldraw_room
        text tldraw_url
        timestamptz started_at
        timestamptz ended_at
        timestamptz created_at
    }

    team_call_messages {
        uuid id PK
        uuid session_id FK
        varchar author_email
        varchar author_name
        varchar kind
        text body
        timestamptz created_at
    }

    users {
        uuid id PK
        varchar email UK
        varchar name
        varchar password_hash
        timestamptz created_at
    }
```

## Группы таблиц

| Группа | Таблицы | Назначение |
|--------|---------|------------|
| Хостинг | `projects`, `applications`, `deployments` | Проекты, приложения, история деплоев |
| Биллинг | `invoices` | Счета и интеграция с 1С |
| Команда | `team_members`, `audit_logs` | Участники, роли, журнал действий |
| Созвоны | `team_call_sessions`, `team_call_messages` | Комнаты созвонов, чат и заметки доски |
| Auth (заготовка) | `users` | Локальные учётные записи (MVP) |

## Созвоны и realtime

```
team_call_sessions
  id              → room id для LiveKit и call WebSocket
  tldraw_room     → room id для tldraw sync WebSocket
  tldraw_url      → метаданные/ссылка на доску (legacy embed)
  status          → active | ended

team_call_messages
  session_id      → FK на team_call_sessions
  kind            → chat | whiteboard | system
  body            → текст сообщения или JSON-снимок доски
```

Realtime-слой **не хранится в PostgreSQL** (in-memory в gateway / tldraw-sync):

- Call signaling: `WS /api/v1/platform/ws/calls/{session_id}`
- Tldraw sync: `WS /api/v1/platform/ws/tldraw/{tldraw_room}`
- LiveKit SFU: отдельный сервис, токен через `GET /api/v1/platform/team/calls/{id}/livekit`

## Связи и каскады

- `applications.project_id` → `ON DELETE CASCADE`
- `deployments.app_id` → `ON DELETE CASCADE`
- `team_call_messages.session_id` → `ON DELETE CASCADE`

## Индексы

Явные индексы в `init_db()` не создаются. Для production рекомендуется добавить:

- `team_members(email)` — уже UNIQUE
- `team_call_sessions(status, created_at DESC)` — активный созвон
- `team_call_messages(session_id, created_at)` — история чата
- `audit_logs(created_at DESC)` — журнал аудита

import os
import re
import secrets
from datetime import datetime, timedelta, timezone
from hashlib import sha256

import jwt

from src.core.database import get_connection, serialize_row
from src.core.platform_settings import PLATFORM_SETTINGS
from src.core.rbac import CurrentUser, ROLE_DESCRIPTIONS, ROLE_LABELS, ROLE_PERMISSIONS
from src.repositories.audit_repository import AuditRepository

TLDRAW_BASE_URL = os.getenv("TLDRAW_BASE_URL", "https://www.tldraw.com/f").rstrip("/")
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "http://livekit:7880").rstrip("/")
LIVEKIT_PUBLIC_URL = os.getenv("LIVEKIT_PUBLIC_URL", "ws://localhost:7880").rstrip("/")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")
LIVEKIT_STUN_URLS = os.getenv("LIVEKIT_STUN_URLS", "stun:stun.l.google.com:19302").split(",")
LIVEKIT_TURN_URL = os.getenv("LIVEKIT_TURN_URL", "")
LIVEKIT_TURN_USERNAME = os.getenv("LIVEKIT_TURN_USERNAME", "")
LIVEKIT_TURN_PASSWORD = os.getenv("LIVEKIT_TURN_PASSWORD", "")

class PlatformRepository:
    def __init__(self, audit_repository: AuditRepository | None = None) -> None:
        self.audit = audit_repository or AuditRepository()

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256."""
        return sha256(password.encode()).hexdigest()

    def _check_password(self, password: str, password_hash: str) -> bool:
        """Check if password matches hash."""
        return self._hash_password(password) == password_hash

    def _get_user_by_email(self, email: str) -> dict | None:
        """Get user by email from database."""
        normalized_email = email.strip().lower()
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM users WHERE email = %s",
                    (normalized_email,),
                )
                row = cur.fetchone()
                return serialize_row(row)

    def _create_user(self, email: str, name: str, password: str) -> dict:
        """Create new user with hashed password."""
        normalized_email = email.strip().lower()
        password_hash = self._hash_password(password)
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (email, name, password_hash)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (email) DO UPDATE SET
                        name = EXCLUDED.name,
                        password_hash = EXCLUDED.password_hash
                    RETURNING *
                    """,
                    (normalized_email, name, password_hash),
                )
                conn.commit()
                return serialize_row(cur.fetchone()) or {}

    def resolve_access_for_email(
        self,
        email: str,
        *,
        auto_activate_invite: bool = False,
        touch_last_seen: bool = False,
    ) -> dict[str, object]:
        normalized_email = email.strip().lower()
        if not normalized_email or normalized_email == "anonymous@gcloude.local":
            return {
                "email": normalized_email or "anonymous@gcloude.local",
                "displayName": "Наблюдатель",
                "role": "viewer",
                "permissions": ROLE_PERMISSIONS["viewer"],
            }

        # Get owner email from PLATFORM_SETTINGS
        owner_email = PLATFORM_SETTINGS["contact_email"].lower()
        
        # Check if user exists in team_members table (from invite)
        member = self._find_team_member_by_email(normalized_email)
        
        # Ensure owner member exists (creates owner if not exists)
        self._ensure_owner_member()

        # If user has an invited status, auto-activate if requested
        if member and member.get("status") == "invited" and auto_activate_invite:
            self._activate_member_by_id(str(member["id"]))
            member = self._find_team_member_by_email(normalized_email)

        # Owner check - if email matches contact_email or if user is the only member
        if normalized_email == owner_email:
            role = "owner"
            display_name = PLATFORM_SETTINGS["contact_name"]
        elif member and member.get("status") == "active":
            # User exists in team_members and is active - use their role
            role = str(member["role"])
            if role not in ROLE_PERMISSIONS:
                role = "viewer"
            display_name = str(member["name"])
        elif member:
            # User exists in team_members but not active - use their role
            role = str(member["role"])
            if role not in ROLE_PERMISSIONS:
                role = "viewer"
            display_name = str(member["name"])
        else:
            # New user - check if this should be the owner
            # If no owner exists in team_members yet, this user becomes owner
            all_members = self._list_team_members()
            owner_exists = any(m.get("role") == "owner" and m.get("status") == "active" for m in all_members)
            
            if not owner_exists:
                # This is the first active user - make them owner
                role = "owner"
                display_name = normalized_email.split("@")[0].replace("-", " ").title()
                # Update PLATFORM_SETTINGS for future reference
                PLATFORM_SETTINGS["contact_name"] = display_name
                PLATFORM_SETTINGS["contact_email"] = normalized_email
                # Also update the member record to be owner
                with get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO team_members (name, email, role, status, activated_at)
                            VALUES (%s, %s, 'owner', 'active', now())
                            ON CONFLICT (email) DO UPDATE SET role = 'owner', status = 'active'
                            RETURNING *
                            """,
                            (display_name, normalized_email),
                        )
                        conn.commit()
                        member = self._format_team_member(serialize_row(cur.fetchone()))
            else:
                # Owner already exists, new user gets viewer role by default
                role = "viewer"
                display_name = normalized_email.split("@")[0].replace("-", " ").title()

        if touch_last_seen and member:
            self._touch_last_seen(normalized_email)

        return {
            "email": normalized_email,
            "displayName": display_name,
            "role": role,
            "permissions": ROLE_PERMISSIONS[role],
        }
        
    def login(self, email: str, password: str = "") -> dict[str, object]:
        normalized_email = email.strip().lower()
        
        # Validate password is provided
        if not password or not password.strip():
            raise ValueError("Password is required")
        
        # Get user from database
        user = self._get_user_by_email(normalized_email)
        if not user:
            raise ValueError("Invalid email or password")
        
        # Check password
        if not self._check_password(password, user.get("password_hash", "")):
            raise ValueError("Invalid email or password")
        
        access = self.resolve_access_for_email(
            email,
            auto_activate_invite=True,
            touch_last_seen=True,
        )
        return {
            "companyName": PLATFORM_SETTINGS["workspace_name"],
            **access,
            "token": "local-platform-token",
        }

    def session_for_email(self, email: str) -> dict[str, object]:
        access = self.resolve_access_for_email(
            email,
            auto_activate_invite=True,
            touch_last_seen=True,
        )
        return {
            "companyName": PLATFORM_SETTINGS["workspace_name"],
            **access,
            "token": "local-platform-token",
        }

    def register(
        self,
        display_name: str,
        email: str,
        password: str = "",
        workspace_name: str = "",
    ) -> dict[str, str]:
        # Validate password
        if not password or not password.strip():
            raise ValueError("Password is required")
        
        workspace = workspace_name.strip() or f"{display_name.split()[0]} workspace"
        
        # Create user in users table with hashed password
        self._create_user(email, display_name, password)
        
        PLATFORM_SETTINGS["workspace_name"] = workspace
        PLATFORM_SETTINGS["contact_name"] = display_name
        PLATFORM_SETTINGS["contact_email"] = email
        self._ensure_owner_member()
        return {
            "companyName": workspace,
            "displayName": display_name,
            "email": email,
            "role": "owner",
            "permissions": ROLE_PERMISSIONS["owner"],
            "token": "local-platform-token",
        }

    def get_settings_form(self) -> dict[str, str]:
        return dict(PLATFORM_SETTINGS)

    def update_settings(self, payload: dict[str, str], actor: CurrentUser | None = None) -> dict[str, str]:
        PLATFORM_SETTINGS.update(payload)
        self.audit.record(
            actor=actor,
            action="settings.update",
            resource_type="settings",
            resource_id="platform",
            message="Обновлены настройки платформы",
            metadata={"fields": sorted(payload.keys())},
        )
        return self.get_settings_form()

    def dashboard(self) -> dict[str, object]:
        return {
            "title": "Обзор кабинета",
            "description": "Единая сводка по проектам, приложениям, доменам и финансам.",
            "cards": [
                self._card("Проекты", "6 активных проектов в production и staging.", "В работе", "success", [self._fact("Команд", "4"), self._fact("Сред", "7")], [self._action("Открыть проекты", "/projects")]),
                self._card("Приложения", "12 клиентских сервисов доступны на локальных доменах.", "Стабильно", "success", [self._fact("Node.js", "5"), self._fact("Python", "7")], [self._action("Открыть приложения", "/applications")]),
                self._card("Биллинг", "2 счета ожидают оплаты и синхронизации с 1С.", "Контроль", "warning", [self._fact("Баланс", "186 500 ₽"), self._fact("Документы", "8")], [self._action("Перейти в биллинг", "/billing", "secondary")]),
            ],
        }

    def projects(self) -> dict[str, object]:
        return {
            "title": "Проекты",
            "description": "Группируйте приложения, домены, команды и среды по проектам.",
            "cards": [
                self._card("billing-core", "Финансовый контур с интеграцией 1С и очередями Kafka.", "Активен", "success", [self._fact("Приложений", "4"), self._fact("Среда", "production")], [self._action("Открыть проект", "/projects/billing-core")]),
                self._card("bot-platform", "Платформа чат-ботов с отдельными staging и production.", "Под контролем", "success", [self._fact("Приложений", "2"), self._fact("Среда", "staging")], [self._action("Открыть проект", "/projects/bot-platform")]),
                self._card("crm-gateway", "Контур CRM-интеграций и клиентских API.", "Подготовка", "warning", [self._fact("Приложений", "3"), self._fact("Среда", "production")], [self._action("Открыть проект", "/projects/crm-gateway")]),
            ],
        }

    def project_details(self, project_id: str) -> dict[str, object]:
        return {
            "title": f"Проект {project_id}",
            "description": "Настройки проекта, сервисы, домены и команда в одном месте.",
            "cards": [
                self._card("Состав проекта", "У проекта есть прод-контур, staging и обязательный набор доменов.", "Проект", "default", [self._fact("Команда", "5 человек"), self._fact("Домены", "3")], [self._action("Открыть домены", "/domains")]),
                self._card("Последний релиз", "Последний релиз прошёл без простоев и ошибок на локальном стенде.", "Успешно", "success", [self._fact("Версия", "v1.8.4"), self._fact("Деплой", "12 минут назад")], [self._action("Открыть деплои", "/deployments", "secondary")]),
            ],
        }

    def applications(self) -> dict[str, object]:
        crm_domain = f"crm.{PLATFORM_SETTINGS['default_app_domain']}"
        bot_domain = f"bot.{PLATFORM_SETTINGS['default_app_domain']}"
        return {
            "title": "Приложения",
            "description": "Управляйте клиентскими микросервисами, адресами и релизами.",
            "cards": [
                self._card("crm-api", "Основной Python-сервис для CRM-контуров.", "Healthy", "success", [self._fact("Домен", crm_domain), self._fact("Runtime", "python")], [self._action("Карточка приложения", "/microservices/crm-api"), self._action("Открыть домен", f"http://{crm_domain}", "secondary", True)]),
                self._card("bot-gateway", "Node.js шлюз для клиентских ботов и webhook-сценариев.", "Healthy", "success", [self._fact("Домен", bot_domain), self._fact("Runtime", "node")], [self._action("Карточка приложения", "/microservices/bot-gateway"), self._action("Открыть домен", f"http://{bot_domain}", "secondary", True)]),
                self._card("billing-worker", "Фоновый сервис для подготовки счетов и документов.", "Pending", "warning", [self._fact("Домен", "internal"), self._fact("Runtime", "python")], [self._action("Карточка приложения", "/microservices/billing-worker")]),
            ],
        }

    def application_details(self, service_id: str) -> dict[str, object]:
        base_domain = PLATFORM_SETTINGS["default_app_domain"]
        domain = f"crm.{base_domain}" if "crm" in service_id else f"bot.{base_domain}"
        return {
            "title": f"Приложение {service_id}",
            "description": "Состояние релиза, адрес, health-check и следующие действия.",
            "cards": [
                self._card("Текущий выпуск", "Приложение доступно в локальной среде через выделенный поддомен.", "Healthy", "success", [self._fact("Версия", "v1.4.2"), self._fact("Домен", domain)], [self._action("Открыть приложение", f"http://{domain}", "primary", True)]),
                self._card("Операции", "Запускайте публикацию, проверяйте активность и контролируйте rollout.", "Контроль", "default", [self._fact("Последний деплой", "20 минут назад"), self._fact("SSL", "локальная схема")], [self._action("История деплоев", "/deployments"), self._action("Журнал активности", "/logs", "secondary")]),
            ],
        }

    def domains(self) -> dict[str, object]:
        dashboard_host = PLATFORM_SETTINGS["dashboard_host"]
        api_host = PLATFORM_SETTINGS["api_host"]
        app_domain = PLATFORM_SETTINGS["default_app_domain"]
        return {
            "title": "Домены",
            "description": "Публичные адреса кабинета, API и приложений.",
            "cards": [
                self._card(dashboard_host, "Основной домен кабинета.", "Активен", "success", [self._fact("Маршрут", "frontend"), self._fact("HTTPS", "host nginx")], [self._action("Открыть кабинет", f"https://{dashboard_host}", "secondary", True)]),
                self._card(api_host, "Выделенный API-хост для gateway-service.", "Активен", "default", [self._fact("Маршрут", "gateway-service"), self._fact("Fallback", "/api")]),
                self._card(f"*.{app_domain}", "Шаблон поддоменов для задеплоенных приложений.", "Готов", "success", [self._fact("Зона", app_domain), self._fact("SSL", "через setup.sh")]),
            ],
        }

    def deployments(self) -> dict[str, object]:
        return {
            "title": "Деплои",
            "description": "Контроль сборок, публикаций и источников артефактов в локальной среде.",
            "cards": [
                self._card("billing-core production", "Последняя сборка прошла через registry и storage без ошибок.", "Успешно", "success", [self._fact("Источник", "git"), self._fact("Runtime", "python")]),
                self._card("bot-platform staging", "Ожидает подтверждения для публикации на локальный поддомен.", "Ожидает", "warning", [self._fact("Источник", "zip upload"), self._fact("Runtime", "node")]),
                self._card("crm-gateway production", "Артефакт уже собран и готов к rollout на стенд клиента.", "Готово", "success", [self._fact("Registry", "registry:5000"), self._fact("Storage", "/platform/storage")]),
            ],
        }

    def billing(self) -> dict[str, object]:
        return {
            "title": "Биллинг",
            "description": "Счета, баланс, юрлица и статус обмена с 1С.",
            "cards": [
                self._card("ООО Гклауд", "Основной договор по платформе и сопровождению инфраструктуры.", "Выставлен", "warning", [self._fact("Сумма", "54 000 ₽"), self._fact("1С", "ожидает оплаты")], [self._action("Документы", "/documents")]),
                self._card("North API JSC", "Счет по клиентскому production-контуру и выделенным доменам.", "Оплачен", "success", [self._fact("Сумма", "132 500 ₽"), self._fact("1С", "синхронизирован")], [self._action("Открыть документы", "/documents", "secondary")]),
            ],
        }

    def activity(self) -> dict[str, object]:
        crm_domain = f"crm.{PLATFORM_SETTINGS['default_app_domain']}"
        return {
            "title": "Активность и логи",
            "description": "История релизов, доменных изменений, счетов и действий команды.",
            "cards": [
                self._card("Релиз billing-core", "Новый релиз опубликован и проверен без деградации.", "12 минут назад", "success", [self._fact("Среда", "production"), self._fact("Статус", "healthy")]),
                self._card(f"Домен {crm_domain}", "Локальный маршрут подтвержден через nginx без ручной настройки hosts.", "25 минут назад", "default", [self._fact("Host", crm_domain), self._fact("Upstream", "demo-crm-app")]),
                self._card("Счёт для ООО Гклауд", "Документ сформирован и передан в бухгалтерский контур.", "1 час назад", "warning", [self._fact("Документ", "INV-2026-004"), self._fact("Статус", "ожидает оплаты")]),
            ],
        }

    def team_overview(self) -> dict[str, object]:
        self._ensure_owner_member()
        members = self._list_team_members()
        role_counts = {
            role: sum(1 for member in members if member["role"] == role)
            for role in ROLE_LABELS
        }
        return {
            "members": members,
            "roles": [
                {
                    "id": role,
                    "name": ROLE_LABELS[role],
                    "description": ROLE_DESCRIPTIONS[role],
                    "members": role_counts[role],
                    "permissions": ROLE_PERMISSIONS[role],
                }
                for role in ROLE_LABELS
            ],
        }

    def accept_team_invite(self, token: str) -> dict[str, object]:
        if not token or not token.strip():
            raise ValueError("Invite token is required.")
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM team_members WHERE invite_token = %s",
                    (token.strip(),),
                )
                row = serialize_row(cur.fetchone())
        if not row:
            raise ValueError("Invite not found. The link may be invalid or already used.")
        if row.get("status") not in ("invited",):
            raise ValueError("This invite is no longer valid.")
        expires_at = row.get("invite_expires_at")
        if expires_at:
            from datetime import datetime, timezone
            try:
                exp = datetime.fromisoformat(str(expires_at))
                if exp.tzinfo is None:
                    exp = exp.replace(tzinfo=timezone.utc)
                if exp < datetime.now(timezone.utc):
                    raise ValueError("Invite has expired. Ask the owner to resend the invite.")
            except ValueError as e:
                if "expired" in str(e):
                    raise
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE team_members
                    SET status = 'active',
                        invite_token = '',
                        activated_at = COALESCE(activated_at, now())
                    WHERE id = %s
                    """,
                    (row["id"],),
                )
                conn.commit()
        self.audit.record(
            actor=None,
            action="team.invite_accepted",
            resource_type="team_member",
            resource_id=str(row["email"]),
            message=f"Участник {row['email']} принял приглашение",
            metadata={"role": row["role"]},
        )
        return self.session_for_email(str(row["email"]))

    def invite_team_member(self, email: str, role: str = "ops", actor: CurrentUser | None = None) -> dict[str, object]:
        normalized_email = email.strip().lower()
        if not normalized_email or "@" not in normalized_email:
            raise ValueError("Valid email is required.")
        if role not in ROLE_LABELS or role == "owner":
            raise ValueError("Unknown team role.")
        if normalized_email == PLATFORM_SETTINGS["contact_email"].lower():
            raise ValueError("Owner is already in the team.")
        if self._find_team_member_by_email(normalized_email):
            raise ValueError("Team member already exists.")

        display_name = normalized_email.split("@", 1)[0].replace(".", " ").replace("-", " ").title()
        invite_token = secrets.token_urlsafe(24)
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO team_members
                      (name, email, role, status, invite_token, invite_expires_at, invited_at, created_by)
                    VALUES (%s, %s, %s, 'invited', %s, %s, now(), %s)
                    """,
                    (display_name, normalized_email, role, invite_token, expires_at, actor.email if actor else ""),
                )
                conn.commit()
        self.audit.record(
            actor=actor,
            action="team.invite",
            resource_type="team_member",
            resource_id=normalized_email,
            message=f"Приглашён участник {normalized_email}",
            metadata={"role": role, "expires_at": expires_at.isoformat()},
        )
        return self.team_overview()

    def update_team_member(
        self,
        member_id: str,
        role: str | None = None,
        status: str | None = None,
        actor: CurrentUser | None = None,
    ) -> dict[str, object]:
        member = self._find_team_member(member_id)
        if not member:
            raise ValueError("Team member not found.")
        if member["role"] == "owner":
            raise ValueError("Owner cannot be changed here.")
        if role is not None:
            if role not in ROLE_LABELS or role == "owner":
                raise ValueError("Unknown team role.")
            member["role"] = role
            member["role_label"] = ROLE_LABELS[role]
        if status is not None:
            if status not in {"active", "invited", "disabled"}:
                raise ValueError("Unknown team status.")
        fields: list[str] = []
        values: list[str] = []
        if role is not None:
            fields.append("role = %s")
            values.append(role)
        if status is not None:
            fields.append("status = %s")
            values.append(status)
            if status == "active":
                fields.append("activated_at = COALESCE(activated_at, now())")
        if fields:
            values.append(member_id)
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"UPDATE team_members SET {', '.join(fields)} WHERE id = %s",
                        values,
                    )
                    conn.commit()
        self.audit.record(
            actor=actor,
            action="team.update",
            resource_type="team_member",
            resource_id=member_id,
            message=f"Обновлён участник {member['email']}",
            metadata={"role": role, "status": status},
        )
        return self.team_overview()

    def delete_team_member(self, member_id: str, actor: CurrentUser | None = None) -> dict[str, object]:
        member = self._find_team_member(member_id)
        if not member:
            raise ValueError("Team member not found.")
        if member["role"] == "owner":
            raise ValueError("Owner cannot be removed.")
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM team_members WHERE id = %s", (member_id,))
                conn.commit()
        self.audit.record(
            actor=actor,
            action="team.delete",
            resource_type="team_member",
            resource_id=member_id,
            message=f"Удалён участник {member['email']}",
            metadata={"role": member["role"], "status": member["status"]},
        )
        return self.team_overview()

    def resend_team_invite(self, member_id: str, actor: CurrentUser | None = None) -> dict[str, object]:
        member = self._find_team_member(member_id)
        if not member:
            raise ValueError("Team member not found.")
        if member["status"] != "invited":
            raise ValueError("Only invited members can receive a new invite.")
        token = secrets.token_urlsafe(24)
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE team_members
                    SET invite_token = %s, invite_expires_at = %s, invited_at = now()
                    WHERE id = %s
                    """,
                    (token, expires_at, member_id),
                )
                conn.commit()
        self.audit.record(
            actor=actor,
            action="team.invite_resend",
            resource_type="team_member",
            resource_id=member_id,
            message=f"Повторно отправлено приглашение {member['email']}",
            metadata={"expires_at": expires_at.isoformat()},
        )
        return self.team_overview()

    def cancel_team_invite(self, member_id: str, actor: CurrentUser | None = None) -> dict[str, object]:
        member = self._find_team_member(member_id)
        if not member:
            raise ValueError("Team member not found.")
        if member["status"] != "invited":
            raise ValueError("Only invited members can be cancelled.")
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE team_members SET status = 'cancelled' WHERE id = %s", (member_id,))
                conn.commit()
        self.audit.record(
            actor=actor,
            action="team.invite_cancel",
            resource_type="team_member",
            resource_id=member_id,
            message=f"Отменено приглашение {member['email']}",
            metadata={"role": member["role"]},
        )
        return self.team_overview()

    def list_audit(self, limit: int = 80, resource_type: str = "") -> dict[str, object]:
        return {
            "items": self.audit.list(limit=limit, resource_type=resource_type),
            "stats": self.audit.stats(),
        }

    def create_call_session(self, title: str, actor: CurrentUser | None = None) -> dict[str, object]:
        # Idempotent: return the existing active call if one is already running.
        existing = self.get_active_call_session()
        if existing:
            return existing

        title = title.strip() or "Обсуждение проекта"
        room = self._tldraw_room(title)
        tldraw_url = self._build_tldraw_url(room)
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO team_call_sessions (title, created_by, tldraw_room, tldraw_url)
                    VALUES (%s, %s, %s, %s)
                    RETURNING *
                    """,
                    (title, actor.email if actor else "", room, tldraw_url),
                )
                conn.commit()
                session = serialize_row(cur.fetchone())
        self.audit.record(
            actor=actor,
            action="team.call_start",
            resource_type="team_call",
            resource_id=str(session["id"]),
            message=f"Создан созвон «{title}»",
            metadata={"tldraw_url": tldraw_url},
        )
        return self.get_call_session(str(session["id"]))

    def get_active_call_session(self) -> dict[str, object] | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM team_call_sessions WHERE status = 'active' ORDER BY created_at DESC LIMIT 1"
                )
                row = serialize_row(cur.fetchone())
        return self.get_call_session(str(row["id"])) if row else None

    def get_call_session(self, session_id: str) -> dict[str, object]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM team_call_sessions WHERE id = %s", (session_id,))
                session = serialize_row(cur.fetchone())
                if not session:
                    raise ValueError("Call session not found.")
                if not session.get("tldraw_url"):
                    room = self._tldraw_room(str(session["title"]))
                    tldraw_url = self._build_tldraw_url(room)
                    cur.execute(
                        "UPDATE team_call_sessions SET tldraw_room = %s, tldraw_url = %s WHERE id = %s RETURNING *",
                        (room, tldraw_url, session_id),
                    )
                    conn.commit()
                    session = serialize_row(cur.fetchone())
                else:
                    normalized_tldraw_url = self._normalize_tldraw_url(str(session["tldraw_url"]))
                    if normalized_tldraw_url != session["tldraw_url"]:
                        cur.execute(
                            "UPDATE team_call_sessions SET tldraw_url = %s WHERE id = %s",
                            (normalized_tldraw_url, session_id),
                        )
                        conn.commit()
                        session["tldraw_url"] = normalized_tldraw_url
                cur.execute(
                    "SELECT * FROM team_call_messages WHERE session_id = %s ORDER BY created_at ASC LIMIT 300",
                    (session_id,),
                )
                messages = [serialize_row(row) for row in cur.fetchall()]
        return {**session, "messages": messages}

    def end_call_session(self, session_id: str, actor: CurrentUser | None = None) -> dict[str, object]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE team_call_sessions
                    SET status = 'ended', ended_at = now()
                    WHERE id = %s
                    RETURNING *
                    """,
                    (session_id,),
                )
                row = serialize_row(cur.fetchone())
                conn.commit()
        if not row:
            raise ValueError("Call session not found.")
        self.audit.record(
            actor=actor,
            action="team.call_end",
            resource_type="team_call",
            resource_id=session_id,
            message=f"Завершён созвон «{row['title']}»",
        )
        return self.get_call_session(session_id)

    def get_livekit_connection(self, session_id: str, actor: CurrentUser | None = None) -> dict[str, str]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, status FROM team_call_sessions WHERE id = %s", (session_id,))
                session = serialize_row(cur.fetchone())
        if not session:
            raise ValueError("Call session not found.")
        if session["status"] != "active":
            raise ValueError("Call session is not active.")
        if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
            raise ValueError("LiveKit is not configured. Set LIVEKIT_API_KEY and LIVEKIT_API_SECRET.")

        identity_base = (actor.email if actor else "guest").strip().lower().replace("@", "-")
        identity = f"{identity_base}-{secrets.token_hex(4)}"
        now = int(datetime.now(tz=timezone.utc).timestamp())
        exp = now + 60 * 60 * 4  # 4 hours — enough for a long call
        payload = {
            "iss": LIVEKIT_API_KEY,
            "sub": identity,
            "identity": identity,   # explicit identity required by livekit-server v1.9+
            "kind": "standard",     # participant kind (standard vs agent)
            "nbf": now - 5,
            "exp": exp,
            "name": actor.display_name if actor else identity_base,
            "video": {
                "room": session_id,
                "roomJoin": True,
                "roomCreate": True,     # allow auto-creation of the room
                "canPublish": True,
                "canSubscribe": True,
                "canPublishData": True,
            },
        }
        token = jwt.encode(payload, LIVEKIT_API_SECRET, algorithm="HS256")
        result = {
            "identity": identity,
            "name": actor.display_name if actor else identity_base,
            "room": session_id,
            "token": token,
            "url": LIVEKIT_PUBLIC_URL,
            "stun_urls": LIVEKIT_STUN_URLS,
        }
        if LIVEKIT_TURN_URL:
            result["turn_url"] = LIVEKIT_TURN_URL
            result["turn_username"] = LIVEKIT_TURN_USERNAME
            result["turn_password"] = LIVEKIT_TURN_PASSWORD
        return result

    def add_call_message(
        self,
        session_id: str,
        body: str,
        kind: str = "chat",
        actor: CurrentUser | None = None,
    ) -> dict[str, object]:
        clean_body = body.strip()
        if not clean_body:
            raise ValueError("Message is required.")
        if kind not in {"chat", "whiteboard", "system"}:
            raise ValueError("Unknown message kind.")
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM team_call_sessions WHERE id = %s", (session_id,))
                if not cur.fetchone():
                    raise ValueError("Call session not found.")
                cur.execute(
                    """
                    INSERT INTO team_call_messages (session_id, author_email, author_name, kind, body)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING *
                    """,
                    (
                        session_id,
                        actor.email if actor else "",
                        actor.display_name if actor else "",
                        kind,
                        clean_body,
                    ),
                )
                conn.commit()
                message = serialize_row(cur.fetchone())
        if kind == "chat":
            self.audit.record(
                actor=actor,
                action="team.call_message",
                resource_type="team_call",
                resource_id=session_id,
                message="Сообщение в созвоне",
            )
        return message

    def _build_tldraw_url(self, room: str) -> str:
        if not TLDRAW_BASE_URL:
            return room
        return self._normalize_tldraw_url(f"{TLDRAW_BASE_URL}/{room}")

    def _normalize_tldraw_url(self, value: str) -> str:
        separator = "&" if "?" in value else "?"
        return value if "embed=" in value else f"{value}{separator}embed=1"

    def _tldraw_room(self, title: str) -> str:
        slug = re.sub(r"[^a-z0-9-]+", "-", title.lower()).strip("-")[:40] or "project"
        return f"gcloude-{slug}-{secrets.token_urlsafe(8).lower().replace('_', '-').replace('-', '')[:10]}"

    def team(self) -> dict[str, object]:
        overview = self.team_overview()
        members = overview["members"]
        return {
            "title": "Команда",
            "description": "Участники кабинета, роли и зоны ответственности по проектам.",
            "cards": [
                self._card(
                    m["name"],
                    f'{m["role_label"]} · {m["email"]}',
                    "Активен" if m["status"] == "active" else "Приглашён",
                    "success" if m["status"] == "active" else "warning",
                    [self._fact("Проекты", str(m["projects"])), self._fact("Роль", m["role_label"])],
                )
                for m in members
            ],
        }

    def _ensure_owner_member(self) -> dict[str, object]:
        name = PLATFORM_SETTINGS["contact_name"]
        email = PLATFORM_SETTINGS["contact_email"].lower()
        existing = self._find_team_member_by_email(email)
        if existing:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE team_members
                        SET name = %s, role = 'owner', status = 'active',
                            activated_at = COALESCE(activated_at, now())
                        WHERE email = %s
                        """,
                        (name, email),
                    )
                    conn.commit()
            return self._find_team_member_by_email(email) or existing
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO team_members (name, email, role, status, activated_at)
                    VALUES (%s, %s, 'owner', 'active', now())
                    RETURNING *
                    """,
                    (name, email),
                )
                conn.commit()
                return self._format_team_member(serialize_row(cur.fetchone()))

    def _list_team_members(self) -> list[dict[str, object]]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM team_members ORDER BY created_at DESC")
                return [self._format_team_member(serialize_row(row)) for row in cur.fetchall()]

    def _find_team_member(self, member_id: str) -> dict[str, object] | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM team_members WHERE id = %s", (member_id,))
                row = serialize_row(cur.fetchone())
                return self._format_team_member(row) if row else None

    def _find_team_member_by_email(self, email: str) -> dict[str, object] | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM team_members WHERE email = %s", (email,))
                row = serialize_row(cur.fetchone())
                return self._format_team_member(row) if row else None

    def _activate_member_by_id(self, member_id: str) -> None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE team_members
                    SET status = 'active', activated_at = COALESCE(activated_at, now())
                    WHERE id = %s AND status = 'invited'
                    """,
                    (member_id,),
                )
                conn.commit()

    def _touch_last_seen(self, email: str) -> None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE team_members SET last_seen_at = now() WHERE email = %s",
                    (email.lower(),),
                )
                conn.commit()

    def _format_team_member(self, row: dict[str, object]) -> dict[str, object]:
        name = str(row["name"])
        role = str(row["role"])
        invite_expires_at = row.get("invite_expires_at")
        invite_url = ""
        if row.get("invite_token"):
            invite_url = f"/accept-invite?token={row['invite_token']}"
        return {
            "id": str(row["id"]),
            "name": name,
            "email": str(row["email"]),
            "role": role,
            "role_label": ROLE_LABELS.get(role, role),
            "projects": int(row.get("projects") or 0),
            "status": str(row["status"]),
            "initials": self._initials(name),
            "permissions": ROLE_PERMISSIONS.get(role, []),
            "invite_url": invite_url,
            "invite_expires_at": invite_expires_at,
            "invited_at": row.get("invited_at"),
            "activated_at": row.get("activated_at"),
            "last_seen_at": row.get("last_seen_at"),
            "created_at": row.get("created_at"),
        }

    def _initials(self, name: str) -> str:
        parts = name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return name[:2].upper() if name else "??"

    def access(self) -> dict[str, object]:
        overview = self.team_overview()
        return {
            "title": "Доступы и роли",
            "description": "Настройка прав для владельцев, операторов, финансов и приглашённых пользователей.",
            "cards": [
                self._card(
                    role["name"],
                    role["description"],
                    "Активна",
                    "success" if role["id"] == "owner" else "default",
                    [
                        self._fact("Пользователей", str(role["members"])),
                        self._fact("Прав", str(len(role["permissions"]))),
                    ],
                )
                for role in overview["roles"]
            ],
        }

    def settings(self) -> dict[str, object]:
        return {
            "title": "Настройки",
            "description": "Параметры кабинета, API, уведомлений и локальной среды для демо.",
            "cards": [
                self._card("API контур", "Кабинет использует same-origin маршрут `/api` и работает даже без hosts.", "Включен", "success", [self._fact("Base URL", "/api"), self._fact("Gateway", "gateway-service")]),
                self._card("Уведомления", "Оповещения по релизам, ошибкам и оплатам собраны в один канал.", "Настроено", "default", [self._fact("Email", PLATFORM_SETTINGS["contact_email"]), self._fact("Событий", "12/день")]),
                self._card("Локальный стенд", "Домены на `.localhost` работают как базовая схема для кабинета и демо-приложений.", "Готов", "success", [self._fact("Dashboard", f"http://{PLATFORM_SETTINGS['dashboard_host']}"), self._fact("Apps", PLATFORM_SETTINGS["default_app_domain"])]),
            ],
        }

    def documents(self) -> dict[str, object]:
        return {
            "title": "Документы",
            "description": "Счета, акты и бухгалтерские документы для юрлиц.",
            "cards": [
                self._card("INV-2026-004", "Счёт по инфраструктуре и сопровождению production-контура.", "Ожидает оплаты", "warning", [self._fact("Юрлицо", "ООО Гклауд"), self._fact("Сумма", "54 000 ₽")]),
                self._card("ACT-2026-001", "Акт по релизам и поддержке микросервисов за март.", "Подписан", "success", [self._fact("Юрлицо", "North API JSC"), self._fact("Период", "Март 2026")]),
            ],
        }

    def _action(
        self,
        label: str,
        to: str,
        tone: str = "primary",
        external: bool = False,
    ) -> dict[str, object]:
        return {"label": label, "to": to, "tone": tone, "external": external}

    def _card(
        self,
        title: str,
        description: str,
        badge_label: str,
        badge_tone: str,
        facts: list[dict[str, str]],
        actions: list[dict[str, object]] | None = None,
    ) -> dict[str, object]:
        return {
            "title": title,
            "description": description,
            "badge": {"label": badge_label, "tone": badge_tone},
            "facts": facts,
            "actions": actions or [],
        }

    def _fact(self, label: str, value: str) -> dict[str, str]:
        return {"label": label, "value": value}

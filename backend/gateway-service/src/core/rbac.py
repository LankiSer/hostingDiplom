from dataclasses import dataclass
from typing import Callable

from fastapi import Depends, Header, HTTPException


ROLE_LABELS = {
    "owner": "Владелец",
    "ops": "DevOps",
    "finance": "Финансы",
    "viewer": "Наблюдатель",
}

ROLE_DESCRIPTIONS = {
    "owner": "Полный доступ к платформе, команде, биллингу и настройкам.",
    "ops": "Управляет проектами, деплоями, доменами, SSL и логами.",
    "finance": "Работает со счетами, документами и выгрузкой для 1С.",
    "viewer": "Смотрит состояние платформы без права менять данные.",
}

ROLE_PERMISSIONS = {
    "owner": [
        "projects:read",
        "projects:write",
        "deploys:read",
        "deploys:write",
        "domains:read",
        "domains:write",
        "logs:read",
        "billing:read",
        "billing:write",
        "documents:read",
        "settings:read",
        "settings:write",
        "team:read",
        "team:write",
        "audit:read",
        "calls:read",
        "calls:write",
    ],
    "ops": [
        "projects:read",
        "projects:write",
        "deploys:read",
        "deploys:write",
        "domains:read",
        "domains:write",
        "logs:read",
        "team:read",
        "audit:read",
        "calls:read",
        "calls:write",
    ],
    "finance": [
        "billing:read",
        "billing:write",
        "documents:read",
        "team:read",
        "audit:read",
        "calls:read",
        "calls:write",
    ],
    "viewer": [
        "projects:read",
        "deploys:read",
        "domains:read",
        "logs:read",
        "billing:read",
        "documents:read",
        "team:read",
        "audit:read",
        "calls:read",
        "calls:write",
    ],
}


@dataclass(frozen=True)
class CurrentUser:
    email: str
    role: str
    display_name: str
    permissions: list[str]


def current_user(
    x_platform_email: str = Header(default="anonymous@gcloude.local"),
    x_platform_role: str = Header(default="viewer"),
    x_platform_name: str = Header(default="Наблюдатель"),
) -> CurrentUser:
    from src.repositories.platform_repository import PlatformRepository

    email = x_platform_email.strip().lower() or "anonymous@gcloude.local"
    access = PlatformRepository().resolve_access_for_email(
        email,
        auto_activate_invite=True,
    )
    display_name = x_platform_name.strip() or str(access["displayName"])
    role = str(access["role"])
    permissions = list(access["permissions"])
    return CurrentUser(
        email=email,
        role=role,
        display_name=display_name,
        permissions=permissions,
    )


def has_permission(user: CurrentUser, permission: str) -> bool:
    return permission in user.permissions


def require_permission(permission: str) -> Callable[[CurrentUser], CurrentUser]:
    def dependency(user: CurrentUser = Depends(current_user)) -> CurrentUser:
        if not has_permission(user, permission):
            raise HTTPException(status_code=403, detail=f"Permission required: {permission}")
        return user

    return dependency

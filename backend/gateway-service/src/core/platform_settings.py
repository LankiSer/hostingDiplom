import os


def load_platform_settings() -> dict[str, str]:
    base = os.getenv("BASE_DOMAIN", "").strip()
    app_domain = os.getenv("APP_DOMAIN", "").strip() or os.getenv("APPS_DOMAIN", "").strip()
    if not app_domain and base:
        app_domain = f"apps.{base}"
    dashboard = os.getenv("DASHBOARD_HOST", "").strip() or (f"app.{base}" if base else "")
    api_host = os.getenv("API_HOST", "").strip() or (f"api.{base}" if base else "")

    return {
        "api_host": api_host or "api.localhost",
        "company_name": "gcloude",
        "contact_email": "owner@gcloude.ru",
        "contact_name": "Platform Owner",
        "dashboard_host": dashboard or "dashboard.localhost",
        "default_app_domain": app_domain or "apps.localhost",
        "support_email": f"support@{base}" if base else "support@localhost",
        "workspace_name": "gcloude control",
    }


PLATFORM_SETTINGS = load_platform_settings()

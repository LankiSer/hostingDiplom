PLATFORM_SETTINGS = {
    "api_host": "api.localhost",
    "company_name": "ООО Гклауд",
    "contact_email": "owner@gcloude.ru",
    "contact_name": "Александр Смирнов",
    "dashboard_host": "dashboard.localhost",
    "default_app_domain": "apps.localhost",
    "support_email": "support@localhost",
    "workspace_name": "gcloude control",
}


class PlatformRepository:
    def login(self, email: str, organization: str) -> dict[str, str]:
        return {
            "companyName": organization or PLATFORM_SETTINGS["company_name"],
            "displayName": PLATFORM_SETTINGS["contact_name"],
            "email": email,
            "role": "owner",
            "token": "local-platform-token",
        }

    def register(
        self,
        company_name: str,
        contact_name: str,
        email: str,
        inn: str,
    ) -> dict[str, str]:
        PLATFORM_SETTINGS["company_name"] = company_name
        PLATFORM_SETTINGS["contact_name"] = contact_name
        PLATFORM_SETTINGS["contact_email"] = email
        return {
            "companyName": company_name,
            "displayName": contact_name,
            "email": email,
            "role": "owner",
            "token": f"local-platform-token-{inn}",
        }

    def get_settings_form(self) -> dict[str, str]:
        return dict(PLATFORM_SETTINGS)

    def update_settings(self, payload: dict[str, str]) -> dict[str, str]:
        PLATFORM_SETTINGS.update(payload)
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
        crm_domain = f"crm.{PLATFORM_SETTINGS['default_app_domain']}"
        return {
            "title": "Домены",
            "description": "Локальные и будущие публичные адреса сервисов под контролем из кабинета.",
            "cards": [
                self._card("localhost", "Базовая точка входа без обязательной настройки hosts.", "Рекомендуется", "success", [self._fact("Маршрут", "frontend + /api"), self._fact("Доступ", "через nginx")]),
                self._card(dashboard_host, "Основной домен кабинета без правки hosts.", "Активен", "success", [self._fact("Маршрут", "frontend"), self._fact("Открытие", f"http://{dashboard_host}")], [self._action("Открыть кабинет", f"http://{dashboard_host}", "secondary", True)]),
                self._card(api_host, "Выделенный API-хост для локального BFF без отдельной настройки DNS.", "Активен", "default", [self._fact("Маршрут", "gateway-service"), self._fact("Fallback", "localhost/api")]),
                self._card(crm_domain, "Клиентский поддомен для демонстрации работы микросервисов.", "Активен", "success", [self._fact("Upstream", "demo-crm-app"), self._fact("Открытие", f"http://{crm_domain}")], [self._action("Открыть сервис", f"http://{crm_domain}", "secondary", True)]),
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

    def team(self) -> dict[str, object]:
        return {
            "title": "Команда",
            "description": "Участники кабинета, роли и зоны ответственности по проектам.",
            "cards": [
                self._card("Александр Смирнов", "Владелец кабинета и ответственный за клиентскую инфраструктуру.", "Owner", "success", [self._fact("Проекты", "6"), self._fact("Доступ", "полный")]),
                self._card("Марина Ковалева", "Финансы и документы по юрлицам.", "Finance", "default", [self._fact("Проекты", "2"), self._fact("Доступ", "billing")]),
                self._card("Илья Воронцов", "Релизы, домены и наблюдаемость production-сервисов.", "Ops", "default", [self._fact("Проекты", "4"), self._fact("Доступ", "deploys + logs")]),
            ],
        }

    def access(self) -> dict[str, object]:
        return {
            "title": "Доступы и роли",
            "description": "Настройка прав для владельцев, операторов, финансов и приглашённых пользователей.",
            "cards": [
                self._card("Owner", "Полный доступ к проектам, приложениям, счетам и настройкам.", "Главная роль", "success", [self._fact("Пользователей", "1"), self._fact("Ограничения", "нет")]),
                self._card("Operations", "Доступ к деплоям, доменам, логам и здоровью приложений.", "Операции", "default", [self._fact("Пользователей", "2"), self._fact("Ограничения", "без billing")]),
                self._card("Finance", "Просмотр баланса, счетов и документов для 1С.", "Финансы", "default", [self._fact("Пользователей", "1"), self._fact("Ограничения", "только billing")]),
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

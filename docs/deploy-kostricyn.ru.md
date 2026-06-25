# Деплой на kostricyn.ru

DNS → HTTP nginx → SSL для кабинета → HTTPS → **отдельный бесплатный сертификат на каждый поддомен приложения** при деплое.

## Схема доменов

| Домен | Назначение | SSL |
|-------|------------|-----|
| `app.kostricyn.ru` | Кабинет (frontend + `/api`) | один cert (app + api) |
| `api.kostricyn.ru` | Gateway API | тот же cert |
| `<slug>.apps.kostricyn.ru` | Приложение из Git | **свой cert на каждый slug** |

Wildcard SSL **не используется** — Let's Encrypt HTTP-01 на каждый поддомен отдельно.

## 1. DNS

Минимум для старта:

```
app.kostricyn.ru   →  IP сервера
api.kostricyn.ru   →  IP сервера
```

Для приложений — **на каждый slug** (или wildcard DNS только для удобства, SSL всё равно отдельный):

```
myweb.apps.kostricyn.ru   →  IP сервера
api-backend.apps.kostricyn.ru   →  IP сервера
```

Либо одна wildcard **DNS**-запись (не SSL):

```
*.apps.kostricyn.ru   →  IP сервера
```

Тогда новые поддомены резолвятся сразу, а сертификат платформа получит сама при деплое.

## 2. Подготовка сервера

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER

git clone <repo> /opt/hosting
cd /opt/hosting/infrastructure/docker
cp .env.production.example .env.production
nano .env.production
```

```env
BASE_DOMAIN=kostricyn.ru
NGINX_CONFIG=nginx.http.conf
NGINX_SSL_ENABLED=false
SSL_AUTO_ISSUE=true
CERTBOT_EMAIL=kostricyn50@mail.ru
```

## 3. Запуск (HTTP)

```bash
cd /opt/hosting/infrastructure/scripts
chmod +x *.sh
./deploy-production.sh
```

Проверка: `http://app.kostricyn.ru`

## 4. SSL для кабинета

```bash
./issue-ssl.sh
```

Делает certbot для `app` + `api`, включает `nginx.https.conf`, `SSL_AUTO_ISSUE=true`.

## 5. SSL для каждого приложения

Для приложений нужен DNS:

```dns
*.apps.kostricyn.ru  A  <IP сервера>
```

В режиме внешнего nginx (`HOST_NGINX_MODE=true`) TLS для приложений завершается на host nginx:

1. Gateway пишет HTTP-конфиг приложения в `platform.d`.
2. Certbot выпускает сертификат для конкретного `slug.apps.kostricyn.ru`.
3. Host nginx берёт сертификат по SNI из `/etc/letsencrypt/live/$ssl_server_name/`.
4. HTTPS-запрос проксируется внутрь на platform nginx `127.0.0.1:8080`.

Для уже созданного приложения можно открыть карточку приложения и нажать **«Выпустить SSL»**.

### Вручную, если авто не сработало

```bash
./issue-app-ssl.sh myweb
# затем передеплойте приложение или обновите nginx-конфиг из кабинета
```

## 6. Hot reload nginx

```bash
./reload-nginx.sh
```

При каждом деплое reload вызывается автоматически.

## 7. Настройки в кабинете

**Настройки → Домены:**

| Поле | Значение |
|------|----------|
| Домен кабинета | `app.kostricyn.ru` |
| Домен API | `api.kostricyn.ru` |
| Базовый домен приложений | `apps.kostricyn.ru` |

## 8. Продление (cron)

`certbot renew` продлевает **все** сертификаты, включая каждый app-поддомен:

```
0 3 * * * /opt/hosting/infrastructure/scripts/renew-ssl.sh >> /var/log/certbot-renew.log 2>&1
```

## 9. Порты

- `80` — ACME + редирект (кабинет) / выпуск cert (apps)
- `443` — HTTPS

## Troubleshooting

| Проблема | Решение |
|----------|---------|
| certbot failed for app | DNS не указывает на сервер; подождите TTL |
| HTTP работает, HTTPS нет | `./issue-app-ssl.sh <slug>` |
| 404 на поддомене | Приложение не задеплоено или нет записи в `platform.d` |
| Лимит Let's Encrypt | ~50 cert/домен/нед — для личного хостинга обычно достаточно |

## Файлы

| Файл | Описание |
|------|----------|
| `nginx/production/nginx.http.conf` | Старт без SSL |
| `nginx/production/nginx.https.conf` | Кабинет + API на HTTPS |
| `nginx/platform.d/<slug>.conf` | Каждое приложение (HTTP→HTTPS) |
| `gateway ... certbot_service.py` | Certbot на каждый деплой |
| `scripts/issue-app-ssl.sh` | Ручной cert для одного slug |

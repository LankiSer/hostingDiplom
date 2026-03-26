# Local Development

## Host Names

Add these entries to `C:\Windows\System32\drivers\etc\hosts`:

```text
127.0.0.1 dashboard.gcloude.local
127.0.0.1 api.gcloude.local
127.0.0.1 crm.apps.gcloude.local
127.0.0.1 bot.apps.gcloude.local
```

## Local Entry Points

- `http://localhost` - dashboard without `hosts`
- `http://localhost/api/v1/platform/dashboard` - local API/BFF without `hosts`
- `http://dashboard.gcloude.local` - customer dashboard through local host name
- `http://api.gcloude.local/api/v1/platform/dashboard` - dedicated API host if `hosts` is configured
- `http://crm.apps.gcloude.local` - demo CRM microservice
- `http://bot.apps.gcloude.local` - demo bot microservice

## Run Stack

From `infrastructure/docker`, start the platform with Docker Compose and open the dashboard via `http://localhost` or `dashboard.gcloude.local`. The dashboard uses same-origin `/api`, so login and registration work even if only `localhost` is configured. Explicit `hosts` entries are still needed for demo subdomains like `crm.apps.gcloude.local`.

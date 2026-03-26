from src.domain.entities import RouteEntity


class GatewayRepository:
    def list_routes(self) -> list[RouteEntity]:
        return [
            RouteEntity(path="/api/v1/auth/login", service="auth-service"),
            RouteEntity(path="/api/v1/projects", service="project-service"),
            RouteEntity(path="/api/v1/deployments", service="deploy-service"),
        ]

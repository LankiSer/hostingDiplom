from src.domain.entities import DomainEntity, SslEntity


class DomainRepository:
    def assign_domain(self, service_name: str, subdomain: str) -> DomainEntity:
        return DomainEntity(service_name=service_name, subdomain=subdomain, ssl="pending")

    def get_ssl_status(self, service_name: str) -> SslEntity:
        return SslEntity(service_name=service_name, ssl="wildcard", status="active")

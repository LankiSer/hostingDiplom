from src.domain.entities import OrganizationEntity


class AuthRepository:
    def save_organization(
        self,
        company_name: str,
        email: str,
        inn: str,
    ) -> OrganizationEntity:
        return OrganizationEntity(
            company_name=company_name,
            email=email,
            inn=inn,
            status="created",
        )

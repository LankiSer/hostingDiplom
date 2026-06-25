from src.domain.entities import UserSession
from src.repositories.repository import AuthRepository
from src.schemas.contracts import OrganizationRegistrationRequest


class AuthService:
    def __init__(self, repository: AuthRepository | None = None) -> None:
        self.repository = repository or AuthRepository()

    def login(self, email: str) -> UserSession:
        # For MVP, we allow login with any email
        # In production, add password validation here
        return UserSession(email=email, token="demo-jwt-token", token_type="bearer")

    def register_organization(
        self,
        payload: OrganizationRegistrationRequest,
    ) -> dict[str, str]:
        # For MVP, we don't validate password
        entity = self.repository.save_organization(
            company_name=payload.company_name,
            email=payload.email,
            inn=payload.inn,
        )
        return {"company_name": entity.company_name, "email": entity.email, "status": entity.status}

from dataclasses import asdict

from src.repositories.repository import UserRepository
from src.schemas.contracts import UserCreateRequest


class UserService:
    def __init__(self, repository: UserRepository | None = None) -> None:
        self.repository = repository or UserRepository()

    def list_users(self) -> list[dict[str, str]]:
        return [asdict(user) for user in self.repository.list_users()]

    def create_user(self, payload: UserCreateRequest) -> dict[str, str]:
        return asdict(self.repository.create_user(email=payload.email, role=payload.role))

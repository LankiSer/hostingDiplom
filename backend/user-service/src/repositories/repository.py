from src.domain.entities import UserEntity


class UserRepository:
    def list_users(self) -> list[UserEntity]:
        return [UserEntity(email="owner@gcloude.ru", role="owner", status="active")]

    def create_user(self, email: str, role: str) -> UserEntity:
        return UserEntity(email=email, role=role, status="created")

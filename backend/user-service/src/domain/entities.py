from dataclasses import dataclass


@dataclass(slots=True)
class UserEntity:
    email: str
    role: str
    status: str

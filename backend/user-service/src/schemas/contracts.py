from pydantic import BaseModel


class UserCreateRequest(BaseModel):
    email: str
    role: str


class UserResponse(BaseModel):
    email: str
    role: str
    status: str

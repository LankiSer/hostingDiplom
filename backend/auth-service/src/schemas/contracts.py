from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    email: str
    token: str
    type: str


class OrganizationRegistrationRequest(BaseModel):
    company_name: str
    email: str
    inn: str = ""


class RegisterRequest(BaseModel):
    email: str
    password: str = ""
    company_name: str = ""
    name: str = ""
    display_name: str = ""


class OrganizationRegistrationResponse(BaseModel):
    company_name: str
    email: str
    status: str

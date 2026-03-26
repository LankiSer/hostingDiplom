from pydantic import BaseModel


class RouteResponse(BaseModel):
    path: str
    service: str

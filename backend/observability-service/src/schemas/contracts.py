from pydantic import BaseModel


class EventResponse(BaseModel):
    target: str
    type: str


class LogResponse(BaseModel):
    lines: list[str]
    service_name: str

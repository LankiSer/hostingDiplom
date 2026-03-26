from dataclasses import dataclass


@dataclass(slots=True)
class RouteEntity:
    path: str
    service: str

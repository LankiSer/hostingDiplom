from dataclasses import dataclass


@dataclass(slots=True)
class EventEntity:
    target: str
    type: str

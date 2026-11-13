from dataclasses import dataclass
from datetime import date


@dataclass
class Feedback:
    id: str
    received: date
    channel: str
    route: str
    stop: str
    text: str
    category: str = "other"
    duplicate_of: str = ""  # id of the original message, empty if this is not a copy

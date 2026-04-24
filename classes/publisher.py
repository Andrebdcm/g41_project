from dataclasses import dataclass
from datetime import datetime

@dataclass
class Publisher:
    publisher_id: int
    publisher_name: str
    created_date: datetime

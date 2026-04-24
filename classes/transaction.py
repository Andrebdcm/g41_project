from dataclasses import dataclass
from datetime import datetime

@dataclass
class Transaction:
    transaction_date: datetime
    amount: float
    publisher_id: int
    magazine_id: int

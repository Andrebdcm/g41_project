from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .gclass import Gclass

@dataclass
class Transaction(Gclass):
    transaction_id: Optional[int] = None
    transaction_date: Optional[datetime] = None
    amount: float = 0.0
    publisher_id: Optional[int] = None
    magazine_id: Optional[int] = None

    @classmethod
    def from_row(cls, row: dict):
        tx_date = None
        if row.get('transaction_date'):
            try:
                tx_date = datetime.strptime(row['transaction_date'], '%Y/%m/%d')
            except:
                pass
        amt = 0.0
        try:
            amt = float(row.get('amount') or 0)
        except:
            pass
        return cls(
            transaction_date=tx_date,
            amount=amt,
            publisher_id=int(row.get('publisher_id')) if row.get('publisher_id') else None,
            magazine_id=int(row.get('magazine_id')) if row.get('magazine_id') else None
        )

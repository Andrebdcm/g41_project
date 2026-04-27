#Entregue por Gonçalo

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .gclass import Gclass

@dataclass
class Publisher(Gclass):
    publisher_id: int = None
    publisher_name: str = ''
    created_date: Optional[datetime] = None

    @classmethod
    def from_row(cls, row: dict):
        created = None
        if row.get('created_date'):
            try:
                created = datetime.strptime(row['created_date'], '%Y/%m/%d')
            except:
                pass
        return cls(
            id=row.get('publisher_id'),
            publisher_id=int(row.get('publisher_id')) if row.get('publisher_id') else None,
            publisher_name=row.get('publisher_name', '').strip(),
            created_date=created
        )

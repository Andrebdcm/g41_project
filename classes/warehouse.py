#Leonor entrega

from dataclasses import dataclass
from typing import Optional
from .gclass import Gclass

@dataclass
class Warehouse(Gclass):
    warehouses_id: Optional[int] = None
    warehouses_info: str = ''

    @classmethod
    def from_row(cls, row: dict):
        wid = row.get('warehouses_id')
        try:
            wid_val = int(wid) if wid not in (None, '', '0') else None
        except:
            wid_val = None
        return cls(
            id=wid_val,
            warehouses_id=wid_val,
            warehouses_info=row.get('warehouses_info', '').strip()
        )

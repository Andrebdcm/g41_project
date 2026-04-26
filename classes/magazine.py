from dataclasses import dataclass
from .gclass import Gclass

@dataclass
class Magazine(Gclass):
    magazine_id: int = None
    magazine_title: str = ''
    magazine_category: str = ''

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id=row.get('magazine_id'),
            magazine_id=int(row.get('magazine_id')) if row.get('magazine_id') else None,
            magazine_title=row.get('magazine_title', '').strip(),
            magazine_category=row.get('magazine_category', '').strip()
        )

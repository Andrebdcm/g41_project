#Entregue por Leonor


from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass
class Gclass:
    id: Optional[int] = None
  
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

from dataclasses import dataclass
from typing import Callable
@dataclass(frozen=True)
class Migration:
    from_version:int
    to_version:int
    fn:Callable[[dict],dict]
    name:str=""

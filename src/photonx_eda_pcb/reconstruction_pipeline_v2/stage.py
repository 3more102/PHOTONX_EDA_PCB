from dataclasses import dataclass
from typing import Callable
@dataclass(frozen=True)
class Stage:
    name:str
    fn:Callable
    requires:tuple[str,...]=()
    produces:tuple[str,...]=()

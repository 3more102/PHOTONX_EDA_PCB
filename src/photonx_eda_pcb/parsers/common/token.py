from dataclasses import dataclass
@dataclass(frozen=True)
class Token:
    kind:str
    text:str
    line:int
    column:int=1

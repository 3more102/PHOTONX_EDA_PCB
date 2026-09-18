from dataclasses import dataclass
@dataclass(frozen=True)
class Query:
    field:str
    operator:str
    value:object

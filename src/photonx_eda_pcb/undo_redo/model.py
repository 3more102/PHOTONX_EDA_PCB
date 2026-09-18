from dataclasses import dataclass
@dataclass(frozen=True)
class Change:
    key:str
    before:object
    after:object
    label:str=""

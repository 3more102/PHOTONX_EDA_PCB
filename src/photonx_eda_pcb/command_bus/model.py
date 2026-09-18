from dataclasses import dataclass,field
@dataclass(frozen=True)
class Command:
    name:str
    payload:dict=field(default_factory=dict)
    source:str="user"

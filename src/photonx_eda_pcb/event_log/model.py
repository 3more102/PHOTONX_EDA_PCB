from dataclasses import dataclass,field
@dataclass(frozen=True)
class Event:
    seq:int
    kind:str
    message:str
    source:str=""
    object_id:str|None=None
    data:dict=field(default_factory=dict)

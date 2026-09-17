from dataclasses import dataclass,field
@dataclass(frozen=True)
class Ipc356Record:
    record_type:str
    net_name:str|None=None
    reference:str|None=None
    pin:str|None=None
    x:float|None=None
    y:float|None=None
    side:str|None=None
    raw:str=""
    attributes:dict=field(default_factory=dict,compare=False)

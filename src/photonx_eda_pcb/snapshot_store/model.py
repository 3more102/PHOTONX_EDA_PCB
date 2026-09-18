from dataclasses import dataclass
@dataclass(frozen=True)
class Snapshot:
    id:str
    parent_id:str|None
    payload:str
    sha256:str
    label:str=""

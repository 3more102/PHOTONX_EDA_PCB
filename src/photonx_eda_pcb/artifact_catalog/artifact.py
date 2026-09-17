from dataclasses import dataclass,field
@dataclass(frozen=True)
class Artifact:
    name:str;kind:str;path:str;sha256:str|None=None;producer:str|None=None;inputs:tuple[str,...]=();metadata:dict=field(default_factory=dict)

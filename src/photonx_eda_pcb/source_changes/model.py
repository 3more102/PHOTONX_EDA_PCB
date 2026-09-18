from dataclasses import dataclass,field
@dataclass(frozen=True)
class SourceState:
    path:str
    sha256:str
    size:int=0
    role:str="unknown"
@dataclass(frozen=True)
class SourceChange:
    path:str
    change_type:str
    before:SourceState|None=None
    after:SourceState|None=None
@dataclass
class ChangeSet:
    changes:list[SourceChange]=field(default_factory=list)

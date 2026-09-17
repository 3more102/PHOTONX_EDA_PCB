from dataclasses import dataclass,field
@dataclass(frozen=True)
class SourceFile:
    path:str
    role:str
    checksum:str|None=None
@dataclass
class ProjectManifest:
    name:str
    sources:list[SourceFile]=field(default_factory=list)
    metadata:dict=field(default_factory=dict)

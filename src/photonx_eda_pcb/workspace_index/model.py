from dataclasses import dataclass,field
@dataclass(frozen=True)
class IndexedArtifact:
    path:str
    role:str
    size:int=0
    sha256:str=""
    tags:tuple[str,...]=()
@dataclass
class WorkspaceIndex:
    artifacts:list[IndexedArtifact]=field(default_factory=list)
    metadata:dict[str,object]=field(default_factory=dict)

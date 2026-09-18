from dataclasses import dataclass,field
@dataclass(frozen=True)
class ReleaseArtifact:
    path:str
    role:str
    sha256:str
    size:int=0
@dataclass
class ReleaseManifest:
    version:str
    commit:str
    artifacts:list[ReleaseArtifact]=field(default_factory=list)
    metadata:dict[str,object]=field(default_factory=dict)

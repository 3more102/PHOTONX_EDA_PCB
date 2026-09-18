from dataclasses import dataclass,field
@dataclass(frozen=True)
class ProjectArtifact:
    role:str
    path:str
    sha256:str=""
    required:bool=False
@dataclass
class ProjectFile:
    name:str
    schema_version:int=1
    artifacts:list[ProjectArtifact]=field(default_factory=list)
    settings:dict[str,object]=field(default_factory=dict)
    metadata:dict[str,object]=field(default_factory=dict)

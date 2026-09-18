from dataclasses import dataclass,field
@dataclass(frozen=True)
class BundleEntry:
    path:str
    role:str
    content:str
    sha256:str
@dataclass
class ArtifactBundle:
    name:str
    entries:list[BundleEntry]=field(default_factory=list)
    metadata:dict[str,object]=field(default_factory=dict)

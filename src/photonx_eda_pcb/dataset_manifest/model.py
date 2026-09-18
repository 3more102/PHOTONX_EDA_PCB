from dataclasses import dataclass,field
@dataclass(frozen=True)
class DatasetFile:
    path:str
    role:str
    sha256:str=""
    bytes:int=0
@dataclass(frozen=True)
class DatasetCase:
    id:str
    files:tuple[DatasetFile,...]
    synthetic:bool=True
    license:str=""
    source:str=""
    intentionally_unknown:tuple[str,...]=()
@dataclass
class DatasetManifest:
    name:str
    version:str
    cases:list[DatasetCase]=field(default_factory=list)

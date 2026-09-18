from dataclasses import dataclass,field
@dataclass(frozen=True)
class PackageRequirement:
    role:str
    minimum:int=1
    required:bool=True
@dataclass
class PackageAssessment:
    present:dict[str,int]=field(default_factory=dict)
    missing:list[str]=field(default_factory=list)
    blockers:list[str]=field(default_factory=list)
    warnings:list[str]=field(default_factory=list)

from dataclasses import dataclass,field
@dataclass
class ReleaseCandidate:
    name:str
    commit:str
    artifacts:list=field(default_factory=list)
    metadata:dict=field(default_factory=dict)
@dataclass(frozen=True)
class ReleaseCandidateDecision:
    name:str
    passed:bool
    blockers:tuple[str,...]
    warnings:tuple[str,...]

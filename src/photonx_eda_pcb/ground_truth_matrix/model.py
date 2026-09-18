from dataclasses import dataclass,field
@dataclass(frozen=True)
class GroundTruthCase:
    id:str
    expected:dict
    observed:dict
    tolerances:dict=field(default_factory=dict)
@dataclass(frozen=True)
class GroundTruthResult:
    id:str
    passed:bool
    mismatches:tuple[str,...]=()

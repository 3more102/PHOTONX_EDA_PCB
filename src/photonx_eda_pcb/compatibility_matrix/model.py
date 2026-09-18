from dataclasses import dataclass,field
@dataclass(frozen=True)
class CompatibilityEntry:
    feature:str
    format:str
    status:str
    notes:str=""
    tests:tuple[str,...]=()
@dataclass
class CompatibilityMatrix:
    entries:list[CompatibilityEntry]=field(default_factory=list)

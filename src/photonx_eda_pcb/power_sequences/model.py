from dataclasses import dataclass
@dataclass(frozen=True)
class SequenceConstraint:
    before:str
    after:str
    reason:str
    confidence:float
    evidence:tuple[str,...]=()

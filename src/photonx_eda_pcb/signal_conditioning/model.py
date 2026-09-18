from dataclasses import dataclass
@dataclass(frozen=True)
class ConditioningStage:
    id:str
    kind:str
    components:tuple[str,...]
    nets:tuple[str,...]
    confidence:float
    evidence:tuple[str,...]=()

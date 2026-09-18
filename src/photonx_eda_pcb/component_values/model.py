from dataclasses import dataclass
@dataclass(frozen=True)
class ValueHypothesis:
    component_id:str
    value:str|None
    confidence:float
    evidence:tuple[str,...]=()

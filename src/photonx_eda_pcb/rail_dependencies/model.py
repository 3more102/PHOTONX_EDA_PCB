from dataclasses import dataclass
@dataclass(frozen=True)
class RailDependency:
    upstream:str
    downstream:str
    via_component:str
    relation:str
    confidence:float
    evidence:tuple[str,...]=()

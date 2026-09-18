from dataclasses import dataclass
@dataclass(frozen=True)
class FunctionalBlock:
    id:str
    components:tuple[str,...]
    nets:tuple[str,...]
    kind:str
    confidence:float
    evidence:tuple[str,...]=()

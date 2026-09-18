from dataclasses import dataclass
@dataclass(frozen=True)
class LengthGroup:
    name:str
    nets:tuple[str,...]
    target_mm:float|None
    tolerance_mm:float|None
    kind:str
    confidence:float

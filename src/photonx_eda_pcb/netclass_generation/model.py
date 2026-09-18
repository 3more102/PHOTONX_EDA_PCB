from dataclasses import dataclass
@dataclass(frozen=True)
class GeneratedNetClass:
    name:str
    nets:tuple[str,...]
    min_width_mm:float
    clearance_mm:float
    confidence:float
    source_roles:tuple[str,...]=()

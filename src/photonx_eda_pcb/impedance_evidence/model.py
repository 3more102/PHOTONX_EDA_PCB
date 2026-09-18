from dataclasses import dataclass
@dataclass(frozen=True)
class ImpedanceEvidence:
    net_id:str
    estimated_ohms:float|None
    confidence:float
    assumptions:tuple[str,...]=()

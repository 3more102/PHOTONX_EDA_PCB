from dataclasses import dataclass,field
from photonx_eda_pcb.provenance import Provenance
@dataclass(frozen=True)
class SlotFeature:
    id:str
    start:tuple[float,float]
    end:tuple[float,float]
    width_mm:float
    plated:str="unknown"
    tool:str|None=None
    provenance:Provenance=field(default_factory=Provenance,compare=False)
@dataclass(frozen=True)
class MechanicalHole:
    id:str
    center:tuple[float,float]
    diameter_mm:float
    plated:str="non-plated"
    tool:str|None=None
    provenance:Provenance=field(default_factory=Provenance,compare=False)

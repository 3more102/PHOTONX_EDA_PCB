from dataclasses import dataclass,field
@dataclass(frozen=True)
class DdrLane:
    name:str
    nets:tuple[str,...]
    role:str
    confidence:float
@dataclass
class DdrTopology:
    lanes:list[DdrLane]=field(default_factory=list)
    controller:str|None=None
    memories:list[str]=field(default_factory=list)
    confidence:float=0.0
    evidence:list[str]=field(default_factory=list)

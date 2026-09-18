from dataclasses import dataclass,field
@dataclass(frozen=True)
class MaskOpening:
    id:str
    center:tuple[float,float]
    size:tuple[float,float]
    layer:str
    source_id:str|None=None
@dataclass
class MaskResult:
    openings:list[MaskOpening]=field(default_factory=list)
    confidence:float=0.0
    evidence:list[str]=field(default_factory=list)

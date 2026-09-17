from dataclasses import dataclass,field

@dataclass
class FootprintReconstruction:
    id:str
    pad_ids:list[str]
    reference:str|None=None
    value:str|None=None
    package_hint:str|None=None
    orientation_deg:float=0.0
    confidence:float=0.0
    evidence:list[str]=field(default_factory=list)

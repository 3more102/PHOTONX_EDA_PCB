from dataclasses import dataclass,field
@dataclass
class ReturnPathEvidence:
    net_id:str
    reference_plane:str|None=None
    continuity_score:float=0.0
    via_penalty:float=0.0
    split_crossings:int=0
    confidence:float=0.0
    evidence:list[str]=field(default_factory=list)

from dataclasses import dataclass,field
@dataclass
class DifferentialPairQuality:
    positive_net:str
    negative_net:str
    score:float
    skew_mm:float
    spacing_variation_mm:float
    via_mismatch:int
    confidence:float=0.0
    notes:list[str]=field(default_factory=list)

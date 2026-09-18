from dataclasses import dataclass,field
@dataclass
class RuleProfile:
    name:str
    min_track_mm:float=.15
    min_clearance_mm:float=.15
    min_drill_mm:float=.2
    min_annular_mm:float=.1
    min_mask_sliver_mm:float=.1
    net_overrides:dict[str,dict[str,float]]=field(default_factory=dict)

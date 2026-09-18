from dataclasses import dataclass
@dataclass(frozen=True)
class FabricationMetrics:
    track_count:int=0
    min_track_mm:float|None=None
    min_clearance_mm:float|None=None
    drill_count:int=0
    min_drill_mm:float|None=None
    via_count:int=0
    board_area_mm2:float|None=None
    acute_features:int=0
@dataclass(frozen=True)
class YieldRisk:
    score:float
    level:str
    drivers:tuple[str,...]=()

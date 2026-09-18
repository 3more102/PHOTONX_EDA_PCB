from dataclasses import dataclass
@dataclass(frozen=True)
class DrcIssue: severity:str; code:str; message:str; object_ids:tuple[str,...]=()
@dataclass(frozen=True)
class DrcConfig:
    min_track_width_mm:float=0.15
    min_drill_mm:float=0.2
    min_annular_ring_mm:float=0.1
    min_clearance_mm:float=0.15
    edge_clearance_mm:float=0.2
    min_drill_copper_clearance_mm:float=0.15
    min_mechanical_copper_clearance_mm:float=0.15

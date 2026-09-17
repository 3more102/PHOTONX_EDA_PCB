from dataclasses import dataclass

@dataclass(frozen=True)
class FabricationRules:
    min_track_mm:float=0.15
    min_clearance_mm:float=0.15
    min_drill_mm:float=0.2
    min_annular_mm:float=0.1
    max_board_width_mm:float|None=None
    max_board_height_mm:float|None=None

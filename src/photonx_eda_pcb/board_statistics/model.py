from dataclasses import dataclass
@dataclass(frozen=True)
class BoardStats:
    tracks:int
    pads:int
    drills:int
    outline_segments:int
    nets:int
    components:int
    total_track_length_mm:float
    board_width_mm:float|None=None
    board_height_mm:float|None=None

from dataclasses import dataclass


@dataclass(frozen=True)
class BoardStats:
    tracks: int
    pads: int
    drills: int
    outline_segments: int
    nets: int
    components: int
    total_track_length_mm: float
    board_width_mm: float | None = None
    board_height_mm: float | None = None
    # Extended physical-evidence statistics are appended with defaults so the
    # historical positional constructor remains backward compatible.
    slots: int = 0
    routes: int = 0
    regions: int = 0
    diagnostics: int = 0
    route_length_mm: float = 0.0
    outline_length_mm: float = 0.0

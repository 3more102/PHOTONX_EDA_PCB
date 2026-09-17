from __future__ import annotations
from math import hypot
from ..models import BoardModel
from ..provenance import Evidence


def attach_drills(board: BoardModel, tolerance_mm: float = 0.15) -> int:
    attached = 0
    for pad in board.pads:
        candidates = []
        for drill in board.drills:
            d = hypot(pad.center.x - drill.center.x, pad.center.y - drill.center.y)
            if d <= tolerance_mm: candidates.append((d, drill))
        if not candidates: continue
        _, drill = min(candidates, key=lambda item: item[0]); pad.drill = drill.diameter
        pad.provenance.add_evidence(Evidence("drill_overlap", f"matched {drill.id} within tolerance", 0.98, drill.provenance.sources[0] if drill.provenance.sources else None)); attached += 1
    return attached

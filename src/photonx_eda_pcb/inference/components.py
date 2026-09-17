from __future__ import annotations
from math import hypot
from ..ids import stable_id
from ..models import BoardModel, ComponentHypothesis


def infer_component_hypotheses(board: BoardModel, max_pair_distance_mm: float = 4.0) -> list[ComponentHypothesis]:
    remaining = {p.id: p for p in board.pads}; result = []
    while remaining:
        a_id = sorted(remaining)[0]; a = remaining.pop(a_id); nearest = None
        for b_id, b in remaining.items():
            distance = hypot(a.center.x - b.center.x, a.center.y - b.center.y)
            if distance <= max_pair_distance_mm and (nearest is None or distance < nearest[0]): nearest = (distance, b_id, b)
        if nearest is None:
            result.append(ComponentHypothesis(stable_id("cmp", a_id), [a_id], "unresolved_pad", 0.15, ["no nearby pad partner"])); continue
        distance, b_id, b = nearest; remaining.pop(b_id); both_drilled = a.drill is not None and b.drill is not None; same_layer = a.layer == b.layer
        confidence = 0.35 + (0.15 if both_drilled else 0.0) + (0.10 if same_layer else 0.0)
        kind = "two_pin_through_hole_candidate" if both_drilled else "two_pad_component_candidate"
        evidence = [f"pad pitch {distance:.3f} mm", "both pads have drill evidence" if both_drilled else "no complete drill evidence", f"layers: {a.layer}, {b.layer}"]
        result.append(ComponentHypothesis(stable_id("cmp", a_id, b_id), sorted([a_id, b_id]), kind, confidence, evidence))
    board.components = result; return result

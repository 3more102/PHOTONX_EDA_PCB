from __future__ import annotations
from math import hypot
from ..ids import stable_id
from ..models import BoardModel,ComponentHypothesis
from ..spatial_connectivity.points import build_point_index,radius_query

def _make_pair(a,b,distance):
    both_drilled=a.drill is not None and b.drill is not None;same_layer=a.layer==b.layer
    confidence=.35+(.15 if both_drilled else 0.0)+(.10 if same_layer else 0.0)
    kind="two_pin_through_hole_candidate" if both_drilled else "two_pad_component_candidate"
    evidence=[f"pad pitch {distance:.3f} mm","both pads have drill evidence" if both_drilled else "no complete drill evidence",f"layers: {a.layer}, {b.layer}"]
    return ComponentHypothesis(stable_id("cmp",a.id,b.id),sorted([a.id,b.id]),kind,confidence,evidence)

def infer_component_hypotheses_bruteforce(board:BoardModel,max_pair_distance_mm:float=4.0)->list[ComponentHypothesis]:
    remaining={p.id:p for p in board.pads};result=[]
    while remaining:
        a_id=sorted(remaining)[0];a=remaining.pop(a_id);nearest=None
        for b_id,b in remaining.items():
            distance=hypot(a.center.x-b.center.x,a.center.y-b.center.y)
            if distance<=max_pair_distance_mm and (nearest is None or (distance,b_id)<(nearest[0],nearest[1])):nearest=(distance,b_id,b)
        if nearest is None:
            result.append(ComponentHypothesis(stable_id("cmp",a_id),[a_id],"unresolved_pad",.15,["no nearby pad partner"]));continue
        distance,b_id,b=nearest;remaining.pop(b_id);result.append(_make_pair(a,b,distance))
    board.components=result;return result

def infer_component_hypotheses(board:BoardModel,max_pair_distance_mm:float=4.0,*,use_spatial_index:bool=True,cell_size_mm:float|None=None)->list[ComponentHypothesis]:
    if not use_spatial_index:return infer_component_hypotheses_bruteforce(board,max_pair_distance_mm)
    pads=list(board.pads);by={p.id:p for p in pads};remaining=set(by);result=[]
    if not pads:
        board.components=[];return []
    idx=build_point_index(((p.id,p) for p in pads),lambda p:(p.center.x,p.center.y),float(cell_size_mm or max(1.0,max_pair_distance_mm)))
    while remaining:
        a_id=min(remaining);remaining.remove(a_id);a=by[a_id]
        nearest=next(((d,bid) for d,bid in radius_query(idx,a.center.x,a.center.y,max_pair_distance_mm) if bid in remaining),None)
        if nearest is None:
            result.append(ComponentHypothesis(stable_id("cmp",a_id),[a_id],"unresolved_pad",.15,["no nearby pad partner"]));continue
        distance,b_id=nearest;remaining.remove(b_id);result.append(_make_pair(a,by[b_id],distance))
    board.components=result;return result

from __future__ import annotations
from math import hypot
from ..ids import stable_id
from ..models import BoardModel,ComponentHypothesis
from ..spatial_connectivity.points import build_point_index,radius_queries

_X2_COMPONENT_REFDES_KIND="gerber_x2_component_refdes"

def _make_pair(a,b,distance):
    both_drilled=a.drill is not None and b.drill is not None;same_layer=a.layer==b.layer
    confidence=.35+(.15 if both_drilled else 0.0)+(.10 if same_layer else 0.0)
    kind="two_pin_through_hole_candidate" if both_drilled else "two_pad_component_candidate"
    evidence=[f"pad pitch {distance:.3f} mm","both pads have drill evidence" if both_drilled else "no complete drill evidence",f"layers: {a.layer}, {b.layer}"]
    return ComponentHypothesis(stable_id("cmp",a.id,b.id),sorted([a.id,b.id]),kind,confidence,evidence)

def _x2_refdes_values(pad):
    provenance=getattr(pad,"provenance",None)
    evidence=getattr(provenance,"evidence",()) if provenance is not None else ()
    return {
        item.detail
        for item in evidence
        if getattr(item,"kind",None)==_X2_COMPONENT_REFDES_KIND
        and isinstance(getattr(item,"detail",None),str)
        and item.detail
    }

def _connected_pad_groups(pads,max_gap_mm):
    remaining={p.id:p for p in pads};groups=[]
    while remaining:
        seed_id=min(remaining);group=[remaining.pop(seed_id)];changed=True
        while changed:
            changed=False
            for pid in sorted(tuple(remaining)):
                pad=remaining[pid]
                if any(hypot(pad.center.x-other.center.x,pad.center.y-other.center.y)<=max_gap_mm for other in group):
                    group.append(remaining.pop(pid));changed=True
        groups.append(sorted(group,key=lambda p:p.id))
    return groups

def _source_x2_components(pads,max_gap_mm):
    by_refdes={};residual=[];ambiguous_refdes=set()
    for pad in pads:
        values=_x2_refdes_values(pad)
        if len(values)==1:
            refdes=next(iter(values));by_refdes.setdefault(refdes,[]).append(pad)
        else:
            residual.append(pad);ambiguous_refdes.update(values)
    components=[]
    for refdes in sorted(by_refdes):
        group=sorted(by_refdes[refdes],key=lambda p:p.id)
        if refdes in ambiguous_refdes:
            residual.extend(group);continue
        connected=_connected_pad_groups(group,max_gap_mm)
        if len(connected)!=1:
            residual.extend(group);continue
        pad_ids=[p.id for p in connected[0]]
        components.append(
            ComponentHypothesis(
                stable_id("cmp","x2",refdes,tuple(pad_ids)),
                pad_ids,
                "x2_component_candidate",
                1.0,
                [
                    f"Gerber X2 TO.P identifies reference {refdes}",
                    f"{len(pad_ids)} pad(s) carry consistent source component evidence",
                ],
                reference=refdes,
            )
        )
    return components,sorted(residual,key=lambda p:p.id)

def infer_component_hypotheses_bruteforce(board:BoardModel,max_pair_distance_mm:float=4.0)->list[ComponentHypothesis]:
    source_components,residual=_source_x2_components(list(board.pads),max_pair_distance_mm)
    remaining={p.id:p for p in residual};result=list(source_components)
    while remaining:
        a_id=sorted(remaining)[0];a=remaining.pop(a_id);nearest=None
        for b_id,b in remaining.items():
            distance=hypot(a.center.x-b.center.x,a.center.y-b.center.y)
            if distance<=max_pair_distance_mm and (nearest is None or (distance,b_id)<(nearest[0],nearest[1])):nearest=(distance,b_id,b)
        if nearest is None:
            result.append(ComponentHypothesis(stable_id("cmp",a_id),[a_id],"unresolved_pad",.15,["no nearby pad partner"]));continue
        distance,b_id,b=nearest;remaining.pop(b_id);result.append(_make_pair(a,b,distance))
    board.components=result;return result

def infer_component_hypotheses(board:BoardModel,max_pair_distance_mm:float=4.0,*,use_spatial_index:bool=True,cell_size_mm:float|None=None,backend:str="auto")->list[ComponentHypothesis]:
    if not use_spatial_index:return infer_component_hypotheses_bruteforce(board,max_pair_distance_mm)
    source_components,pads=_source_x2_components(list(board.pads),max_pair_distance_mm)
    by={p.id:p for p in pads};remaining=set(by);result=list(source_components)
    if not pads:
        board.components=result;return result
    idx=build_point_index(((p.id,p) for p in pads),lambda p:(p.center.x,p.center.y),float(cell_size_mm or max(1.0,max_pair_distance_mm)))
    neighbor_lists=radius_queries(idx,((p.center.x,p.center.y,max_pair_distance_mm) for p in pads),backend=backend)
    neighbors={p.id:items for p,items in zip(pads,neighbor_lists)}
    while remaining:
        a_id=min(remaining);remaining.remove(a_id);a=by[a_id]
        nearest=next(((d,bid) for d,bid in neighbors[a_id] if bid in remaining),None)
        if nearest is None:
            result.append(ComponentHypothesis(stable_id("cmp",a_id),[a_id],"unresolved_pad",.15,["no nearby pad partner"]));continue
        distance,b_id=nearest;remaining.remove(b_id);result.append(_make_pair(a,by[b_id],distance))
    board.components=result;return result

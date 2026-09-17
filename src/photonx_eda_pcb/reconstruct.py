from __future__ import annotations
from math import hypot
import networkx as nx
from shapely.geometry import Point as SPoint, LineString
from .models import BoardModel, ComponentHypothesis


def _shape(obj):
    if hasattr(obj,'start'):
        return LineString([(obj.start.x,obj.start.y),(obj.end.x,obj.end.y)]).buffer(obj.width/2, cap_style=1)
    return SPoint(obj.center.x,obj.center.y).buffer(obj.diameter/2)


def attach_drills(board: BoardModel, tolerance=0.2):
    for pad in board.pads:
        for hole in board.holes:
            if hypot(pad.center.x-hole.center.x,pad.center.y-hole.center.y) <= tolerance:
                pad.drill=hole.diameter
                break


def reconstruct_connectivity(board: BoardModel, tolerance=0.03):
    objs=[*board.pads,*board.tracks]
    g=nx.Graph()
    for o in objs: g.add_node(o.id)
    shapes={o.id:_shape(o) for o in objs}
    for i,a in enumerate(objs):
        for b in objs[i+1:]:
            if a.layer != b.layer: continue
            if shapes[a.id].buffer(tolerance).intersects(shapes[b.id]):
                g.add_edge(a.id,b.id)
    board.nets={}
    for n,comp in enumerate(nx.connected_components(g), start=1):
        name=f"N$${n}"
        ids=sorted(comp)
        board.nets[name]=ids
        for o in objs:
            if o.id in comp: o.net=name
    return g


def infer_components(board: BoardModel, pair_distance=4.0):
    remaining=set(p.id for p in board.pads)
    pads={p.id:p for p in board.pads}
    comps=[]; ci=1
    while remaining:
        a_id=min(remaining); remaining.remove(a_id); a=pads[a_id]
        near=[]
        for b_id in remaining:
            b=pads[b_id]
            d=hypot(a.center.x-b.center.x,a.center.y-b.center.y)
            if d <= pair_distance: near.append((d,b_id))
        if near:
            d,b_id=min(near); remaining.remove(b_id)
            b=pads[b_id]
            through=a.drill is not None and b.drill is not None
            kind="2-pin THT device" if through else "2-pad SMD device"
            conf=0.62 if through else 0.55
            evidence=[f"two pads separated by {d:.2f} mm", "both pads drilled" if through else "surface pads"]
            comps.append(ComponentHypothesis(f"C?{ci}",[a_id,b_id],kind,conf,evidence)); ci+=1
        else:
            comps.append(ComponentHypothesis(f"C?{ci}",[a_id],"unresolved single pad",0.25,["no nearby partner pad"])); ci+=1
    board.components=comps
    return comps

from __future__ import annotations
import networkx as nx
from .geometry import copper_shape
from .spatial import layer_candidate_pairs
from ..models import BoardModel

def _prepare(board):
    objects=[*board.tracks,*board.pads,*getattr(board,"regions",())]
    g=nx.Graph()
    for obj in objects:g.add_node(obj.id,layer=obj.layer,kind=type(obj).__name__)
    shapes={obj.id:copper_shape(obj) for obj in objects}
    index={obj.id:obj for obj in objects}
    return objects,g,shapes,index

def build_physical_graph_bruteforce(board:BoardModel,tolerance_mm:float=0.03)->nx.Graph:
    objects,g,shapes,_=_prepare(board)
    for i,a in enumerate(objects):
        for b in objects[i+1:]:
            if a.layer!=b.layer:continue
            if shapes[a.id].buffer(tolerance_mm).intersects(shapes[b.id]):
                g.add_edge(a.id,b.id,reason="geometry_touch")
    return g

def build_physical_graph(board:BoardModel,tolerance_mm:float=0.03,*,use_spatial_index:bool=True,cell_size_mm:float|None=None)->nx.Graph:
    if not use_spatial_index:return build_physical_graph_bruteforce(board,tolerance_mm)
    objects,g,shapes,index=_prepare(board)
    for aid,bid in layer_candidate_pairs(objects,shapes,tolerance_mm,cell_size_mm):
        a=index[aid];b=index[bid]
        if a.layer!=b.layer:continue
        if shapes[aid].buffer(tolerance_mm).intersects(shapes[bid]):
            g.add_edge(aid,bid,reason="geometry_touch")
    return g

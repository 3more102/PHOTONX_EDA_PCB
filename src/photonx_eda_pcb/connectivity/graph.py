from __future__ import annotations
import networkx as nx
from .geometry import copper_shape
from ..models import BoardModel


def build_physical_graph(board: BoardModel, tolerance_mm: float = 0.03) -> nx.Graph:
    objects = [*board.tracks, *board.pads]
    g = nx.Graph()
    for obj in objects: g.add_node(obj.id, layer=obj.layer, kind=type(obj).__name__)
    shapes = {obj.id: copper_shape(obj) for obj in objects}
    for i, a in enumerate(objects):
        for b in objects[i + 1:]:
            if a.layer != b.layer: continue
            if shapes[a.id].buffer(tolerance_mm).intersects(shapes[b.id]): g.add_edge(a.id, b.id, reason="geometry_touch")
    return g

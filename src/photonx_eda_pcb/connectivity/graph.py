from __future__ import annotations

import networkx as nx

from .geometry import copper_shape
from .spatial import layer_candidate_pairs
from ..models import BoardModel


def _prepare(board):
    objects = [*board.tracks, *board.pads, *getattr(board, "regions", ())]
    graph = nx.Graph()
    for obj in objects:
        graph.add_node(obj.id, layer=obj.layer, kind=type(obj).__name__)
    shapes = {obj.id: copper_shape(obj) for obj in objects}
    index = {obj.id: obj for obj in objects}
    return objects, graph, shapes, index


def _add_proven_via_edges(graph, index, via_spans):
    for span in via_spans or ():
        if not bool(getattr(span, "proven", False)):
            continue
        from_layer = getattr(span, "from_layer", None)
        to_layer = getattr(span, "to_layer", None)
        if from_layer is None or to_layer is None or from_layer == to_layer:
            continue

        pad_ids = sorted(
            {
                pad_id
                for pad_id in getattr(span, "pad_ids", ())
                if pad_id in index
            }
        )
        for i, left_id in enumerate(pad_ids):
            left = index[left_id]
            for right_id in pad_ids[i + 1 :]:
                right = index[right_id]
                if left.layer == right.layer:
                    continue
                graph.add_edge(
                    left_id,
                    right_id,
                    reason="plated_via_span",
                    drill_id=str(span.drill_id),
                    from_layer=str(from_layer),
                    to_layer=str(to_layer),
                    confidence=float(span.confidence),
                    evidence=tuple(getattr(span, "evidence", ())),
                )


def build_physical_graph_bruteforce(
    board: BoardModel,
    tolerance_mm: float = 0.03,
    *,
    via_spans=None,
) -> nx.Graph:
    objects, graph, shapes, index = _prepare(board)
    for i, left in enumerate(objects):
        for right in objects[i + 1 :]:
            if left.layer != right.layer:
                continue
            if shapes[left.id].buffer(tolerance_mm).intersects(shapes[right.id]):
                graph.add_edge(left.id, right.id, reason="geometry_touch")
    _add_proven_via_edges(graph, index, via_spans)
    return graph


def build_physical_graph(
    board: BoardModel,
    tolerance_mm: float = 0.03,
    *,
    use_spatial_index: bool = True,
    cell_size_mm: float | None = None,
    via_spans=None,
) -> nx.Graph:
    if not use_spatial_index:
        return build_physical_graph_bruteforce(
            board,
            tolerance_mm,
            via_spans=via_spans,
        )

    objects, graph, shapes, index = _prepare(board)
    for left_id, right_id in layer_candidate_pairs(
        objects,
        shapes,
        tolerance_mm,
        cell_size_mm,
    ):
        left = index[left_id]
        right = index[right_id]
        if left.layer != right.layer:
            continue
        if shapes[left_id].buffer(tolerance_mm).intersects(shapes[right_id]):
            graph.add_edge(left_id, right_id, reason="geometry_touch")

    _add_proven_via_edges(graph, index, via_spans)
    return graph

from __future__ import annotations

import math

import networkx as nx

from .geometry import copper_shape
from .spatial import layer_candidate_pairs
from ..geometry_kernel.drills import drill_shape
from ..models import BoardModel


def _prepare(board):
    objects = [*board.tracks, *board.pads, *getattr(board, "regions", ())]
    graph = nx.Graph()
    for obj in objects:
        graph.add_node(obj.id, layer=obj.layer, kind=type(obj).__name__)
    shapes = {obj.id: copper_shape(obj) for obj in objects}
    index = {obj.id: obj for obj in objects}
    return objects, graph, shapes, index


def _barrel_contact_drill(board, drill_id):
    drill = next((item for item in board.drills if item.id == drill_id), None)
    if drill is None or getattr(drill, "plating", None) != "plated":
        return None
    try:
        diameter = float(drill.diameter)
        x = float(drill.center.x)
        y = float(drill.center.y)
    except (TypeError, ValueError, AttributeError):
        return None
    if diameter <= 0.0 or not all(math.isfinite(v) for v in (diameter, x, y)):
        return None
    return drill


def _add_proven_via_edges(
    graph,
    index,
    shapes,
    board,
    via_spans,
    tolerance_mm,
):
    for span in via_spans or ():
        if not bool(getattr(span, "proven", False)):
            continue
        from_layer = getattr(span, "from_layer", None)
        to_layer = getattr(span, "to_layer", None)
        if from_layer is None or to_layer is None or from_layer == to_layer:
            continue

        span_layers = tuple(
            dict.fromkeys(
                layer
                for layer in getattr(span, "layers", lambda: ())()
                if layer is not None
            )
        )
        if len(span_layers) < 2:
            span_layers = tuple(dict.fromkeys((from_layer, to_layer)))
        span_layer_set = set(span_layers)

        pad_ids = {
            pad_id
            for pad_id in getattr(span, "pad_ids", ())
            if pad_id in index and index[pad_id].layer in span_layer_set
        }
        contact_ids = set(pad_ids)

        drill_id = str(getattr(span, "drill_id", ""))
        drill = _barrel_contact_drill(board, drill_id)
        if drill is not None:
            barrel = drill_shape(drill)
            for object_id, obj in index.items():
                if obj.layer not in span_layer_set:
                    continue
                if shapes[object_id].buffer(tolerance_mm).intersects(barrel):
                    contact_ids.add(object_id)

        ordered_ids = sorted(contact_ids)
        for i, left_id in enumerate(ordered_ids):
            left = index[left_id]
            for right_id in ordered_ids[i + 1 :]:
                right = index[right_id]
                if left.layer == right.layer:
                    continue
                graph.add_edge(
                    left_id,
                    right_id,
                    reason="plated_via_span",
                    drill_id=drill_id,
                    from_layer=str(from_layer),
                    to_layer=str(to_layer),
                    confidence=float(span.confidence),
                    evidence=tuple(getattr(span, "evidence", ())),
                    contact=(
                        "pad_span"
                        if left_id in pad_ids and right_id in pad_ids
                        else "barrel_touch"
                    ),
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
    _add_proven_via_edges(
        graph,
        index,
        shapes,
        board,
        via_spans,
        tolerance_mm,
    )
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

    _add_proven_via_edges(
        graph,
        index,
        shapes,
        board,
        via_spans,
        tolerance_mm,
    )
    return graph

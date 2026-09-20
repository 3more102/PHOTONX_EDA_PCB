from __future__ import annotations

import math

import networkx as nx

from .geometry import copper_shape
from .spatial import layer_candidate_pairs
from ..geometry_kernel import drill_shape
from ..models import BoardModel, CopperRegion, Track


def _prepare(board):
    objects = [*board.tracks, *board.pads, *getattr(board, "regions", ())]
    graph = nx.Graph()
    for obj in objects:
        graph.add_node(obj.id, layer=obj.layer, kind=type(obj).__name__)
    shapes = {obj.id: copper_shape(obj) for obj in objects}
    index = {obj.id: obj for obj in objects}
    return objects, graph, shapes, index


def _span_layer_names(span, index):
    names = tuple(getattr(span, "layer_names", ()) or ())
    if names:
        return names

    fallback = []
    for layer in (
        getattr(span, "from_layer", None),
        getattr(span, "to_layer", None),
    ):
        if layer is not None and layer not in fallback:
            fallback.append(layer)
    for pad_id in getattr(span, "pad_ids", ()):
        pad = index.get(pad_id)
        layer = getattr(pad, "layer", None)
        if layer is not None and layer not in fallback:
            fallback.append(layer)
    return tuple(fallback)


def _valid_plated_drill(drill):
    if drill is None or getattr(drill, "plating", None) != "plated":
        return False
    try:
        diameter = float(drill.diameter)
        x = float(drill.center.x)
        y = float(drill.center.y)
    except (AttributeError, TypeError, ValueError):
        return False
    return (
        math.isfinite(diameter)
        and diameter > 0.0
        and math.isfinite(x)
        and math.isfinite(y)
    )


def _barrel_contact_ids(
    index,
    shapes,
    drill,
    span_layers,
    tolerance_mm,
):
    barrel = drill_shape(drill)
    contacts = set()
    for object_id, obj in index.items():
        if not isinstance(obj, (Track, CopperRegion)):
            continue
        if obj.layer not in span_layers:
            continue
        if shapes[object_id].buffer(tolerance_mm).intersects(barrel):
            contacts.add(object_id)
    return contacts


def _add_proven_via_edges(
    graph,
    index,
    shapes,
    board,
    via_spans,
    tolerance_mm,
):
    drills = {drill.id: drill for drill in board.drills}
    for span in via_spans or ():
        if not bool(getattr(span, "proven", False)):
            continue
        from_layer = getattr(span, "from_layer", None)
        to_layer = getattr(span, "to_layer", None)
        if from_layer is None or to_layer is None or from_layer == to_layer:
            continue

        drill = drills.get(str(getattr(span, "drill_id", "")))
        if not _valid_plated_drill(drill):
            continue

        span_layers = set(_span_layer_names(span, index))
        if from_layer not in span_layers or to_layer not in span_layers:
            continue

        evidence_pad_ids = sorted(
            {
                pad_id
                for pad_id in getattr(span, "pad_ids", ())
                if pad_id in index
                and getattr(index[pad_id], "layer", None) in span_layers
            }
        )
        if len({index[pad_id].layer for pad_id in evidence_pad_ids}) < 2:
            continue

        barrel_contact_ids = _barrel_contact_ids(
            index,
            shapes,
            drill,
            span_layers,
            tolerance_mm,
        )
        connected_ids = sorted(set(evidence_pad_ids) | barrel_contact_ids)

        for i, left_id in enumerate(connected_ids):
            left = index[left_id]
            for right_id in connected_ids[i + 1 :]:
                right = index[right_id]
                if left.layer == right.layer:
                    continue
                reason = (
                    "plated_via_span"
                    if left_id in evidence_pad_ids and right_id in evidence_pad_ids
                    else "plated_via_barrel_contact"
                )
                graph.add_edge(
                    left_id,
                    right_id,
                    reason=reason,
                    drill_id=str(span.drill_id),
                    from_layer=str(from_layer),
                    to_layer=str(to_layer),
                    confidence=float(span.confidence),
                    evidence=tuple(getattr(span, "evidence", ())),
                    evidence_pad_ids=tuple(evidence_pad_ids),
                    barrel_contact_ids=tuple(sorted(barrel_contact_ids)),
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

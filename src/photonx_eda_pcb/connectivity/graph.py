from __future__ import annotations
import networkx as nx
from .geometry import copper_shape
from .spatial import layer_candidate_pairs
from ..copper_solver.barrel import barrel_is_electrical, barrel_layers
from ..models import BoardModel
from ..stackup import infer_stackup
from ..via_span.candidates import (
    build_pad_candidate_index,
    pads_near_drill,
    pads_near_drill_bruteforce,
)


def _prepare(board):
    objects = [*board.tracks, *board.pads, *getattr(board, "regions", ())]
    g = nx.Graph()
    for obj in objects:
        g.add_node(obj.id, layer=obj.layer, kind=type(obj).__name__)
    shapes = {obj.id: copper_shape(obj) for obj in objects}
    index = {obj.id: obj for obj in objects}
    return objects, g, shapes, index


def _add_proven_barrel_edges(
    board: BoardModel,
    graph: nx.Graph,
    tolerance_mm: float,
    *,
    use_spatial_index: bool,
    cell_size_mm: float | None = None,
) -> None:
    if not board.drills or not board.pads:
        return

    ordered_layers = infer_stackup(board).copper_layers()
    pad_index = pad_by_id = None
    if use_spatial_index:
        pad_index, pad_by_id = build_pad_candidate_index(
            board, tolerance_mm, cell_size_mm
        )

    for drill in sorted(board.drills, key=lambda obj: obj.id):
        if not barrel_is_electrical(drill):
            continue

        layers = tuple(barrel_layers(drill, ordered_layers))
        if len(layers) < 2:
            continue

        if use_spatial_index:
            pads = pads_near_drill(
                board,
                drill,
                tolerance_mm,
                index=pad_index,
                pad_by_id=pad_by_id,
            )
        else:
            pads = pads_near_drill_bruteforce(board, drill, tolerance_mm)

        layer_set = set(layers)
        pads = [pad for pad in pads if pad.id in graph and pad.layer in layer_set]

        for i, a in enumerate(pads):
            for b in pads[i + 1:]:
                if a.layer == b.layer:
                    continue
                graph.add_edge(
                    a.id,
                    b.id,
                    reason="proven_plated_barrel",
                    drill_id=drill.id,
                    layer_span=layers,
                )


def build_physical_graph_bruteforce(
    board: BoardModel,
    tolerance_mm: float = 0.03,
    *,
    drill_tolerance_mm: float = 0.15,
) -> nx.Graph:
    objects, g, shapes, _ = _prepare(board)
    for i, a in enumerate(objects):
        for b in objects[i + 1:]:
            if a.layer != b.layer:
                continue
            if shapes[a.id].buffer(tolerance_mm).intersects(shapes[b.id]):
                g.add_edge(a.id, b.id, reason="geometry_touch")

    _add_proven_barrel_edges(
        board,
        g,
        drill_tolerance_mm,
        use_spatial_index=False,
    )
    return g


def build_physical_graph(
    board: BoardModel,
    tolerance_mm: float = 0.03,
    *,
    use_spatial_index: bool = True,
    cell_size_mm: float | None = None,
    drill_tolerance_mm: float = 0.15,
) -> nx.Graph:
    if not use_spatial_index:
        return build_physical_graph_bruteforce(
            board,
            tolerance_mm,
            drill_tolerance_mm=drill_tolerance_mm,
        )

    objects, g, shapes, index = _prepare(board)
    for aid, bid in layer_candidate_pairs(
        objects, shapes, tolerance_mm, cell_size_mm
    ):
        a = index[aid]
        b = index[bid]
        if a.layer != b.layer:
            continue
        if shapes[aid].buffer(tolerance_mm).intersects(shapes[bid]):
            g.add_edge(aid, bid, reason="geometry_touch")

    _add_proven_barrel_edges(
        board,
        g,
        drill_tolerance_mm,
        use_spatial_index=True,
        cell_size_mm=cell_size_mm,
    )
    return g

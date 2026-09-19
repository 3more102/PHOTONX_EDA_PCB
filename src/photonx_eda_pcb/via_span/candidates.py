from math import hypot

from photonx_eda_pcb.spatial_connectivity import AABB, SpatialHashIndex, aabb_queries


def _pad_box(p, tolerance_mm):
    r = max(float(tolerance_mm), max(float(p.size_x), float(p.size_y)) / 2)
    return AABB(
        p.center.x - r,
        p.center.y - r,
        p.center.x + r,
        p.center.y + r,
    )


def build_pad_candidate_index(board, tolerance_mm=.15, cell_size_mm=None):
    idx = SpatialHashIndex(float(cell_size_mm or max(1.0, tolerance_mm * 8)))
    for p in board.pads:
        idx.insert(p.id, _pad_box(p, tolerance_mm))
    return idx, {p.id: p for p in board.pads}


def pads_near_drill_bruteforce(board, drill, tolerance_mm=.15):
    out = []
    for p in board.pads:
        r = max(p.size_x, p.size_y) / 2
        if hypot(
            p.center.x - drill.center.x,
            p.center.y - drill.center.y,
        ) <= max(tolerance_mm, r):
            out.append(p)
    return sorted(out, key=lambda p: p.id)


def _filter_pad_candidates(drill, candidate_ids, pad_by_id, tolerance_mm):
    out = []
    for pid in candidate_ids:
        p = pad_by_id[pid]
        r = max(p.size_x, p.size_y) / 2
        if hypot(
            p.center.x - drill.center.x,
            p.center.y - drill.center.y,
        ) <= max(tolerance_mm, r):
            out.append(p)
    return sorted(out, key=lambda p: p.id)


def pads_near_drills(
    board,
    drills,
    tolerance_mm=.15,
    *,
    index=None,
    pad_by_id=None,
    spatial_backend="auto",
):
    drills = list(drills)
    if not drills:
        return []

    if index is None:
        index, pad_by_id = build_pad_candidate_index(board, tolerance_mm)
    elif pad_by_id is None:
        pad_by_id = {p.id: p for p in board.pads}

    query_boxes = (
        AABB(d.center.x, d.center.y, d.center.x, d.center.y)
        for d in drills
    )
    candidate_lists = aabb_queries(
        index,
        query_boxes,
        backend=spatial_backend,
    )
    return [
        _filter_pad_candidates(d, candidate_ids, pad_by_id, tolerance_mm)
        for d, candidate_ids in zip(drills, candidate_lists)
    ]


def pads_near_drill(
    board,
    drill,
    tolerance_mm=.15,
    *,
    index=None,
    pad_by_id=None,
    spatial_backend="auto",
):
    return pads_near_drills(
        board,
        (drill,),
        tolerance_mm,
        index=index,
        pad_by_id=pad_by_id,
        spatial_backend=spatial_backend,
    )[0]

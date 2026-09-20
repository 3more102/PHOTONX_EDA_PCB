from shapely.geometry import Point as SPoint

from photonx_eda_pcb.geometry_kernel import pad_shape
from photonx_eda_pcb.spatial_connectivity import AABB, SpatialHashIndex


def _pad_box(pad, tolerance_mm):
    x0, y0, x1, y1 = pad_shape(pad).bounds
    expand = max(0.0, float(tolerance_mm))
    return AABB(x0 - expand, y0 - expand, x1 + expand, y1 + expand)


def _drill_center_contacts_pad(pad, drill, tolerance_mm):
    copper = pad_shape(pad)
    tolerance = max(0.0, float(tolerance_mm))
    if tolerance:
        copper = copper.buffer(tolerance)
    return copper.covers(SPoint(float(drill.center.x), float(drill.center.y)))


def build_pad_candidate_index(board, tolerance_mm=.15, cell_size_mm=None):
    idx = SpatialHashIndex(float(cell_size_mm or max(1.0, tolerance_mm * 8)))
    for pad in board.pads:
        idx.insert(pad.id, _pad_box(pad, tolerance_mm))
    return idx, {pad.id: pad for pad in board.pads}


def pads_near_drill_bruteforce(board, drill, tolerance_mm=.15):
    return sorted(
        (
            pad
            for pad in board.pads
            if _drill_center_contacts_pad(pad, drill, tolerance_mm)
        ),
        key=lambda pad: pad.id,
    )


def pads_near_drill(
    board,
    drill,
    tolerance_mm=.15,
    *,
    index=None,
    pad_by_id=None,
):
    if index is None:
        index, pad_by_id = build_pad_candidate_index(board, tolerance_mm)

    query = AABB(
        drill.center.x,
        drill.center.y,
        drill.center.x,
        drill.center.y,
    )
    out = []
    for pad_id in index.query(query):
        pad = pad_by_id[pad_id]
        if _drill_center_contacts_pad(pad, drill, tolerance_mm):
            out.append(pad)
    return sorted(out, key=lambda pad: pad.id)

from .model import ViaSpanCandidate
from .candidates import (
    build_pad_candidate_index,
    pads_near_drill_bruteforce,
    pads_near_drills,
)
from .evidence import span_evidence


def resolve_via_spans(
    board,
    stackup,
    tolerance_mm=0.15,
    *,
    use_spatial_index=True,
    cell_size_mm=None,
    spatial_backend="auto",
):
    copper = [x.name for x in stackup.copper_layers()]
    out = []

    if use_spatial_index:
        if board.pads:
            index, pad_by_id = build_pad_candidate_index(
                board,
                tolerance_mm,
                cell_size_mm,
            )
            pad_groups = pads_near_drills(
                board,
                board.drills,
                tolerance_mm,
                index=index,
                pad_by_id=pad_by_id,
                spatial_backend=spatial_backend,
            )
        else:
            pad_groups = [[] for _ in board.drills]
    else:
        pad_groups = [
            pads_near_drill_bruteforce(board, d, tolerance_mm)
            for d in board.drills
        ]

    for d, pads in zip(board.drills, pad_groups):
        layers = [p.layer for p in pads if p.layer in copper]
        uniq = []
        for layer in layers:
            if layer not in uniq:
                uniq.append(layer)

        if len(uniq) >= 2:
            uniq = sorted(uniq, key=copper.index)
            a, b = uniq[0], uniq[-1]
            proven = d.plating == "plated"
            conf = 0.95 if proven else 0.7
        elif len(uniq) == 1:
            a = b = uniq[0]
            proven = False
            conf = 0.35
        else:
            a = b = None
            proven = False
            conf = 0.1

        out.append(
            ViaSpanCandidate(
                d.id,
                a,
                b,
                conf,
                span_evidence(d, pads),
                proven,
            )
        )
    return out

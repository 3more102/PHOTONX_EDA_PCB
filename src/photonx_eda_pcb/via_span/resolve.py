from .model import ViaSpanCandidate
from .candidates import (
    build_pad_candidate_index,
    pads_near_drill,
    pads_near_drill_bruteforce,
)
from .evidence import span_evidence
from ..x2_span import mapped_x2_span_layers


def resolve_via_spans(
    board,
    stackup,
    tolerance_mm=0.15,
    *,
    use_spatial_index=True,
    cell_size_mm=None,
):
    copper = [x.name for x in stackup.copper_layers()]
    out = []
    index = pad_by_id = None
    if use_spatial_index and board.pads:
        index, pad_by_id = build_pad_candidate_index(
            board,
            tolerance_mm,
            cell_size_mm,
        )

    for drill in board.drills:
        drill.layer_span=None
        drill.span_proven=False
        if use_spatial_index:
            pads = pads_near_drill(
                board,
                drill,
                tolerance_mm,
                index=index,
                pad_by_id=pad_by_id,
            )
        else:
            pads = pads_near_drill_bruteforce(
                board,
                drill,
                tolerance_mm,
            )

        mapped_span, span_issue = mapped_x2_span_layers(
            board,
            stackup,
            drill,
        )

        if mapped_span is not None:
            if span_issue is not None:
                copper_pads = []
                from_layer = to_layer = None
                layer_ids = ()
                proven = False
                confidence = 0.1
            else:
                layer_ids = tuple(mapped_span)
                allowed = set(layer_ids)
                copper_pads = [
                    pad
                    for pad in pads
                    if pad.layer in allowed
                ]
                from_layer = layer_ids[0]
                to_layer = layer_ids[-1]
                drill.layer_span=(from_layer,to_layer)
                drill.span_proven=True
                proven = (
                    drill.plating == "plated"
                    and len(layer_ids) >= 2
                )
                confidence = (
                    0.99
                    if proven
                    else (0.97 if drill.plating == "non-plated" else 0.8)
                )
        else:
            copper_pads = [pad for pad in pads if pad.layer in copper]
            layers = [pad.layer for pad in copper_pads]
            uniq = []
            for layer in layers:
                if layer not in uniq:
                    uniq.append(layer)

            if len(uniq) >= 2:
                uniq = sorted(uniq, key=copper.index)
                from_layer, to_layer = uniq[0], uniq[-1]
                lo = copper.index(from_layer)
                hi = copper.index(to_layer)
                layer_ids = tuple(copper[lo : hi + 1])
                proven = drill.plating == "plated"
                confidence = 0.95 if proven else 0.7
            elif len(uniq) == 1:
                from_layer = to_layer = uniq[0]
                layer_ids = (uniq[0],)
                proven = False
                confidence = 0.35
            else:
                from_layer = to_layer = None
                layer_ids = ()
                proven = False
                confidence = 0.1

        out.append(
            ViaSpanCandidate(
                drill.id,
                from_layer,
                to_layer,
                confidence,
                span_evidence(
                    drill,
                    pads,
                    mapped_layer_ids=layer_ids if span_issue is None else (),
                    span_issue=span_issue,
                ),
                proven,
                tuple(sorted(pad.id for pad in copper_pads)),
                layer_ids,
            )
        )
    return out

from .model import ViaSpanCandidate
from .candidates import (
    build_pad_candidate_index,
    pads_near_drill,
    pads_near_drill_bruteforce,
)
from .evidence import span_evidence


def _mapped_x2_span_layers(board, stackup, drill):
    if not bool(getattr(drill, "span_proven", False)):
        return None, None

    declared = getattr(drill, "layer_span", None)
    if declared is None or len(declared) != 2:
        return (), "missing or malformed explicit layer-span tuple"

    try:
        start, end = sorted((int(declared[0]), int(declared[1])))
    except (TypeError, ValueError):
        return (), "non-integer X2 copper-layer ordinal"
    if start < 1 or end <= start:
        return (), f"invalid X2 copper span L{start}..L{end}"

    copper = [item.name for item in stackup.copper_layers()]
    x2_stackup = board.metadata.get("x2_copper_stackup", {})
    if (
        isinstance(x2_stackup, dict)
        and x2_stackup.get("status") == "declared"
    ):
        declared_layers = tuple(
            str(name) for name in x2_stackup.get("layers", ())
        )
        if tuple(copper) != declared_layers:
            return (), "declared X2 stackup does not match resolved copper order"
        if end > len(copper):
            return (
                (),
                (
                    f"declared span L{start}..L{end} exceeds "
                    f"{len(copper)}-layer X2 stackup"
                ),
            )
        return tuple(copper[start - 1 : end]), None

    kind = str(getattr(drill, "span_kind", "") or "").lower()
    if (
        (start, end) == (1, 2)
        and kind in {"pth", "npth"}
        and copper == ["F.Cu", "B.Cu"]
    ):
        return tuple(copper), None

    return (
        (),
        (
            "explicit X2 span cannot be mapped safely without a declared "
            "ordinal copper stackup"
        ),
    )


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

        mapped_span, span_issue = _mapped_x2_span_layers(
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

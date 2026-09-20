def span_evidence(
    drill,
    pads,
    *,
    mapped_layer_ids=(),
    span_issue=None,
):
    ev=[f"drill {drill.id} overlaps {len(pads)} pad candidate(s)"]
    layers=sorted({p.layer for p in pads})
    if layers:
        ev.append("observed layers: "+", ".join(layers))
    if drill.plating!="unknown":
        ev.append(f"plating metadata: {drill.plating}")

    declared=getattr(drill,"x2_layer_span",None)
    if declared is not None:
        lo,hi=declared
        kind=getattr(drill,"x2_span_kind",None)
        detail=f"X2 declared copper span: L{lo}..L{hi}"
        if kind:
            detail+=f" ({kind})"
        ev.append(detail)
        if mapped_layer_ids:
            ev.append(
                "X2 mapped copper span: "+", ".join(mapped_layer_ids)
            )
        if span_issue:
            ev.append("X2 span unresolved: "+str(span_issue))
    return ev

from photonx_eda_pcb.excellon_routing import assess_route_export_readiness


def route_omission_manifest(board):
    readiness=assess_route_export_readiness(getattr(board,"routes",()))
    return {
        "exported_routes":list(readiness.exportable),
        "omitted_routes":list(readiness.omitted),
        "reasons":dict(readiness.reasons),
    }


def validate_route_omission_manifest(data):
    exported=list(data.get("exported_routes",()))
    ids=list(data.get("omitted_routes",()))
    reasons=data.get("reasons",{})
    issues=[]
    if len(exported)!=len(set(exported)):issues.append("ROUTE_EXPORT_DUPLICATE_ID")
    if len(ids)!=len(set(ids)):issues.append("ROUTE_OMISSION_DUPLICATE_ID")
    if set(exported)&set(ids):issues.append("ROUTE_BOTH_EXPORTED_AND_OMITTED")
    for rid in ids:
        if rid not in reasons:issues.append("ROUTE_OMISSION_WITHOUT_REASON")
    return issues

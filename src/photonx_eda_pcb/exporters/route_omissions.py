def route_omission_manifest(board):
    routes=getattr(board,"routes",())
    return {"omitted_routes":[r.id for r in routes],"reasons":{r.id:"KICAD_ARBITRARY_ROUTE_UNSUPPORTED" for r in routes}}
def validate_route_omission_manifest(data):
    ids=list(data.get("omitted_routes",()))
    reasons=data.get("reasons",{})
    issues=[]
    if len(ids)!=len(set(ids)):issues.append("ROUTE_OMISSION_DUPLICATE_ID")
    for rid in ids:
        if rid not in reasons:issues.append("ROUTE_OMISSION_WITHOUT_REASON")
    return issues

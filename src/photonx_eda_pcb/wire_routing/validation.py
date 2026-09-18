def validate_route(r):
    issues=[]
    if len(r.points)<2:issues.append("WIRE_ROUTE_TOO_SHORT")
    if not 0<=r.confidence<=1:issues.append("WIRE_ROUTE_CONFIDENCE_RANGE")
    for a,b in zip(r.points,r.points[1:]):
        if a[0]!=b[0] and a[1]!=b[1]:issues.append("WIRE_ROUTE_NON_ORTHOGONAL")
    return issues

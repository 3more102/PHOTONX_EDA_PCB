def validate_route(route):
    issues=[]
    if not route.id:issues.append("ROUTE_ID_EMPTY")
    if route.width_mm<=0:issues.append("ROUTE_WIDTH_NONPOSITIVE")
    if len(route.points)<2:issues.append("ROUTE_TOO_SHORT")
    if route.plated not in {"unknown","plated","non-plated","non_plated"}:issues.append("ROUTE_PLATING_INVALID")
    for a,b in zip(route.points,route.points[1:]):
        if a==b:issues.append("ROUTE_ZERO_LENGTH_SEGMENT")
    return issues

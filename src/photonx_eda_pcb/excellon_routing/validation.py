from ..core.numeric import is_finite_number

def validate_route(route):
    issues=[]
    if not route.id:issues.append("ROUTE_ID_EMPTY")
    if not is_finite_number(route.width_mm):issues.append("ROUTE_WIDTH_NONFINITE")
    elif route.width_mm<=0:issues.append("ROUTE_WIDTH_NONPOSITIVE")
    if len(route.points)<2:issues.append("ROUTE_TOO_SHORT")
    if route.plated not in {"unknown","plated","non-plated","non_plated"}:issues.append("ROUTE_PLATING_INVALID")
    if not all(
        isinstance(point,(tuple,list))
        and len(point)==2
        and all(is_finite_number(value) for value in point)
        for point in route.points
    ):
        issues.append("ROUTE_COORDINATE_INVALID")
    for a,b in zip(route.points,route.points[1:]):
        if a==b:issues.append("ROUTE_ZERO_LENGTH_SEGMENT")
    return issues

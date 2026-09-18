from .metrics import polygon_area
def validate_polygon(points):
    issues=[]
    if len(points)<3:issues.append("POLYGON_TOO_FEW_POINTS")
    elif polygon_area(points)<=0:issues.append("POLYGON_ZERO_AREA")
    return issues

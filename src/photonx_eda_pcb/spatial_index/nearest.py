from math import hypot
def nearest_point(origin,points):
    items=list(points)
    if not items:return None
    return min(items,key=lambda point:(hypot(point.x-origin.x,point.y-origin.y),point.x,point.y))

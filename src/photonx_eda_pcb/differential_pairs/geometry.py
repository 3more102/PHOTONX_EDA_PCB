from math import hypot
def polyline_length(points):
    return sum(hypot(b[0]-a[0],b[1]-a[1]) for a,b in zip(points,points[1:]))
def endpoint_distance(a,b):
    return hypot(float(a[0])-float(b[0]),float(a[1])-float(b[1]))

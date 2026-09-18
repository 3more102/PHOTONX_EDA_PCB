from math import hypot
def excess_length(points):
    if len(points)<2:return 0.0
    routed=sum(hypot(b[0]-a[0],b[1]-a[1]) for a,b in zip(points,points[1:]))
    direct=hypot(points[-1][0]-points[0][0],points[-1][1]-points[0][1])
    return max(0.0,routed-direct)

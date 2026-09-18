from math import hypot
def polygon_area(points):
    pts=list(points)
    return abs(0.5*sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts))))
def polygon_perimeter(points):
    pts=list(points)
    return sum(hypot(pts[(i+1)%len(pts)][0]-pts[i][0],pts[(i+1)%len(pts)][1]-pts[i][1]) for i in range(len(pts)))
